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
from tools.lops_asset_builder_v3.texture_variant_detector import TextureVariantDetector

# Keep strong references to progress dialogs so they don't get garbage-collected
# when the local function scope ends (we close the main dialog during build).
_LIVE_PROGRESS_DIALOGS: list[SimpleProgressDialog] = []

def _register_progress_dialog(dlg: SimpleProgressDialog):
    try:
        if dlg not in _LIVE_PROGRESS_DIALOGS:
            _LIVE_PROGRESS_DIALOGS.append(dlg)
        try:
            # Remove reference when the dialog is destroyed by the user
            dlg.destroyed.connect(lambda _o=None: _unregister_progress_dialog(dlg))
        except Exception:
            pass
    except Exception:
        pass

def _unregister_progress_dialog(dlg: SimpleProgressDialog):
    try:
        if dlg in _LIVE_PROGRESS_DIALOGS:
            _LIVE_PROGRESS_DIALOGS.remove(dlg)
    except Exception:
        pass


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

    def _load_geo_variant_config(self):
        """Load configurable geo variant suffixes and regex patterns.

        Sources (in precedence order):
        1) Environment variables:
           - LOPS_GEO_SUFFIXES: comma/semicolon separated list of suffix literals
           - LOPS_GEO_SUFFIX_PATTERNS: comma/semicolon separated list of regex patterns
           - LOPS_GEO_SUFFIX_MODE: 'override' or 'extend' (default: extend)
        2) JSON file next to this module: geo_variant_config.json
           {
             "mode": "extend" | "override",
             "suffixes": ["_high", "_low", "_lod0"],
             "patterns": [r"_[A-Z]$", r"_v\\d+$"]
           }
        """
        try:
            mode = "extend"
            # JSON file (lower precedence than env for contents but may set default mode)
            cfg_path = os.path.join(os.path.dirname(__file__), "geo_variant_config.json")
            file_suffixes = []
            file_patterns = []
            if os.path.exists(cfg_path):
                import json
                with open(cfg_path, "r") as f:
                    data = json.load(f) or {}
                if isinstance(data, dict):
                    m = str(data.get("mode", "extend")).strip().lower()
                    if m in ("extend", "override"):
                        mode = m
                    if isinstance(data.get("suffixes"), list):
                        file_suffixes = [str(s) for s in data.get("suffixes") if str(s)]
                    if isinstance(data.get("patterns"), list):
                        file_patterns = [str(p) for p in data.get("patterns") if str(p)]
            # Env vars override JSON contents
            env_mode = os.environ.get("LOPS_GEO_SUFFIX_MODE")
            if env_mode:
                env_mode_l = env_mode.strip().lower()
                if env_mode_l in ("extend", "override"):
                    mode = env_mode_l
            env_suffixes = os.environ.get("LOPS_GEO_SUFFIXES")
            env_patterns = os.environ.get("LOPS_GEO_SUFFIX_PATTERNS")
            suffixes = list(file_suffixes)
            patterns = list(file_patterns)
            if env_suffixes:
                parts = [p.strip() for p in re.split(r"[;,]", env_suffixes) if p.strip()]
                if parts:
                    suffixes = parts
            if env_patterns:
                parts = [p.strip() for p in re.split(r"[;,]", env_patterns) if p.strip()]
                if parts:
                    patterns = parts
            # Apply mode
            if mode == "override":
                base_suffixes = []
                base_patterns = []
            else:
                base_suffixes = list(self.VARIANT_SUFFIXES)
                base_patterns = list(self.VARIANT_PATTERNS)
            # Merge (preserve order, remove duplicates)
            merged_suffixes = []
            seen = set()
            for s in base_suffixes + suffixes:
                if not s:
                    continue
                if s not in seen:
                    merged_suffixes.append(s)
                    seen.add(s)
            merged_patterns = []
            seen_p = set()
            for p in base_patterns + patterns:
                if not p:
                    continue
                if p not in seen_p:
                    # Validate regex lazily; keep even if invalid to skip later safely
                    merged_patterns.append(p)
                    seen_p.add(p)
            self.variant_suffixes = merged_suffixes
            self.variant_patterns = merged_patterns
        except Exception:
            # On any error, keep defaults already copied in __init__
            pass

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
        # Geo variant suffix/pattern config (instance-level, configurable)
        self.variant_suffixes: List[str] = list(self.VARIANT_SUFFIXES)
        self.variant_patterns: List[str] = list(self.VARIANT_PATTERNS)
        self._load_geo_variant_config()

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
            variants = list(data['variants'])

            # Sort variants deterministically so that, when no explicit main exists,
            # the first variant after sorting is considered the main. This ensures
            # patterns like _A, _B, _C choose _A as main.
            def _variant_sort_key(filename: str):
                # Extract suffix using the existing logic
                _bn, suf = self._extract_base_and_suffix(filename)
                s = suf or ""
                s_low = s.lower()
                # Single letter _A/_b
                m = re.match(r'^_([A-Za-z])$', s)
                if m:
                    ch = m.group(1).upper()
                    return (0, ord(ch) - ord('A'))
                # Pure numbered _1
                m = re.match(r'^_(\d+)$', s)
                if m:
                    return (1, int(m.group(1)))
                # Versioned _v1
                m = re.match(r'^_v(\d+)$', s_low)
                if m:
                    return (2, int(m.group(1)))
                # Quality _high/_mid/_low → High < Mid < Low
                if s_low in ['_high', '_mid', '_low']:
                    order = {'_high': 0, '_mid': 1, '_low': 2}
                    return (3, order[s_low])
                # LOD _lodN
                m = re.match(r'^_lod(\d+)$', s_low)
                if m:
                    return (4, int(m.group(1)))
                # Other known words get moderate priority by name
                known_suffixes = ['_proxy', '_render', '_sim', '_hero', '_background']
                if s_low in known_suffixes:
                    return (5, known_suffixes.index(s_low))
                # Fallback: lexicographic on full filename
                return (9, filename.lower())

            variants.sort(key=_variant_sort_key)

            if main_file is None and variants:
                # No clear main file, pick the first sorted variant as main
                main_file = variants[0]
                variants = variants[1:]

            if main_file is None:
                continue

            # Detect material variants and choose main textures folder
            main_textures, material_variants = self._find_material_variants(folder_path)

            # If no variant structure detected, fall back to generic textures folder
            if not main_textures:
                main_textures = self._find_texture_folder(folder_path)

            # Determine common suffix pattern
            detected_suffix = self._detect_common_suffix(data['suffixes'])

            asset = DetectedAsset(
                name=base_name,
                main_file=os.path.join(folder_path, main_file),
                base_path=folder_path,
                geo_variants=[os.path.join(folder_path, v) for v in variants],
                texture_path=main_textures,
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
        for suffix in (self.variant_suffixes or self.VARIANT_SUFFIXES):
            try:
                if name.endswith(suffix):
                    base_name = name[:-len(suffix)].rstrip('_')
                    return (base_name, suffix)
            except Exception:
                continue

        # 2. Check for pattern-based variants (regex patterns)
        for pattern in (self.variant_patterns or self.VARIANT_PATTERNS):
            try:
                match = re.search(pattern, name)
            except re.error:
                # Skip invalid regex patterns from config
                match = None
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

    def _find_material_variants(self, base_path: str) -> Tuple[str, List[str]]:
        """Find material variant folders and choose a single main variant.

        Priority for main textures: 4K > 2K > 1K. If none of these exist,
        fall back to the first detected variant. The returned main path will be
        one of the detected variant folders; the remaining detected variant
        folders will be returned as material variant list.

        Returns:
            (main_textures_path, material_variant_paths)
        """
        texture_path = self._find_texture_folder(base_path)

        if not texture_path or not os.path.isdir(texture_path):
            return "", []

        # Use intelligent texture variant detector
        detector = TextureVariantDetector()
        detected_variants = detector.detect_variants(texture_path)

        if not detected_variants:
            return "", []

        # Choose main/variant list using detector's configurable priority logic
        best, others = detector.choose_main_variant(detected_variants)
        if not best:
            return "", []
        main_path = best.folder_path
        variants = [v.folder_path for v in others]
        return main_path, variants


class BatchUIProgressReporter:
    """Simplified progress reporter based on a fixed number of tasks (materials).

    - Total tasks are precomputed before building (sum of estimated materials per
      material folder across all selected assets).
    - Each time the builder logs "Created material …" we increment the done count
      by 1. No dynamic total changes during build; the bar is stable and monotonic.
    - When an asset finishes, we top up any remaining tasks allocated to that
      asset to ensure the segment completes (useful when folders had zero
      discoverable textures and templates were created instead).
    """
    def __init__(self, dialog: SimpleProgressDialog, asset_index: int, asset_label: str, expected_tasks_for_asset: int):
        self.dialog = dialog
        self.asset_index = max(1, int(asset_index))
        self.asset_label = asset_label or f"Asset {self.asset_index}"
        self.expected = max(1, int(expected_tasks_for_asset))
        self._local_done = 0
        # Store total_assets for progress formatting
        self.total_assets = getattr(dialog, '_total_assets', 0)
        # Initialize shared counters on dialog
        if not hasattr(self.dialog, "_tasks_total"):
            self.dialog._tasks_total = 0
        if not hasattr(self.dialog, "_tasks_done"):
            self.dialog._tasks_done = 0
        try:
            self.dialog.log(f"\n=== [{self.asset_index}] Building {self.asset_label} ===")
            self.dialog.set_message(f"Starting {self.asset_label}…")
        except Exception:
            pass

    def _inc(self, n: int = 1):
        try:
            self._local_done += n
            self.dialog._tasks_done = min(int(self.dialog._tasks_done) + n, int(self.dialog._tasks_total))
            self.dialog.set_value(int(self.dialog._tasks_done))
        except Exception:
            pass

    def set_total(self, total: int):
        # Not used; total is set by the caller using precomputed tasks
        return

    def step(self, message: str = None):
        if self.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")
        if message:
            try:
                # Check if this is a material creation message
                mat_match = re.search(r"Created material\s+(\d+)\s*/\s*(\d+)\s*:\s*(.+)", message)
                if mat_match:
                    # Extract material count and name from the message
                    mat_current = mat_match.group(1)
                    mat_total = mat_match.group(2)
                    mat_name = mat_match.group(3)

                    # Format asset progress (e.g., "24/85")
                    if self.total_assets > 0:
                        asset_progress = f"({self.asset_index}/{self.total_assets})"
                    else:
                        asset_progress = f"({self.asset_index})"

                    # Enhanced message: "Building RootPlatform (24/85) - Created material 2/3: Material_Name"
                    enhanced_message = f"Building {self.asset_label} {asset_progress} - Created material {mat_current}/{mat_total}: {mat_name}"
                    self.dialog.set_message(enhanced_message)
                    self.dialog.log(enhanced_message)
                else:
                    # Regular message without enhancement
                    self.dialog.set_message(message)
                    self.dialog.log(f"[{self.asset_index}] {message}")
            except Exception:
                # Fallback to original behavior on any error
                try:
                    self.dialog.set_message(message)
                    self.dialog.log(f"[{self.asset_index}] {message}")
                except Exception:
                    pass
            # Count material creation steps: "Created material n/X: ..."
            try:
                if re.search(r"Created material\s+\d+\s*/\s*\d+\s*:\s*", message):
                    self._inc(1)
            except Exception:
                pass

    def log(self, message: str):
        try:
            self.dialog.log(f"[{self.asset_index}] {message}")
        except Exception:
            pass

    def is_cancelled(self) -> bool:
        try:
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 50)
        except Exception:
            pass
        try:
            return bool(getattr(self.dialog, 'cancelled', False) or getattr(self.dialog, 'force_kill', False))
        except Exception:
            return False

    def mark_finished(self, message: str | None = None):
        # Top up remaining tasks for this asset so we reach its expected share
        remaining = max(0, int(self.expected) - int(self._local_done))
        if remaining:
            self._inc(remaining)
        if message:
            try:
                self.dialog.log(f"[{self.asset_index}] {message}")
            except Exception:
                pass


