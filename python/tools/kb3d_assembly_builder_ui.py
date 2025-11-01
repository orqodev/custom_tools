# Simple UI for KB3D Assembly Builder
# Provides a PySide-based dialog (PySide6 preferred) to collect inputs and run tools.kb3d_assembly_builder.build_kb3d_assembly

import os
import sys

# Try to import PySide6 first; if unavailable, fall back to PySide2 for compatibility
try:
    from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
    PYSIDE_VARIANT = "PySide6"
except Exception:  # pragma: no cover
    try:
        from PySide2 import QtWidgets, QtCore, QtGui  # type: ignore
        PYSIDE_VARIANT = "PySide2"
    except Exception:
        QtWidgets = None
        QtCore = None
        QtGui = None
        PYSIDE_VARIANT = None


class OutputBuffer(object):
    """Helper to capture stdout/stderr and forward to a callback."""

    def __init__(self, write_cb):
        self._write_cb = write_cb

    def write(self, text):
        if text:
            self._write_cb(str(text))

    def flush(self):
        pass


class KB3DAssemblyBuilderDialog(QtWidgets.QDialog):  # type: ignore[misc]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KB3D Assembly Builder")
        self.setMinimumWidth(700)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Form fields
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        # parts_source_folder
        self.parts_edit = QtWidgets.QLineEdit()
        parts_browse = QtWidgets.QPushButton("Browse…")
        parts_browse.clicked.connect(lambda: self._browse_dir(self.parts_edit))
        form.addRow("Parts Source Folder:", self._with_browse(self.parts_edit, parts_browse))

        # merged_bgeo
        self.bgeo_edit = QtWidgets.QLineEdit()
        bgeo_browse = QtWidgets.QPushButton("Browse…")
        bgeo_browse.clicked.connect(lambda: self._browse_file(self.bgeo_edit, "BGEO Files (*.bgeo *.bgeo.sc);;All Files (*.*)"))
        form.addRow("Merged BGEO:", self._with_browse(self.bgeo_edit, bgeo_browse))

        # models_base
        self.models_edit = QtWidgets.QLineEdit()
        models_browse = QtWidgets.QPushButton("Browse…")
        models_browse.clicked.connect(lambda: self._browse_dir(self.models_edit))
        form.addRow("Models Base Folder:", self._with_browse(self.models_edit, models_browse))

        # assembly_name
        self.assembly_edit = QtWidgets.QLineEdit()
        form.addRow("Assembly Name:", self.assembly_edit)

        # materials_folder (optional)
        self.materials_edit = QtWidgets.QLineEdit()
        materials_browse = QtWidgets.QPushButton("Browse…")
        materials_browse.clicked.connect(lambda: self._browse_dir(self.materials_edit))
        form.addRow("Materials Folder (optional):", self._with_browse(self.materials_edit, materials_browse))

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        layout.addLayout(btns)
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.clicked.connect(self._on_run)
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btns.addStretch(1)
        btns.addWidget(self.run_btn)
        btns.addWidget(self.close_btn)

        # Output log
        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Log output will appear here…")
        layout.addWidget(self.output)

        # Info label if running outside Houdini
        self.env_label = QtWidgets.QLabel()
        layout.addWidget(self.env_label)
        self._update_env_label()

    def _with_browse(self, line_edit, browse_btn):
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(line_edit)
        h.addWidget(browse_btn)
        return w

    def _browse_dir(self, target_line: 'QtWidgets.QLineEdit'):
        start = target_line.text() or os.path.expanduser("~")
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", start)
        if d:
            target_line.setText(d)

    def _browse_file(self, target_line: 'QtWidgets.QLineEdit', filter_str: str = "All Files (*.*)"):
        start = target_line.text() or os.path.expanduser("~")
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", start, filter_str)
        if f:
            target_line.setText(f)

    def _append_output(self, text: str):
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QtGui.QTextCursor.End)
        QtWidgets.QApplication.processEvents()

    def _set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        for w in (self.parts_edit, self.bgeo_edit, self.models_edit, self.assembly_edit, self.materials_edit):
            w.setEnabled(not running)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor if running else QtCore.Qt.ArrowCursor)

    def _update_env_label(self):
        try:
            import hou  # noqa: F401
            self.env_label.setText("Environment: Houdini detected (hou available)")
        except Exception:
            self.env_label.setText("Environment: hou not detected. This tool is intended to run inside Houdini.")

    def _validate(self):
        errors = []
        parts = self.parts_edit.text().strip()
        if not parts or not os.path.isdir(parts):
            errors.append("Parts source folder is missing or invalid.")
        bgeo = self.bgeo_edit.text().strip()
        if not bgeo or not os.path.isfile(bgeo):
            errors.append("Merged BGEO file is missing or invalid.")
        models = self.models_edit.text().strip()
        if not models:
            errors.append("Models base folder is required.")
        asm = self.assembly_edit.text().strip()
        if not asm:
            errors.append("Assembly name is required.")
        # materials optional; if provided, ensure folder
        mats = self.materials_edit.text().strip()
        if mats and not os.path.isdir(mats):
            errors.append("Materials folder path is invalid.")
        return errors

    def _on_run(self):
        errs = self._validate()
        if errs:
            QtWidgets.QMessageBox.warning(self, "Validation Errors", "\n".join(errs))
            return

        # Prepare arguments
        kwargs = dict(
            parts_source_folder=self.parts_edit.text().strip(),
            merged_bgeo=self.bgeo_edit.text().strip(),
            models_base=self.models_edit.text().strip(),
            assembly_name=self.assembly_edit.text().strip(),
            materials_folder=(self.materials_edit.text().strip() or None),
        )

        # Run builder and capture stdout
        try:
            self._set_running(True)
            self.output.clear()
            self._append_output("Starting KB3D Assembly Builder...\n\n")

            # Lazy import to allow the dialog to open outside Houdini and show a message
            try:
                from tools.kb3d_assembly_builder import build_kb3d_assembly
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Import Error", f"Failed to import builder.\nThis tool must run inside Houdini.\n\nError: {e}")
                return

            # Redirect stdout/stderr
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = OutputBuffer(self._append_output)
            sys.stderr = OutputBuffer(self._append_output)
            try:
                result = build_kb3d_assembly(**kwargs)
            finally:
                sys.stdout, sys.stderr = old_out, old_err

            if result:
                self._append_output(f"\nSuccess! Assembly USD created at:\n  {result}\n")
                QtWidgets.QMessageBox.information(self, "KB3D Assembly Builder", f"Assembly created:\n{result}")
            else:
                self._append_output("\nBuilder returned no result. See log above for details.\n")
                QtWidgets.QMessageBox.warning(self, "KB3D Assembly Builder", "Builder did not produce a result. Check inputs and log.")
        except Exception as e:
            self._append_output(f"\nERROR: {e}\n")
            QtWidgets.QMessageBox.critical(self, "KB3D Assembly Builder", f"An error occurred:\n{e}")
        finally:
            self._set_running(False)


def show_kb3d_assembly_builder_ui(parent=None):
    """Convenience to show the dialog from Houdini shelf or Python shell."""
    # If running inside Houdini, try to parent to the main window
    if parent is None:
        try:
            import hou  # type: ignore
            parent = hou.qt.mainWindow()  # type: ignore[attr-defined]
        except Exception:
            parent = None

    if QtWidgets is None:
        raise RuntimeError("PySide is not available. This UI must run inside Houdini or an environment with PySide installed.")

    dlg = KB3DAssemblyBuilderDialog(parent)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg


if __name__ == "__main__":
    if QtWidgets is None:
        raise SystemExit("PySide is not available. Run this inside Houdini.")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    dlg = show_kb3d_assembly_builder_ui(None)
    if app is not None and not QtWidgets.QApplication.instance().startingUp():
        # PySide6 uses exec(), PySide2 uses exec_()
        if hasattr(app, "exec"):
            app.exec()
        else:
            app.exec_()
