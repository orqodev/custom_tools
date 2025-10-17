"""
PySide6 dialog for selecting asset/material variants for the LOPS asset builder.
Pure UI: no LOP logic inside. Returns a dict via .data().

Fields:
- Main Asset File Path (file picker, Geometry)
- Asset Name (auto-filled from Main Asset File Path; editable)
- Asset Variant Set name (default: geo_variant)
- Asset Variant Files list (multi select, Geometry)
- Main Textures Folder (folder picker)
- Material Variant Set name (default: mtl_variant)
- Material Variant Folders list (multi select, folders)

Buttons: OK / Cancel, Add/Remove for both lists.

Python 3.11, PySide6.
"""
from __future__ import annotations

from typing import List, Dict
import os

from PySide6 import QtWidgets, QtCore, QtGui


def _basename_variant(name: str) -> str:
    base = os.path.basename(name.rstrip("/\\"))
    # Replace spaces with underscores and limit length
    base = base.replace(" ", "_")[:64] if base else "item"
    return base


class _ListEditor(QtWidgets.QWidget):
    """Reusable list editor with Add/Remove buttons."""

    def __init__(self, parent: QtWidgets.QWidget | None, mode: str = "file", file_filter: str | None = None) -> None:
        super().__init__(parent)
        self.mode = mode  # "file" or "dir"
        self.file_filter = file_filter
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.listw = QtWidgets.QListWidget(self)
        self.listw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # Improve visibility of long paths and overall height
        self.listw.setMinimumHeight(160)
        self.listw.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        self.listw.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self.listw.setUniformItemSizes(True)
        self.listw.setWordWrap(False)
        self.listw.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listw.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        layout.addWidget(self.listw)

        btns = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("Add", self)
        self.btn_remove = QtWidgets.QPushButton("Remove", self)
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_remove)
        btns.addStretch(1)
        layout.addLayout(btns)

        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)

    def items(self) -> List[str]:
        return [self.listw.item(i).text() for i in range(self.listw.count())]

    def set_items(self, values: List[str]) -> None:
        self.listw.clear()
        for v in values:
            if not v:
                continue
            item = QtWidgets.QListWidgetItem(v)
            item.setToolTip(v)
            self.listw.addItem(item)

    def _on_add(self) -> None:
        if self.mode == "file":
            title = "Select files"
            flt = self.file_filter or "Geometry (*.usd *.usda *.usdc *.abc *.obj *.bgeo *.bgeo.sc);;All Files (*)"
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                title,
                "",
                flt,
            )
            for f in files or []:
                if f:
                    item = QtWidgets.QListWidgetItem(f)
                    item.setToolTip(f)
                    self.listw.addItem(item)
        else:
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder")
            if dir_:
                item = QtWidgets.QListWidgetItem(dir_)
                item.setToolTip(dir_)
                self.listw.addItem(item)

    def _on_remove(self) -> None:
        for it in self.listw.selectedItems():
            row = self.listw.row(it)
            self.listw.takeItem(row)


