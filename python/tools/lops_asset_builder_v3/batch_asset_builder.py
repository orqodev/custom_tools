"""
LOPS Asset Builder v3 - Batch Asset Builder UI

Interactive tool to scan asset folders, detect variants, and generate JSON
configuration files for CLI batch processing.

Features:
- Scan folder structure to detect geometry files and variants
- Auto-detect material variant folders
- Identify variants by suffix patterns (LOD, _high, _low, etc.)
- Generate JSON configs with all detected variants
- Preview and edit before saving
- Batch mode: Generate configs for multiple assets
- Execute builds directly from UI

Usage:
    from tools.lops_asset_builder_v3 import batch_asset_builder
    batch_asset_builder.show_batch_asset_builder()
"""

from __future__ import annotations

import os
import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from PySide6 import QtWidgets, QtCore, QtGui
import hou

from tools.lops_asset_builder_v3 import lops_asset_builder_cli
from tools.lops_asset_builder_v3.asset_builder_ui import SimpleProgressDialog
from modules.misc_utils import slugify


@dataclass
class DetectedAsset:
    """Represents a detected asset with its variants."""
    name: str
    main_file: str
    base_path: str
    geo_variants: List[str] = field(default_factory=list)
    texture_path: str = ""
    material_variants: List[str] = field(default_factory=list)
    detected_suffix: str = ""