class CollapsibleSection(QtWidgets.QWidget):
    """A simple collapsible container with a clickable header and a content area."""
    def __init__(self, title: str = "", content: QtWidgets.QWidget | None = None, parent=None):
        super().__init__(parent)
        self._content_widget = None
        self._content_area = QtWidgets.QScrollArea()
        self._content_area.setWidgetResizable(True)
        self._content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=True)
        self._toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self._toggle_button.setArrowType(QtCore.Qt.DownArrow)
        self._toggle_button.clicked.connect(self._on_toggled)
        try:
            self._toggle_button.setStyleSheet("QToolButton { font-weight: bold; }")
        except Exception:
            pass

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)
        lay.addWidget(self._toggle_button)
        lay.addWidget(self._content_area)

        if content is not None:
            self.setContentWidget(content)

    def setTitle(self, title: str):
        self._toggle_button.setText(title)

    def setContentWidget(self, widget: QtWidgets.QWidget):
        self._content_widget = widget
        self._content_area.setWidget(widget)

    def _on_toggled(self):
        expanded = self._toggle_button.isChecked()
        self._toggle_button.setArrowType(QtCore.Qt.DownArrow if expanded else QtCore.Qt.RightArrow)
        self._content_area.setVisible(expanded)
        # Trigger a relayout so the parent dialog resizes the section height
        try:
            self.updateGeometry()
            self.parentWidget() and self.parentWidget().updateGeometry()
        except Exception:
            pass

    def isExpanded(self) -> bool:
        return self._toggle_button.isChecked()