class AssetMaterialVariantsDialog(QtWidgets.QDialog):
    """Small dialog to collect asset/material variant authoring data.

    Accept returns True when OK is pressed and data is valid, False otherwise.
    Use data() to retrieve a dictionary with all fields.
    """

    def __init__(self, default_asset: str = "", default_maps: str = "", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("LOPS Asset Builder")
        self.setModal(True)
        self._build_ui(default_asset, default_maps)

    def _build_ui(self, default_asset: str, default_maps: str) -> None:
        lay = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        # Main Asset File Path
        self.ed_main_asset = QtWidgets.QLineEdit(default_asset or "")
        btn_asset = QtWidgets.QPushButton("…")
        btn_asset.setFixedWidth(28)
        row_asset = QtWidgets.QHBoxLayout()
        row_asset.addWidget(self.ed_main_asset)
        row_asset.addWidget(btn_asset)
        form.addRow("Main Asset File Path", row_asset)
        btn_asset.clicked.connect(self._pick_asset)

        # Asset Name (auto)
        self.ed_asset_name = QtWidgets.QLineEdit("")
        form.addRow("Asset Name", self.ed_asset_name)
        # Keep asset name in sync when main asset path changes (if user hasn't edited it)
        self._user_edited_asset_name = False
        self.ed_asset_name.textEdited.connect(self._on_asset_name_edited)
        self.ed_main_asset.textChanged.connect(self._on_main_asset_changed)
        # Initialize from default
        self._on_main_asset_changed(self.ed_main_asset.text())

        # Asset Variant Set name
        self.ed_asset_vset = QtWidgets.QLineEdit("geo_variant")
        form.addRow("Asset Variant Set", self.ed_asset_vset)

        # Asset Variant Files list
        self.asset_list = _ListEditor(self, mode="file")
        form.addRow("Asset Variant Files", self.asset_list)

        # Main Texture Folder (moved up to replace Material Name)
        self.ed_main_maps = QtWidgets.QLineEdit(default_maps or "")
        btn_maps = QtWidgets.QPushButton("…")
        btn_maps.setFixedWidth(28)
        row_maps = QtWidgets.QHBoxLayout()
        row_maps.addWidget(self.ed_main_maps)
        row_maps.addWidget(btn_maps)
        form.addRow("Main Textures Folder", row_maps)
        btn_maps.clicked.connect(self._pick_folder)

        # Material Variant Set
        self.ed_look_vset = QtWidgets.QLineEdit("mtl_variant")
        form.addRow("Material Variant Set", self.ed_look_vset)

        # Material Variant Folders list
        self.maps_list = _ListEditor(self, mode="dir")
        form.addRow("Material Variant Folders", self.maps_list)

        # Lookdev setup toggle
        self.cb_create_lookdev = QtWidgets.QCheckBox("Create Lookdev Setup")
        # Disabled by default per request
        self.cb_create_lookdev.setChecked(False)
        form.addRow("Lookdev Setup", self.cb_create_lookdev)

        # Setup Light Rig toggle
        self.cb_create_light_rig = QtWidgets.QCheckBox("Setup Light Rig")
        self.cb_create_light_rig.setChecked(True)
        form.addRow("Light Rig", self.cb_create_light_rig)

        # Environment Lights enable and HDRI paths (optional)
        self.cb_enable_env_lights = QtWidgets.QCheckBox("Enable Environment Lights")
        self.cb_enable_env_lights.setChecked(False)
        form.addRow("Environment Lights", self.cb_enable_env_lights)
        image_filter = "Images (*.exr *.hdr *.rat *.jpg *.jpeg *.png *.tif *.tiff);;All Files (*)"
        self.env_lights_list = _ListEditor(self, mode="file", file_filter=image_filter)
        form.addRow("Env Light HDRI Paths", self.env_lights_list)

        # React to lookdev toggle to enable/disable dependent controls (use boolean signal)
        self.cb_create_lookdev.toggled.connect(self._on_lookdev_toggled)
        self.cb_enable_env_lights.toggled.connect(self._update_env_lights_enabled)
        # Initialize state
        self._on_lookdev_toggled(self.cb_create_lookdev.isChecked())

        lay.addLayout(form)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        lay.addWidget(btn_box)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        # Small size policy
        self.resize(560, 640)

    def _pick_asset(self) -> None:
        val, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select main geometry file",
            "",
            "Geometry (*.usd *.usda *.usdc *.abc *.obj *.bgeo *.bgeo.sc);;All Files (*)",
        )
        if val:
            self.ed_main_asset.setText(val)

    def _pick_folder(self) -> None:
        val = QtWidgets.QFileDialog.getExistingDirectory(self, "Select texture folder")
        if val:
            self.ed_main_maps.setText(val)

    # Helpers for Asset Name auto-fill
    def _derive_asset_name(self, path: str) -> str:
        base = os.path.basename(path) if path else ""
        if not base:
            return ""
        # Strip .bgeo.sc specially, otherwise strip last extension
        if base.endswith(".bgeo.sc"):
            base = base[:-len(".bgeo.sc")]
        else:
            if "." in base:
                base = base.split(".")[0]
        return base

    def _on_asset_name_edited(self, _text: str) -> None:
        # Mark that user manually edited; stop auto-updating
        self._user_edited_asset_name = True

    def _on_main_asset_changed(self, text: str) -> None:
        if not self._user_edited_asset_name:
            derived = self._derive_asset_name(text)
            self.ed_asset_name.setText(derived)

    def _on_lookdev_toggled(self, enabled: bool) -> None:
        # Enable/disable dependent widgets when Lookdev is toggled
        self.cb_create_light_rig.setEnabled(bool(enabled))
        # The env lights list is enabled only if lookdev is on AND the env lights checkbox is checked
        self.cb_enable_env_lights.setEnabled(bool(enabled))
        self._update_env_lights_enabled()

    def _update_env_lights_enabled(self) -> None:
        # Called when either lookdev toggle or env checkbox changes
        enabled = bool(self.cb_create_lookdev.isChecked()) and bool(self.cb_enable_env_lights.isChecked())
        self.env_lights_list.setEnabled(enabled)

    def data(self) -> Dict[str, object]:
        return {
            "main_asset_file_path": self.ed_main_asset.text().strip(),
            "asset_name_input": self.ed_asset_name.text().strip(),
            "asset_variant_set": (self.ed_asset_vset.text().strip() or "geo_variant"),
            "asset_variants": [s for s in self.asset_list.items() if s],
            "material_variant_set": (self.ed_look_vset.text().strip() or "mtl_variant"),
            "main_textures": self.ed_main_maps.text().strip(),
            "material_variants": [s for s in self.maps_list.items() if s],
            "create_lookdev_setup": bool(self.cb_create_lookdev.isChecked()),
            "create_light_rig": bool(self.cb_create_light_rig.isChecked()),
            "enable_env_lights": bool(self.cb_enable_env_lights.isChecked()),
            "env_light_paths": [s for s in self.env_lights_list.items() if s],
        }