class AssetScanner:
    """Scan folders to detect assets and variants."""

    # Common geometry file extensions
    GEO_EXTENSIONS = ['.abc', '.usd', '.usda', '.usdc', '.obj', '.fbx', '.bgeo', '.bgeo.sc']

    # Common variant suffixes to detect
    VARIANT_SUFFIXES = [
        '_high', '_mid', '_low',           # LOD variants
        '_lod0', '_lod1', '_lod2', '_lod3', # LOD numbered
        '_proxy', '_render', '_sim',       # Purpose variants
        '_hero', '_background',            # Quality variants
        'High', 'Mid', 'Low',              # Capitalized
        'LOD0', 'LOD1', 'LOD2',            # Capitalized LOD
    ]

    # Additional patterns for single-letter and numbered variants
    # Will be checked separately with regex
    VARIANT_PATTERNS = [
        r'_[A-Z]$',         # Single uppercase letter: _A, _B, _C
        r'_[a-z]$',         # Single lowercase letter: _a, _b, _c
        r'_v\d+$',          # Version numbered: _v1, _v2, _v3
        r'_var\d+$',        # Variant numbered: _var1, _var2
        r'_\d+$',           # Pure numbered: _1, _2, _3
    ]

    # Material variant folder patterns
    MATERIAL_FOLDER_PATTERNS = [
        r'.*\d+k$',           # Resolution: 2k, 4k, 8k
        r'.*_(clean|dirty|rusty|damaged|weathered)$',  # Condition
        r'.*_(red|blue|green|yellow|white|black)$',     # Color
        r'.*_(day|night|wet|dry)$',                     # State
        r'.*(variant|var|look|mat).*\d+$',              # Numbered variants
    ]

    def __init__(self):
        self.detected_assets: List[DetectedAsset] = []
        self.textures_root: Optional[str] = None

    def scan_folder(self, folder_path: str, recursive: bool = False) -> List[DetectedAsset]:
        """
        Scan folder for assets and detect variants.

        Args:
            folder_path: Path to scan
            recursive: Scan subdirectories

        Returns:
            List of detected assets
        """
        expanded_path = hou.text.expandString(folder_path)

        if not os.path.isdir(expanded_path):
            return []

        self.detected_assets = []

        if recursive:
            self._scan_recursive(expanded_path)
        else:
            self._scan_single_folder(expanded_path)

        return self.detected_assets

    def _scan_recursive(self, base_path: str):
        """Recursively scan for asset folders."""
        for root, dirs, files in os.walk(base_path):
            # Look for folders with geometry files
            geo_files = [f for f in files if self._is_geometry_file(f)]

            if geo_files:
                self._analyze_folder(root, geo_files)

    def _scan_single_folder(self, folder_path: str):
        """Scan a single folder for assets."""
        geo_files = []

        for item in os.listdir(folder_path):
            if self._is_geometry_file(item):
                geo_files.append(item)

        if geo_files:
            self._analyze_folder(folder_path, geo_files)

    def _is_geometry_file(self, filename: str) -> bool:
        """Check if file is a geometry file."""
        lower = filename.lower()

        # Check for .bgeo.sc first
        if lower.endswith('.bgeo.sc'):
            return True

        # Check other extensions
        for ext in self.GEO_EXTENSIONS:
            if lower.endswith(ext):
                return True

        return False

    def _analyze_folder(self, folder_path: str, geo_files: List[str]):
        """Analyze geometry files in a folder to detect main asset and variants."""

        # Group files by base name
        asset_groups = {}

        for geo_file in geo_files:
            base_name, suffix = self._extract_base_and_suffix(geo_file)

            if base_name not in asset_groups:
                asset_groups[base_name] = {
                    'main': None,
                    'variants': [],
                    'suffixes': []
                }

            if suffix:
                asset_groups[base_name]['variants'].append(geo_file)
                asset_groups[base_name]['suffixes'].append(suffix)
            else:
                # No suffix = likely the main file
                if asset_groups[base_name]['main'] is None:
                    asset_groups[base_name]['main'] = geo_file
                else:
                    # Multiple files without suffix, treat as variants
                    asset_groups[base_name]['variants'].append(geo_file)

        # Create DetectedAsset for each group
        for base_name, data in asset_groups.items():
            # Determine main file
            main_file = data['main']
            if main_file is None and data['variants']:
                # No clear main file, use first variant
                main_file = data['variants'][0]
                variants = data['variants'][1:]
            else:
                variants = data['variants']

            if main_file is None:
                continue

            # Detect texture folder
            texture_path = self._find_texture_folder(folder_path)

            # Detect material variants
            material_variants = self._find_material_variants(folder_path)

            # Determine common suffix pattern
            detected_suffix = self._detect_common_suffix(data['suffixes'])

            asset = DetectedAsset(
                name=base_name,
                main_file=os.path.join(folder_path, main_file),
                base_path=folder_path,
                geo_variants=[os.path.join(folder_path, v) for v in variants],
                texture_path=texture_path,
                material_variants=material_variants,
                detected_suffix=detected_suffix
            )

            self.detected_assets.append(asset)

    def _extract_base_and_suffix(self, filename: str) -> Tuple[str, str]:
        """
        Extract base name and variant suffix from filename.

        Handles various patterns:
        - Standard suffixes: _high, _low, _proxy, etc.
        - Single letters: _A, _B, _a, _b
        - Versioned: _v1, _v2
        - Numbered: _01, _02, _1, _2

        Returns:
            (base_name, suffix)
        """
        # Remove extension(s)
        name = filename
        if name.lower().endswith('.bgeo.sc'):
            name = name[:-8]  # .bgeo.sc is 8 characters
        else:
            name = os.path.splitext(name)[0]

        # 1. Check for exact suffix matches first (most specific)
        for suffix in self.VARIANT_SUFFIXES:
            if name.endswith(suffix):
                base_name = name[:-len(suffix)].rstrip('_')
                return (base_name, suffix)

        # 2. Check for pattern-based variants (regex patterns)
        for pattern in self.VARIANT_PATTERNS:
            match = re.search(pattern, name)
            if match:
                # Extract the matched suffix
                suffix = match.group(0)
                base_name = name[:match.start()].rstrip('_')
                return (base_name, suffix)

        # 3. No variant detected
        return (name, "")

    def _detect_common_suffix(self, suffixes: List[str]) -> str:
        """Detect common suffix pattern from list of suffixes."""
        if not suffixes:
            return ""

        # Check if all suffixes match a pattern
        if all('_lod' in s.lower() for s in suffixes):
            return "LOD"
        elif all(s.lower() in ['_high', '_mid', '_low'] for s in suffixes):
            return "Quality"
        elif all(re.match(r'_[A-Z]$', s) for s in suffixes):
            return "Letter (Uppercase)"
        elif all(re.match(r'_[a-z]$', s) for s in suffixes):
            return "Letter (Lowercase)"
        elif all(re.match(r'_v\d+$', s) for s in suffixes):
            return "Versioned"
        elif all(re.match(r'_\d+$', s) for s in suffixes):
            return "Numbered"
        elif all(s.startswith('_') and len(s) > 1 for s in suffixes):
            return "Custom Suffix"

        return "Mixed"

    def _find_texture_folder(self, base_path: str) -> str:
        """Find texture folder near the asset or use global textures_root if set."""
        # If a global textures root was provided, prefer it
        if self.textures_root and os.path.isdir(self.textures_root):
            return self.textures_root

        candidates = [
            os.path.join(base_path, 'textures'),
            os.path.join(base_path, 'Textures'),
            os.path.join(base_path, 'tex'),
            os.path.join(base_path, 'maps'),
            os.path.join(os.path.dirname(base_path), 'textures'),
            os.path.join(os.path.dirname(base_path), 'Textures'),
        ]

        for candidate in candidates:
            if os.path.isdir(candidate):
                return candidate

        return ""

    def _find_material_variants(self, base_path: str) -> List[str]:
        """Find material variant folders."""
        texture_path = self._find_texture_folder(base_path)

        if not texture_path or not os.path.isdir(texture_path):
            return []

        variants = []

        for item in os.listdir(texture_path):
            item_path = os.path.join(texture_path, item)

            if not os.path.isdir(item_path):
                continue

            # Check if folder matches material variant patterns
            for pattern in self.MATERIAL_FOLDER_PATTERNS:
                if re.match(pattern, item.lower()):
                    variants.append(item_path)
                    break

        return variants


