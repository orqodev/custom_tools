"""
KB3D Proper Assembly Builder UI - Simple PySide6 dialog for building KB3D assemblies

Creates proper KB3D structure (payload → geo + mtl) with texture variants and instancing.

Usage:
    from tools.kb3d_proper_assembly_builder_ui import show_ui
    show_ui()
"""

import os
import hou
from PySide6 import QtCore, QtWidgets, QtGui


class KB3DAssemblyBuilderUI(QtWidgets.QDialog):
    """Simple UI for KB3D Proper Assembly Builder."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("KB3D Proper Assembly Builder")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        # Apply Houdini styling
        self.setStyleSheet(hou.qt.styleSheet())

        self._setup_ui()
        self._connect_signals()
        self._load_defaults()

    def _setup_ui(self):
        """Create UI layout."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QtWidgets.QLabel(
            "<h2>KB3D Proper Assembly Builder</h2>"
            "<p>Creates correct KB3D structure: payload → geo.usd + mtl.usd</p>"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Add separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        # Form layout for inputs
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # Source Parts Folder
        self.source_parts_edit = QtWidgets.QLineEdit()
        self.source_parts_edit.setPlaceholderText("Path to parts folder (e.g., /geo/AssetName/)...")
        source_layout = QtWidgets.QHBoxLayout()
        source_layout.addWidget(self.source_parts_edit)
        source_browse = QtWidgets.QPushButton("Browse")
        source_browse.clicked.connect(self._browse_source_parts)
        source_layout.addWidget(source_browse)
        form_layout.addRow("Parts Folder:", source_layout)

        # Add info label for source
        source_info = QtWidgets.QLabel(
            "💡 Folder containing part subfolders (each with geo.usd/bgeo)"
        )
        source_info.setStyleSheet("color: #888; font-size: 10px; padding-left: 150px;")
        form_layout.addRow("", source_info)

        # Asset Name
        self.asset_name_edit = QtWidgets.QLineEdit()
        self.asset_name_edit.setPlaceholderText("KB3D_MTM_AssetName_A")
        form_layout.addRow("Asset Name:", self.asset_name_edit)

        # Add auto-detect button
        auto_detect_layout = QtWidgets.QHBoxLayout()
        auto_detect_btn = QtWidgets.QPushButton("Auto-detect from filename")
        auto_detect_btn.clicked.connect(self._auto_detect_name)
        auto_detect_layout.addWidget(auto_detect_btn)
        auto_detect_layout.addStretch()
        form_layout.addRow("", auto_detect_layout)

        # Models Folder
        self.models_folder_edit = QtWidgets.QLineEdit()
        self.models_folder_edit.setPlaceholderText("Path to Models folder...")
        models_layout = QtWidgets.QHBoxLayout()
        models_layout.addWidget(self.models_folder_edit)
        models_browse = QtWidgets.QPushButton("Browse")
        models_browse.clicked.connect(self._browse_models_folder)
        models_layout.addWidget(models_browse)
        form_layout.addRow("Models Folder:", models_layout)

        # Materials Folder
        self.materials_folder_edit = QtWidgets.QLineEdit()
        self.materials_folder_edit.setPlaceholderText("Path to Materials folder...")
        materials_layout = QtWidgets.QHBoxLayout()
        materials_layout.addWidget(self.materials_folder_edit)
        materials_browse = QtWidgets.QPushButton("Browse")
        materials_browse.clicked.connect(self._browse_materials_folder)
        materials_layout.addWidget(materials_browse)
        form_layout.addRow("Materials Folder:", materials_layout)

        layout.addLayout(form_layout)

        # Options group
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout()
        options_layout.setSpacing(8)

        # Detect instanceable checkbox
        self.detect_instanceable_check = QtWidgets.QCheckBox(
            "Auto-detect instanceable parts (marks duplicates for efficient instancing)"
        )
        self.detect_instanceable_check.setChecked(True)
        options_layout.addWidget(self.detect_instanceable_check)

        # Texture variants
        variants_layout = QtWidgets.QHBoxLayout()
        variants_layout.addWidget(QtWidgets.QLabel("Texture Variants:"))

        self.variant_jpg1k = QtWidgets.QCheckBox("jpg1k")
        self.variant_jpg1k.setChecked(True)
        variants_layout.addWidget(self.variant_jpg1k)

        self.variant_jpg2k = QtWidgets.QCheckBox("jpg2k")
        self.variant_jpg2k.setChecked(True)
        variants_layout.addWidget(self.variant_jpg2k)

        self.variant_png4k = QtWidgets.QCheckBox("png4k")
        self.variant_png4k.setChecked(True)
        variants_layout.addWidget(self.variant_png4k)

        variants_layout.addStretch()
        options_layout.addLayout(variants_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Info section
        info_group = QtWidgets.QGroupBox("Structure Info")
        info_layout = QtWidgets.QVBoxLayout()

        info_text = QtWidgets.QLabel(
            "<b>Output Structure:</b><br>"
            "Models/AssetName/<br>"
            "├── <b>payload.usd</b> - Main assembly (refs mtl + geo)<br>"
            "├── <b>geo.usd</b> - Geometry with instanceables<br>"
            "├── <b>mtl.usd</b> - Material library refs + variants<br>"
            "└── <b>AssetName.usd</b> - Convenience wrapper<br><br>"
            "<b>Benefits:</b> 8x smaller files, texture switching, efficient instancing"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.validate_btn = QtWidgets.QPushButton("Validate Inputs")
        self.validate_btn.clicked.connect(self._validate_inputs)
        button_layout.addWidget(self.validate_btn)

        self.build_btn = QtWidgets.QPushButton("Build Assembly")
        self.build_btn.clicked.connect(self._build_assembly)
        self.build_btn.setStyleSheet(
            "QPushButton { background-color: #4a7c59; color: white; font-weight: bold; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #5a8c69; }"
        )
        button_layout.addWidget(self.build_btn)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect signals."""
        # Auto-fill models/materials folders when one is set
        self.models_folder_edit.textChanged.connect(self._on_models_folder_changed)
        self.materials_folder_edit.textChanged.connect(self._on_materials_folder_changed)

    def _load_defaults(self):
        """Load default values from environment or last used."""
        # Try to get from $JOB or common locations
        job = os.environ.get("JOB", "")
        if job:
            models_path = os.path.join(job, "Models")
            if os.path.exists(models_path):
                self.models_folder_edit.setText(models_path)

            materials_path = os.path.join(job, "Materials")
            if os.path.exists(materials_path):
                self.materials_folder_edit.setText(materials_path)

    def _browse_source_parts(self):
        """Browse for source parts folder."""
        current = self.source_parts_edit.text() or os.environ.get("HIP", "")

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Parts Folder",
            current
        )

        if path:
            self.source_parts_edit.setText(path)
            # Auto-detect asset name from folder
            self._auto_detect_name()

    def _browse_models_folder(self):
        """Browse for Models folder."""
        current = self.models_folder_edit.text() or os.environ.get("JOB", "")

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Models Folder",
            current
        )

        if path:
            self.models_folder_edit.setText(path)

    def _browse_materials_folder(self):
        """Browse for Materials folder."""
        current = self.materials_folder_edit.text() or os.environ.get("JOB", "")

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Materials Folder",
            current
        )

        if path:
            self.materials_folder_edit.setText(path)

    def _auto_detect_name(self):
        """Auto-detect asset name from parts folder name."""
        source = self.source_parts_edit.text()
        if not source:
            return

        # Extract folder name
        name = os.path.basename(source.rstrip('/'))

        self.asset_name_edit.setText(name)

    def _on_models_folder_changed(self, text):
        """Auto-fill materials folder based on models folder."""
        if not text or self.materials_folder_edit.text():
            return

        # Try to find Materials folder as sibling
        parent = os.path.dirname(text)
        materials = os.path.join(parent, "Materials")
        if os.path.exists(materials):
            self.materials_folder_edit.setText(materials)

    def _on_materials_folder_changed(self, text):
        """Auto-fill models folder based on materials folder."""
        if not text or self.models_folder_edit.text():
            return

        # Try to find Models folder as sibling
        parent = os.path.dirname(text)
        models = os.path.join(parent, "Models")
        if os.path.exists(models):
            self.models_folder_edit.setText(models)

    def _validate_inputs(self):
        """Validate all inputs and show results."""
        errors = []
        warnings = []

        # Check source parts folder
        source = self.source_parts_edit.text()
        if not source:
            errors.append("Parts folder is required")
        elif not os.path.exists(source):
            errors.append(f"Parts folder not found: {source}")
        elif not os.path.isdir(source):
            errors.append(f"Parts path is not a folder: {source}")
        else:
            # Count parts
            part_count = len([d for d in os.listdir(source)
                            if os.path.isdir(os.path.join(source, d))])
            if part_count == 0:
                errors.append("Parts folder is empty (no subfolders found)")
            else:
                warnings.append(f"Found {part_count} parts in folder")

        # Check asset name
        asset_name = self.asset_name_edit.text()
        if not asset_name:
            errors.append("Asset name is required")
        elif not asset_name.replace('_', '').replace('-', '').isalnum():
            warnings.append("Asset name contains special characters (will be sanitized)")

        # Check models folder
        models = self.models_folder_edit.text()
        if not models:
            errors.append("Models folder is required")
        elif not os.path.exists(models):
            warnings.append(f"Models folder doesn't exist (will be created): {models}")

        # Check materials folder
        materials = self.materials_folder_edit.text()
        if not materials:
            errors.append("Materials folder is required")
        elif not os.path.exists(materials):
            errors.append(f"Materials folder not found: {materials}")
        else:
            # Count materials
            mat_count = len([d for d in os.listdir(materials)
                           if os.path.isdir(os.path.join(materials, d))])
            if mat_count == 0:
                warnings.append("Materials folder is empty!")
            else:
                warnings.append(f"Found {mat_count} materials in library")

        # Check texture variants
        variants = self._get_texture_variants()
        if not variants:
            warnings.append("No texture variants selected")

        # Show results
        if errors:
            QtWidgets.QMessageBox.critical(
                self,
                "Validation Failed",
                "<b>Errors found:</b><br>" + "<br>".join(f"• {e}" for e in errors)
            )
            self.status_label.setText("❌ Validation failed")
            self.status_label.setStyleSheet("color: #c44; font-style: italic;")
            return False
        elif warnings:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Validation Warnings")
            msg.setText("<b>Warnings found:</b>")
            msg.setInformativeText("<br>".join(f"• {w}" for w in warnings))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)

            if msg.exec() == QtWidgets.QMessageBox.Cancel:
                return False

            self.status_label.setText("⚠️ Validation passed with warnings")
            self.status_label.setStyleSheet("color: #c94; font-style: italic;")
            return True
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Validation Passed",
                "✅ All inputs are valid!\n\nReady to build assembly."
            )
            self.status_label.setText("✅ Validation passed")
            self.status_label.setStyleSheet("color: #4a7c59; font-style: italic;")
            return True

    def _get_texture_variants(self):
        """Get selected texture variants."""
        variants = []
        if self.variant_jpg1k.isChecked():
            variants.append("jpg1k")
        if self.variant_jpg2k.isChecked():
            variants.append("jpg2k")
        if self.variant_png4k.isChecked():
            variants.append("png4k")
        return variants

    def _build_assembly(self):
        """Build the KB3D assembly."""
        # Validate first
        if not self._validate_inputs():
            return

        # Get inputs
        parts_folder = self.source_parts_edit.text()
        asset_name = self.asset_name_edit.text()
        models_folder = self.models_folder_edit.text()
        materials_folder = self.materials_folder_edit.text()
        texture_variants = self._get_texture_variants()

        # Disable UI during build
        self.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Building assembly...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")

        try:
            # Import and run builder (from parts)
            from tools.kb3d_from_parts_builder import build_from_parts

            payload_path = build_from_parts(
                parts_folder=parts_folder,
                asset_name=asset_name,
                models_folder=models_folder,
                materials_folder=materials_folder,
                texture_variants=texture_variants
            )

            # Success
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"✅ Assembly created successfully!")
            self.status_label.setStyleSheet("color: #4a7c59; font-style: italic; font-weight: bold;")

            # Show success dialog with path
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Success!")
            msg.setText("<b>KB3D Assembly Created Successfully!</b>")
            msg.setInformativeText(
                f"<b>Payload:</b> {payload_path}<br><br>"
                f"<b>Structure:</b><br>"
                f"• payload.usd - Main assembly<br>"
                f"• geo.usd - Geometry with instances<br>"
                f"• mtl.usd - Materials with variants<br>"
                f"• {asset_name}.usd - Convenience wrapper"
            )
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

        except Exception as e:
            # Error
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Build failed: {str(e)}")
            self.status_label.setStyleSheet("color: #c44; font-style: italic;")

            QtWidgets.QMessageBox.critical(
                self,
                "Build Failed",
                f"<b>Failed to build assembly:</b><br><br>{str(e)}"
            )

            import traceback
            traceback.print_exc()

        finally:
            # Re-enable UI
            self.setEnabled(True)


def show_ui():
    """Show the KB3D Assembly Builder UI."""
    # Get parent widget (Houdini main window)
    parent = hou.qt.mainWindow()

    # Close existing dialog if open
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(widget, KB3DAssemblyBuilderUI):
            widget.close()

    # Create and show dialog
    dialog = KB3DAssemblyBuilderUI(parent)
    dialog.show()

    return dialog


if __name__ == "__main__":
    show_ui()