class SimpleProgressDialog(QtWidgets.QDialog):
    def __init__(self, title="LOPs Asset Builder v3", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)
        self.setMinimumWidth(600)
        layout = QtWidgets.QVBoxLayout(self)
        self.title_label = QtWidgets.QLabel(title)
        self.progress_bar = QtWidgets.QProgressBar()
        self.message_label = QtWidgets.QLabel("")
        self.log_edit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        # Configure log appearance and behavior
        # Wrap long lines to the widget width to avoid horizontal growth and x-scroll during processing
        self.log_edit.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        # Break even very long "words" (paths, code) so x-scrollbar never appears
        self.log_edit.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        # Keep horizontal scrollbar hidden to prevent accidental horizontal scrolling
        self.log_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.log_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.log_edit.setStyleSheet(
            "background-color: #111; color: #eee; font-family: Consolas, 'Courier New', monospace; font-size: 12px;"
        )
        # Buttons
        self.button_box = QtWidgets.QHBoxLayout()
        self.kill_btn = QtWidgets.QPushButton("Kill Process")
        self.kill_btn.setEnabled(True)  # Enabled during processing per requirement
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setEnabled(False)  # Close remains disabled
        self.button_box.addStretch(1)
        self.button_box.addWidget(self.kill_btn)
        self.button_box.addWidget(self.close_btn)
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.message_label)
        layout.addWidget(self.log_edit)
        layout.addLayout(self.button_box)
        self._max = 100
        self.progress_bar.setRange(0, self._max)
        # Internal flags
        self.cancelled = False
        self.finished = False
        # Wire buttons (kill remains connected but disabled)
        self.kill_btn.clicked.connect(self._on_kill)
        self.close_btn.clicked.connect(self._on_close)

    def _on_kill(self):
        self.cancelled = True
        self.log_edit.append("User requested to kill the process...")
        QtWidgets.QApplication.processEvents()

    def _on_close(self):
        self.hide()

    def set_total(self, total: int):
        self._max = max(1, int(total))
        self.progress_bar.setRange(0, self._max)

    def set_value(self, value: int):
        self.progress_bar.setValue(max(0, min(int(value), self._max)))
        QtWidgets.QApplication.processEvents()

    def set_message(self, msg: str):
        self.message_label.setText(msg)
        QtWidgets.QApplication.processEvents()

    def log(self, msg: str):
        self.log_edit.append(msg)
        # Auto-scroll to bottom to keep the latest log visible
        try:
            self.log_edit.moveCursor(QtGui.QTextCursor.End)
        except Exception:
            # Fallback: ensure cursor visible without hard dependency
            self.log_edit.ensureCursorVisible()
        QtWidgets.QApplication.processEvents()

    def mark_finished(self):
        self.finished = True
        # On completion: disable Kill button and keep Close disabled per requirement
        self.kill_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.message_label.setText("Finished.")
        QtWidgets.QApplication.processEvents()


