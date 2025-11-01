#!/usr/bin/env python
"""
Standalone Texture to MaterialX Converter

A simplified version of tex_to_mtlx that directly creates MaterialX and USD files
from texture folders without requiring a material library node in Houdini.

This tool uses the modular materialx_exporter and usd_exporter modules, making it
suitable for integration into the main tex_to_mtlx tool or use independently.

Features:
    - Simple UI asking for texture folder
    - Auto-detects materials from texture naming
    - Creates .mtlx files directly
    - Optionally creates .usd files with variants
    - No Houdini nodes required
    - Can export multiple materials at once

Usage:
    # From Houdini Python Shell or shelf tool:
    from tools.material_tools.tex_to_mtlx_standalone import show_standalone_converter
    show_standalone_converter()

    # Or use programmatically:
    from tools.material_tools.tex_to_mtlx_standalone import convert_textures_to_materialx
    convert_textures_to_materialx('/path/to/textures', '/path/to/output')
"""

import os
import re
import hou
from PySide6 import QtWidgets, QtCore
from collections import defaultdict
from typing import Dict, List, Optional

from .materialx_exporter import MaterialXExporter
from .usd_exporter import USDExporter
from tools.material_tools.TexToMtlX_V2.txmtlx_config import (
    TEXTURE_EXT,
    TEXTURE_TYPE,
    TEXTURE_TYPE_SORTED,
    UDIM_PATTERN,
    SIZE_PATTERN
)
from modules.misc_utils import slugify