class BatchUIProgressReporter:
    """Progress reporter that shows per-asset logs and batch percentage in a single dialog.

    Implements the interface expected by lops_asset_builder_cli.build_asset:
    - set_total(total)
    - step(message=None)
    - log(message)
    - is_cancelled()
    - mark_finished(message=None)
    """
    def __init__(self, dialog: SimpleProgressDialog, total_assets: int, asset_index: int, asset_label: str = ""):
        self.dialog = dialog
        self.total_assets = max(1, int(total_assets))
        self.asset_index = max(1, int(asset_index))
        self.asset_label = asset_label or f"Asset {self.asset_index}"
        self.verbose = True
        # inner progress
        self._inner_total = 100
        self._inner_step = 0
        # Ensure dialog range accommodates batch percentage (0..total_assets*100)
        try:
            self.dialog.set_total(self.total_assets * 100)
        except Exception:
            pass
        # Header for this asset
        try:
            self.dialog.log(f"\n=== [{self.asset_index}/{self.total_assets}] Building {self.asset_label} ===")
        except Exception:
            pass

    def _update_overall_progress(self, message: str | None = None):
        # Compute overall progress units out of total_assets*100
        frac_inner = 0.0
        if self._inner_total > 0:
            frac_inner = float(self._inner_step) / float(self._inner_total)
        overall_units = int(((self.asset_index - 1) + frac_inner) * 100)
        try:
            # Update message and bar
            if message:
                title = f"Building assets [{self.asset_index}/{self.total_assets}] — {self.asset_label}"
                self.dialog.set_message(message)
                # Also log message for history
                self.dialog.log(f"[{self.asset_index}/{self.total_assets}] {message}")
            self.dialog.set_value(overall_units)
        except Exception:
            pass

    def set_total(self, total: int):
        # Inner total for this asset
        try:
            self._inner_total = max(1, int(total))
        except Exception:
            self._inner_total = 100
        self._inner_step = 0
        self._update_overall_progress(f"Preparing {self.asset_label}")

    def step(self, message: str = None):
        self._inner_step += 1
        if self.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")
        self._update_overall_progress(message)

    def log(self, message: str):
        try:
            self.dialog.log(f"[{self.asset_index}/{self.total_assets}] {message}")
        except Exception:
            pass

    def is_cancelled(self) -> bool:
        # Pump events so ESC presses are handled
        try:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)
        except Exception:
            pass
        try:
            # Consider both soft cancel and force kill flags
            cancelled = bool(getattr(self.dialog, 'cancelled', False))
            force_kill = bool(getattr(self.dialog, 'force_kill', False))
            return cancelled or force_kill
        except Exception:
            return False

    def mark_finished(self, message: str | None = None):
        # Do not emit an extra log by default to avoid duplicate "Done/Finished" lines
        # The underlying builder will already call progress.mark_finished("Done").
        if message:
            try:
                self.dialog.log(f"[{self.asset_index}/{self.total_assets}] {message}")
            except Exception:
                pass
        # Force end of this asset to advance to the next boundary
        self._inner_step = self._inner_total
        # Update progress without adding an extra textual message when None
        self._update_overall_progress(message)