class ProgressReporter:
    def __init__(self, title="LOPs Asset Builder v3"):
        self._use_qt = False
        self._step = 0
        self._total = 100
        self._dialog = None
        self._cancelled = False
        try:
            app = QtWidgets.QApplication.instance()
            if app is not None:
                self._dialog = SimpleProgressDialog(title)
                self._dialog.show()
                self._use_qt = True
        except Exception:
            self._use_qt = False

    def set_total(self, total: int):
        self._total = max(1, int(total))
        if self._use_qt:
            self._dialog.set_total(self._total)

    def step(self, message: str = None):
        self._step += 1
        if self.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")
        if self._use_qt:
            if message:
                self._dialog.set_message(message)
                self._dialog.log(message)
            self._dialog.set_value(self._step)
        else:
            if message:
                print(f"[Progress] {self._step}/{self._total}: {message}")

    def log(self, message: str):
        if self._use_qt:
            self._dialog.log(message)
        else:
            print(message)

    def request_cancel(self):
        self._cancelled = True

    def is_cancelled(self) -> bool:
        if self._use_qt and self._dialog is not None:
            # sync from dialog
            if getattr(self._dialog, 'cancelled', False):
                self._cancelled = True
        return self._cancelled

    def mark_finished(self, message: str | None = None):
        if message:
            self.log(message)
        if self._use_qt and self._dialog is not None:
            try:
                self._dialog.mark_finished()
            except Exception:
                pass

    def close(self):
        # Keep the dialog open to allow log review; user can close manually.
        if self._use_qt and self._dialog is not None:
            # Do not close here; just enable close if not already
            try:
                self._dialog.mark_finished()
            except Exception:
                pass

# Override accept to validate inputs before closing the dialog
def _validate_path_exists(path: str) -> bool:
    return bool(path and os.path.exists(path))


def _is_file(path: str) -> bool:
    return os.path.isfile(path) if path else False


def _is_dir(path: str) -> bool:
    return os.path.isdir(path) if path else False


# Patch the dialog class with an accept override adding validation
orig_accept = AssetMaterialVariantsDialog.accept

def _validated_accept(self: AssetMaterialVariantsDialog):
    data = self.data()
    main_asset = data.get("main_asset_file_path") or ""
    maps_folder = data.get("main_textures") or ""
    # Validate required entries
    if not _is_file(main_asset):
        QtWidgets.QMessageBox.critical(self, "Invalid input", "Main asset file is invalid or not selected.")
        return
    if not _is_dir(maps_folder):
        QtWidgets.QMessageBox.critical(self, "Invalid input", "Main texture folder is invalid or not selected.")
        return
    # If OK
    return orig_accept(self)

# Monkey-patch the method so callers don't need to change usage
AssetMaterialVariantsDialog.accept = _validated_accept
