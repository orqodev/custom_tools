import hou
import os
from PySide6 import QtWidgets, QtCore

class MergeHipDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge HIP into Current Scene")
        self.setMinimumWidth(520)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)  # keep instance alive

        # --- widgets ---
        self.path_edit = QtWidgets.QLineEdit()
        self.browse_btn = QtWidgets.QPushButton("Browse…")
        self.pattern_edit = QtWidgets.QLineEdit("*")
        self.overwrite_chk = QtWidgets.QCheckBox("Overwrite on conflict")
        self.ignore_warn_chk = QtWidgets.QCheckBox("Ignore load warnings")
        self.ignore_warn_chk.setChecked(True)
        self.merge_btn = QtWidgets.QPushButton("Merge")
        self.close_btn = QtWidgets.QPushButton("Close")

        # --- layout ---
        form = QtWidgets.QFormLayout()
        file_row = QtWidgets.QHBoxLayout()
        file_row.addWidget(self.path_edit)
        file_row.addWidget(self.browse_btn)
        form.addRow("File (.hip/.hiplc/.hipnc):", file_row)
        form.addRow("Node pattern:", self.pattern_edit)
        form.addRow("", self.overwrite_chk)
        form.addRow("", self.ignore_warn_chk)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.close_btn)
        btn_row.addWidget(self.merge_btn)

        outer = QtWidgets.QVBoxLayout(self)
        outer.addLayout(form)
        outer.addStretch(1)
        outer.addLayout(btn_row)

        # --- sensible default ---
        default_dir = "/home/tushita/houdini21.0/custom_tools/templates"
        if os.path.isdir(default_dir):
            self.path_edit.setText(default_dir)

        # --- signals (UniqueConnection avoids duplicates on reloads) ---
        self.browse_btn.clicked.connect(self._on_browse, QtCore.Qt.UniqueConnection)
        self.merge_btn.clicked.connect(self._on_merge, QtCore.Qt.UniqueConnection)
        self.close_btn.clicked.connect(self.close, QtCore.Qt.UniqueConnection)

    def _on_browse(self):
        start_dir = self.path_edit.text().strip() or hou.expandString("$HIP")
        dlg = QtWidgets.QFileDialog(self, "Select HIP file", start_dir,
                                    "Houdini Files (*.hip *.hiplc *.hipnc);;All Files (*)")
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dlg.exec():  # modal just for the file dialog
            files = dlg.selectedFiles()
            if files:
                self.path_edit.setText(files[0])

    def _on_merge(self):
        if getattr(self, "_merge_in_progress", False):
            return
        self._merge_in_progress = True

        try:
            path = hou.expandString(self.path_edit.text().strip())
            if (not path) or (not os.path.isfile(path)) or (
                    os.path.splitext(path)[1].lower() not in {".hip", ".hiplc", ".hipnc"}):
                hou.ui.setStatusMessage("Please select a valid .hip/.hiplc/.hipnc file.",
                                        severity=hou.severityType.Warning)
                return

            pattern = (self.pattern_edit.text().strip() or "*")
            overwrite = self.overwrite_chk.isChecked()

            # Honor user preference, default is checked to avoid Houdini modals.
            ignore_warnings = self.ignore_warn_chk.isChecked()

            warn_text = None
            # Use Houdini's operation context to avoid extra Qt modal/progress UI
            try:
                with hou.InterruptableOperation("Merging HIP file…", open_interrupt_dialog=False):
                    try:
                        hou.hipFile.merge(path, pattern, overwrite, ignore_warnings)
                    except hou.LoadWarning as w:
                        warn_text = str(w)
            except Exception:
                # re-raise to outer handler after ensuring no extra UI remains
                raise

            # Use a non-blocking status for success/warnings to avoid extra modals.
            if warn_text:
                hou.ui.setStatusMessage(f"Merge finished with warnings: {warn_text}",
                                        severity=hou.severityType.ImportantMessage)
            else:
                hou.ui.setStatusMessage(f"Merged: {path}", severity=hou.severityType.Message)

            # Close the tool window after a completed merge (success or warnings)
            self.close()

        except Exception as e:
            # On real error, show a single modal (progress already closed above)
            hou.ui.displayMessage(f"Merge failed:\n{e}")

        finally:
            self._merge_in_progress = False

def show_merge_dialog():
    # Reuse singleton instance to prevent double-open
    dlg = getattr(hou.session, "_merge_hip_dlg", None)
    if dlg is None or not isinstance(dlg, MergeHipDialog):
        try:
            parent = hou.qt.mainWindow()
        except Exception:
            parent = None
        dlg = MergeHipDialog(parent)
        hou.session._merge_hip_dlg = dlg

    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
