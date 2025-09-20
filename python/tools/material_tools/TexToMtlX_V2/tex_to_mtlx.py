import hou
import os
import pprint
import re
import subprocess
import time
import logging
import threading


from PySide6 import QtWidgets, QtGui, QtCore
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.misc_utils import slugify, slugify_name_material,_sanitize

from tools.material_tools.TexToMtlX_V2.txmtlx_config import (
    TEXT_TO_DISPLAY,
    TEXTURE_EXT,
    TEXTURE_TYPE,
    UDIM_PATTERN,
    TEXTURE_TYPE_SORTED,
    SIZE_PATTERN,
    DEFAULT_DROP_TOKENS,
    WORKER_FRACTION,
    DEFAULT_IMAKETX_PATH,
    UI_CONFIG,
    MAX_WORKERS,
)
from tools.material_tools.TexToMtlX_v2.txmtlx_config import SKIP_KEYS


class TxToMtlx(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # SETUP CENTRAL WIDGET FOR UI
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # WINDOW PROPERTIES
        self.setWindowTitle(UI_CONFIG.get("window_title", "TexToMtlX v2"))
        w, h = UI_CONFIG.get("window_size", (600, 800))
        self.resize(w, h)
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - w) // 2
            y = (screen_geometry.height() - h) // 2
            self.move(x, y)
        except Exception:
            pass
        try:
            self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        except Exception:
            pass

        ## DATA
        self.mtlTX = False

        self._setup_help_section()
        self._setup_material_section()
        self._setup_list_section()
        self._setup_create_section()
        self._setup_connections()
        self.init_constants()

    def init_constants(self):
        ''' Initialize constants values used throughout the class'''

        # For material library information
        self.node_path = None
        self.node_lib = None
        self.folders_path = []

        # Texture related constants
        self.TEXTURE_EXT = TEXTURE_EXT
        self.TEXTURE_TYPE = TEXTURE_TYPE
        self.UDIM_PATTERN = UDIM_PATTERN
        self.SIZE_PATTERN = SIZE_PATTERN
        self.texture_list = {}

    def _setup_help_section(self):
        '''Setup the help button section'''
        self.help_layout = QtWidgets.QVBoxLayout()

        self.bt_instructions = QtWidgets.QPushButton("Instructions")
        self.bt_instructions.setMinimumHeight(80)
        self.help_layout.addWidget(self.bt_instructions)
        self.main_layout.addLayout(self.help_layout)

    def _setup_material_section(self):
        '''Setup the material library section'''

        self.material_layout = QtWidgets.QGridLayout()
        # MATERIAL LIBRARY
        self.bt_lib = QtWidgets.QPushButton("Material Lib")
        self.bt_lib.setMinimumHeight(70)
        self.material_layout.addWidget(self.bt_lib, 0, 0, 2, 1)
        # OPEN FOLDER
        self.bt_open_folder = QtWidgets.QPushButton("Open Folder")
        self.bt_open_folder.setMinimumHeight(40)
        self.bt_open_folder.setEnabled(False)
        self.material_layout.addWidget(self.bt_open_folder, 0, 1)
        # TX CHECKBOX
        self.checkbox = QtWidgets.QCheckBox("Convert to TX?")
        self.checkbox.setEnabled(False)
        self.material_layout.addWidget(self.checkbox, 1, 1)

        self.main_layout.addLayout(self.material_layout)

        self.cb_sanitize = QtWidgets.QCheckBox("Sanitize Material Names")
        self.cb_sanitize.setChecked(True)
        self.le_drop_tokens = QtWidgets.QLineEdit(",".join(DEFAULT_DROP_TOKENS[:5]))
        san_row = QtWidgets.QHBoxLayout()
        san_row.addWidget(self.cb_sanitize)
        san_row.addWidget(QtWidgets.QLabel("Drop tokens (comma separated)"))
        san_row.addWidget(self.le_drop_tokens)
        self.main_layout.addLayout(san_row)

    def _setup_list_section(self):
        '''Setup the material list section'''
        self.list_layout = QtWidgets.QVBoxLayout()

        # HEADER LAYOUT
        self.header_layout = QtWidgets.QHBoxLayout()

        self.lb_material_list = QtWidgets.QLabel("List of Materials:")
        self.bt_sel_all = QtWidgets.QPushButton("All")
        self.bt_sel_non = QtWidgets.QPushButton("Reset")

        self.bt_sel_all.setEnabled(False)
        self.bt_sel_non.setEnabled(False)

        self.header_layout.addWidget(self.lb_material_list)
        self.header_layout.addWidget(self.bt_sel_all)
        self.header_layout.addWidget(self.bt_sel_non)

        # MATERIAL LIST
        self.material_list = QtWidgets.QListView()
        self.material_list.setMinimumHeight(200)
        self.model = QtGui.QStandardItemModel()
        self.material_list.setModel(self.model)
        self.material_list.setSelectionMode(QtWidgets.QListView.MultiSelection)

        self.list_layout.addLayout(self.header_layout)
        self.list_layout.addWidget(self.material_list)
        self.main_layout.addLayout(self.list_layout)

    def _setup_create_section(self):
        """Setup the create button and progress bar section"""
        self.create_layout = QtWidgets.QVBoxLayout()

        # Create Button
        self.bt_create = QtWidgets.QPushButton("Create Materials")
        self.bt_create.setMinimumHeight(50)
        self.bt_create.setEnabled(False)

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setValue(0)

        self.create_layout.addWidget(self.bt_create)
        self.create_layout.addWidget(self.progress_bar)

        self.main_layout.addLayout(self.create_layout)

    def _setup_connections(self):
        '''Setup Signal Connections'''

        self.bt_instructions.clicked.connect(self.help_menu)
        self.bt_lib.clicked.connect(self.get_mtl_lib)
        self.bt_open_folder.clicked.connect(self.open_folder)
        self.checkbox.stateChanged.connect(self.on_checkbox)
        self.bt_sel_all.clicked.connect(self.select_all_mtl)
        self.bt_sel_non.clicked.connect(self.deselect_all_mtl)
        self.bt_create.clicked.connect(self.create_materials)

    def help_menu(self):
        ''' Simple Method to show instructions on how to use the tool'''
        text_to_display = TEXT_TO_DISPLAY
        hou.ui.displayMessage(text_to_display, severity=hou.severityType.ImportantMessage)

    def get_mtl_lib(self):
        ''' Get the base material librare where the materials are going to be saved'''
        self.node_path = hou.ui.selectNode(
            title="Please select one material library",
            node_type_filter=hou.nodeTypeFilter.ShopMaterial)
        if self.node_path:
            # Grabbing the material library object
            self.node_lib = hou.node(self.node_path)
            # Check if the material library select is inside a locked HDA
            if self.node_lib.isInsideLockedHDA():
                hou.ui.displayMessage(
                    "This isn't a valid material lib to create the materials. Please select again",
                    severity=hou.severityType.Error)
            else:
                self.bt_open_folder.setEnabled(True)

    def open_folder(self):
        '''
        Grab the folder that contains the textures
        And resets the UI
        '''
        self.model.clear()
        self.progress_bar.setValue(0)
        # Dictionary for textures
        self.texture_list = {}

        folders_to_check = hou.ui._selectFile(
            title="Select folder(s)", file_type=hou.fileType.Directory, multiple_select=True)

        folder_path = [hou.text.expandString(folder.strip())
                            for folder in folders_to_check.split(';') if folder.strip()]
        folder_path = [folder for folder in folder_path if self.folder_with_textures(folder)]

        if folder_path:
            for folder in folder_path:
                if self.folder_with_textures(folder):
                    self.bt_create.setEnabled(True)
                    self.checkbox.setEnabled(True)
                    self.get_texture_details(folder)
                else:
                    hou.ui.displayMessage(
                        "There are not textures inside this folder or any valid textures. \n\nCheck Instructions",
                        severity=hou.severityType.Error
                    )

    def get_texture_details(self, path):
        ''' Get the details for the texture inside a folder'''

        try:
            # Validate the path
            texture_list = defaultdict(lambda: defaultdict(list))
            if not os.path.exists(path):
                raise ValueError(f"Path does not exist: {path}")
            # Get all the valid texture inside the folder
            valid_files = []
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                # Conditions
                is_file = os.path.isfile(file_path)
                valid_extension = file.lower().endswith(tuple(self.TEXTURE_EXT))
                check_underscore = "_" in file
                if is_file and valid_extension and check_underscore:
                    valid_files.append(file)
            # Process files - textures
            for file in valid_files:
                split_text = os.path.splitext(file)[0]
                split_text = split_text.split("_")
                material_name = split_text[0]
                # Find the texture type
                texture_type = None
                for tx_type in self.TEXTURE_TYPE:
                    for tx in split_text[1:]:
                        if tx.lower() == tx_type:
                            texture_type = tx_type
                            index = split_text.index(tx)
                            material_name = '_'.join(split_text[:index])
                            break
                if not texture_type:
                    continue
                # Get UDIM and Size
                material_name = slugify(material_name)
                udim_match = self.UDIM_PATTERN.search(file)
                size_match = self.SIZE_PATTERN.search(file)
                # Update texture list
                texture_list[material_name][texture_type].append(file)
                texture_list[material_name]['UDIM'] = bool(udim_match)
                texture_list[material_name]['FOLDER_PATH'] = path
                if size_match:
                    texture_list[material_name]['Size'] = size_match.group(1)
            # Convert defaultdict to regular dictionary
            texture_list = dict(texture_list)
            _new_dict = {}
            for mat, text_dat in texture_list.items():
                _new_dict[mat] = dict(text_dat)
            self.texture_list.update(_new_dict)
            # Update the UI
            self.model.clear()
            for mat in self.texture_list:
                self.model.appendRow(QtGui.QStandardItem(mat))
            self.bt_sel_all.setEnabled(True)
            self.bt_sel_non.setEnabled(True)
            return self.texture_list
        except Exception as e:
            hou.ui.displayMessage(f"Error retrieving the textures details: {str(e)}", severity=hou.severityType.Error)

    def folder_with_textures(self, folder):
        '''
        Check to see it the folder contains any valid textures
        Args:
            folder:

        Returns:

        '''

        if not os.path.exists(folder):
            return False
        try:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if not os.path.isfile(file_path):
                    continue
                if not file.lower().endswith(tuple(self.TEXTURE_EXT)):
                    continue
                if "_" in file:
                    return True
        except (OSError, PermissionError) as e:
            hou.ui.displayMessage(
                f"Error accessing folder {folder}: {str(e)}", severity=hou.severityType.Error
            )
            return False

    def on_checkbox(self, _state):
        self.mtlTX = self.checkbox.isChecked()

    def select_all_mtl(self):
        ''' Selects all the items in the list view'''
        selection_model = self.material_list.selectionModel()
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            selection_model.setCurrentIndex(index, QtCore.QItemSelectionModel.Select)

    def deselect_all_mtl(self):
        ''' Clear all selected items in the list view'''
        self.material_list.clearSelection()

    def create_materials(self):
        ''' Passes the info needed to the MtlxMaterialClass'''

        selected_rows = self.material_list.selectedIndexes()

        if len(selected_rows) == 0:
            hou.ui.displayMessage(f"Please select at least one material.", severity=hou.severityType.Error)
            return

        # Show sanitization dialog
        drop_tokens = set()
        if self.cb_sanitize.isChecked() and self.le_drop_tokens.text().strip():
            drop_tokens = {t.strip().lower() for t in self.le_drop_tokens.text().split(',') if t.strip()}
        self.sanitize_options = {"enabled": self.cb_sanitize.isChecked(), "drop_tokens": drop_tokens}

        self.progress_bar.setMaximum(len(selected_rows))
        progress_bar_default = 0
        # Common data
        print(self.mtlTX,"TX1")
        common_data = {
            'mtlTX': self.mtlTX,
            'path': self.node_path,
            'node': self.node_lib,
        }

        for index in selected_rows:
            row = index.row()
            key = list(self.texture_list.keys())[row]
            create_material = MtlxMaterial(key, **common_data,folder_path=self.texture_list[key]["FOLDER_PATH"], texture_list=self.texture_list, sanitize_options=self.sanitize_options)
            create_material.create_materialx()

            self.progress_bar.setValue(progress_bar_default + 1)
            progress_bar_default += 1

        hou.ui.displayMessage(f"Material creation completed!!", severity=hou.severityType.Message)