class ConfigGeneratorDialog(QtWidgets.QDialog):
    """UI for generating LOPS Asset Builder configs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LOPS Batch Asset Builder")
        self.setModal(False)
        # Increase overall UI height by ~25% for better visibility
        self.resize(720, 675)

        self.scanner = AssetScanner()
        self.detected_assets: List[DetectedAsset] = []
        self.filtered_assets: List[DetectedAsset] = []
        # Store selected environment light files (HDRIs)
        self.env_light_paths: List[str] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        outer_layout = QtWidgets.QVBoxLayout(self)

        # Create a scroll area to contain the full UI so everything remains reachable
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(6, 6, 6, 6)
        scroll_layout.setSpacing(6)

        # Header
        header = QtWidgets.QLabel(
            "Scan folders to detect assets and generate JSON configs for CLI batch processing"
        )
        header.setWordWrap(True)
        scroll_layout.addWidget(header)

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

        # Variant generation mode
        variant_mode_layout = QtWidgets.QHBoxLayout()
        self.cb_generate_list_variants = QtWidgets.QCheckBox("Generate variants by list")
        self.cb_generate_list_variants.setChecked(True)
        self.cb_generate_list_variants.setToolTip(
            "When checked: Main asset and variants are kept separate (PropCargo as main, PropCargo_B/C as variants).\n"
            "When unchecked: All files treated as letter-based variants (PropCargo→A, PropCargo_B→B, PropCargo_C→C)"
        )
        variant_mode_layout.addWidget(self.cb_generate_list_variants)
        variant_mode_layout.addStretch()
        scan_layout.addLayout(variant_mode_layout)

        # Scan button
        self.btn_scan = QtWidgets.QPushButton("Scan Folder")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.clicked.connect(self._scan_folder)
        scan_layout.addWidget(self.btn_scan)

        scroll_layout.addWidget(scan_group)

        # Results section (non-collapsible)
        results_content = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout(results_content)
        results_layout.setContentsMargins(6, 6, 6, 6)
        results_layout.setSpacing(4)
        results_content.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        # Section title
        results_title = QtWidgets.QLabel("2. Detected Assets")
        try:
            results_title.setStyleSheet("font-weight: bold;")
        except Exception:
            pass
        scroll_layout.addWidget(results_title)

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

        scroll_layout.addWidget(results_content)

        # Details section (non-collapsible)
        details_content = QtWidgets.QWidget()
        details_layout = QtWidgets.QVBoxLayout(details_content)
        details_layout.setContentsMargins(5, 5, 5, 5)
        details_layout.setSpacing(4)

        details_title = QtWidgets.QLabel("3. Asset Details")
        try:
            details_title.setStyleSheet("font-weight: bold;")
        except Exception:
            pass
        scroll_layout.addWidget(details_title)

        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        # Make the details area larger and use space more efficiently
        self.details_text.setMinimumHeight(280)
        self.details_text.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.details_text.setStyleSheet("QTextEdit { padding: 2px; }")
        try:
            # Reduce inner document margin to use more space for text
            self.details_text.document().setDocumentMargin(4)
        except Exception:
            pass
        details_layout.addWidget(self.details_text)

        scroll_layout.addWidget(details_content)

        # Config options (non-collapsible)
        config_content = QtWidgets.QWidget()
        config_layout = QtWidgets.QFormLayout(config_content)

        config_title = QtWidgets.QLabel("4. Config Options")
        try:
            config_title.setStyleSheet("font-weight: bold;")
        except Exception:
            pass
        scroll_layout.addWidget(config_title)

        # === Network/Layout Settings ===
        # Create Network Boxes
        network_boxes_row = QtWidgets.QHBoxLayout()
        self.cb_create_network_boxes = QtWidgets.QCheckBox()
        self.cb_create_network_boxes.setChecked(False)
        self.cb_create_network_boxes.setToolTip("Create network boxes around node groups (disable for easier layout)")
        network_boxes_row.addWidget(self.cb_create_network_boxes)
        network_boxes_help = QtWidgets.QLabel("Organize nodes in boxes (disable for flat layout)")
        network_boxes_help.setStyleSheet("color: gray; font-size: 10px;")
        network_boxes_row.addWidget(network_boxes_help)
        network_boxes_row.addStretch(1)
        config_layout.addRow("Create Network Boxes:", network_boxes_row)

        # Skip MatchSize Node
        skip_matchsize_row = QtWidgets.QHBoxLayout()
        self.cb_skip_matchsize = QtWidgets.QCheckBox()
        self.cb_skip_matchsize.setChecked(False)
        self.cb_skip_matchsize.setToolTip("Skip matchsize node creation in component geometry (use when assets already have correct scale)")
        skip_matchsize_row.addWidget(self.cb_skip_matchsize)
        skip_matchsize_help = QtWidgets.QLabel("Skip size normalization (assets keep original scale)")
        skip_matchsize_help.setStyleSheet("color: gray; font-size: 10px;")
        skip_matchsize_row.addWidget(skip_matchsize_help)
        skip_matchsize_row.addStretch(1)
        config_layout.addRow("Skip MatchSize Node:", skip_matchsize_row)

        # Lowercase Material Names
        lowercase_row = QtWidgets.QHBoxLayout()
        self.cb_lowercase_material_names = QtWidgets.QCheckBox()
        self.cb_lowercase_material_names.setChecked(False)
        self.cb_lowercase_material_names.setToolTip("Convert material path to lowercase before deriving prim name")
        lowercase_row.addWidget(self.cb_lowercase_material_names)
        lowercase_help = QtWidgets.QLabel("Lowercase material names in geometry builder")
        lowercase_help.setStyleSheet("color: gray; font-size: 10px;")
        lowercase_row.addWidget(lowercase_help)
        lowercase_row.addStretch(1)
        config_layout.addRow("Lowercase Material Names:", lowercase_row)

        # Use Custom Component Output
        custom_comp_row = QtWidgets.QHBoxLayout()
        self.cb_use_custom_component_output = QtWidgets.QCheckBox()
        self.cb_use_custom_component_output.setChecked(False)
        self.cb_use_custom_component_output.setToolTip("When enabled, build with custom Component Output node; when off, use standard componentoutput")
        custom_comp_row.addWidget(self.cb_use_custom_component_output)
        custom_comp_help = QtWidgets.QLabel("Use custom Component Output node")
        custom_comp_help.setStyleSheet("color: gray; font-size: 10px;")
        custom_comp_row.addWidget(custom_comp_help)
        custom_comp_row.addStretch(1)
        config_layout.addRow("Use Custom Component Output:", custom_comp_row)

        # Create Geo Variants
        geo_variants_row = QtWidgets.QHBoxLayout()
        self.cb_create_geo_variants = QtWidgets.QCheckBox()
        self.cb_create_geo_variants.setChecked(False)
        self.cb_create_geo_variants.setToolTip("Include geometry variants if detected (disable to use only main geometry file)")
        geo_variants_row.addWidget(self.cb_create_geo_variants)
        geo_variants_help = QtWidgets.QLabel("Include detected geometry variants")
        geo_variants_help.setStyleSheet("color: gray; font-size: 10px;")
        geo_variants_row.addWidget(geo_variants_help)
        geo_variants_row.addStretch(1)
        config_layout.addRow("Create Geo Variants:", geo_variants_row)

        # Create Material Variants
        material_variants_row = QtWidgets.QHBoxLayout()
        self.cb_create_material_variants = QtWidgets.QCheckBox()
        self.cb_create_material_variants.setChecked(False)
        self.cb_create_material_variants.setToolTip("Include material variants if detected (disable to use only main texture folder)")
        material_variants_row.addWidget(self.cb_create_material_variants)
        material_variants_help = QtWidgets.QLabel("Include detected material variants")
        material_variants_help.setStyleSheet("color: gray; font-size: 10px;")
        material_variants_row.addWidget(material_variants_help)
        material_variants_row.addStretch(1)
        config_layout.addRow("Create Material Variants:", material_variants_row)

        # Add separator
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setFrameShadow(QtWidgets.QFrame.Sunken)
        config_layout.addRow(separator1)

        # === LookDev Settings ===
        # Create Lookdev
        lookdev_row = QtWidgets.QHBoxLayout()
        self.cb_create_lookdev = QtWidgets.QCheckBox()
        self.cb_create_lookdev.setChecked(False)
        lookdev_row.addWidget(self.cb_create_lookdev)
        lookdev_help = QtWidgets.QLabel("Setup turntable, camera, and render nodes")
        lookdev_help.setStyleSheet("color: gray; font-size: 10px;")
        lookdev_row.addWidget(lookdev_help)
        lookdev_row.addStretch(1)
        config_layout.addRow("Create Lookdev:", lookdev_row)

        # Create Light Rig
        light_rig_row = QtWidgets.QHBoxLayout()
        self.cb_create_light_rig = QtWidgets.QCheckBox()
        self.cb_create_light_rig.setChecked(False)
        light_rig_row.addWidget(self.cb_create_light_rig)
        light_rig_help = QtWidgets.QLabel("Add 3-point lighting setup (key, fill, rim)")
        light_rig_help.setStyleSheet("color: gray; font-size: 10px;")
        light_rig_row.addWidget(light_rig_help)
        light_rig_row.addStretch(1)
        config_layout.addRow("Create Light Rig:", light_rig_row)

        # Env lights controls: inline checkbox + buttons + count + help text
        env_row = QtWidgets.QHBoxLayout()
        self.cb_enable_env_lights = QtWidgets.QCheckBox("Enable Env Lights")
        self.cb_enable_env_lights.setChecked(False)
        env_row.addWidget(self.cb_enable_env_lights)
        env_lights_help = QtWidgets.QLabel("HDRI dome lighting")
        env_lights_help.setStyleSheet("color: gray; font-size: 10px;")
        env_row.addWidget(env_lights_help)
        self.btn_add_env = QtWidgets.QPushButton("Add…")
        self.btn_add_env.setToolTip("Add one or more HDRI files (.exr, .hdr, .rat) for environment lighting")
        self.btn_add_env.clicked.connect(self._browse_env_lights)
        env_row.addWidget(self.btn_add_env)
        self.btn_clear_env = QtWidgets.QPushButton("Clear")
        self.btn_clear_env.clicked.connect(self._clear_env_lights)
        env_row.addWidget(self.btn_clear_env)
        env_row.addStretch(1)
        self.lbl_env_count = QtWidgets.QLabel("0 files")
        env_row.addWidget(self.lbl_env_count)
        config_layout.addRow("Environment Lights:", env_row)

        # Readonly box to display env light paths
        self.env_paths_edit = QtWidgets.QTextEdit()
        self.env_paths_edit.setReadOnly(True)
        # Make the env lights box smaller per request
        self.env_paths_edit.setMinimumHeight(48)
        self.env_paths_edit.setPlaceholderText("Selected environment light paths will appear here…")
        try:
            self.env_paths_edit.setStyleSheet("QTextEdit { padding: 2px; font-family: Consolas, 'Courier New', monospace; font-size: 11px; }")
            self.env_paths_edit.document().setDocumentMargin(4)
        except Exception:
            pass
        config_layout.addRow("Env Light Paths:", self.env_paths_edit)
        # Toggle enable state of env light controls based on checkbox
        try:
            self.cb_enable_env_lights.toggled.connect(self._update_env_enabled)
        except Exception:
            pass

        scroll_layout.addWidget(config_content)

        # Initialize env light controls enabled/disabled state
        try:
            self._update_env_enabled()
        except Exception:
            pass

        # Action buttons
        action_layout = QtWidgets.QHBoxLayout()

        # Only keep build action; config files can be saved on build via prompt
        self.btn_build_now = QtWidgets.QPushButton("Build Now (Selected)")
        self.btn_build_now.clicked.connect(self._build_now)
        self.btn_build_now.setStyleSheet("background-color: #4a7c59; font-weight: bold;")
        action_layout.addWidget(self.btn_build_now)

        scroll_layout.addLayout(action_layout)

        # Finalize scroll area
        scroll.setWidget(scroll_widget)
        outer_layout.addWidget(scroll)

        # Status bar (kept outside the scroll area)
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #333; color: #eee;")
        outer_layout.addWidget(self.status_label)

    def _update_env_ui(self):
        """Refresh env lights count label and paths display."""
        try:
            self.lbl_env_count.setText(f"{len(self.env_light_paths)} files")
        except Exception:
            pass
        try:
            self.env_paths_edit.setPlainText("\n".join(self.env_light_paths))
        except Exception:
            pass

    def _update_env_enabled(self):
        """Enable/disable env lights widgets based on the checkbox state."""
        enabled = False
        try:
            enabled = bool(self.cb_enable_env_lights.isChecked())
        except Exception:
            enabled = False
        # Disable or enable the Add and Clear buttons and the paths display box
        for w in (getattr(self, 'btn_add_env', None), getattr(self, 'btn_clear_env', None), getattr(self, 'env_paths_edit', None)):
            try:
                if w is not None:
                    w.setEnabled(enabled)
            except Exception:
                pass

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

    def _expand_assets_to_individual_variants(self, assets: List[DetectedAsset]) -> List[DetectedAsset]:
        """
        Expand each detected asset group into individual assets (one per geometry file).

        Example:
          Input:  1 asset with main=PropCargo, variants=[PropCargo_B, PropCargo_C]
          Output: 3 assets:
                  - PropCargo_A (main=PropCargo, variants=[PropCargo_B, PropCargo_C])
                  - PropCargo_B (main=PropCargo_B, variants=[PropCargo, PropCargo_C])
                  - PropCargo_C (main=PropCargo_C, variants=[PropCargo, PropCargo_B])
        """
        expanded_assets = []

        for asset in assets:
            # Collect all geometry files (main + variants)
            all_geo_files = [asset.main_file] + asset.geo_variants

            # Sort files to maintain consistent ordering
            def _variant_sort_key(filepath: str):
                filename = os.path.basename(filepath)
                base_name, suffix = self._extract_base_and_suffix_from_path(filepath)
                s = suffix or ""
                s_low = s.lower()

                # Single letter _A/_B/_C
                m = re.match(r'^_([A-Za-z])$', s)
                if m:
                    ch = m.group(1).upper()
                    return (0, ord(ch) - ord('A'))

                # Files without suffix come first
                if not s:
                    return (-1, filename.lower())

                # Pure numbered _1, _2
                m = re.match(r'^_(\d+)$', s)
                if m:
                    return (1, int(m.group(1)))

                # Fallback: lexicographic
                return (9, filename.lower())

            all_geo_files.sort(key=_variant_sort_key)

            # Create one DetectedAsset for each geometry file
            for i, geo_file in enumerate(all_geo_files):
                # Determine asset name with letter suffix
                base_filename = os.path.basename(geo_file)
                name_without_ext = os.path.splitext(base_filename)[0]
                if name_without_ext.lower().endswith('.bgeo'):
                    name_without_ext = name_without_ext[:-5]  # Remove .bgeo from .bgeo.sc

                # Extract base and suffix
                base_name, existing_suffix = self._extract_base_and_suffix_from_path(geo_file)

                # Assign letter position
                letter = chr(ord('A') + i)

                # If file already has a letter suffix, use it; otherwise add the letter
                if existing_suffix and re.match(r'^_[A-Z]$', existing_suffix):
                    display_name = f"{base_name}{existing_suffix}"
                elif not existing_suffix:
                    display_name = f"{base_name}_{letter}"
                else:
                    # Has a different suffix (like _B, _C from scanning), use as-is but show position
                    display_name = name_without_ext

                # Create variants list (all other files except this one)
                variants = [f for f in all_geo_files if f != geo_file]

                # Create new DetectedAsset for this specific file
                individual_asset = DetectedAsset(
                    name=display_name,
                    main_file=geo_file,
                    base_path=asset.base_path,
                    geo_variants=variants,
                    texture_path=asset.texture_path,
                    material_variants=asset.material_variants,
                    detected_suffix=f"Position {letter}"
                )

                expanded_assets.append(individual_asset)

        return expanded_assets

    def _browse_env_lights(self):
        """Browse and add one or more environment light (HDRI) files."""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Environment Light Files",
            "",
            "HDRI Files (*.exr *.hdr *.rat);;All Files (*)"
        )
        if files:
            # Merge unique paths preserving order
            existing = set(self.env_light_paths)
            for f in files:
                if f and f not in existing:
                    self.env_light_paths.append(f)
                    existing.add(f)
            # Update UI to reflect new list
            self._update_env_ui()

    def _clear_env_lights(self):
        """Clear selected environment lights list."""
        self.env_light_paths = []
        self._update_env_ui()

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

        # If "Generate variants by list" is unchecked, expand each asset into individual items
        if not self.cb_generate_list_variants.isChecked():
            self.detected_assets = self._expand_assets_to_individual_variants(self.detected_assets)

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
        """Filter detected assets by search text and sort by name asc/desc, then populate list,
        preserving current selections when possible (e.g., when clearing the search bar)."""
        # Capture currently selected items' stable keys (use main_file path which is unique per asset)
        selected_keys = set()
        try:
            for item in self.asset_list.selectedItems():
                asset = item.data(QtCore.Qt.UserRole)
                if asset and getattr(asset, 'main_file', None):
                    selected_keys.add(asset.main_file)
        except Exception:
            selected_keys = set()

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

        # Attempt to restore previous selection for items that are still visible under the new filter
        restored = 0
        try:
            for i in range(self.asset_list.count()):
                item = self.asset_list.item(i)
                asset = item.data(QtCore.Qt.UserRole)
                if asset and getattr(asset, 'main_file', None) in selected_keys:
                    item.setSelected(True)
                    restored += 1
        except Exception:
            pass

        # If nothing is restored, itemSelectionChanged signal will have cleared details and count.
        # If items were restored, _on_selection_changed will update details and selection count accordingly.
        return

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

    def _get_variant_list_by_mode(self, asset: DetectedAsset) -> Tuple[str, List[str]]:
        """
        Generate variant list based on the checkbox mode.

        Note: When "Generate variants by list" is unchecked, assets are already
        expanded into individual items during scanning, so each asset already has
        its correct main_file and geo_variants set up.

        Returns:
            (main_asset_path, variant_paths_list)
        """
        # Simply return the asset's main file and variants as-is
        # The expansion logic in _expand_assets_to_individual_variants already
        # set these up correctly based on the checkbox state
        return asset.main_file, asset.geo_variants

    def _extract_base_and_suffix_from_path(self, filepath: str) -> Tuple[str, str]:
        """Helper to extract base and suffix from full file path."""
        filename = os.path.basename(filepath)

        # Remove extension(s)
        name = filename
        if name.lower().endswith('.bgeo.sc'):
            name = name[:-8]
        else:
            name = os.path.splitext(name)[0]

        # Check for single letter suffix pattern _A, _B, _C
        m = re.search(r'_([A-Z])$', name)
        if m:
            suffix = m.group(0)
            base_name = name[:m.start()]
            return (base_name, suffix)

        # Check for other patterns
        m = re.search(r'_([a-z])$', name)
        if m:
            suffix = m.group(0)
            base_name = name[:m.start()]
            return (base_name, suffix)

        # No variant detected
        return (name, "")

    def _get_config_for_asset(self, asset: DetectedAsset) -> Dict:
        """Generate config dictionary for an asset."""
        # Get variant list based on mode
        main_asset_path, variant_paths = self._get_variant_list_by_mode(asset)

        config = {
            "main_asset_file_path": main_asset_path,
            "folder_textures": asset.texture_path or f"{asset.base_path}/textures",
            "asset_name": asset.name,
        }

        # Add geometry variants only if checkbox is enabled
        if variant_paths and self.cb_create_geo_variants.isChecked():
            config["asset_variants"] = variant_paths

        # Add material variants only if checkbox is enabled
        if asset.material_variants and self.cb_create_material_variants.isChecked():
            config["mtl_variants"] = asset.material_variants

        # Add options
        config["create_lookdev"] = self.cb_create_lookdev.isChecked()
        config["create_light_rig"] = self.cb_create_light_rig.isChecked()
        config["enable_env_lights"] = self.cb_enable_env_lights.isChecked()
        config["create_network_boxes"] = self.cb_create_network_boxes.isChecked()
        config["skip_matchsize"] = self.cb_skip_matchsize.isChecked()
        # Lowercase material names toggle for VEX wrangle
        try:
            config["lowercase_material_names"] = self.cb_lowercase_material_names.isChecked()
        except Exception:
            # Default to True if checkbox missing for any reason
            config["lowercase_material_names"] = True
        # Add env light files if provided
        if getattr(self, 'env_light_paths', None):
            config["env_light_paths"] = list(self.env_light_paths)

        # Component output mode
        try:
            config["use_custom_component_output"] = self.cb_use_custom_component_output.isChecked()
        except Exception:
            config["use_custom_component_output"] = True

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
        assets_in_order: List[DetectedAsset] = []
        for item in selected:
            asset: DetectedAsset = item.data(QtCore.Qt.UserRole)
            assets_in_order.append(asset)

        # Create the progress dialog FIRST so it shows immediately
        # We'll use a simple task count estimation (100 per asset) to avoid pre-scanning files
        progress_dialog = SimpleProgressDialog(title="LOPs Asset Builder v3 — Building Assets", parent=None)

        # Simple estimate: 100 tasks per asset (avoids slow file scanning before showing dialog)
        total_tasks = total_assets * 100

        try:
            # Ensure the dialog is visible and brought to front so the progress bar is shown
            progress_dialog.show()
            # Keep a strong reference so it doesn't close after completion due to GC
            try:
                _register_progress_dialog(progress_dialog)
            except Exception:
                pass
            try:
                progress_dialog.raise_()
                progress_dialog.activateWindow()
            except Exception:
                pass
            # Initialize progress range using total tasks and start at 0
            try:
                progress_dialog._tasks_total = int(total_tasks)
                progress_dialog._tasks_done = 0
                # Store total number of assets for progress formatting in reporter
                progress_dialog._total_assets = int(total_assets)
            except Exception:
                pass
            progress_dialog.set_total(int(total_tasks))
            progress_dialog.set_value(0)
            progress_dialog.set_message(f"Starting batch build of {total_assets} asset(s)…")
            progress_dialog.log(f"Starting batch build of {total_assets} asset(s). Progress is based on {total_tasks} material creation task(s).")
            # Close the main dialog so only the progress window remains visible
            try:
                self.close()
            except Exception:
                try:
                    self.hide()
                except Exception:
                    pass
        except Exception:
            pass

        cancelled = False
        for idx, asset in enumerate(assets_in_order, start=1):
            config = self._get_config_for_asset(asset)

            # Log current building status to the progress dialog instead of updating the closed main dialog
            try:
                progress_dialog.log(f"Building {asset.name} ({idx}/{total_assets})…")
            except Exception:
                pass
            QtWidgets.QApplication.processEvents()

            reporter = BatchUIProgressReporter(
                progress_dialog,
                asset_index=idx,
                asset_label=asset.name,
                expected_tasks_for_asset=100  # Simple fixed estimate per asset
            )

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

        # Finalize progress dialog and log summary directly in it (no extra dialogs)
        try:
            success_count = sum(1 for _, r in results if getattr(r, 'success', False))
            failed_count = len(results) - success_count
            summary_header = "Build cancelled by user" if cancelled else "Batch build completed"
            progress_dialog.set_message(summary_header)
            progress_dialog.log("\n=== SUMMARY ===")
            progress_dialog.log(f"Success: {success_count}")
            progress_dialog.log(f"Failed:  {failed_count}")
            if failed_count > 0:
                progress_dialog.log("Failed assets:")
                for name, result in results:
                    if not getattr(result, 'success', False):
                        progress_dialog.log(f"  • {name}: {getattr(result, 'message', '')}")
            # Clamp progress to 100% at the end using the precomputed tasks total
            try:
                total_final = int(getattr(progress_dialog, "_tasks_total", 0) or progress_dialog.progress_bar.maximum())
                progress_dialog.set_total(total_final)
                progress_dialog.set_value(total_final)
            except Exception:
                pass
            progress_dialog.mark_finished()
        except Exception:
            pass

        # Do not show any QMessageBox or reopen the main dialog — only the progress dialog should remain visible
        return


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