class ConfigGeneratorDialog(QtWidgets.QDialog):
    """UI for generating LOPS Asset Builder configs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LOPS Batch Asset Builder")
        self.setModal(False)
        self.resize(720, 540)

        self.scanner = AssetScanner()
        self.detected_assets: List[DetectedAsset] = []
        self.filtered_assets: List[DetectedAsset] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel(
            "Scan folders to detect assets and generate JSON configs for CLI batch processing"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Scan section
        scan_group = QtWidgets.QGroupBox("1. Scan for Assets")
        scan_layout = QtWidgets.QVBoxLayout(scan_group)

        # Folder selection
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.addWidget(QtWidgets.QLabel("Geometry Folder:"))
        self.folder_edit = QtWidgets.QLineEdit()
        folder_layout.addWidget(self.folder_edit)
        self.btn_browse = QtWidgets.QPushButton("Browse…")
        self.btn_browse.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.btn_browse)
        scan_layout.addLayout(folder_layout)

        # Textures folder selection
        tex_layout = QtWidgets.QHBoxLayout()
        tex_layout.addWidget(QtWidgets.QLabel("Textures Folder (optional):"))
        self.textures_edit = QtWidgets.QLineEdit()
        tex_layout.addWidget(self.textures_edit)
        self.btn_browse_textures = QtWidgets.QPushButton("Browse…")
        self.btn_browse_textures.clicked.connect(self._browse_textures_folder)
        tex_layout.addWidget(self.btn_browse_textures)
        scan_layout.addLayout(tex_layout)

        # Scan options
        options_layout = QtWidgets.QHBoxLayout()
        self.cb_recursive = QtWidgets.QCheckBox("Scan subdirectories recursively")
        self.cb_recursive.setChecked(False)
        options_layout.addWidget(self.cb_recursive)
        options_layout.addStretch()
        scan_layout.addLayout(options_layout)

        # Scan button
        self.btn_scan = QtWidgets.QPushButton("Scan Folder")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.clicked.connect(self._scan_folder)
        scan_layout.addWidget(self.btn_scan)

        layout.addWidget(scan_group)

        # Results section
        results_group = QtWidgets.QGroupBox("2. Detected Assets")
        results_layout = QtWidgets.QVBoxLayout(results_group)
        results_layout.setContentsMargins(6, 6, 6, 6)
        results_layout.setSpacing(4)
        results_group.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        # Filter and sort controls
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(QtWidgets.QLabel("Search:"))
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter by asset name…")
        self.search_edit.textChanged.connect(self._apply_filter_and_sort)
        controls_layout.addWidget(self.search_edit)

        controls_layout.addSpacing(10)
        controls_layout.addWidget(QtWidgets.QLabel("Sort:"))
        self.sort_combo = QtWidgets.QComboBox()
        self.sort_combo.addItems(["Name A→Z", "Name Z→A"]) 
        self.sort_combo.currentIndexChanged.connect(self._apply_filter_and_sort)
        controls_layout.addWidget(self.sort_combo)
        controls_layout.addStretch()
        results_layout.addLayout(controls_layout)

        # Asset list
        self.asset_list = QtWidgets.QListWidget()
        self.asset_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        # Make the list occupy more space
        self.asset_list.setMinimumHeight(320)
        self.asset_list.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.asset_list.setStyleSheet("QListWidget { padding: 2px; }")
        self.asset_list.itemSelectionChanged.connect(self._on_selection_changed)
        results_layout.addWidget(self.asset_list)

        # Selection buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_select_all = QtWidgets.QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.asset_list.selectAll)
        btn_layout.addWidget(self.btn_select_all)

        self.btn_select_none = QtWidgets.QPushButton("Clear Selection")
        self.btn_select_none.clicked.connect(self.asset_list.clearSelection)
        btn_layout.addWidget(self.btn_select_none)

        btn_layout.addStretch()

        self.lbl_selection_count = QtWidgets.QLabel("0 selected")
        btn_layout.addWidget(self.lbl_selection_count)

        results_layout.addLayout(btn_layout)

        layout.addWidget(results_group)

        # Details section
        details_group = QtWidgets.QGroupBox("3. Asset Details")
        details_layout = QtWidgets.QVBoxLayout(details_group)
        details_layout.setContentsMargins(5, 5, 5, 5)
        details_layout.setSpacing(4)

        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        # Make the details area larger and use space more efficiently
        self.details_text.setMinimumHeight(200)
        self.details_text.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.details_text.setStyleSheet("QTextEdit { padding: 2px; }")
        try:
            # Reduce inner document margin to use more space for text
            self.details_text.document().setDocumentMargin(4)
        except Exception:
            pass
        details_layout.addWidget(self.details_text)

        layout.addWidget(details_group)

        # Config options
        config_group = QtWidgets.QGroupBox("4. Config Options")
        config_layout = QtWidgets.QFormLayout(config_group)

        self.cb_create_lookdev = QtWidgets.QCheckBox()
        self.cb_create_lookdev.setChecked(True)
        config_layout.addRow("Create Lookdev:", self.cb_create_lookdev)

        self.cb_create_light_rig = QtWidgets.QCheckBox()
        self.cb_create_light_rig.setChecked(True)
        config_layout.addRow("Create Light Rig:", self.cb_create_light_rig)

        self.cb_enable_env_lights = QtWidgets.QCheckBox()
        self.cb_enable_env_lights.setChecked(False)
        config_layout.addRow("Enable Env Lights:", self.cb_enable_env_lights)

        layout.addWidget(config_group)

        # Action buttons
        action_layout = QtWidgets.QHBoxLayout()

        # Only keep build action; config files can be saved on build via prompt
        self.btn_build_now = QtWidgets.QPushButton("Build Now (Selected)")
        self.btn_build_now.clicked.connect(self._build_now)
        self.btn_build_now.setStyleSheet("background-color: #4a7c59; font-weight: bold;")
        action_layout.addWidget(self.btn_build_now)

        layout.addLayout(action_layout)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #333; color: #eee;")
        layout.addWidget(self.status_label)

    def _browse_folder(self):
        """Browse for folder."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Geometry Folder"
        )
        if folder:
            self.folder_edit.setText(folder)

    def _browse_textures_folder(self):
        """Browse for textures root folder."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Textures Folder"
        )
        if folder:
            self.textures_edit.setText(folder)

    def _scan_folder(self):
        """Scan folder for assets."""
        folder = self.folder_edit.text().strip()

        if not folder:
            QtWidgets.QMessageBox.warning(self, "No Folder", "Please select a folder to scan.")
            return

        # Set optional textures root into scanner before scanning
        textures_root = self.textures_edit.text().strip() if hasattr(self, 'textures_edit') else ''
        self.scanner.textures_root = textures_root if textures_root and os.path.isdir(textures_root) else None

        self.status_label.setText("Scanning...")
        QtWidgets.QApplication.processEvents()

        # Scan
        recursive = self.cb_recursive.isChecked()
        self.detected_assets = self.scanner.scan_folder(folder, recursive)

        # Update list via filter/sort pipeline
        self._apply_filter_and_sort()
        self.status_label.setText(f"Found {len(self.detected_assets)} assets")

    def _populate_asset_list(self, assets: List[DetectedAsset]):
        """Populate the asset list widget with given assets."""
        self.asset_list.clear()
        for asset in assets:
            item_text = f"{asset.name} ({len(asset.geo_variants)} geo variants, {len(asset.material_variants)} mat variants)"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, asset)
            self.asset_list.addItem(item)

    def _apply_filter_and_sort(self):
        """Filter detected assets by search text and sort by name asc/desc, then populate list."""
        assets = list(self.detected_assets) if self.detected_assets else []

        # Filter
        query = ""
        try:
            query = (self.search_edit.text() or "").strip().lower()
        except Exception:
            query = ""
        if query:
            assets = [a for a in assets if query in a.name.lower()]

        # Sort
        desc = False
        try:
            desc = (self.sort_combo.currentIndex() == 1)
        except Exception:
            desc = False
        assets.sort(key=lambda a: a.name.lower(), reverse=desc)

        # Store and display
        self.filtered_assets = assets
        self._populate_asset_list(self.filtered_assets)

        # Reset selection and details on new filter
        if hasattr(self, 'lbl_selection_count'):
            self.lbl_selection_count.setText("0 selected")
        if hasattr(self, 'details_text'):
            self.details_text.clear()

    def _on_selection_changed(self):
        """Handle selection change."""
        selected = self.asset_list.selectedItems()
        self.lbl_selection_count.setText(f"{len(selected)} selected")

        if not selected:
            self.details_text.clear()
            return

        # Show details for all selected assets
        details_blocks = []
        for item in selected:
            asset: DetectedAsset = item.data(QtCore.Qt.UserRole)
            details = []
            details.append(f"<b>Asset Name:</b> {asset.name}")
            details.append(f"<b>Main File:</b> {os.path.basename(asset.main_file)}")
            details.append(f"<b>Base Path:</b> {asset.base_path}")

            if asset.geo_variants:
                details.append(f"<br><b>Geometry Variants:</b> ({len(asset.geo_variants)})")
                for v in asset.geo_variants:
                    details.append(f"&nbsp;&nbsp;• {os.path.basename(v)}")

            if asset.texture_path:
                details.append(f"<br><b>Texture Path:</b> {asset.texture_path}")

            if asset.material_variants:
                details.append(f"<br><b>Material Variants:</b> ({len(asset.material_variants)})")
                for v in asset.material_variants:
                    details.append(f"&nbsp;&nbsp;• {os.path.basename(v)}")

            if asset.detected_suffix:
                details.append(f"<br><b>Detected Suffix Pattern:</b> {asset.detected_suffix}")

            details_blocks.append("<br>".join(details))

        self.details_text.setHtml("<hr>".join(details_blocks))

    def _show_asset_details(self, asset: DetectedAsset):
        """Show asset details."""
        details = []
        details.append(f"<b>Asset Name:</b> {asset.name}")
        details.append(f"<b>Main File:</b> {os.path.basename(asset.main_file)}")
        details.append(f"<b>Base Path:</b> {asset.base_path}")

        if asset.geo_variants:
            details.append(f"\n<b>Geometry Variants:</b> ({len(asset.geo_variants)})")
            for v in asset.geo_variants:
                details.append(f"  • {os.path.basename(v)}")

        if asset.texture_path:
            details.append(f"\n<b>Texture Path:</b> {asset.texture_path}")

        if asset.material_variants:
            details.append(f"\n<b>Material Variants:</b> ({len(asset.material_variants)})")
            for v in asset.material_variants:
                details.append(f"  • {os.path.basename(v)}")

        if asset.detected_suffix:
            details.append(f"\n<b>Detected Suffix Pattern:</b> {asset.detected_suffix}")

        self.details_text.setHtml("<br>".join(details))

    def _get_config_for_asset(self, asset: DetectedAsset) -> Dict:
        """Generate config dictionary for an asset."""
        config = {
            "main_asset_file_path": asset.main_file,
            "folder_textures": asset.texture_path or f"{asset.base_path}/textures",
            "asset_name": asset.name,
        }

        if asset.geo_variants:
            config["asset_variants"] = asset.geo_variants

        if asset.material_variants:
            config["mtl_variants"] = asset.material_variants

        # Add options
        config["create_lookdev"] = self.cb_create_lookdev.isChecked()
        config["create_light_rig"] = self.cb_create_light_rig.isChecked()
        config["enable_env_lights"] = self.cb_enable_env_lights.isChecked()

        return config

    def _generate_single_config(self):
        """Generate config for selected asset."""
        selected = self.asset_list.selectedItems()

        if not selected:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select an asset.")
            return

        asset: DetectedAsset = selected[0].data(QtCore.Qt.UserRole)

        # Ask for save location
        default_name = f"{asset.name}_config.json"
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Config", default_name, "JSON Files (*.json)"
        )

        if not filepath:
            return

        # Generate config
        config = self._get_config_for_asset(asset)

        # Save
        try:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            self.status_label.setText(f"Config saved: {filepath}")
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Config saved:\n{filepath}\n\nUse with CLI:\nlops_asset_builder_cli.build_asset_from_file('{filepath}')"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")

    def _generate_batch_config(self):
        """Generate batch config for all assets."""
        if not self.detected_assets:
            QtWidgets.QMessageBox.warning(self, "No Assets", "No assets detected. Please scan first.")
            return

        # Ask for save location
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Batch Config", "batch_config.json", "JSON Files (*.json)"
        )

        if not filepath:
            return

        # Generate configs for all assets as a flat list of full-config objects
        batch_config = [self._get_config_for_asset(asset) for asset in self.detected_assets]

        # Save
        try:
            with open(filepath, 'w') as f:
                json.dump(batch_config, f, indent=2)
            self.status_label.setText(f"Batch config saved: {filepath}")
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Batch config saved with {len(self.detected_assets)} assets:\n{filepath}\n\n"
                f"Use with CLI:\n"
                f"with open('{filepath}') as f:\n"
                f"    data = json.load(f)\n"
                f"lops_asset_builder_cli.build_assets_batch(data)"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")

    def _build_now(self):
        """Build selected assets now."""
        selected = self.asset_list.selectedItems()

        if not selected:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select assets to build.")
            return

        # Ask if user wants to save config(s) for later CLI use
        save_reply = QtWidgets.QMessageBox.question(
            self,
            "Save Configs",
            "Do you want to save configuration file(s) for the selected asset(s) before building?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if save_reply == QtWidgets.QMessageBox.Yes:
            try:
                if len(selected) == 1:
                    # Single asset: ask for file path
                    asset: DetectedAsset = selected[0].data(QtCore.Qt.UserRole)
                    default_name = f"{asset.name}_config.json"
                    filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
                        self, "Save Config", default_name, "JSON Files (*.json)"
                    )
                    if filepath:
                        config = self._get_config_for_asset(asset)
                        with open(filepath, 'w') as f:
                            json.dump(config, f, indent=2)
                        self.status_label.setText(f"Config saved: {filepath}")
                else:
                    # Multiple assets: ask for directory and write one file per asset
                    target_dir = QtWidgets.QFileDialog.getExistingDirectory(
                        self, "Select Directory to Save Configs"
                    )
                    if target_dir:
                        count = 0
                        for item in selected:
                            asset: DetectedAsset = item.data(QtCore.Qt.UserRole)
                            filename = f"{asset.name}_config.json"
                            filepath = os.path.join(target_dir, filename)
                            config = self._get_config_for_asset(asset)
                            with open(filepath, 'w') as f:
                                json.dump(config, f, indent=2)
                            count += 1
                        self.status_label.setText(f"Saved {count} config files to: {target_dir}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save configs: {e}")
                # Continue to build even if save failed

        # Confirm build
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Build",
            f"Build {len(selected)} asset(s) now?\n\nThis will create LOPS networks in the current scene.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        # Build assets with progress UI
        results = []
        total_assets = len(selected)
        progress_dialog = SimpleProgressDialog(title="LOPs Asset Builder v3 — Building Assets", parent=self)
        try:
            # Ensure the dialog is visible and brought to front so the progress bar is shown
            progress_dialog.show()
            try:
                progress_dialog.raise_()
                progress_dialog.activateWindow()
            except Exception:
                pass
            progress_dialog.set_total(total_assets * 100)
            progress_dialog.set_message(f"Starting batch build of {total_assets} asset(s)…")
            progress_dialog.log(f"Starting batch build of {total_assets} asset(s)…")
        except Exception:
            pass

        cancelled = False
        for idx, item in enumerate(selected, start=1):
            asset: DetectedAsset = item.data(QtCore.Qt.UserRole)
            config = self._get_config_for_asset(asset)

            self.status_label.setText(f"Building {asset.name} ({idx}/{total_assets})…")
            QtWidgets.QApplication.processEvents()

            reporter = BatchUIProgressReporter(progress_dialog, total_assets=total_assets, asset_index=idx, asset_label=asset.name)

            try:
                result = lops_asset_builder_cli.build_asset(config, progress=reporter)
            except KeyboardInterrupt:
                # User cancelled via dialog
                cancelled = True
                # Mark finished for the current reporter
                try:
                    reporter.mark_finished("Cancelled by user")
                except Exception:
                    pass
                break
            except Exception as e:
                # Unexpected error, wrap into a failed BuildResult-like object
                class _Tmp:
                    def __init__(self, e):
                        self.success = False
                        self.message = str(e)
                        self.error = e
                        self.duration = 0.0
                result = _Tmp(e)

            results.append((asset.name, result))
            # Ensure we mark the per-asset finished to push progress to boundary
            try:
                # Advance progress to the next asset without emitting a duplicate finish line
                reporter.mark_finished()
            except Exception:
                pass

            # Check cancellation flag set on dialog between assets
            try:
                if getattr(progress_dialog, 'cancelled', False):
                    cancelled = True
                    break
            except Exception:
                pass

        # Finalize progress dialog
        try:
            if cancelled:
                progress_dialog.set_message("Build cancelled by user")
                progress_dialog.log("Build cancelled by user")
            else:
                progress_dialog.set_message("Batch build completed")
            progress_dialog.mark_finished()
        except Exception:
            pass

        # Show results
        success_count = sum(1 for _, r in results if getattr(r, 'success', False))
        failed_count = len(results) - success_count

        message = f"Build {'Cancelled' if cancelled else 'Complete'}:\n\n"
        message += f"Success: {success_count}\n"
        message += f"Failed: {failed_count}\n\n"

        if failed_count > 0:
            message += "Failed assets:\n"
            for name, result in results:
                if not getattr(result, 'success', False):
                    message += f"  • {name}: {getattr(result, 'message', '')}\n"

        self.status_label.setText(f"Build {'cancelled' if cancelled else 'complete'}: {success_count} success, {failed_count} failed")
        QtWidgets.QMessageBox.information(self, "Build Results", message)


def show_batch_asset_builder():
    """Show the Batch Asset Builder dialog."""
    dialog = ConfigGeneratorDialog(hou.qt.mainWindow())
    dialog.show()
    return dialog


# Backward-compatible alias
def show_config_generator():
    return show_batch_asset_builder()


# For testing
if __name__ == "__main__":
    show_batch_asset_builder()