class StandaloneMaterialXConverter(QtWidgets.QMainWindow):
    """
    Standalone UI for converting textures to MaterialX/USD files.
    """

    def __init__(self):
        super().__init__()

        # Setup central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Window properties
        self.setWindowTitle("Standalone MaterialX Converter")
        self.resize(700, 650)

        try:
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - 700) // 2
            y = (screen_geometry.height() - 650) // 2
            self.move(x, y)
        except Exception:
            pass

        try:
            self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        except Exception:
            pass

        # Initialize exporters
        self.mtlx_exporter = MaterialXExporter()
        self.usd_exporter = USDExporter()

        # Data
        self.texture_folder = None
        self.output_folder = None
        self.detected_materials = {}

        # Setup UI
        self._setup_help_section()
        self._setup_folder_section()
        self._setup_options_section()
        self._setup_materials_list()
        self._setup_export_section()

    def _setup_help_section(self):
        """Setup help text."""
        help_text = QtWidgets.QLabel(
            "<b>Standalone MaterialX/USD Converter</b><br>"
            "Convert texture folders directly to MaterialX and USD files without creating Houdini nodes.<br>"
            "Auto-detects materials based on texture naming conventions."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("padding: 10px; background-color: #2a2a2a; border-radius: 5px;")
        self.main_layout.addWidget(help_text)

    def _setup_folder_section(self):
        """Setup folder selection section."""
        folder_group = QtWidgets.QGroupBox("Folders")
        folder_layout = QtWidgets.QVBoxLayout()

        # Texture folder
        tex_row = QtWidgets.QHBoxLayout()
        tex_row.addWidget(QtWidgets.QLabel("Texture Folder:"))
        self.texture_folder_edit = QtWidgets.QLineEdit()
        self.texture_folder_edit.setPlaceholderText("Select folder containing textures...")
        tex_row.addWidget(self.texture_folder_edit, 1)

        browse_tex_btn = QtWidgets.QPushButton("Browse...")
        browse_tex_btn.clicked.connect(self._browse_texture_folder)
        tex_row.addWidget(browse_tex_btn)

        scan_btn = QtWidgets.QPushButton("Scan")
        scan_btn.clicked.connect(self._scan_textures)
        scan_btn.setStyleSheet("font-weight: bold;")
        tex_row.addWidget(scan_btn)

        folder_layout.addLayout(tex_row)

        # Output folder
        out_row = QtWidgets.QHBoxLayout()
        out_row.addWidget(QtWidgets.QLabel("Output Folder:"))
        self.output_folder_edit = QtWidgets.QLineEdit()
        self.output_folder_edit.setPlaceholderText("Select output folder for .mtlx and .usd files...")
        out_row.addWidget(self.output_folder_edit, 1)

        browse_out_btn = QtWidgets.QPushButton("Browse...")
        browse_out_btn.clicked.connect(self._browse_output_folder)
        out_row.addWidget(browse_out_btn)

        folder_layout.addLayout(out_row)

        folder_group.setLayout(folder_layout)
        self.main_layout.addWidget(folder_group)

    def _setup_options_section(self):
        """Setup export options."""
        options_group = QtWidgets.QGroupBox("Export Options")
        options_layout = QtWidgets.QVBoxLayout()

        # MaterialX option
        self.create_mtlx_check = QtWidgets.QCheckBox("Create MaterialX (.mtlx) files")
        self.create_mtlx_check.setChecked(True)
        options_layout.addWidget(self.create_mtlx_check)

        # USD option
        self.create_usd_check = QtWidgets.QCheckBox("Create USD (.usd) files")
        self.create_usd_check.setChecked(True)
        options_layout.addWidget(self.create_usd_check)

        # Relative texture path
        rel_path_row = QtWidgets.QHBoxLayout()
        rel_path_row.addWidget(QtWidgets.QLabel("Relative Texture Path:"))
        self.rel_tex_path_edit = QtWidgets.QLineEdit()
        self.rel_tex_path_edit.setText("../../Textures/png4k/")
        self.rel_tex_path_edit.setPlaceholderText("e.g., ../../Textures/png4k/")
        self.rel_tex_path_edit.setToolTip("Relative path prefix for textures in MaterialX files")
        rel_path_row.addWidget(self.rel_tex_path_edit, 1)
        options_layout.addLayout(rel_path_row)

        # UDIM detection
        self.detect_udim_check = QtWidgets.QCheckBox("Auto-detect UDIM textures")
        self.detect_udim_check.setChecked(True)
        options_layout.addWidget(self.detect_udim_check)

        # KB3D variants
        self.kb3d_variants_check = QtWidgets.QCheckBox("Add KB3D-style texture variants to USD")
        self.kb3d_variants_check.setChecked(False)
        self.kb3d_variants_check.setToolTip("Adds jpg1k, jpg2k, jpg4k, png1k, png2k, png4k variants to USD files")
        options_layout.addWidget(self.kb3d_variants_check)

        # Separator
        options_layout.addWidget(QtWidgets.QLabel(""))

        # KB3D Metadata section
        metadata_label = QtWidgets.QLabel("<b>USD Metadata (KB3D Kit Info)</b>")
        options_layout.addWidget(metadata_label)

        # Kit Display Name
        kit_name_row = QtWidgets.QHBoxLayout()
        kit_name_row.addWidget(QtWidgets.QLabel("Kit Display Name:"))
        self.kit_display_name_edit = QtWidgets.QLineEdit()
        self.kit_display_name_edit.setText("Custom Materials")
        self.kit_display_name_edit.setPlaceholderText("e.g., My Custom Kit")
        self.kit_display_name_edit.setToolTip("Human-readable name for the material kit")
        kit_name_row.addWidget(self.kit_display_name_edit, 1)
        options_layout.addLayout(kit_name_row)

        # Kit ID
        kit_id_row = QtWidgets.QHBoxLayout()
        kit_id_row.addWidget(QtWidgets.QLabel("Kit ID:"))
        self.kit_id_edit = QtWidgets.QLineEdit()
        self.kit_id_edit.setText("custom_materials")
        self.kit_id_edit.setPlaceholderText("e.g., my_custom_kit")
        self.kit_id_edit.setToolTip("Unique identifier for the kit (lowercase, underscores)")
        kit_id_row.addWidget(self.kit_id_edit, 1)
        options_layout.addLayout(kit_id_row)

        # Kit Version
        kit_version_row = QtWidgets.QHBoxLayout()
        kit_version_row.addWidget(QtWidgets.QLabel("Kit Version:"))
        self.kit_version_edit = QtWidgets.QLineEdit()
        self.kit_version_edit.setText("1.0.0")
        self.kit_version_edit.setPlaceholderText("e.g., 1.0.0")
        self.kit_version_edit.setToolTip("Version number (semver format recommended)")
        kit_version_row.addWidget(self.kit_version_edit, 1)
        options_layout.addLayout(kit_version_row)

        options_group.setLayout(options_layout)
        self.main_layout.addWidget(options_group)

    def _setup_materials_list(self):
        """Setup detected materials list."""
        materials_group = QtWidgets.QGroupBox("Detected Materials")
        materials_layout = QtWidgets.QVBoxLayout()

        # Header
        header_row = QtWidgets.QHBoxLayout()
        self.materials_label = QtWidgets.QLabel("No materials detected")
        header_row.addWidget(self.materials_label)
        header_row.addStretch()

        self.select_all_btn = QtWidgets.QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all_materials)
        self.select_all_btn.setEnabled(False)
        header_row.addWidget(self.select_all_btn)

        self.deselect_all_btn = QtWidgets.QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self._deselect_all_materials)
        self.deselect_all_btn.setEnabled(False)
        header_row.addWidget(self.deselect_all_btn)

        materials_layout.addLayout(header_row)

        # List view
        self.materials_list = QtWidgets.QListWidget()
        self.materials_list.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
        self.materials_list.setMinimumHeight(200)
        materials_layout.addWidget(self.materials_list)

        materials_group.setLayout(materials_layout)
        self.main_layout.addWidget(materials_group)

    def _setup_export_section(self):
        """Setup export button and progress."""
        export_layout = QtWidgets.QVBoxLayout()

        # Export button
        self.export_btn = QtWidgets.QPushButton("Export Materials")
        self.export_btn.setMinimumHeight(50)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.export_btn.clicked.connect(self._export_materials)
        export_layout.addWidget(self.export_btn)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setValue(0)
        export_layout.addWidget(self.progress_bar)

        self.main_layout.addLayout(export_layout)

    def _browse_texture_folder(self):
        """Browse for texture folder."""
        folder = hou.ui.selectFile(
            title="Select Texture Folder",
            file_type=hou.fileType.Directory
        )

        if folder:
            folder = hou.text.expandString(folder.strip())
            self.texture_folder_edit.setText(folder)

    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = hou.ui.selectFile(
            title="Select Output Folder",
            file_type=hou.fileType.Directory
        )

        if folder:
            folder = hou.text.expandString(folder.strip())
            self.output_folder_edit.setText(folder)

    def _scan_textures(self):
        """Scan texture folder for materials."""
        texture_folder = self.texture_folder_edit.text().strip()

        if not texture_folder:
            hou.ui.displayMessage("Please select a texture folder", severity=hou.severityType.Error)
            return

        texture_folder = hou.text.expandString(texture_folder)

        if not os.path.exists(texture_folder):
            hou.ui.displayMessage(f"Folder does not exist:\n{texture_folder}", severity=hou.severityType.Error)
            return

        # Detect materials
        self.detected_materials = self._detect_materials_in_folder(texture_folder)

        if not self.detected_materials:
            hou.ui.displayMessage(
                "No materials detected in this folder.\n\n"
                "Expected texture naming: MaterialName_textureType.ext\n"
                "e.g., MyMaterial_basecolor.png, MyMaterial_normal.png",
                severity=hou.severityType.Warning
            )
            return

        # Update UI
        self.materials_list.clear()
        for mat_name, tex_info in self.detected_materials.items():
            # Count actual texture types (exclude metadata keys)
            skip_keys = {'UDIM', 'Size', 'FOLDER_PATH'}
            texture_count = sum(1 for k in tex_info.keys() if k not in skip_keys)

            # Build display text
            item_text = f"{mat_name} ({texture_count} texture types"
            if tex_info.get('Size'):
                item_text += f", {tex_info['Size']}"
            if tex_info.get('UDIM'):
                item_text += ", UDIM"
            item_text += ")"

            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, mat_name)
            self.materials_list.addItem(item)

        self.materials_label.setText(f"Detected {len(self.detected_materials)} material(s)")
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        # Auto-select all
        self.materials_list.selectAll()

    def _detect_materials_in_folder(self, folder: str) -> Dict:
        """
        Detect materials in folder based on texture naming.
        Uses same logic as tex_to_mtlx to properly identify materials.

        Returns:
            dict: Material name -> texture_list dict (same structure as tex_to_mtlx)
        """
        try:
            # Use the exact same logic as tex_to_mtlx.get_texture_details()
            texture_list = defaultdict(lambda: defaultdict(list))

            if not os.path.exists(folder):
                return {}

            # Get all valid texture files
            valid_files = []
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                # Conditions
                is_file = os.path.isfile(file_path)
                valid_extension = file.lower().endswith(tuple(TEXTURE_EXT))
                check_underscore = "_" in file
                if is_file and valid_extension and check_underscore:
                    valid_files.append(file)

            # Process files - textures (exact same logic as tex_to_mtlx)
            for file in valid_files:
                split_text = os.path.splitext(file)[0]
                split_text = split_text.split("_")
                material_name = split_text[0]

                # Find the texture type
                texture_type = None
                for tx_type in TEXTURE_TYPE:
                    for tx in split_text[1:]:
                        if tx.lower() == tx_type:
                            texture_type = tx_type
                            index = split_text.index(tx)
                            material_name = '_'.join(split_text[:index])
                            break

                if not texture_type:
                    continue

                # Get UDIM and Size
                udim_match = UDIM_PATTERN.search(file)
                size_match = SIZE_PATTERN.search(file)

                # Clean material name but PRESERVE CASING (don't use slugify which lowercases)
                # Just replace spaces and hyphens with underscores
                clean_name = material_name.replace(' ', '_').replace('-', '_')

                # Update texture list
                texture_list[clean_name][texture_type].append(file)
                texture_list[clean_name]['UDIM'] = bool(udim_match)
                texture_list[clean_name]['FOLDER_PATH'] = folder
                if size_match:
                    texture_list[clean_name]['Size'] = size_match.group(1)

            # Convert defaultdict to regular dictionary
            texture_list = dict(texture_list)
            _new_dict = {}
            for mat, text_dat in texture_list.items():
                _new_dict[mat] = dict(text_dat)

            return _new_dict

        except Exception as e:
            print(f"Error detecting materials: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def _select_all_materials(self):
        """Select all materials in list."""
        self.materials_list.selectAll()

    def _deselect_all_materials(self):
        """Deselect all materials."""
        self.materials_list.clearSelection()

    def _export_materials(self):
        """Export selected materials."""
        # Get selections
        selected_items = self.materials_list.selectedItems()
        if not selected_items:
            hou.ui.displayMessage("Please select at least one material", severity=hou.severityType.Error)
            return

        texture_folder = hou.text.expandString(self.texture_folder_edit.text().strip())
        output_folder = hou.text.expandString(self.output_folder_edit.text().strip())

        if not output_folder:
            hou.ui.displayMessage("Please select an output folder", severity=hou.severityType.Error)
            return

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        # Get options
        create_mtlx = self.create_mtlx_check.isChecked()
        create_usd = self.create_usd_check.isChecked()
        rel_tex_path = self.rel_tex_path_edit.text().strip() or None
        detect_udim = self.detect_udim_check.isChecked()
        kb3d_variants = self.kb3d_variants_check.isChecked()

        # Get KB3D metadata
        kit_info = {
            'kitDisplayName': self.kit_display_name_edit.text().strip() or 'Custom Materials',
            'kitId': self.kit_id_edit.text().strip() or 'custom_materials',
            'kitVersion': self.kit_version_edit.text().strip() or '1.0.0'
        }

        # Progress
        self.progress_bar.setMaximum(len(selected_items))
        progress_value = 0

        # Results
        results = {'success': [], 'failed': []}

        # Export each material
        for item in selected_items:
            mat_name = item.data(QtCore.Qt.UserRole)

            try:
                # Create material folder
                mat_folder = os.path.join(output_folder, mat_name)
                os.makedirs(mat_folder, exist_ok=True)

                mtlx_file = None

                # Export MaterialX
                if create_mtlx:
                    mtlx_file = os.path.join(mat_folder, f"{mat_name}.mtlx")
                    mtlx_result = self.mtlx_exporter.export_from_folder(
                        texture_folder=texture_folder,
                        output_file=mtlx_file,
                        material_name=mat_name,
                        relative_texture_path=rel_tex_path,
                        detect_udim=detect_udim
                    )

                    if not mtlx_result['success']:
                        results['failed'].append(f"{mat_name} (MaterialX): {mtlx_result['error']}")
                        continue

                # Export USD (.usd extension with ASCII format inside, like KB3D)
                if create_usd and mtlx_file:
                    # KB3D uses .usd extension but the file is ASCII format (human-readable)
                    # We match this behavior: .usd extension, ASCII content
                    usd_file = os.path.join(mat_folder, f"{mat_name}.usd")

                    if kb3d_variants:
                        # Use KB3D-style USD with variants (ASCII format)
                        from .usd_exporter import create_kb3d_style_usd
                        usd_result = create_kb3d_style_usd(
                            material_name=mat_name,
                            mtlx_file=f"./{mat_name}.mtlx",
                            output_file=usd_file,
                            kit_info=kit_info  # Use user-provided metadata
                        )
                    else:
                        # Simple USD reference (ASCII format)
                        usd_result = self.usd_exporter.create_simple_usd_reference(
                            material_name=mat_name,
                            mtlx_file=f"./{mat_name}.mtlx",
                            output_file=usd_file
                        )

                    if not usd_result['success']:
                        results['failed'].append(f"{mat_name} (USD): {usd_result['error']}")
                        continue

                results['success'].append(mat_name)

            except Exception as e:
                results['failed'].append(f"{mat_name}: {str(e)}")

            progress_value += 1
            self.progress_bar.setValue(progress_value)

        # Show summary
        msg = f"Export Complete\n\n"
        msg += f"Successful: {len(results['success'])}\n"
        msg += f"Failed: {len(results['failed'])}\n\n"
        msg += f"Output folder:\n{output_folder}"

        if results['failed']:
            msg += f"\n\nErrors:\n"
            for err in results['failed'][:5]:
                msg += f"- {err}\n"
            if len(results['failed']) > 5:
                msg += f"... and {len(results['failed']) - 5} more"

        hou.ui.displayMessage(msg, severity=hou.severityType.Message)


def show_standalone_converter():
    """Show the standalone MaterialX converter dialog."""
    dialog = StandaloneMaterialXConverter()
    dialog.show()
    return dialog


def convert_textures_to_materialx(
    texture_folder: str,
    output_folder: str,
    create_mtlx: bool = True,
    create_usd: bool = True,
    kit_info: Optional[Dict] = None,
    **kwargs
) -> Dict:
    """
    Batch convert textures to MaterialX/USD files without UI.
    Uses tex_to_mtlx detection logic for consistency.

    Args:
        texture_folder: Path to texture folder
        output_folder: Output folder for materials
        create_mtlx: Create MaterialX files
        create_usd: Create USD files
        kit_info: KB3D metadata dict with kitDisplayName, kitId, kitVersion
        **kwargs: Additional options

    Returns:
        dict: Results summary
    """
    # Default kit info if not provided
    if kit_info is None:
        kit_info = {
            'kitDisplayName': 'Custom Materials',
            'kitId': 'custom_materials',
            'kitVersion': '1.0.0'
        }
    mtlx_exporter = MaterialXExporter()
    usd_exporter = USDExporter()

    # Detect materials using tex_to_mtlx logic
    try:
        texture_list = defaultdict(lambda: defaultdict(list))

        # Get all valid texture files
        valid_files = []
        for file in os.listdir(texture_folder):
            file_path = os.path.join(texture_folder, file)
            is_file = os.path.isfile(file_path)
            valid_extension = file.lower().endswith(tuple(TEXTURE_EXT))
            check_underscore = "_" in file
            if is_file and valid_extension and check_underscore:
                valid_files.append(file)

        # Process files
        for file in valid_files:
            split_text = os.path.splitext(file)[0]
            split_text = split_text.split("_")
            material_name = split_text[0]

            # Find the texture type
            texture_type = None
            for tx_type in TEXTURE_TYPE:
                for tx in split_text[1:]:
                    if tx.lower() == tx_type:
                        texture_type = tx_type
                        index = split_text.index(tx)
                        material_name = '_'.join(split_text[:index])
                        break

            if not texture_type:
                continue

            # Clean material name but PRESERVE CASING (don't lowercase)
            clean_name = material_name.replace(' ', '_').replace('-', '_')
            texture_list[clean_name][texture_type].append(file)
            texture_list[clean_name]['FOLDER_PATH'] = texture_folder

        # Convert to dict
        materials = dict(texture_list)

    except Exception as e:
        print(f"Error detecting materials: {e}")
        return {'success': [], 'failed': [f'Detection error: {e}']}

    # Export each material
    results = {'success': [], 'failed': []}

    for mat_name in materials:
        mat_folder = os.path.join(output_folder, mat_name)
        os.makedirs(mat_folder, exist_ok=True)

        try:
            mtlx_file = None

            if create_mtlx:
                mtlx_file = os.path.join(mat_folder, f"{mat_name}.mtlx")
                mtlx_result = mtlx_exporter.export_from_folder(
                    texture_folder=texture_folder,
                    output_file=mtlx_file,
                    material_name=mat_name,
                    **kwargs
                )

                if not mtlx_result['success']:
                    results['failed'].append(f"{mat_name}: {mtlx_result['error']}")
                    continue

            if create_usd and mtlx_file:
                usd_file = os.path.join(mat_folder, f"{mat_name}.usd")
                # Use KB3D style with user metadata
                from .usd_exporter import create_kb3d_style_usd
                usd_result = create_kb3d_style_usd(
                    material_name=mat_name,
                    mtlx_file=f"./{mat_name}.mtlx",
                    output_file=usd_file,
                    kit_info=kit_info  # Use provided metadata
                )

                if not usd_result['success']:
                    results['failed'].append(f"{mat_name}: {usd_result['error']}")
                    continue

            results['success'].append(mat_name)

        except Exception as e:
            results['failed'].append(f"{mat_name}: {str(e)}")

    return results


# For testing
if __name__ == '__main__':
    show_standalone_converter()