class MtlxMaterial:

    def __init__(self, mat, mtlTX, path, node, folder_path, texture_list, sanitize_options=None):
        self.material_to_create = mat
        self.mtlTX = mtlTX
        self.node_path = path
        self.node_lib = node
        self.texture_list = texture_list
        self.imaketx_path = DEFAULT_IMAKETX_PATH
        self.folder_path = folder_path
        self.sanitize_options = sanitize_options or {'enabled': True, 'drop_tokens': None}

        self.init_constants()
        self._setup_imaketx()

    def init_constants(self):
        self.TEXTURE_TYPE_SORTED = TEXTURE_TYPE_SORTED
        # Variables to setupt the worker pool
        print(self.mtlTX,"TX")
        self.WORKER_LIMIT = max(1,int(MAX_WORKERS * WORKER_FRACTION))

    def _setup_imaketx(self):
        """Initialize imaketx tool"""
        # Expand $HB (Houdini bin folder for the running version)
        houdini_bin = hou.text.expandString("$HB")
        if not houdini_bin or not os.path.isdir(houdini_bin):
            raise RuntimeError("Could not resolve $HB (Houdini bin folder).")

        # Construct imaketx path relative to this Houdini version
        self.imaketx_path = os.path.join(houdini_bin, "imaketx").replace(os.sep, "/")

        if not os.path.exists(self.imaketx_path):
            raise RuntimeError(f"imaketx tool not found at: {self.imaketx_path}")

    def _convert_to_tx(self, textures_paths):
        """Convert textures to TX using parallel processing with correct progress."""
        if not self.mtlTX:
            return

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("TX CONVERSION")

        # Normalize absolute paths and dedupe
        tex_paths = []
        for p in textures_paths:
            full = os.path.join(self.folder_path, p) if not os.path.isabs(p) else p
            if full.lower().endswith(".rat"):
                continue
            if os.path.isfile(full):
                tex_paths.append(os.path.abspath(full))
        tex_paths = sorted(set(tex_paths))
        total = len(tex_paths)
        if total == 0:
            logger.info("No textures to convert.")
            return True

        def convert_single_texture(texture_path):
            thread_id = threading.current_thread().ident
            start = time.time()
            try:
                logger.info(f"Thread {thread_id}: Starting conversion of {os.path.basename(texture_path)}")
                out_path = os.path.splitext(texture_path)[0] + ".tx"
                cmd = f'"{self.imaketx_path}" "{texture_path}" "{out_path}" "--newer"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                dur = time.time() - start
                if result.returncode == 0:
                    logger.info(f"Thread {thread_id}: Finished {os.path.basename(texture_path)} in {dur:.2f} s")
                    return True
                else:
                    logger.error(f"Thread {thread_id}: Failed {os.path.basename(texture_path)}: {result.stderr.strip()}")
                    return False
            except Exception as e:
                logger.error(f"Thread {thread_id}: Error {os.path.basename(texture_path)}: {e}")
                return False

        start_all = time.time()
        completed = failed = 0

        with ThreadPoolExecutor(max_workers=self.WORKER_LIMIT) as ex:
            future_to_tex = {ex.submit(convert_single_texture, p): p for p in tex_paths}

            # Iterate ONCE over completions
            for i, fut in enumerate(as_completed(future_to_tex), start=1):
                try:
                    ok = fut.result()
                    completed += 1 if ok else 0
                    failed    += 0 if ok else 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Unhandled error: {e}")

                # Proper progress: 0..100%
                pct = (i / total) * 100.0
                logger.info(f"Progress: {pct:.1f}% ({i}/{total})")

        dur_all = time.time() - start_all
        logger.info(f"Completed conversion in {dur_all:.2f} seconds, Successfully converted: {completed}, Failed: {failed}")
        return failed == 0

    def create_materialx(self):
        '''Creates a MaterialX setup'''

        try:
            ## Get the material info and handle TX conversion
            material_lib_info = self._prepare_material_info()

            ## Create and setup the material subnet for MaterialX
            subnet_context = self._create_material_subnet(material_lib_info)

            mtlx_standard_surf, mtlx_displacement = self._create_main_nodes(subnet_context)

            # Setup the place 2d node if needed
            place2d = self._setup_place2d(subnet_context, material_lib_info)

            # Process all textures
            self._process_textures(subnet_context, mtlx_standard_surf, mtlx_displacement, material_lib_info, place2d)

            # Handle the bump and normals maps
            self._setup_bump_normal(subnet_context, mtlx_standard_surf, material_lib_info, place2d)

            self._layout_nodes(subnet_context)

        except Exception as e:
            print(f"Failed to create material subnet.{str(e)}")
            hou.ui.displayMessage(f"Error creating MaterialX : {str(e)}", severity=hou.severityType.Error)

    def _prepare_material_info(self):
        ''' Prepares the material information and handles the TX conversion '''
        # From the material dictionare gets the infor for the material to be created
        material_lib_info = self.texture_list[self.material_to_create]
        # TX conversion
        if self.mtlTX:
            all_textures = []
            for texture_type, texture_path in material_lib_info.items():
                if texture_type not in ['UDIM', 'Size']:
                    if isinstance(texture_path, list):
                        all_textures.extend(texture_path)
                self._convert_to_tx(all_textures)
        return material_lib_info
        # Returns the texture information for the material we want to convert

    def _create_material_subnet(self, material_lib_info):
        ''' Create and setup the material subnet
        Args:
            material_lib_info (dict) - this is the dictionary with the information regarding the material we want to create
        Returns:
            subnet_context - subnet MtxMaterial to use as context to create the material and others nodes
        '''
        # Create canonical name using sanitization options
        if self.sanitize_options['enabled']:
            # Use slugify with custom drop tokens if provided
            canonical = slugify_name_material(self.material_to_create, self.sanitize_options['drop_tokens'])
        else:
            # Use original material name without sanitization
            canonical = self.material_to_create

        material_name = f"{canonical}_{material_lib_info['Size']}" \
                        if 'Size' in material_lib_info else canonical

        # Remove existing material if it exists
        existing_material = self.node_lib.node(material_name)
        if existing_material:
            existing_material.destroy()
        mtlx_subnet = self.node_lib.createNode("subnet", material_name)
        subnet_context = self.node_lib.node(mtlx_subnet.name())
        delete_subnet_output = subnet_context.allItems()
        for index, item in enumerate(delete_subnet_output):
            delete_subnet_output[index].destroy()

        self._setup_material_parameters(mtlx_subnet)
        mtlx_subnet.setMaterialFlag(True)
        return mtlx_subnet

    def _setup_material_parameters(self, mtlx_subnet):
        ''' Setting up the USD material X builder parameters
        Args:
            mtlx_subnet - default subnet
        Return:
            mtlx_subnet - with the correct parameters
        '''

        hou_parm_template_group = hou.ParmTemplateGroup()

        # FOLDER MATERIALX
        hou_parm_template = hou.FolderParmTemplate("folder1", "MaterialX Builder",
                                                   folder_type=hou.folderType.Collapsible, default_value=0,
                                                   ends_tab_group=False)
        hou_parm_template.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})

        # Inherent from the class
        hou_parm_template2 = hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0,
                                                 max=10, min_is_strict=False, max_is_strict=False,
                                                 look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1,
                                                 menu_items=(["0", "1", "2"]),
                                                 menu_labels=(["Never", "Always", "Material Flag"]), icon_names=([]),
                                                 item_generator_script="",
                                                 item_generator_script_language=hou.scriptLanguage.Python,
                                                 menu_type=hou.menuType.Normal, menu_use_token=False)
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # Class Arc
        hou_parm_template2 = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=([
            "n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]),
                                                    default_expression=([
                                                        "n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]),
                                                    default_expression_language=([hou.scriptLanguage.Python]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.Regular, menu_items=(
                ["none", "reference", "inherit", "specialize", "represent"]), menu_labels=(
                ["None", "Reference", "Inherit", "Specialize", "Represent"]), icon_names=([]), item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        #  Class Prim Path
        hou_parm_template2 = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1,
                                                    default_value=(["/__class_mtl__/`$OS`"]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.Regular, menu_items=([]),
                                                    menu_labels=([]), icon_names=([]), item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags(
            {"script_action": "import lopshaderutils\nlopshaderutils.selectPrimFromInputOrFile(kwargs)",
             "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.",
             "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim",
             "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # Separator
        hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # Tab Menu Mask
        hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(
            ["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.Regular, menu_items=([]),
                                                    menu_labels=([]), icon_names=([]), item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags({"spare_category": "Tab Menu"})
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # Render Context Name
        hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1,
                                                    default_value=(["mtlx"]), naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.Regular, menu_items=([]),
                                                    menu_labels=([]), icon_names=([]), item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # Force Translation of Children
        hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children",
                                                    default_value=True)
        hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        hou_parm_template_group.append(hou_parm_template)

        mtlx_subnet.setParmTemplateGroup(hou_parm_template_group)

        return mtlx_subnet

    def _create_main_nodes(self, subnet_context):
        ''' Create the main material nodes
        Args:
            subnet_context - the subnet where we want to create these nodes
        Returns:
            tuple - node for standard surface and node for the displacement
        '''

        # Create main nodes

        mtlx_standard_surf = subnet_context.createNode("mtlxstandard_surface", slugify(self.material_to_create + "_mtlxSurface"))
        mtlx_displacement = subnet_context.createNode("mtlxdisplacement", slugify(self.material_to_create + "_mtlxDisplacement"))

        # Create output nodes




        surface_out = self._create_output_nodes(subnet_context, "surface")
        displacement_out = self._create_output_nodes(subnet_context, "displacement")

        # Connect outputs
        surface_out.setInput(0, mtlx_standard_surf)
        displacement_out.setInput(0, mtlx_displacement)

        return mtlx_standard_surf, mtlx_displacement

    def _create_output_nodes(self, context, output_type):
        ''' Create an output connect nodes
        Args:
            context - where to create the node
            output_type - is the type of connector we want to create
        Returns:
            node - output connector node
            '''

        node = context.createNode("subnetconnector", slugify(f"{output_type}_output"))
        node.parm("connectorkind").set("output")
        node.parm("parmname").set(output_type)
        node.parm("parmlabel").set(output_type.capitalize())
        node.parm("parmtype").set(output_type)
        color = hou.Color(0.89, 0.69, 0.6) if output_type == "surface" else hou.Color(0.6, 0.69, 0.89)
        node.setColor(color)
        return node

    def _setup_place2d(self, subnet_context, material_lib_info):
        '''Setup the place2d nodes for non-UDIM textures
        Args:
            subnet_context - the subnet where we want to create these nodes
            material_lib_info - textures details
        Returns:
            nodes - place2d nodes
         '''

        if not material_lib_info.get('UDIM', True):
            nodes = {
                'coord': subnet_context.createNode("mtlxtexcoord", slugify(f"{self.material_to_create}_texcoord")),
                'scale': subnet_context.createNode("mtlxconstant", slugify(f"{self.material_to_create}_scale")),
                'rotate': subnet_context.createNode("mtlxconstant", slugify(f"{self.material_to_create}_rotation")),
                'offset': subnet_context.createNode("mtlxconstant", slugify(f"{self.material_to_create}_offset")),
                'place2d': subnet_context.createNode("mtlxplace2d", slugify(f"{self.material_to_create}_place2d")),
            }

            nodes['scale'].parm('value').set(1)

            # Connect nodes
            nodes['place2d'].setInput(0, nodes['coord'])
            nodes['place2d'].setInput(2, nodes['scale'])
            nodes['place2d'].setInput(3, nodes['rotate'])
            nodes['place2d'].setInput(4, nodes['offset'])

            return nodes['place2d']

        return None

    def _process_textures(self, subnet_context, mtlx_standard_surf, mtlx_displacement, material_lib_info, place2d):
        '''
        Processs and setup all the textures
        subnet_context - The USD subnet where we are going to create the textures
        mtlx_standard_surf - the material we are going to connect the textures to
        mtlx_displacement - connecting the disp textrure
        material_lib_info - contains the information regarding the textures for the material
        place2d - if no UDIM we used this system to control de texture
        '''

        input_names = mtlx_standard_surf.inputNames()

        for texture_type, texture_info in self._iterate_textures(material_lib_info):
            # Create and setup the texture node
            texture_node = self._create_texture_node(subnet_context, texture_info, material_lib_info)
            if place2d and not material_lib_info.get('UDIM', True):
                texture_node.setInput(2, place2d)
            # Connect textures base on type
            self._connect_textures(texture_node, texture_type, mtlx_standard_surf, mtlx_displacement, input_names)

    def _iterate_textures(self, material_lib_info):
        ''' Iterator for processsing textures based on their types and ignore the skip_keys'''
        skip_keys = SKIP_KEYS
        for texture in material_lib_info:
            if texture in skip_keys:
                continue
            for texture_type, variants in self.TEXTURE_TYPE_SORTED.items():
                if any(variant in texture.lower() for variant in variants):
                    texture_info = {
                        'name': texture,
                        'file': material_lib_info[texture][0],
                        'type': texture_type,
                    }
                    yield texture_type, texture_info

    def _create_texture_node(self, subnet_context, texture_info, material_lib_info):
        ''' Create and setupt a texture node based on its type'''
        # Check the node type base on the UDIM
        node_type = "mtlximage" if material_lib_info.get("UDIM", False) else "mtlxtiledimage"

        # Create the node
        texture_node = subnet_context.createNode(node_type, slugify(texture_info["name"]))

        # Setup base texture_path
        texture_path = self._get_texture_path(texture_info['name'], material_lib_info)
        texture_node.parm('file').set(texture_path)

        # Configure node based on the texture type
        self._configure_texture_node(texture_node, texture_info["type"])

        return texture_node

    def _get_texture_path(self, texture_name, material_lib_info):
        '''
        Get the full path for a texture, handling TX conversion if needed
        Args:
            texture_name - textures name
            material_lib_info - the dictionary with the textures for the material we want to create
        Returns:
            path - self.folder_path + texture_value
        '''

        texture_value = material_lib_info[texture_name][0]
        if self.mtlTX:
            base_name = texture_value.split(".")[0]
            texture_value = f"{base_name}.tx"
        active_project = hou.getenv("PROJECT")
        project_path = hou.getenv("JOB")
        project_base_path = None
        if project_path:
            project_base_path = os.path.basename(project_path)
        if self.folder_path.endswith("/"):
            self.folder_path = self.folder_path[:-1]
        if (active_project and project_base_path) and (active_project.lower() == project_base_path.lower() and project_path.lower() in self.folder_path.lower()):
            new_path = self.folder_path.lower().replace(project_path.lower(),"$JOB")
            texture_path = f"{new_path}/{texture_value}"
        else:
            texture_path = f"{self.folder_path}/{texture_value}"
        if material_lib_info.get("UDIM", False):
            texture_path = re.sub(r'\d{4}', '<UDIM>', texture_path)
        return texture_path

    def _configure_texture_node(self, node, texture_type):
        '''
        Configure a texture node based on its type
        Args:
            node - the image node we want to change
            texture_type - value that defines if we are working with a colour or raw data
        Returns:
        '''

        # Default config
        signature = "float"
        colorspace = "raw"

        if texture_type in ["texturesColor", 'texturesSSS']:
            signature = "color3"
            colorspace = "srgb_texture"

        node.parm("signature").set(signature)
        node.parm("filecolorspace").set(colorspace)

    def _connect_textures(self, texture_node, texture_type, mtlx_standard_surf, mtlx_displacement, input_names):
        '''Connect a texture node to the material based on its type '''
        connection_map = {
            'texturesColor': {
                'input': 'base_color',
                'setup': self._setup_color_texture
            },
            "texturesMetal": {
                'input': 'metalness',
                'setup': self._setup_direct_texture
            },
            "texturesSpecular": {
                'input': 'specular',
                'setup': self._setup_direct_texture
            },
            "texturesRough": {
                'input': 'specular_roughness',
                'setup': self._setup_roughness_texture
            },
            "texturesTrans": {
                'input': 'transmission',
                'setup': self._setup_direct_texture
            },
            "texturesGloss": {
                'input': 'specular_roughness',
                'setup': self._setup_glossiness_texture
            },
            "texturesEmm": {
                'input': 'emission',
                'setup': self._setup_direct_texture
            },
            "texturesAlpha": {
                'input': 'opacity',
                'setup': self._setup_direct_texture
            },
            "texturesSSS": {
                'input': 'subsurface_color',
                'setup': self._setup_sss_texture
            },
        }

        if texture_type in connection_map:
            config = connection_map[texture_type]
            config['setup'](texture_node, mtlx_standard_surf, input_names.index(config["input"]))

        if texture_type == "texturesDisp":
            self._setup_displacement_texture(texture_node, mtlx_displacement)

        if texture_type == "texturesExtra":
            self._setup_mask_texture(texture_node)

    def _setup_color_texture(self, texture_node, mtlx_standard_surf, input_index):
        '''Setup for colour texture with a range node'''
        range_node = texture_node.parent().createNode("mtlxrange", slugify(texture_node.name() + "_CC"))
        range_node.setInput(0, texture_node)
        range_node.parm("signature").set("color3")
        mtlx_standard_surf.setInput(input_index, range_node)

    def _setup_displacement_texture(self, texture_node, mtlx_displacement):
        '''Setup the displacement map with a range node'''
        mtlx_displacement.setInput(0, texture_node)

    def _setup_roughness_texture(self, texture_node, mtlx_standard_surf, input_index):
        '''Setup the roughness texture with a range node'''
        range_node = texture_node.parent().createNode("mtlxrange", slugify(texture_node.name() + "_ADJ"))
        range_node.setInput(0, texture_node)
        mtlx_standard_surf.setInput(input_index, range_node)

    def _setup_glossiness_texture(self, texture_node, mtlx_standard_surf, input_index):
        '''Setup the glossiness texture with a range node'''
        range_node = texture_node.parent().createNode("mtlxrange", slugify(texture_node.name() + "_ADJ"))
        range_node.setInput(0, texture_node)
        range_node.parm("outlow").set(1)
        range_node.parm("outhigh").set(0)
        mtlx_standard_surf.setInput(input_index, range_node)

    def _setup_sss_texture(self, texture_node, mtlx_standard_surf, input_index):
        '''Setup the SSS texture with a range node'''
        range_node = texture_node.parent().createNode("mtlxrange", _sanitize(texture_node.name() + "_ADJ"))
        range_node.setInput(0, texture_node)
        range_node.parm("signature").set("color3")
        mtlx_standard_surf.setInput(input_index, range_node)
        mtlx_standard_surf.parm("subsurface").set(1)

    def _setup_direct_texture(self, texture_node, mtlx_standard_surf, input_index):
        '''Setup the direct connection for another textures'''
        mtlx_standard_surf.setInput(input_index, texture_node)

    def _setup_mask_texture(self, texture_node):
        ''' Setup for user or mask texture'''
        separate_node = texture_node.parent().createNode("mtlxseparate3c", _sanitize(texture_node.name() + "_SPLIT"))
        separate_node.setInput(0, texture_node)

    def _setup_bump_normal(self, subnet_context, mtlx_standard_surf, material_lib_info, place2d):
        ''' Setup the bump and normal textures nodes and connections'''
        # Create mtLx image based on UDIM on or off

        node_type = "mtlximage" if material_lib_info.get("UDIM",False) else "mtlxtiledimage"

        def _create_bump():
            ''' Create and setup bump node and returns the bumps node'''
            bump_node = subnet_context.createNode("mtlxbump", 'mtlxBump')
            bump_image = subnet_context.createNode(node_type, 'bump')
            bump_image.parm("signature").set("float")
            bump_image.parm("filecolorspace").set("raw")
            bump_path = self._get_texture_path(bump_normal_data["bump"], material_lib_info)
            bump_image.parm("file").set(bump_path)

            if place2d and not material_lib_info.get("UDIM",True):
                bump_image.setInput(2, place2d)

            bump_node.setInput(0, bump_image)

            return bump_node

        def _create_normal():
            ''' Create and setup normal node and returns the normal node'''
            normal_node = subnet_context.createNode("mtlxnormalmap", 'mtlxNormal')
            normal_image = subnet_context.createNode(node_type, 'normal')
            normal_image.parm("signature").set("vector3")
            normal_image.parm("filecolorspace").set("raw")
            normal_path = self._get_texture_path(bump_normal_data["normal"], material_lib_info)
            normal_image.parm("file").set(normal_path)

            if place2d and not material_lib_info.get("UDIM",True):
                normal_image.setInput(2, place2d)

            normal_node.setInput(0, normal_image)

            return normal_node


        input_names = mtlx_standard_surf.inputNames()
        bump_normal_data = self._find_bump_normal_textures(material_lib_info)

        if not any(bump_normal_data.values()):
            return

        if bump_normal_data["bump"] and bump_normal_data["normal"]:
            bump_node = _create_bump()
            normal_node = _create_normal()
            bump_node.setInput(2, normal_node)
            mtlx_standard_surf.setInput(input_names.index("normal"), bump_node)

        elif bump_normal_data["bump"]:
            bump_node = _create_bump()
            mtlx_standard_surf.setInput(input_names.index("normal"), bump_node)

        elif bump_normal_data["normal"]:
            normal_node = _create_normal()
            mtlx_standard_surf.setInput(input_names.index("normal"), normal_node)

    def _find_bump_normal_textures(self, material_lib_info):
        ''' Find bump and normal textures
        Args:
            material_lib_info (dict): material lib info
        Returns:
            dictionary with the values for bump and normal values
        '''

        texture_type_sorted = {
            "texturesBump": ["bump", "bmp", "height"],
            "texturesNormal": ["normal", "nor", "nrm", "nrml", "norm"]
            }

        result = { 'bump' : None, 'normal' : None }

        for texture in material_lib_info:
            for texture_name, texture_value in texture_type_sorted.items():
                if texture in texture_value:
                    key = 'bump' if texture_name == "texturesBump" else 'normal'
                    result[key] = texture

        return result

    def _layout_nodes(self, subnet_context):
        ''' Layout nodes in the network'''
        subnet_context.layoutChildren()
        self.node_lib.layoutChildren()

