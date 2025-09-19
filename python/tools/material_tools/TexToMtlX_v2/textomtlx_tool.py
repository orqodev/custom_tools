import os
import re
import time
import logging
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

import hou
from PySide6 import QtWidgets, QtCore, QtGui
try:
    import PyOpenColorIO as ocio
except Exception:
    ocio = None

# v2 shared config/resolver
from .txmtlx_config import (
    TEXTURE_EXT,
    TEXTURE_TYPE,
    TEXTURE_TYPE_SORTED,
    SIZE_PATTERN,
    DEFAULT_DROP_TOKENS,
    WORKER_FRACTION,
    DEFAULT_IMAKETX_PATH,
    DEFAULT_MATLIB_PREFIX,
    MATLIB_NAME_PREFIX,
    UI_CONFIG,
)
from .mtx_cs_resolver import (
    UDIM_PATTERN,
    guess_semantics_and_colorspace,
    case_insensitive_replace,
    replace_udim_token,
    normalize_job_path,
    slugify,
)


class TexToMtlX(QtWidgets.QMainWindow):
    # Deterministic internal naming for texture->surface mapping
    NAMING_MAP = {
        'color': {'input': 'base_color', 'label': 'basecolor_tex'},
        'metal': {'input': 'metalness', 'label': 'metalness_tex'},
        'rough': {'input': 'specular_roughness', 'label': 'roughness_tex'},
        'specular': {'input': 'specular', 'label': 'specular_tex'},
        'gloss': {'input': 'specular_roughness', 'label': 'gloss_tex'},
        'emission': {'input': 'emission', 'label': 'emission_tex'},
        'alpha': {'input': 'opacity', 'label': 'opacity_tex'},
        'transmission': {'input': 'transmission', 'label': 'transmission_tex'},
        'sss': {'input': 'subsurface_color', 'label': 'sss_tex'},
        'displacement': {'input': None, 'label': 'displacement_tex'},
        'normal': {'input': None, 'label': 'normal_tex'},
        'bump': {'input': None, 'label': 'bump_tex'},
        'ao': {'input': None, 'label': 'ao_tex'},
        'mask': {'input': None, 'label': 'mask_tex'},
    }
    def __init__(self):
        super().__init__()
        self.setWindowTitle(UI_CONFIG.get("window_title", "TexToMtlX v2"))
        w, h = UI_CONFIG.get("window_size", (600, 800))
        self.resize(w, h)
        try:
            self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        except Exception:
            pass

        # State
        self.texture_list = {}
        self.node_lib = None
        self.node_path = None
        self.mtlTX = False
        self.report_success = []
        self.report_failures = {}

        self._build_ui()
        self._add_help_menu()
        self._connect()
        self.init_constants()
        self._detect_renderers()

    # ---------- Init/Config ----------
    def init_constants(self):
        # Use shared config and patterns
        self.TEXTURE_EXT = TEXTURE_EXT
        self.TEXTURE_TYPE_SORTED = TEXTURE_TYPE_SORTED
        self.SIZE_PATTERN = SIZE_PATTERN
        self.UDIM_PATTERN = UDIM_PATTERN
        # workers
        max_workers = max(1, os.cpu_count() or 1)
        self.WORKER_LIMIT = max(1, int(max_workers * WORKER_FRACTION))
        # imaketx
        hb = hou.text.expandString("$HB")
        self.imaketx_path = os.path.join(hb, "imaketx").replace(os.sep, "/") if hb else DEFAULT_IMAKETX_PATH

    def _detect_renderers(self):
        # karma is always available in Solaris context
        self.arnold_available = False
        detected_paths = False
        detected_node = False
        try:
            # Detect by houdiniPath for HtoA package
            for p in hou.houdiniPath():
                if "htoa" in p:
                    detected_paths = True
                    break
        except Exception:
            detected_paths = False
        try:
            # Detect by node type availability in MAT context
            mat_cat = hou.nodeTypeCategories().get('Mat')
            if mat_cat and hou.nodeType(mat_cat, 'arnold_materialbuilder') is not None:
                detected_node = True
        except Exception:
            detected_node = False
        self.arnold_available = bool(detected_paths or detected_node)
        # Reflect UI state
        self.cb_renderer_arnold.setEnabled(self.arnold_available)
        if not self.arnold_available:
            self.cb_renderer_arnold.setChecked(False)
            self.cb_renderer_arnold.setToolTip("Arnold (HtoA) not detected. Ensure the HtoA plugin is installed/enabled or that 'arnold_materialbuilder' node type is available.")
        else:
            self.cb_renderer_arnold.setToolTip("Arnold detected. Enable to also build an Arnold material variant.")

    # ---------- UI ----------
    def _build_ui(self):
        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)
        root = QtWidgets.QVBoxLayout(cw)

        # Material lib row
        row1 = QtWidgets.QHBoxLayout()
        self.bt_pick_lib = QtWidgets.QPushButton("Pick Material Library")
        self.bt_open_folder = QtWidgets.QPushButton("Open Texture Folder(s)")
        self.bt_open_folder.setEnabled(False)
        row1.addWidget(self.bt_pick_lib)
        row1.addWidget(self.bt_open_folder)
        root.addLayout(row1)

        # Options row
        opt = QtWidgets.QHBoxLayout()
        self.cb_tx = QtWidgets.QCheckBox("Convert to TX")
        self.cb_tx.setEnabled(False)
        opt.addWidget(self.cb_tx)

        # Renderer options
        render_group = QtWidgets.QGroupBox("Renderer Options")
        rg_l = QtWidgets.QHBoxLayout(render_group)
        self.cb_renderer_karma = QtWidgets.QCheckBox("Karma")
        self.cb_renderer_karma.setChecked(True)
        self.cb_renderer_arnold = QtWidgets.QCheckBox("Arnold")
        rg_l.addWidget(self.cb_renderer_karma)
        rg_l.addWidget(self.cb_renderer_arnold)
        opt.addWidget(render_group)
        root.addLayout(opt)

        # Optional features (default off) - true collapsed section
        # Master toggle lives in root; options live in a group box hidden by default
        self.cb_enable_optional = QtWidgets.QCheckBox("Enable Optional Features")
        self.cb_enable_optional.setChecked(False)
        root.addWidget(self.cb_enable_optional)

        self.optional_group = QtWidgets.QGroupBox("Optional Features")
        opt_container_layout = QtWidgets.QGridLayout(self.optional_group)
        self.cb_stage_matlib = QtWidgets.QCheckBox("Create/Reuse /stage Material Library")
        self.cb_collect = QtWidgets.QCheckBox("Create Collect Node (if both renderers)")
        self.cb_disp_remap = QtWidgets.QCheckBox("Enable Displacement Remap")
        self.sp_disp_scale = QtWidgets.QDoubleSpinBox()
        self.sp_disp_scale.setRange(-1000, 1000)
        self.sp_disp_scale.setDecimals(4)
        self.sp_disp_scale.setSingleStep(0.01)
        self.sp_disp_scale.setValue(0.1)
        self.sp_remap_low = QtWidgets.QDoubleSpinBox(); self.sp_remap_low.setRange(-1000, 1000); self.sp_remap_low.setValue(-0.5)
        self.sp_remap_high = QtWidgets.QDoubleSpinBox(); self.sp_remap_high.setRange(-1000, 1000); self.sp_remap_high.setValue(0.5)
        opt_container_layout.addWidget(QtWidgets.QLabel("Displacement Scale"), 0, 0)
        opt_container_layout.addWidget(self.sp_disp_scale, 0, 1)
        opt_container_layout.addWidget(self.cb_disp_remap, 1, 0, 1, 2)
        opt_container_layout.addWidget(QtWidgets.QLabel("Remap Low"), 2, 0)
        opt_container_layout.addWidget(self.sp_remap_low, 2, 1)
        opt_container_layout.addWidget(QtWidgets.QLabel("Remap High"), 3, 0)
        opt_container_layout.addWidget(self.sp_remap_high, 3, 1)
        opt_container_layout.addWidget(self.cb_stage_matlib, 4, 0, 1, 2)
        opt_container_layout.addWidget(self.cb_collect, 5, 0, 1, 2)
        root.addWidget(self.optional_group)

        # Initialize collapsed: hide entire group and disable its children
        def _set_optional_enabled(enabled: bool):
            self.optional_group.setVisible(enabled)
            for w in self.optional_group.findChildren(QtWidgets.QWidget):
                w.setEnabled(enabled)
        _set_optional_enabled(False)
        self.cb_enable_optional.toggled.connect(_set_optional_enabled)

        # Sanitization
        self.cb_sanitize = QtWidgets.QCheckBox("Sanitize Material Names")
        self.cb_sanitize.setChecked(True)
        self.le_drop_tokens = QtWidgets.QLineEdit(",".join(DEFAULT_DROP_TOKENS[:5]))
        san_row = QtWidgets.QHBoxLayout()
        san_row.addWidget(self.cb_sanitize)
        san_row.addWidget(QtWidgets.QLabel("Drop tokens (comma separated)"))
        san_row.addWidget(self.le_drop_tokens)
        root.addLayout(san_row)

        # Material list
        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel("Materials found:"))
        self.bt_all = QtWidgets.QPushButton("All")
        self.bt_none = QtWidgets.QPushButton("None")
        self.bt_all.setEnabled(False); self.bt_none.setEnabled(False)
        header.addWidget(self.bt_all); header.addWidget(self.bt_none)
        root.addLayout(header)

        self.list_view = QtWidgets.QListView()
        self.list_model = QtGui.QStandardItemModel()
        self.list_view.setModel(self.list_model)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        root.addWidget(self.list_view)

        # Run
        self.bt_create = QtWidgets.QPushButton("Create Materials")
        self.bt_create.setEnabled(False)
        self.progress = QtWidgets.QProgressBar()
        root.addWidget(self.bt_create)
        root.addWidget(self.progress)

    def _connect(self):
        self.bt_pick_lib.clicked.connect(self._pick_material_lib)
        self.bt_open_folder.clicked.connect(self._pick_folders)
        self.cb_tx.stateChanged.connect(lambda s: setattr(self, 'mtlTX', s == QtCore.Qt.Checked))
        self.bt_all.clicked.connect(self._select_all)
        self.bt_none.clicked.connect(self._select_none)
        self.bt_create.clicked.connect(self._create_selected)

    # ---------- Picking ----------
    def _pick_material_lib(self):
        node_path = hou.ui.selectNode(title="Select Material Library (/mat, matnet or materiallibrary)", node_type_filter=hou.nodeTypeFilter.ShopMaterial)
        if not node_path:
            return
        node = hou.node(node_path)
        if not node or node.isInsideLockedHDA():
            hou.ui.displayMessage("Invalid or locked material library.", severity=hou.severityType.Error)
            return
        self.node_path = node_path
        self.node_lib = node
        self.bt_open_folder.setEnabled(True)
        self.cb_tx.setEnabled(True)

    def _pick_folders(self):
        self.texture_list.clear()
        self.list_model.clear()
        self.progress.setValue(0)
        folders = hou.ui._selectFile(title="Select texture folder(s)", file_type=hou.fileType.Directory, multiple_select=True)
        if not folders:
            return
        folder_paths = [hou.text.expandString(f.strip()) for f in folders.split(';') if f.strip()]
        for folder in folder_paths:
            self._scan_folder(folder)
        if self.texture_list:
            self.bt_create.setEnabled(True)
            self.bt_all.setEnabled(True)
            self.bt_none.setEnabled(True)
            for mat in sorted(self.texture_list.keys()):
                item = QtGui.QStandardItem(mat)
                item.setEditable(False)
                self.list_model.appendRow(item)

    # ---------- Scan ----------
    def _scan_folder(self, folder: str):
        if not os.path.isdir(folder):
            return
        tex_dict = defaultdict(lambda: defaultdict(list))
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        for file in files:
            low = file.lower()
            _, ext = os.path.splitext(low)
            if ext not in self.TEXTURE_EXT:
                continue
            if "_" not in file:
                continue
            # Determine material name and type by token occurrences
            name_wo_ext = os.path.splitext(file)[0]
            parts = name_wo_ext.split("_")
            material_name = slugify(parts[0])
            detected_type = None
            split_idx = None
            for t_type, cfg in TEXTURE_TYPE.items():
                for tok in cfg["tokens"]:
                    if tok.lower().strip("_") in [p.lower() for p in parts[1:]]:
                        detected_type = t_type
                        # material name is everything before this token occurrence
                        try:
                            split_idx = next(i for i, p in enumerate(parts) if p.lower() == tok.lower().strip("_"))
                        except StopIteration:
                            split_idx = None
                        break
                if detected_type:
                    break
            if not detected_type:
                continue
            # Build prefix up to split point and drop color-space tokens and extra separators
            if split_idx is not None and split_idx > 0:
                prefix = "_".join(parts[:split_idx])
            else:
                prefix = parts[0]
            # Normalize separators like " - " first
            prefix = re.sub(r"\s*-\s*", "_", prefix)
            # Remove color space tags
            CS_TAG_RX = re.compile(r"(?i)\b(srgb|acescg|aces|linear|scene[-_ ]?linear|raw)\b")
            prefix = CS_TAG_RX.sub("", prefix)
            # Collapse underscores
            prefix = re.sub(r"[_\s]+", "_", prefix).strip("_")
            material_name = slugify(prefix) or material_name

            tex_dict[material_name][detected_type].append(file)
            tex_dict[material_name]['UDIM'] = bool(self.UDIM_PATTERN.search(file))
            tex_dict[material_name]['FOLDER_PATH'] = folder
            size_m = self.SIZE_PATTERN.search(file)
            if size_m:
                tex_dict[material_name]['Size'] = size_m.group(1)
        # merge
        for k, v in tex_dict.items():
            self.texture_list[k] = dict(v)

    # ---------- Creation flow ----------
    def _select_all(self):
        sm = self.list_view.selectionModel()
        for r in range(self.list_model.rowCount()):
            idx = self.list_model.index(r, 0)
            sm.select(idx, QtCore.QItemSelectionModel.Select)

    def _select_none(self):
        self.list_view.clearSelection()

    def _create_selected(self):
        idxs = self.list_view.selectedIndexes()
        if not idxs:
            hou.ui.displayMessage("Select at least one material.", severity=hou.severityType.Error)
            return
        self.report_success = []
        self.report_failures = {}
        self.progress.setMaximum(len(idxs))
        # sanitization
        drop_tokens = set()
        if self.cb_sanitize.isChecked() and self.le_drop_tokens.text().strip():
            drop_tokens = {t.strip().lower() for t in self.le_drop_tokens.text().split(',') if t.strip()}
        sanitize = {"enabled": self.cb_sanitize.isChecked(), "drop_tokens": drop_tokens}

        for n, idx in enumerate(idxs, 1):
            mat = self.list_model.itemFromIndex(idx).text()
            try:
                self._create_material(mat, sanitize)
                self.report_success.append(mat)
            except Exception as e:
                self.report_failures[mat] = str(e)
            self.progress.setValue(n)
        self._show_report()

    def _create_material(self, mat_name: str, sanitize_options: dict):
        info = self.texture_list.get(mat_name)
        if not info:
            raise RuntimeError("Missing texture info")
        # Pre-TX conversion list
        if self.mtlTX:
            all_src = []
            for k, v in info.items():
                if k in ("UDIM", "Size", "FOLDER_PATH"):
                    continue
                if isinstance(v, list):
                    all_src.extend([os.path.join(info['FOLDER_PATH'], f) for f in v])
            self._convert_to_tx(all_src)

        # Create subnet (MaterialX-first) in chosen library or stage material library
        context_node = self.node_lib
        matlib_node = None
        if self.cb_stage_matlib.isChecked():
            # only if we are in /stage context
            stage = hou.node('/stage')
            if stage:
                lib_name = f"{MATLIB_NAME_PREFIX}_{os.path.basename(info['FOLDER_PATH']).strip() or 'Tex'}"
                matlib_node = stage.node(lib_name) or stage.createNode('materiallibrary', lib_name)
                matlib_node.parm('matpathprefix').set(DEFAULT_MATLIB_PREFIX)
                context_node = matlib_node
        subnet = self._create_material_subnet(context_node, mat_name, info, sanitize_options)
        mtlx_surf, mtlx_disp = self._create_main_nodes(subnet, mat_name)
        place2d = self._setup_place2d(subnet, info)

        # Process textures (MaterialX/Karma path)
        self._process_textures(subnet, mtlx_surf, mtlx_disp, info, place2d)
        self._setup_bump_normal(subnet, mtlx_surf, info, place2d)
        subnet.layoutChildren()
        context_node.layoutChildren()

        # Optional Arnold path
        arnold_node = None
        if self.cb_renderer_arnold.isChecked() and self.arnold_available:
            arnold_node = self._build_arnold_network(context_node, mat_name, info)

        # If both exist and collect wanted
        if self.cb_collect.isChecked() and (arnold_node is not None) and (subnet is not None):
            try:
                # top-level collect uses slugified material to match assignment conventions
                collect = context_node.createNode('collect', slugify(mat_name))
                collect.setInput(0, subnet)
                collect.setInput(1, arnold_node)
            except Exception:
                pass

    # ---------- TX conversion ----------
    def _convert_to_tx(self, abs_paths):
        if not abs_paths:
            return
        logger = logging.getLogger("TX_CONVERSION_V2")
        logger.setLevel(logging.INFO)

        def convert_single(pth):
            t0 = time.time()
            try:
                out = os.path.splitext(pth)[0] + ".tx"
                cmd = f'"{self.imaketx_path}" "{pth}" "{out}" "--newer"'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                ok = res.returncode == 0
                if not ok:
                    logger.error(f"Failed TX: {pth} -> {res.stderr}")
                return ok
            except Exception as e:
                logger.error(f"Error TX {pth}: {e}")
                return False

        futures = []
        ok_count = 0
        fail_count = 0
        with ThreadPoolExecutor(max_workers=self.WORKER_LIMIT) as ex:
            for p in abs_paths:
                futures.append(ex.submit(convert_single, p))
            for fut in as_completed(futures):
                try:
                    if fut.result():
                        ok_count += 1
                    else:
                        fail_count += 1
                except Exception:
                    fail_count += 1
        return ok_count > 0 and fail_count == 0

    # ---------- Subnet/Nodes ----------
    def _create_material_subnet(self, context_node, mat_name, info, sanitize_options):
        canonical = mat_name
        pre = canonical
        if sanitize_options.get('enabled'):
            canonical = slugify(mat_name)
            drops = sanitize_options.get('drop_tokens') or set()
            if drops:
                for d in drops:
                    canonical = canonical.replace(d, "")
                canonical = slugify(canonical)
        # finalize canonical with CS token stripping, size attach rule and tail cleanup
        canonical = self._finalize_canonical(canonical, info)
        try:
            print(f"[TexToMtlX] canonical: pre='{pre}' -> post='{canonical}' size='{info.get('Size','')}'")
        except Exception:
            pass
        old = context_node.node(canonical)
        if old:
            old.destroy()
        subnet = context_node.createNode('subnet', canonical)
        # clean default items
        for it in list(subnet.allItems()):
            try:
                it.destroy()
            except Exception:
                pass
        # setup parms similar to legacy (MaterialX-first)
        # Keep minimal to avoid bloat; Solaris recognizes outputs by subnetconnector
        subnet.setMaterialFlag(True)
        return subnet

    # ---- Canonical material name finalization ----
    def _finalize_canonical(self, name: str, info: dict) -> str:
        # Remove color-space tokens and tidy separators
        CS_TAG_RX = re.compile(r"(?i)\b(srgb|acescg|aces|linear|scene[-_ ]?linear|raw)\b")
        n = CS_TAG_RX.sub("", name)
        n = re.sub(r"[_\s]+", "_", n).strip("_")
        # Only attach size if truly like '1k', '2k', etc.
        sz = info.get('Size')
        if sz and re.match(r"(?i)^\d{1,2}k$", sz):
            n_with_size = f"{n}_{sz.lower()}"
        else:
            n_with_size = n
        # Keep vNNN tails
        if re.search(r"(?i)(?:^|_)(v\d{2,4})$", n_with_size):
            return n_with_size
        # Keep real size tails
        if re.search(r"(?i)_\d{1,2}k$", n_with_size):
            return n_with_size
        # Drop accidental trailing plain number (not vNNN, not size)
        n_with_size = re.sub(r"(?<!v)(?:^|_)\d{2,4}$", "", n_with_size).strip("_")
        return n_with_size

    def _create_main_nodes(self, subnet, mat_name):
        # v1 naming: keep readable suffixes without slugifying internal node names
        surf = subnet.createNode('mtlxstandard_surface', 'mtlxSurface')
        disp = subnet.createNode('mtlxdisplacement', 'mtlxDisplacement')
        out_surface = self._create_output(subnet, 'surface')
        out_disp = self._create_output(subnet, 'displacement')
        out_surface.setInput(0, surf)
        out_disp.setInput(0, disp)
        return surf, disp

    def _create_output(self, subnet, kind):
        # v1 naming for outputs
        node = subnet.createNode('subnetconnector', f"{kind}_output")
        node.parm('connectorkind').set('output')
        node.parm('parmname').set(kind)
        node.parm('parmlabel').set(kind.capitalize())
        node.parm('parmtype').set(kind)
        return node

    def _setup_place2d(self, subnet, info):
        if info.get('UDIM', False):
            return None
        coord = subnet.createNode('mtlxtexcoord', 'texcoord')
        scale = subnet.createNode('mtlxconstant', 'scale'); scale.parm('value').set(1)
        rot = subnet.createNode('mtlxconstant', 'rotation')
        off = subnet.createNode('mtlxconstant', 'offset')
        p2d = subnet.createNode('mtlxplace2d', 'place2d')
        p2d.setInput(0, coord)
        p2d.setInput(2, scale)
        p2d.setInput(3, rot)
        p2d.setInput(4, off)
        return p2d

    # ---------- Texture processing ----------
    def _process_textures(self, subnet, surf, disp, info, place2d):
        input_names = surf.inputNames()
        for tex_type, tex_info in self._iterate_textures(info):
            node = self._create_texture_node(subnet, tex_info, info)
            if place2d and not info.get('UDIM', False):
                node.setInput(0, place2d)
            self._connect_texture(node, tex_type, surf, disp, input_names)

    def _iterate_textures(self, info):
        skip = {'UDIM', 'Size', 'FOLDER_PATH', 'normal', 'bump'}
        # If height is being used as bump (because no displacement), record the resolved key to skip from displacement consumption
        height_used_as_bump = None
        if not ('displacement' in info):
            # reuse finder to see if bump would resolve via height
            height_used_as_bump = self._find_tex_key(info, 'bump')
        for k, v in info.items():
            if k in skip:
                continue
            # k is a texture label in original dict, but we have mapping types from TEXTURE_TYPE_SORTED
            for t_type, cfg in self.TEXTURE_TYPE_SORTED:
                tokens = [t.strip('_').lower() for t in cfg['tokens']]
                if any(tok in k.lower() for tok in tokens):
                    # If this candidate is displacement via a height key that was already used as bump, skip it
                    if t_type == 'displacement' and height_used_as_bump and k == height_used_as_bump:
                        continue
                    yield t_type, {
                        'name': k,
                        'file': v[0] if isinstance(v, list) and v else v,
                        'type': t_type,
                    }
                    break

    def _create_texture_node(self, subnet, texture_info, info):
        node_type = 'mtlxtiledimage' if info.get('UDIM', False) else 'mtlximage'
        # Determine deterministic label from NAMING_MAP
        ttype = texture_info['type']
        label = self.NAMING_MAP.get(ttype, {}).get('label', self._safe_human_name(texture_info['name'], subnet))
        # ensure uniqueness but don't slugify arbitrary
        base_label = label
        name = base_label
        i = 1
        while subnet.node(name) is not None:
            i += 1
            name = f"{base_label}_{i}"
        tex_node = subnet.createNode(node_type, name)
        # configure signature/colorspace immediately to avoid Houdini locking
        # file path is needed to choose colorspace only for color maps; normal/data are forced
        file_path = self._get_texture_path(texture_info['name'], info)
        self._configure_texture_node(tex_node, texture_info['type'], file_path)
        # then set file parm
        tex_node.parm('file').set(file_path)
        return tex_node

    # ---------- Naming helpers (v1 internal style) ----------
    def _safe_human_name(self, base_name: str, parent_node):
        # minimal sanitize: non-alnum/underscore -> underscore
        raw = str(base_name)
        safe = re.sub(r"[^A-Za-z0-9_]", "_", raw)
        # prefix if starts with digit
        if safe and safe[0].isdigit():
            safe = "n_" + safe
        # collapse consecutive underscores
        safe = re.sub(r"_+", "_", safe).strip("_") or "node"
        # ensure unique under parent
        if parent_node is not None:
            name = safe
            i = 1
            while parent_node.node(name) is not None:
                i += 1
                name = f"{safe}{i}"
            return name
        return safe

    def _get_texture_path(self, texture_name, info):
        # get first file for this logical texture
        file_rel = None
        # texture_name can be either the type bucket key or original k; try both
        if texture_name in info:
            file_rel = info[texture_name][0] if isinstance(info[texture_name], list) else info[texture_name]
        else:
            # search by best-effort among buckets for a file that matches name
            for k, v in info.items():
                if isinstance(v, list) and v and (texture_name in v or any(texture_name.lower() in f.lower() for f in v)):
                    file_rel = v[0]
                    break
        if not file_rel:
            raise RuntimeError(f"Texture path not found for {texture_name}")
        # TX swap
        if self.mtlTX:
            base, _ = os.path.splitext(file_rel)
            file_rel = base + '.tx'
        folder = info.get('FOLDER_PATH', '')
        # $JOB normalization
        project_path = hou.getenv('JOB') or ''
        normalized_folder = normalize_job_path(folder, project_path) if project_path else folder
        if normalized_folder.endswith('/'):
            normalized_folder = normalized_folder[:-1]
        full = f"{normalized_folder}/{file_rel}"
        # UDIM token replacement (first match)
        if info.get('UDIM', False):
            full = replace_udim_token(full)
        return full

    # ---- Colorspace/signature inference helpers per policies P1-P4 ----
    def _strip_udim(self, basename: str) -> str:
        return re.sub(r'_(\d{4})(?=\.[^.]+$)', '', basename, flags=re.I)

    def _lower_name(self, path: str) -> str:
        return self._strip_udim(os.path.basename(path)).lower()

    def parse_colorspace_from_name(self, path: str):
        name = self._lower_name(path)
        # Order: ACES-ACEScg -> ACEScg -> ACES -> linear -> srgb -> raw
        patterns = [
            (r'(^|[_. -])aces\s*[-]\s*acescg($|[_. -])', 'acescg', 'aces-acescg'),
            (r'(^|[_. -])acescg($|[_. -])', 'acescg', 'acescg'),
            (r'(^|[_. -])aces($|[_. -])', 'aces', 'aces'),
            (r'(^|[_. -])(lin|linear|scene[_ -]?linear)($|[_. -])', 'scene_linear', 'linear'),
            (r'(^|[_. -])s[_ -]?rgb($|[_. -])', 'srgb', 'srgb'),
            (r'(^|[_. -])raw($|[_. -])', 'raw', 'raw'),
        ]
        for rx, intent, tag in patterns:
            if re.search(rx, name, re.I):
                return {"intent": intent, "matched": tag}
        return {"intent": None, "matched": None}

    def _infer_semantics(self, tex_type: str, path: str):
        # T1/T2: determine kind and explicit tag from filename tokens
        name = self._lower_name(path)
        ext = os.path.splitext(name)[1]
        # classify by type tokens first (semantics-first safety)
        if tex_type == 'normal':
            kind = 'normal'
        elif tex_type in ('rough','metal','specular','alpha','ao','mask','bump','displacement','gloss','transmission'):
            kind = 'data'
        else:
            # fallback to filename hints
            if re.search(r'(normal|nrm|nor|nrml)', name, re.I):
                kind = 'normal'
            elif re.search(r'(rough(ness)?|rgh|metal(lic|ness)?|spec(ular)?|alpha|opacity|ao|occlusion|mask|id|height(map)?|disp|displace|dsp)', name, re.I):
                kind = 'data'
            else:
                kind = 'color'
        explicit = self.parse_colorspace_from_name(path)
        intent = explicit["intent"]
        # Map intent to canonical cs for chooser purposes
        map_to_cs = {
            'srgb': 'srgb_texture',
            'scene_linear': 'scene_linear',
            'acescg': 'scene_linear',
            'aces': 'scene_linear',
            'raw': 'raw',
            None: None,
        }
        explicit_cs = map_to_cs.get(intent)
        unsafe_tag = False
        # unsafe if data/normal tries to force srgb/linear
        if kind in ('data','normal') and explicit_cs in ('srgb_texture','scene_linear'):
            unsafe_tag = True
        return {"kind": kind, "explicit_cs": explicit_cs, "intent": intent, "unsafe_tag": unsafe_tag, "ext": ext}

    # ---- OCIO integration ----
    def _load_ocio_config(self):
        if getattr(self, '_ocio_loaded', False):
            return
        self._ocio_loaded = True
        self._ocio_cs_map = {}
        self._ocio_roles = {}
        if ocio is None:
            return
        cfg = None
        try:
            path = os.getenv('OCIO')
            if path and os.path.exists(path):
                cfg = ocio.Config.CreateFromFile(path)
        except Exception:
            cfg = None
        if cfg is None:
            try:
                cfg = ocio.GetCurrentConfig()
            except Exception:
                cfg = None
        if cfg is None:
            return
        try:
            # Collect colorspaces
            for cs in cfg.getColorSpaces():
                name = cs.getName()
                self._ocio_cs_map[name.lower()] = name
            # Collect roles
            for role in ('scene_linear', 'raw', 'data', 'reference', 'compositing_log', 'color_picking', 'default'):    
                try:
                    n = cfg.getRole(role)
                    if n:
                        self._ocio_roles[role] = n
                except Exception:
                    pass
        except Exception:
            pass

    def _map_intent_to_ocio(self, intent: str, kind: str):
        """Return best OCIO colorspace name for intent using active config.
        intent in {'acescg','aces','scene_linear','srgb','raw'}; kind in {'color','data','normal'}.
        """
        self._load_ocio_config()
        if kind in ('data','normal'):
            # Always RAW for safety
            # Prefer role raw
            raw_name = self._ocio_roles.get('raw') or next((v for k,v in self._ocio_cs_map.items() if 'raw' in k), None)
            return raw_name or 'raw'
        if intent is None:
            return None
        lower_names = self._ocio_cs_map
        def find_contains(substrs):
            for k, v in lower_names.items():
                if any(s in k for s in substrs):
                    return v
            return None
        if intent == 'acescg' or intent == 'aces':
            # prefer explicit ACEScg name
            cs = find_contains(['acescg'])
            if cs:
                return cs
            # fall back to scene_linear role
            if 'scene_linear' in self._ocio_roles:
                return self._ocio_roles['scene_linear']
            return None
        if intent == 'scene_linear':
            if 'scene_linear' in self._ocio_roles:
                return self._ocio_roles['scene_linear']
            cs = find_contains(['scene_linear','linear'])
            if cs:
                return cs
            return None
        if intent == 'srgb':
            cs = find_contains(['srgb'])
            if cs:
                return cs
            return None
        if intent == 'raw':
            raw_name = self._ocio_roles.get('raw') or find_contains(['raw'])
            return raw_name or 'raw'
        return None

    def _choose_signature_and_cs(self, kind: str, explicit_cs: str|None, ext: str):
        # T3 rules
        if kind == 'normal':
            return ('color3', 'raw')
        if kind == 'data':
            return ('float', 'raw')
        # color
        if explicit_cs == 'raw':
            return ('color3', 'raw')
        if explicit_cs == 'scene_linear':
            return ('color3', 'scene_linear')
        if explicit_cs == 'srgb_texture':
            return ('color3', 'srgb_texture')
        if ext == '.exr':
            return ('color3', 'scene_linear')
        return ('color3', 'srgb_texture')

    # ---- MtlX filecolorspace menu helpers ----
    def _get_filecolorspace_parm(self, img_node):
        # Prefer 'filecolorspace2' if present (MaterialX nodes with OCIO menu), else fallback
        p = img_node.parm('filecolorspace2')
        if p is not None:
            return p
        return img_node.parm('filecolorspace')

    def _menu_items_labels(self, parm):
        try:
            items = list(parm.menuItems())
            labels = list(parm.menuLabels())
            return items, labels
        except Exception:
            return [], []

    def _pick_menu_value(self, parm, preferred_names):
        # Try to find a menu item that matches any preferred name (exact then substring), against items and labels.
        if parm is None:
            return None
        items, labels = self._menu_items_labels(parm)
        low_items = [i.lower() for i in items]
        low_labels = [l.lower() for l in labels]
        prefs = [p.lower() for p in preferred_names if p]
        # exact match first
        for p in prefs:
            if p in low_items:
                return items[low_items.index(p)]
            if p in low_labels:
                return items[low_labels.index(p)] if low_labels.index(p) < len(items) else None
        # substring match
        for p in prefs:
            for idx, li in enumerate(low_items):
                if p in li:
                    return items[idx]
            for idx, ll in enumerate(low_labels):
                if p in ll:
                    return items[idx] if idx < len(items) else None
        return None

    def _preferred_for_intent(self, intent, ext, kind):
        # Build ranked names for menu matching
        if kind in ('data','normal'):
            return ('Raw','Utility - Raw','raw')
        # Color kinds only
        linear_list = ('ACEScg','acescg','ACES - ACEScg','scene_linear','linear','lin')
        srgb_list = ('sRGB - Texture','sRGB','srgb_texture')
        if intent in ('acescg','aces','scene_linear'):
            return linear_list
        if intent in ('srgb_texture','srgb'):
            return srgb_list
        if intent == 'raw':
            return ('Raw','Utility - Raw','raw')
        # No intent → heuristic by extension
        if ext.lower() == '.exr':
            return linear_list
        return srgb_list

    def apply_mtlx_sig_and_cs(self, img_node, *, kind: str, intent, file_path: str):
        # Set signature first
        sig = 'color3' if kind in ('color','normal') else 'float'
        try:
            if img_node.parm('signature'):
                img_node.parm('signature').set(sig)
        except Exception:
            pass
        # Choose colorspace from node's own menu
        parm = self._get_filecolorspace_parm(img_node)
        if parm is not None:
            prefs = self._preferred_for_intent(intent, os.path.splitext(file_path)[1], kind)
            picked = self._pick_menu_value(parm, prefs)
            if picked is not None:
                try:
                    parm.set(picked)
                except Exception:
                    pass

    def _configure_texture_node(self, node, tex_type, file_path):
        # Compute semantics and route to menu-based setter. Adds warning comment on unsafe tags.
        sem = self._infer_semantics(tex_type, file_path)
        if sem.get('unsafe_tag') and hasattr(node, 'setComment'):
            try:
                node.setComment('Ignored unsafe cs tag for data/normal; forced RAW')
            except Exception:
                pass
        # For normals, ensure kind='normal' so signature=color3 and colorspace RAW are chosen.
        self.apply_mtlx_sig_and_cs(node, kind=sem['kind'], intent=sem.get('intent'), file_path=file_path)

    def _connect_texture(self, texture_node, tex_type, surf, disp, input_names):
        mapping = {
            'color': ('base_color', self._setup_color),
            'metal': ('metalness', self._setup_direct),
            'specular': ('specular', self._setup_direct),
            'rough': ('specular_roughness', self._setup_range),
            'transmission': ('transmission', self._setup_direct),
            'gloss': ('specular_roughness', self._setup_invert_range),
            'emission': ('emission', self._setup_direct_enable_emission),
            'alpha': ('opacity', self._setup_direct),
            'sss': ('subsurface_color', self._setup_color_sss),
        }
        if tex_type in mapping:
            inp_name, func = mapping[tex_type]
            idx = input_names.index(inp_name) if inp_name in input_names else None
            if idx is not None:
                func(texture_node, surf, idx)
        if tex_type == 'displacement':
            self._setup_displacement(texture_node, disp)

    def _setup_color(self, tex_node, surf, idx):
        base = tex_node.name()
        rng = tex_node.parent().createNode('mtlxrange', f"{base}_CC")
        rng.parm('signature').set('color3')
        rng.setInput(0, tex_node)
        surf.setInput(idx, rng)

    def _setup_range(self, tex_node, surf, idx):
        base = tex_node.name()
        rng = tex_node.parent().createNode('mtlxrange', f"{base}_ADJ")
        rng.setInput(0, tex_node)
        surf.setInput(idx, rng)

    def _setup_invert_range(self, tex_node, surf, idx):
        base = tex_node.name()
        rng = tex_node.parent().createNode('mtlxrange', f"{base}_INV")
        rng.parm('outlow').set(1)
        rng.parm('outhigh').set(0)
        rng.setInput(0, tex_node)
        surf.setInput(idx, rng)

    def _setup_color_sss(self, tex_node, surf, idx):
        base = tex_node.name()
        rng = tex_node.parent().createNode('mtlxrange', f"{base}_SSS")
        rng.parm('signature').set('color3')
        rng.setInput(0, tex_node)
        surf.setInput(idx, rng)
        if surf.parm('subsurface'):
            surf.parm('subsurface').set(1)

    def _setup_direct(self, tex_node, surf, idx):
        surf.setInput(idx, tex_node)

    def _setup_direct_enable_emission(self, tex_node, surf, idx):
        surf.setInput(idx, tex_node)
        if surf.parm('emission'):
            surf.parm('emission').set(1)

    def _setup_displacement(self, tex_node, disp):
        disp.parm('scale').set(self.sp_disp_scale.value())
        node_in = tex_node
        if self.sender() is None:
            pass
        if self.cb_disp_remap.isChecked():
            base = tex_node.name()
            remap = tex_node.parent().createNode('mtlxremap', f"{base}_DISP_REMAP")
            remap.parm('outlow').set(self.sp_remap_low.value())
            remap.parm('outhigh').set(self.sp_remap_high.value())
            remap.setInput(0, tex_node)
            node_in = remap
        disp.setInput(0, node_in)

    # ---------- Bump/Normal ----------
    def _find_tex_key(self, info: dict, logical_type: str):
        """Find the actual key name for a logical texture type ('bump' or 'normal').
        Order:
        1) exact key present in info (case-sensitive as stored)
        2) search info.keys() using tokens from TEXTURE_TYPE[logical_type]['tokens'] (case-insensitive contains)
        Special case: when logical_type == 'bump', allow using a 'height' token as bump ONLY if no displacement token/key exists in info.
        Returns the matching key string or None.
        """
        if not info or logical_type not in TEXTURE_TYPE:
            return None
        # 1) exact
        if logical_type in info:
            return logical_type
        lowers = {k.lower(): k for k in info.keys()}
        # 2) token-based search for the requested logical type
        tokens = TEXTURE_TYPE[logical_type].get('tokens', [])
        for tok in tokens:
            t = tok.strip('_').lower()
            for k_lower, orig in lowers.items():
                if t and t in k_lower:
                    return orig
        # 3) height-as-bump fallback: only when searching for bump AND displacement not present
        if logical_type == 'bump':
            has_disp = False
            # check if a displacement key exists directly or via tokens
            if 'displacement' in info:
                has_disp = True
            else:
                disp_tokens = [x.strip('_').lower() for x in TEXTURE_TYPE.get('displacement', {}).get('tokens', [])]
                for dtk in disp_tokens:
                    if any(dtk in k for k in lowers.keys()):
                        has_disp = True
                        break
            if not has_disp:
                # find a height-like key to use as bump
                height_aliases = {'height', 'heightmap'}
                for k_lower, orig in lowers.items():
                    if any(h in k_lower for h in height_aliases):
                        return orig
        return None

    def _setup_bump_normal(self, subnet_context, mtlx_standard_surf, material_lib_info, place2d):
        ''' Setup the bump and normal textures nodes and connections'''
        # Node type: use tiledimage for UDIM sets, single-image otherwise
        node_type = "mtlxtiledimage" if material_lib_info.get("UDIM", False) else "mtlximage"


        input_names = mtlx_standard_surf.inputNames()
        # Resolve bump/normal keys using the new helper
        bump_key = self._find_tex_key(material_lib_info, 'bump')
        normal_key = self._find_tex_key(material_lib_info, 'normal')
        if not bump_key and not normal_key:
            return

        # Create deterministic image node names using NAMING_MAP labels with uniqueness
        def _unique_name(parent, base):
            name = base
            i = 1
            while parent.node(name) is not None:
                i += 1
                name = f"{base}_{i}"
            return name

        def _create_bump_from_key(key):
            bump_node = subnet_context.createNode("mtlxbump", 'mtlxBump')
            base_label = self.NAMING_MAP.get('bump', {}).get('label', 'bump_tex')
            bump_image = subnet_context.createNode(node_type, _unique_name(subnet_context, base_label))
            bump_path = self._get_texture_path(key, material_lib_info)
            self._configure_texture_node(bump_image, 'bump', bump_path)
            bump_image.parm("file").set(bump_path)
            if place2d and not material_lib_info.get("UDIM", False):
                bump_image.setInput(0, place2d)
            bump_node.setInput(0, bump_image)
            return bump_node

        def _create_normal_from_key(key):
            normal_node = subnet_context.createNode("mtlxnormalmap", 'mtlxNormal')
            base_label = self.NAMING_MAP.get('normal', {}).get('label', 'normal_tex')
            normal_image = subnet_context.createNode(node_type, _unique_name(subnet_context, base_label))
            normal_path = self._get_texture_path(key, material_lib_info)
            self._configure_texture_node(normal_image, 'normal', normal_path)
            normal_image.parm("file").set(normal_path)
            if place2d and not material_lib_info.get("UDIM", False):
                normal_image.setInput(0, place2d)
            normal_node.setInput(0, normal_image)
            return normal_node

        # Build graph
        if bump_key and normal_key:
            bump_node = _create_bump_from_key(bump_key)
            normal_node = _create_normal_from_key(normal_key)
            bump_node.setInput(2, normal_node)
            if 'normal' in input_names:
                mtlx_standard_surf.setInput(input_names.index('normal'), bump_node)
        elif bump_key:
            bump_node = _create_bump_from_key(bump_key)
            if 'normal' in input_names:
                mtlx_standard_surf.setInput(input_names.index('normal'), bump_node)
        elif normal_key:
            normal_node = _create_normal_from_key(normal_key)
            if 'normal' in input_names:
                mtlx_standard_surf.setInput(input_names.index('normal'), normal_node)


    # ---------- Arnold MVP ----------
    def _build_arnold_network(self, context_node, mat_name, info):
        try:
            # Verify node type availability before creating
            mat_cat = hou.nodeTypeCategories().get('Mat')
            if not (mat_cat and hou.nodeType(mat_cat, 'arnold_materialbuilder')):
                return None
            # arnold builder top-level uses slugified mat name for predictability
            ar = context_node.createNode('arnold_materialbuilder', 'arnold_' + slugify(mat_name))
            out = ar.node('OUT_material')
            surf = ar.createNode('standard_surface', 'mtlxSurface')
            if out:
                out.setInput(0, surf)
            # iterate textures, simple mapping
            for tex_type, tex_info in self._iterate_textures(info):
                # Deterministic label for Arnold image nodes as well
                base_label = self.NAMING_MAP.get(tex_type, {}).get('label', f"{tex_type}_tex")
                name = base_label
                i = 1
                while ar.node(name) is not None:
                    i += 1
                    name = f"{base_label}_{i}"
                img = ar.createNode('image', name)
                # file parm is 'filename' in Arnold image
                p = self._get_texture_path(tex_info['name'], info)
                if img.parm('filename'):
                    img.parm('filename').set(p)
                # decide colorspace using the same policy as MaterialX
                sem = self._infer_semantics(tex_type, p)
                sig, cs = self._choose_signature_and_cs(sem['kind'], sem['explicit_cs'], sem['ext'])
                # set color_family/color_space when parms exist; enforce RAW for data/normal
                if img.parm('color_family') and img.parm('color_space'):
                    if sem['kind'] in ('data', 'normal'):
                        img.parm('color_family').set('Utility'); img.parm('color_space').set('Raw')
                        try:
                            if sem.get('unsafe_tag'):
                                img.setComment('Ignored unsafe cs tag; forced RAW')
                        except Exception:
                            pass
                    else:
                        # Try OCIO mapping for color maps
                        ocio_name = self._map_intent_to_ocio(sem.get('intent'), sem['kind'])
                        if ocio_name and 'acescg' in ocio_name.lower():
                            img.parm('color_family').set('ACES'); img.parm('color_space').set('ACEScg')
                        elif ocio_name and 'srgb' in ocio_name.lower():
                            img.parm('color_family').set('Utility'); img.parm('color_space').set('sRGB - Texture')
                        elif ocio_name and 'raw' in ocio_name.lower():
                            img.parm('color_family').set('Utility'); img.parm('color_space').set('Raw')
                        else:
                            if cs == 'scene_linear':
                                img.parm('color_family').set('ACES'); img.parm('color_space').set('ACEScg')
                            elif cs == 'raw':
                                img.parm('color_family').set('Utility'); img.parm('color_space').set('Raw')
                            else:
                                img.parm('color_family').set('Utility'); img.parm('color_space').set('sRGB - Texture')
                # connect
                if tex_type == 'color':
                    surf.setNamedInput('base_color', img, 'rgba')
                elif tex_type == 'metal':
                    surf.setNamedInput('metalness', img, 'r')
                elif tex_type == 'rough':
                    surf.setNamedInput('specular_roughness', img, 'r')
                elif tex_type == 'emission':
                    surf.setNamedInput('emission_color', img, 'rgb')
                    if surf.parm('emission'):
                        surf.parm('emission').set(1)
                elif tex_type == 'alpha':
                    surf.setNamedInput('opacity', img, 'r')
                elif tex_type == 'transmission':
                    surf.setNamedInput('transmission', img, 'r')
                elif tex_type in ('normal',):
                    n = ar.createNode('normal_map')
                    n.setNamedInput('input', img, 'rgba')
                    surf.setNamedInput('normal', n, 'vector')
                elif tex_type == 'displacement':
                    # simple displacement path via OUT_material if available
                    mul = ar.createNode('arnold::multiply', 'displacement_amount')
                    if mul.parm('input2r'):
                        for ch in ('r', 'g', 'b'):
                            mul.parm(f'input2{ch}').set(self.sp_disp_scale.value())
                    mul.setNamedInput('input1', img, 'rgb')
                    if out:
                        out.setNamedInput('displacement', mul, 'rgb')
            ar.layoutChildren()
            ar.setMaterialFlag(False)
            return ar
        except Exception as e:
            # Fail silently to keep Karma-only path working
            return None

    # ---------- Report ----------
    def _show_report(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Material Conversion Report")
        layout = QtWidgets.QVBoxLayout(dlg)
        if self.report_success:
            layout.addWidget(QtWidgets.QLabel(f"✓ Successfully created {len(self.report_success)} materials:"))
            lst = QtWidgets.QListWidget(); lst.addItems(self.report_success); layout.addWidget(lst)
        if self.report_failures:
            layout.addWidget(QtWidgets.QLabel(f"✗ Failed to create {len(self.report_failures)} materials:"))
            lstf = QtWidgets.QListWidget()
            for k, v in self.report_failures.items():
                lstf.addItem(f"{k}: {v}")
            layout.addWidget(lstf)
        btn = QtWidgets.QPushButton("Close"); btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.resize(500, 400)
        dlg.exec()


    # ---------- Help menu ----------
    def _add_help_menu(self):
        try:
            mb = self.menuBar() if hasattr(self, 'menuBar') else None
            # QMainWindow has menuBar(); but if not available, create a simple button-less fallback
            if mb is None:
                mb = self.menuBar()
            help_menu = mb.addMenu("Help")
            act = help_menu.addAction("Instructions")
            act.triggered.connect(self._show_instructions)
        except Exception:
            # fallback: ignore if running in non-Qt contexts
            pass

    def _show_instructions(self):
        text_to_display = (
            "Instructions\n\n\nSupports textures with  and without UDIMs.\n"
            "\nMATERIAL_TEXTURE_UDIM or MATERIAL_TEXTURE \n"
            "\nFor Example: tires_Alb_1001.tif or tires_Alb_tif\n"
            "\nNaming Convention for the textures:\n"
            "\nColor: diffuse, diff, albedo, alb, base, col, color, basecolor,\n"
            "\nMetal: diffuse, metalness, metal, mlt, met,\n"
            "\nSpecular: specular, specularity, spec, spc,\n"
            "\nRoughness: roughness, rough, rgh,\n"
            "\nTransmission: transmission, transparency, trans,\n"
            "\nSSS: transluncecy, sss,\n"
            "\nEmission: emission, emissive, emit, emm,\n"
            "\nOpacity: opacity, opac, alpha,\n"
            "\nBump: bump, bmp,\n"
            "\nHeight: Displacement,displace, disp, dsp, heightmap, height,\n"
            "\nAO: ambient_occlusion, ao, occlusion, cavity,\n"
            "\nMask/ID: mask, id, matid,\n"
            "\nNormal: normal, nor, nrm, nrml, norm,\n"
        )
        try:
            hou.ui.displayMessage(text_to_display, severity=hou.severityType.ImportantMessage)
        except Exception:
            pass

def show_ttmx_v2():
    win = TexToMtlX()
    win.show()
    return win
