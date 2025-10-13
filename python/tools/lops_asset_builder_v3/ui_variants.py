"""
PySide6 dialog for selecting asset/material variants for the LOPS asset builder.
Pure UI: no LOP logic inside. Returns a dict via .data().

Fields:
- Main Asset File Path (file picker, Geometry)
- Asset Name (auto-filled from Main Asset File Path; editable)
- Asset Variant Set name (default: assetVariant)
- Asset Variant Files list (multi select, Geometry)
- Main Texture Folder (folder picker)
- Material Variant Set name (default: lookVariant)
- Material Variant Folders list (multi select, folders)

Buttons: OK / Cancel, Add/Remove for both lists.

Python 3.11, PySide6.
"""
from __future__ import annotations

from typing import List, Dict
import os

from PySide6 import QtWidgets, QtCore


def _basename_variant(name: str) -> str:
    base = os.path.basename(name.rstrip("/\\"))
    # Replace spaces with underscores and limit length
    base = base.replace(" ", "_")[:64] if base else "item"
    return base


class _ListEditor(QtWidgets.QWidget):
    """Reusable list editor with Add/Remove buttons."""

    def __init__(self, parent: QtWidgets.QWidget | None, mode: str = "file") -> None:
        super().__init__(parent)
        self.mode = mode  # "file" or "dir"
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.listw = QtWidgets.QListWidget(self)
        self.listw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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
            self.listw.addItem(v)

    def _on_add(self) -> None:
        if self.mode == "file":
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                "Select geometry files",
                "",
                "Geometry (*.usd *.usda *.usdc *.abc *.obj *.bgeo *.bgeo.sc);;All Files (*)",
            )
            for f in files or []:
                if f:
                    self.listw.addItem(f)
        else:
            dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder")
            if dir_:
                self.listw.addItem(dir_)

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
        self.setWindowTitle("Asset & Material Variants")
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
        self.ed_asset_vset = QtWidgets.QLineEdit("assetVariant")
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
        form.addRow("Main Texture Folder", row_maps)
        btn_maps.clicked.connect(self._pick_folder)

        # Material Variant Set
        self.ed_look_vset = QtWidgets.QLineEdit("lookVariant")
        form.addRow("Material Variant Set", self.ed_look_vset)

        # Material Variant Folders list
        self.maps_list = _ListEditor(self, mode="dir")
        form.addRow("Material Variant Folders", self.maps_list)

        lay.addLayout(form)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        lay.addWidget(btn_box)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        # Small size policy
        self.resize(520, 520)

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

    def data(self) -> Dict[str, object]:
        return {
            "main_asset": self.ed_main_asset.text().strip(),
            "asset_name": self.ed_asset_name.text().strip(),
            "asset_variant_set": (self.ed_asset_vset.text().strip() or "assetVariant"),
            "asset_variants": [s for s in self.asset_list.items() if s],
            "material_variant_set": (self.ed_look_vset.text().strip() or "lookVariant"),
            "main_textures": self.ed_main_maps.text().strip(),
            "material_variants": [s for s in self.maps_list.items() if s],
        }
