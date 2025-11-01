"""
Asset Folder Analyzer UI - Interactive tool for scanning and importing asset folders

This tool provides a graphical interface to:
- Scan asset folders and identify structure
- Preview assets, variants, and materials
- Import geometry as USD references with spatial distribution
- Expand MaterialX materials to editable VOP networks
"""

import hou
import os
from PySide6 import QtWidgets, QtGui, QtCore

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.asset_folder_scanner import scan_asset_folder
from modules.usd_reference_importer import import_scanned_assets
from modules.usd_material_expander import expand_materials_from_folder


class AssetFolderAnalyzerUI(QtWidgets.QMainWindow):
    """
    Main UI for Asset Folder Analyzer with scanning and import capabilities.
    """

    def __init__(self):
        super().__init__()

        # Set up window
        self.setWindowTitle("Asset Folder Analyzer")
        self.resize(1000, 800)

        # Center window
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - 1000) // 2
            y = (screen_geometry.height() - 800) // 2
            self.move(x, y)
        except Exception:
            pass

        # Parent to Houdini
        try:
            self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        except Exception:
            pass

        # Data
        self.scan_result = None
        self.folder_path = None

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Title section
        title_label = QtWidgets.QLabel("Asset Folder Analyzer")
        title_font = QtGui.QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Folder selection section
        folder_group = self._create_folder_section()
        main_layout.addWidget(folder_group)

        # Splitter for results and actions
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        # Results section
        results_widget = self._create_results_section()
        splitter.addWidget(results_widget)

        # Actions section
        actions_widget = self._create_actions_section()
        splitter.addWidget(actions_widget)

        splitter.setSizes([500, 300])
        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select a folder to scan.")

    def _create_folder_section(self):
        """Create the folder selection section."""
        group = QtWidgets.QGroupBox("1. Select Asset Folder")
        layout = QtWidgets.QVBoxLayout(group)

        # Folder path input
        folder_layout = QtWidgets.QHBoxLayout()

        self.folder_path_input = QtWidgets.QLineEdit()
        self.folder_path_input.setPlaceholderText("Path to asset folder...")
        folder_layout.addWidget(self.folder_path_input)

        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)

        layout.addLayout(folder_layout)

        # Subfolder configuration
        subfolder_layout = QtWidgets.QHBoxLayout()

        subfolder_layout.addWidget(QtWidgets.QLabel("Geometry Subfolder:"))
        self.geo_subfolder_input = QtWidgets.QLineEdit("geo")
        self.geo_subfolder_input.setMaximumWidth(150)
        subfolder_layout.addWidget(self.geo_subfolder_input)

        subfolder_layout.addWidget(QtWidgets.QLabel("Texture Subfolder:"))
        self.tex_subfolder_input = QtWidgets.QLineEdit("tex")
        self.tex_subfolder_input.setMaximumWidth(150)
        subfolder_layout.addWidget(self.tex_subfolder_input)

        subfolder_layout.addStretch()
        layout.addLayout(subfolder_layout)

        # Scan button
        self.scan_btn = QtWidgets.QPushButton("Scan Folder")
        self.scan_btn.setMinimumHeight(50)
        self.scan_btn.clicked.connect(self._scan_folder)
        scan_font = QtGui.QFont()
        scan_font.setPointSize(12)
        scan_font.setBold(True)
        self.scan_btn.setFont(scan_font)
        layout.addWidget(self.scan_btn)

        return group

    def _create_results_section(self):
        """Create the scan results display section."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        group = QtWidgets.QGroupBox("2. Scan Results")
        group_layout = QtWidgets.QVBoxLayout(group)

        # Summary section
        summary_layout = QtWidgets.QHBoxLayout()

        self.geo_count_label = QtWidgets.QLabel("Geometry Files: 0")
        summary_layout.addWidget(self.geo_count_label)

        self.tex_count_label = QtWidgets.QLabel("Texture Folders: 0")
        summary_layout.addWidget(self.tex_count_label)

        self.variant_count_label = QtWidgets.QLabel("Variants: 0")
        summary_layout.addWidget(self.variant_count_label)

        summary_layout.addStretch()
        group_layout.addLayout(summary_layout)

        # Tabs for detailed info
        self.results_tabs = QtWidgets.QTabWidget()

        # Geometry files tab with collapse/expand buttons
        geo_tab_widget = QtWidgets.QWidget()
        geo_tab_layout = QtWidgets.QVBoxLayout(geo_tab_widget)
        geo_tab_layout.setContentsMargins(0, 0, 0, 0)

        # Tree control buttons (small, aligned to right)
        geo_controls_layout = QtWidgets.QHBoxLayout()
        geo_controls_layout.addStretch()  # Push buttons to the right

        expand_all_btn = QtWidgets.QPushButton("Expand All")
        expand_all_btn.setFixedSize(80, 25)
        expand_all_btn.clicked.connect(lambda: self.geo_tree.expandAll())
        geo_controls_layout.addWidget(expand_all_btn)

        collapse_all_btn = QtWidgets.QPushButton("Collapse All")
        collapse_all_btn.setFixedSize(80, 25)
        collapse_all_btn.clicked.connect(lambda: self.geo_tree.collapseAll())
        geo_controls_layout.addWidget(collapse_all_btn)

        geo_tab_layout.addLayout(geo_controls_layout)

        # Geometry tree
        self.geo_tree = QtWidgets.QTreeWidget()
        self.geo_tree.setHeaderLabels(["Name", "Type", "Path"])
        self.geo_tree.setColumnWidth(0, 250)
        self.geo_tree.setColumnWidth(1, 100)
        geo_tab_layout.addWidget(self.geo_tree)

        self.results_tabs.addTab(geo_tab_widget, "Geometry Files")

        # Texture folders tab
        self.tex_tree = QtWidgets.QTreeWidget()
        self.tex_tree.setHeaderLabels(["Folder", "Resolution", "Textures", "Path"])
        self.tex_tree.setColumnWidth(0, 200)
        self.tex_tree.setColumnWidth(1, 100)
        self.tex_tree.setColumnWidth(2, 100)
        self.results_tabs.addTab(self.tex_tree, "Texture Folders")

        # Details tab
        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.results_tabs.addTab(self.details_text, "Details")

        group_layout.addWidget(self.results_tabs)
        layout.addWidget(group)

        return widget

    def _create_actions_section(self):
        """Create the actions section with workflow-based buttons."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        group = QtWidgets.QGroupBox("3. Asset Workflows")
        group_layout = QtWidgets.QVBoxLayout(group)

        # View selected details button
        details_btn_layout = QtWidgets.QHBoxLayout()
        details_btn_layout.addStretch()

        self.view_details_btn = QtWidgets.QPushButton("View Selected Asset Details")
        self.view_details_btn.setFixedSize(180, 28)
        self.view_details_btn.setEnabled(False)
        self.view_details_btn.clicked.connect(self._view_selected_details)
        details_btn_layout.addWidget(self.view_details_btn)

        group_layout.addLayout(details_btn_layout)

        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        group_layout.addWidget(separator)

        # LOPS Asset Builder V3
        builder_layout = QtWidgets.QVBoxLayout()
        builder_label = QtWidgets.QLabel("Build Complete LOPS Asset (Component + Materials + LookDev)")
        builder_label_font = QtGui.QFont()
        builder_label_font.setBold(True)
        builder_label.setFont(builder_label_font)
        builder_layout.addWidget(builder_label)

        self.lops_builder_btn = QtWidgets.QPushButton("🏗 LOPS Asset Builder V3")
        self.lops_builder_btn.setMinimumHeight(45)
        self.lops_builder_btn.setEnabled(False)
        self.lops_builder_btn.clicked.connect(self._launch_lops_builder)
        builder_font = QtGui.QFont()
        builder_font.setPointSize(11)
        builder_font.setBold(True)
        self.lops_builder_btn.setFont(builder_font)
        builder_layout.addWidget(self.lops_builder_btn)

        group_layout.addLayout(builder_layout)

        # Separator
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setFrameShadow(QtWidgets.QFrame.Sunken)
        group_layout.addWidget(separator2)

        # Quick Actions section
        quick_label = QtWidgets.QLabel("Quick Actions")
        quick_label_font = QtGui.QFont()
        quick_label_font.setBold(True)
        quick_label.setFont(quick_label_font)
        group_layout.addWidget(quick_label)

        # TexToMtlX button
        self.tex_to_mtlx_btn = QtWidgets.QPushButton("📄 Create Materials from Textures (TexToMtlX)")
        self.tex_to_mtlx_btn.setMinimumHeight(35)
        self.tex_to_mtlx_btn.setEnabled(False)
        self.tex_to_mtlx_btn.clicked.connect(self._launch_tex_to_mtlx)
        group_layout.addWidget(self.tex_to_mtlx_btn)

        # Add to Asset Library button
        self.add_library_btn = QtWidgets.QPushButton("📚 Add Selected to Asset Library")
        self.add_library_btn.setMinimumHeight(35)
        self.add_library_btn.setEnabled(False)
        self.add_library_btn.clicked.connect(self._add_to_asset_library)
        group_layout.addWidget(self.add_library_btn)

        # Generate Thumbnail button
        self.gen_thumb_btn = QtWidgets.QPushButton("📷 Generate Thumbnail for Selected")
        self.gen_thumb_btn.setMinimumHeight(35)
        self.gen_thumb_btn.setEnabled(False)
        self.gen_thumb_btn.clicked.connect(self._generate_thumbnail)
        group_layout.addWidget(self.gen_thumb_btn)

        layout.addWidget(group)

        return widget

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Asset Folder",
            os.path.expanduser("~"),
            QtWidgets.QFileDialog.ShowDirsOnly
        )

        if folder:
            self.folder_path_input.setText(folder)

    def _scan_folder(self):
        """Scan the selected folder."""
        folder_path = self.folder_path_input.text().strip()

        if not folder_path:
            QtWidgets.QMessageBox.warning(
                self,
                "No Folder Selected",
                "Please select a folder to scan."
            )
            return

        if not os.path.exists(folder_path):
            QtWidgets.QMessageBox.warning(
                self,
                "Folder Not Found",
                f"The folder does not exist:\n{folder_path}"
            )
            return

        # Update status
        self.status_bar.showMessage("Scanning folder...")
        QtWidgets.QApplication.processEvents()

        try:
            # Scan the folder
            geo_subfolder = self.geo_subfolder_input.text().strip()
            tex_subfolder = self.tex_subfolder_input.text().strip()

            self.scan_result = scan_asset_folder(
                folder_path,
                geo_subfolder=geo_subfolder,
                tex_subfolder=tex_subfolder
            )
            self.folder_path = folder_path

            # Update UI with results
            self._display_results()

            # Enable action buttons
            self.lops_builder_btn.setEnabled(True)
            self.tex_to_mtlx_btn.setEnabled(True)
            self.add_library_btn.setEnabled(True)
            self.gen_thumb_btn.setEnabled(True)
            self.view_details_btn.setEnabled(True)

            self.status_bar.showMessage("Scan complete!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Scan Error",
                f"Error scanning folder:\n{str(e)}"
            )
            self.status_bar.showMessage("Scan failed!")

    def _display_results(self):
        """Display scan results in the UI."""
        if not self.scan_result:
            return

        # Update summary counts
        geo_count = len(self.scan_result.get('geometry_files', {}))
        tex_count = len(self.scan_result.get('texture_folders', {}))

        # Count variants
        variant_count = 0
        for file_info in self.scan_result.get('geometry_files', {}).values():
            if file_info.get('is_variant'):
                variant_count += 1

        self.geo_count_label.setText(f"Geometry Files: {geo_count}")
        self.tex_count_label.setText(f"Texture Folders: {tex_count}")
        self.variant_count_label.setText(f"Variants: {variant_count}")

        # Populate geometry tree
        self.geo_tree.clear()
        geo_files = self.scan_result.get('geometry_files', {})

        # Group by folder
        folders = {}
        for name, info in geo_files.items():
            rel_dir = info.get('relative_dir', '')
            if rel_dir not in folders:
                folders[rel_dir] = []
            folders[rel_dir].append((name, info))

        for folder_name in sorted(folders.keys()):
            folder_item = QtWidgets.QTreeWidgetItem([folder_name, "Folder", ""])
            folder_item.setFont(0, QtGui.QFont("", -1, QtGui.QFont.Bold))

            for name, info in sorted(folders[folder_name]):
                file_type = "Variant" if info.get('is_variant') else "Main"
                file_item = QtWidgets.QTreeWidgetItem([
                    info.get('filename', name),
                    file_type,
                    info.get('path', '')
                ])
                folder_item.addChild(file_item)

            self.geo_tree.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)

        # Populate texture tree
        self.tex_tree.clear()
        tex_folders = self.scan_result.get('texture_folders', {})

        for path, info in sorted(tex_folders.items(), key=lambda x: x[1].get('priority', 0), reverse=True):
            item = QtWidgets.QTreeWidgetItem([
                info.get('name', ''),
                info.get('resolution', 'unknown'),
                str(info.get('texture_count', 0)),
                path
            ])

            # Highlight main texture folder
            if path == self.scan_result.get('main_textures'):
                font = QtGui.QFont()
                font.setBold(True)
                item.setFont(0, font)
                item.setForeground(0, QtGui.QColor(100, 200, 100))

            self.tex_tree.addTopLevelItem(item)

        # Update details text
        import pprint
        details = pprint.pformat(self.scan_result, width=100)
        self.details_text.setPlainText(details)

    def _view_selected_details(self):
        """View details of selected assets in a new window."""
        selected_items = self.geo_tree.selectedItems()

        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection",
                "Please select one or more assets in the Geometry Files tree."
            )
            return

        # Collect details for selected items
        details_text = "=" * 70 + "\n"
        details_text += "SELECTED ASSET DETAILS\n"
        details_text += "=" * 70 + "\n\n"

        for item in selected_items:
            # Skip folder items
            if item.text(1) == "Folder":
                continue

            asset_path = item.text(2)
            asset_name = item.text(0)
            asset_type = item.text(1)

            # Find asset info in scan results
            geo_files = self.scan_result.get('geometry_files', {})
            asset_info = None

            for name, info in geo_files.items():
                if info.get('path') == asset_path:
                    asset_info = info
                    break

            if asset_info:
                details_text += f"Asset: {asset_name}\n"
                details_text += f"Type: {asset_type}\n"
                details_text += f"Path: {asset_path}\n"
                details_text += f"Extension: {asset_info.get('extension', 'N/A')}\n"
                details_text += f"Folder: {asset_info.get('relative_dir', 'N/A')}\n"

                if asset_info.get('is_variant'):
                    details_text += f"Variant Suffix: {asset_info.get('variant_suffix', 'N/A')}\n"
                    details_text += f"Base Name: {asset_info.get('true_base_name', 'N/A')}\n"

                details_text += "\n" + "-" * 70 + "\n\n"

        # Create details dialog
        details_dialog = QtWidgets.QDialog(self)
        details_dialog.setWindowTitle("Selected Asset Details")
        details_dialog.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(details_dialog)

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        text_edit.setPlainText(details_text)
        layout.addWidget(text_edit)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(details_dialog.close)
        layout.addWidget(close_btn)

        details_dialog.exec_()

    def _launch_lops_builder(self):
        """Launch LOPS Asset Builder V3 with pre-filled data from scan."""
        if not self.scan_result:
            return

        try:
            from tools.lops_asset_builder_v3.lops_asset_builder_v3 import create_component_builder

            # Get selected asset from tree
            selected_items = self.geo_tree.selectedItems()

            # Pre-populate with scan data if we can
            main_asset = self.scan_result.get('main_asset')
            main_textures = self.scan_result.get('main_textures')

            QtWidgets.QMessageBox.information(
                self,
                "LOPS Asset Builder V3",
                f"Launching LOPS Asset Builder V3...\n\n"
                f"Suggested inputs from scan:\n"
                f"  Main Asset: {os.path.basename(main_asset) if main_asset else 'N/A'}\n"
                f"  Textures: {os.path.basename(main_textures) if main_textures else 'N/A'}\n"
                f"  Asset Variants: {len(self.scan_result.get('asset_variants', []))}\n"
                f"  Material Variants: {len(self.scan_result.get('material_variants', []))}\n\n"
                f"The Asset Builder dialog will open.\n"
                f"You can use the paths from the scan results."
            )

            # Launch the tool
            create_component_builder()

            self.status_bar.showMessage("LOPS Asset Builder V3 launched")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Launch Error",
                f"Error launching LOPS Asset Builder V3:\n{str(e)}"
            )

    def _launch_tex_to_mtlx(self):
        """Launch TexToMtlX tool with texture folder from scan."""
        if not self.scan_result:
            return

        try:
            from tools.tex_to_mtlx import TxToMtlx

            main_textures = self.scan_result.get('main_textures')

            QtWidgets.QMessageBox.information(
                self,
                "TexToMtlX Tool",
                f"Launching TexToMtlX...\n\n"
                f"Detected texture folder:\n{main_textures if main_textures else 'N/A'}\n\n"
                f"The TexToMtlX dialog will open.\n"
                f"Use 'Open Folder' to select the texture folder."
            )

            # Launch the tool
            tool = TxToMtlx()
            tool.show()

            self.status_bar.showMessage("TexToMtlX launched")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Launch Error",
                f"Error launching TexToMtlX:\n{str(e)}"
            )

    def _add_to_asset_library(self):
        """Add selected assets to Houdini asset library."""
        selected_items = self.geo_tree.selectedItems()

        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection",
                "Please select one or more assets to add to the library."
            )
            return

        # Collect asset paths
        asset_paths = []
        for item in selected_items:
            if item.text(1) != "Folder":
                asset_paths.append(item.text(2))

        QtWidgets.QMessageBox.information(
            self,
            "Add to Asset Library",
            f"Feature Coming Soon!\n\n"
            f"Will add {len(asset_paths)} asset(s) to Houdini's asset library.\n\n"
            f"This will integrate with Houdini's asset browser."
        )

    def _generate_thumbnail(self):
        """Generate thumbnail for selected asset."""
        selected_items = self.geo_tree.selectedItems()

        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection",
                "Please select an asset to generate a thumbnail."
            )
            return

        asset_path = None
        for item in selected_items:
            if item.text(1) != "Folder":
                asset_path = item.text(2)
                break

        if asset_path:
            QtWidgets.QMessageBox.information(
                self,
                "Generate Thumbnail",
                f"Feature Coming Soon!\n\n"
                f"Will generate thumbnail for:\n{os.path.basename(asset_path)}\n\n"
                f"This will create a preview image for the asset browser."
            )


def show_asset_folder_analyzer():
    """
    Show the Asset Folder Analyzer UI.
    """
    global asset_analyzer_window

    try:
        asset_analyzer_window.close()
        asset_analyzer_window.deleteLater()
    except:
        pass

    asset_analyzer_window = AssetFolderAnalyzerUI()
    asset_analyzer_window.show()

    return asset_analyzer_window



