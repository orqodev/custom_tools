import os
import hou
import voptoolutils
import shiboken2
from typing import List, Type
from pxr import Usd, UsdGeom
from PySide2 import QtCore, QtGui, QtWidgets as QtW
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
from tools.lops_asset_builder_v2.lops_asset_builder_v2 import create_camera_lookdev, create_karma_nodes
from tools.lops_light_rig_pipeline import setup_light_rig_pipeline
from modules.misc_utils import _sanitize, slugify


class _PathRow(QtW.QWidget):
    """Editable geometry-file path row widget."""

    def __init__(self, parent=None):
        super(_PathRow, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QtW.QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)  # Add proper margins for better spacing
        layout.setSpacing(8)  # Add spacing between widgets

        # Path input field with better text handling
        self.path_edit = QtW.QLineEdit()
        self.path_edit.setPlaceholderText("File path...")
        self.path_edit.setText("")  # Ensure empty by default

        # Remove fixed maximum width to allow proper column alignment
        self.path_edit.setMinimumWidth(200)  # Set minimum width instead

        # Set font size for better readability and text handling
        font = self.path_edit.font()
        font.setPointSize(9)  # Slightly smaller font for better text display
        self.path_edit.setFont(font)

        # Enable text eliding for long paths
        self.path_edit.setToolTip("Full path will be shown in tooltip")

        # Browse button with consistent sizing
        self.browse_btn = QtW.QPushButton("Browse...")
        self.browse_btn.setMinimumWidth(80)
        self.browse_btn.setMaximumWidth(120)  # Allow some flexibility
        self.browse_btn.clicked.connect(self.browse_file)

        # Delete button with consistent sizing and red styling
        self.delete_btn = QtW.QPushButton("✖")  # Use symbol for more compact display
        self.delete_btn.setMinimumWidth(30)
        self.delete_btn.setMaximumWidth(40)
        self.delete_btn.setToolTip("Delete this row")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                color: #d32f2f;
                font-weight: bold;
                border: 1px solid #d32f2f;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
                color: #ffebee;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
                color: #ffffff;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_row)

        # Set button font size to match
        self.browse_btn.setFont(font)
        self.delete_btn.setFont(font)

        # Add widgets with better proportions for column alignment
        # Path edit gets most space (stretch factor 5), browse button gets fixed space (stretch 0), delete gets fixed space (stretch 0)
        layout.addWidget(self.path_edit, 5)  # Takes most available space
        layout.addWidget(self.browse_btn, 0)  # Fixed size
        layout.addWidget(self.delete_btn, 0)  # Fixed size

    def browse_file(self):
        """Open file browser for geometry files - supports multiple file selection."""
        # Find the main dialog window to ensure proper z-index
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        # Use Qt's native file dialog with multiple selection enabled
        file_paths, _ = QtW.QFileDialog.getOpenFileNames(
            main_dialog,
            "Select Geometry Files",
            "",
            "Geometry Files (*.bgeo *.bgeo.sc *.abc *.obj *.fbx);;All Files (*)"
        )

        if file_paths:
            # Set the first file in the current path row
            self.path_edit.setText(file_paths[0])

            # If multiple files were selected, create additional path rows for the remaining files
            if len(file_paths) > 1:
                # Find the parent _GroupWidget to add new path rows
                group_widget = self.parent()
                if isinstance(group_widget, _GroupWidget):
                    for additional_path in file_paths[1:]:
                        # Add a new path row and set its path
                        group_widget.add_path_row()
                        # Get the last added path row and set its path
                        new_path_row = group_widget.path_rows[-1]
                        new_path_row.set_path(additional_path)

    def delete_row(self):
        """Signal parent to delete this row."""
        # Find the _GroupWidget parent by traversing up the widget hierarchy
        group_widget = self.parent()
        while group_widget and not isinstance(group_widget, _GroupWidget):
            group_widget = group_widget.parent()

        if isinstance(group_widget, _GroupWidget):
            group_widget.remove_path_row(self)

    def get_path(self):
        """Get the file path."""
        return self.path_edit.text().strip()

    def set_path(self, path):
        """Set the file path with proper text eliding and tooltip."""
        self.path_edit.setText(path)

        # Set full path as tooltip for long paths
        if path:
            self.path_edit.setToolTip(f"Full path: {path}")

            # If path is too long, ensure it's displayed properly
            # The QLineEdit will automatically handle text scrolling when focused
            # but we can also set cursor position to show the filename
            if len(path) > 50:  # If path is long
                # Move cursor to end to show filename by default
                self.path_edit.setCursorPosition(len(path))
        else:
            self.path_edit.setToolTip("Full path will be shown in tooltip")


class _GroupWidget(QtW.QWidget):
    """Full Asset Group block with name, paths list, and materials."""

    def __init__(self, parent=None):
        super(_GroupWidget, self).__init__(parent)
        self.path_rows = []
        self.setup_ui()

    def setup_ui(self):
        layout = QtW.QVBoxLayout(self)

        # Group frame
        group_frame = QtW.QGroupBox("Assets Group")
        group_layout = QtW.QVBoxLayout(group_frame)

        # Group name
        name_layout = QtW.QHBoxLayout()
        name_layout.addWidget(QtW.QLabel("Group Name:"))
        self.name_edit = QtW.QLineEdit()
        self.name_edit.setPlaceholderText("group_N")
        name_layout.addWidget(self.name_edit)
        group_layout.addLayout(name_layout)

        # Asset paths section
        paths_label = QtW.QLabel("Asset Paths:")
        group_layout.addWidget(paths_label)

        # Scrollable area for paths
        scroll_area = QtW.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(250)  # Increased from 150 to give more space

        self.paths_widget = QtW.QWidget()
        self.paths_layout = QtW.QVBoxLayout(self.paths_widget)
        self.paths_layout.setContentsMargins(5, 5, 5, 5)  # Add margins for better spacing
        self.paths_layout.setSpacing(3)  # Add spacing between path rows

        # Add stretch at the end to push all path rows to the top
        # This ensures new rows are always added from top to bottom with space at bottom
        self.paths_layout.addStretch(1)

        scroll_area.setWidget(self.paths_widget)
        group_layout.addWidget(scroll_area)

        # Add Files button for bulk import
        add_files_btn = QtW.QPushButton("Add Files...")
        add_files_btn.clicked.connect(self.add_files_bulk)
        group_layout.addWidget(add_files_btn)

        # Materials folder section
        materials_layout = QtW.QHBoxLayout()
        materials_layout.addWidget(QtW.QLabel("Materials folder path:"))
        self.materials_folder_edit = QtW.QLineEdit()
        self.materials_folder_edit.setPlaceholderText("Select materials folder...")
        materials_layout.addWidget(self.materials_folder_edit)

        materials_browse_btn = QtW.QPushButton("Browse...")
        materials_browse_btn.clicked.connect(self.browse_materials_folder)
        materials_layout.addWidget(materials_browse_btn)

        group_layout.addLayout(materials_layout)

        # Remove group button
        remove_btn = QtW.QPushButton("Remove Group")
        remove_btn.clicked.connect(self.remove_group)
        group_layout.addWidget(remove_btn)

        layout.addWidget(group_frame)

        # No initial path row - user must use "Add Files..." button

    def add_path_row(self):
        """Add a new path row."""
        path_row = _PathRow(self)
        self.path_rows.append(path_row)

        # Insert the new path row before the stretch item (which is always the last item)
        # This ensures rows are added from top to bottom with space remaining at the bottom
        insert_index = self.paths_layout.count() - 1  # Insert before the stretch
        self.paths_layout.insertWidget(insert_index, path_row)

        # Connect validation for the new path row to the main dialog
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        if isinstance(main_dialog, _AssetGroupsDialog):
            path_row.path_edit.textChanged.connect(main_dialog.update_ok_button)

    def add_files_bulk(self):
        """Open file dialog to select multiple geometry files and create path rows for each."""
        # Find the main dialog window to ensure proper z-index
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        # Use Qt's native file dialog with multiple selection enabled
        file_paths, _ = QtW.QFileDialog.getOpenFileNames(
            main_dialog,
            "Select Geometry Files",
            "",
            "Geometry Files (*.bgeo *.bgeo.sc *.abc *.obj *.fbx);;All Files (*)"
        )

        if file_paths:
            # Check if we have an empty row to reuse
            empty_row = None
            for row in self.path_rows:
                if not row.get_path():
                    empty_row = row
                    break

            # If we have an empty row, use it for the first file
            if empty_row and file_paths:
                empty_row.set_path(file_paths[0])
                remaining_files = file_paths[1:]
            else:
                remaining_files = file_paths

            # Create new rows for remaining files
            for file_path in remaining_files:
                self.add_path_row()
                # Set the path for the newly created row
                new_row = self.path_rows[-1]
                new_row.set_path(file_path)

    def remove_path_row(self, path_row):
        """Remove a path row."""
        self.path_rows.remove(path_row)
        self.paths_layout.removeWidget(path_row)
        path_row.deleteLater()

        # Update OK button state in the main dialog
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        if isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog.update_ok_button()

    def browse_materials_folder(self):
        """Open folder browser for materials folder."""
        # Find the main dialog window to ensure proper z-index
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        # Use Qt's native folder dialog
        folder_path = QtW.QFileDialog.getExistingDirectory(
            main_dialog,
            "Select Materials Folder",
            ""
        )
        if folder_path:
            self.materials_folder_edit.setText(folder_path)

    def remove_group(self):
        """Signal parent to remove this group."""
        # Find the main dialog window
        main_dialog = self
        while main_dialog.parent() and not isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog = main_dialog.parent()

        if isinstance(main_dialog, _AssetGroupsDialog):
            main_dialog.remove_group_widget(self)

    def get_group_data(self):
        """Get the group data as a dictionary."""
        asset_paths = [row.get_path() for row in self.path_rows if row.get_path()]

        if not asset_paths:
            return None

        # Get base path from first asset
        base_path = os.path.dirname(asset_paths[0]) if asset_paths else ""

        # Get materials folder path
        texture_folder = self.materials_folder_edit.text().strip()

        return {
            "group_name": self.name_edit.text().strip() or "Unnamed_Group",
            "asset_paths": asset_paths,
            "base_path": base_path,
            "texture_folder": texture_folder,
            "material_names": []  # leave empty; workflow will fill later
        }

    def is_valid(self):
        """Check if group has at least one valid path."""
        return any(row.get_path() for row in self.path_rows)


class _AssetGroupsDialog(QtW.QDialog):
    """Scrollable dialog hosting any number of _GroupWidget with integrated progress tracking."""

    # Define custom signals for better communication
    processing_started = QtCore.Signal()
    processing_finished = QtCore.Signal()
    group_processed = QtCore.Signal(int, str)  # group_index, group_name
    log_message = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(_AssetGroupsDialog, self).__init__(parent)
        self.group_widgets = []
        self.result_data = []
        self.processing_mode = False
        self.ready_for_processing = False
        self.total_groups = 0
        self.current_group = 0
        self.log_buffer = io.StringIO()

        # Set proper window attributes for better management
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.setup_ui()
        self._connect_signals()

    def setup_ui(self):
        self.setWindowTitle("LOPS Asset Builder - Asset Groups")
        self.setMinimumSize(600, 400)
        self.resize(800, 600)

        layout = QtW.QVBoxLayout(self)

        # Asset Scope input at the top
        scope_layout = QtW.QHBoxLayout()
        scope_layout.addWidget(QtW.QLabel("Asset Builder:"))
        self.asset_scope_edit = QtW.QLineEdit()
        self.asset_scope_edit.setPlaceholderText("Enter asset scope name (e.g., ASSET, PROPS, CHARACTERS)...")
        self.asset_scope_edit.setText("ASSET")  # Default value
        scope_layout.addWidget(self.asset_scope_edit)
        layout.addLayout(scope_layout)

        # Instructions
        self.instructions = QtW.QLabel(
            "Define asset groups for the LOPS Asset Builder workflow.\n"
            "Each group must contain at least one geometry file path."
        )
        self.instructions.setWordWrap(True)
        layout.addWidget(self.instructions)

        # Scrollable area for groups
        self.scroll_area = QtW.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.groups_widget = QtW.QWidget()
        self.groups_layout = QtW.QVBoxLayout(self.groups_widget)

        self.scroll_area.setWidget(self.groups_widget)
        layout.addWidget(self.scroll_area)

        # Add group button
        self.add_group_btn = QtW.QPushButton("➕ Add Group")
        layout.addWidget(self.add_group_btn)

        # Progress section (initially hidden)
        self.progress_widget = QtW.QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QtW.QVBoxLayout(self.progress_widget)
        progress_layout.setSpacing(2)
        progress_layout.setContentsMargins(5, 10, 5, 10)

        # Progress title - reduced to 50% size
        self.progress_title = QtW.QLabel("Asset Builder Workflow")
        self.progress_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2e7d32; margin: 0px;")
        progress_layout.addWidget(self.progress_title)

        # Progress bar - reduced to 50% height
        self.progress_bar = QtW.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { height: 14px; margin: 0px; }")
        progress_layout.addWidget(self.progress_bar)

        # Current group label - reduced to 50% size
        self.current_group_label = QtW.QLabel("Initializing workflow...")
        self.current_group_label.setStyleSheet("font-size:14 px; margin: 0px;")
        progress_layout.addWidget(self.current_group_label)

        # Add a separator line before logs - made thinner
        separator = QtW.QFrame()
        separator.setFrameShape(QtW.QFrame.HLine)
        separator.setFrameShadow(QtW.QFrame.Sunken)
        separator.setStyleSheet("color: #cccccc; margin: 0px; max-height: 1px;")
        progress_layout.addWidget(separator)

        # Log display area - reduced title size to 50%
        log_label = QtW.QLabel("Workflow Logs")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 0px;")
        progress_layout.addWidget(log_label)

        self.log_display = QtW.QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QtGui.QFont("Consolas", 9))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)
        # Set both minimum and maximum height to ensure visibility - increased for more log content
        self.log_display.setMinimumHeight(200)
        self.log_display.setMaximumHeight(500)
        # Add some initial placeholder text to ensure the widget is visible
        self.log_display.setPlaceholderText("Processing logs will appear here...")
        progress_layout.addWidget(self.log_display)

        layout.addWidget(self.progress_widget)

        # Dialog buttons
        button_layout = QtW.QHBoxLayout()

        self.ok_btn = QtW.QPushButton("OK")
        self.ok_btn.setDefault(True)  # Make OK button default

        self.cancel_btn = QtW.QPushButton("Cancel")

        self.close_btn = QtW.QPushButton("Close")
        self.close_btn.setVisible(False)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # Add initial group
        self.add_group_widget()

        # Update OK button state
        self.update_ok_button()

    def _connect_signals(self):
        """Connect all signals and slots for better event handling."""
        # Button connections
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.close_btn.clicked.connect(self.close_dialog)

        # Add group button connection
        self.add_group_btn.clicked.connect(self.add_group_widget)

        # Custom signal connections
        self.log_message.connect(self._on_log_message)
        self.processing_started.connect(self._on_processing_started)
        self.processing_finished.connect(self._on_processing_finished)
        self.group_processed.connect(self._on_group_processed)

    def _on_log_message(self, message):
        """Handle log message signal."""
        self.add_log(message)

    def _on_processing_started(self):
        """Handle processing started signal."""
        self.ok_btn.setEnabled(False)
        self.add_group_btn.setEnabled(False)

    def _on_processing_finished(self):
        """Handle processing finished signal."""
        self.ok_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)

    def _on_group_processed(self, group_index, group_name):
        """Handle group processed signal."""
        self.update_progress(group_index, group_name, f"Completed processing: {group_name}")

    def add_group_widget(self):
        """Add a new group widget."""
        group_widget = _GroupWidget(self)

        # Set default group name with proper indexing
        group_index = len(self.group_widgets) + 1
        group_widget.name_edit.setText(f"group_{group_index}")

        self.group_widgets.append(group_widget)
        self.groups_layout.addWidget(group_widget)

        # Connect validation
        for path_row in group_widget.path_rows:
            path_row.path_edit.textChanged.connect(self.update_ok_button)
        group_widget.name_edit.textChanged.connect(self.update_ok_button)

    def remove_group_widget(self, group_widget):
        """Remove a group widget."""
        if len(self.group_widgets) > 1:  # Keep at least one group
            self.group_widgets.remove(group_widget)
            self.groups_layout.removeWidget(group_widget)
            group_widget.deleteLater()
            self.update_ok_button()

    def update_ok_button(self):
        """Update OK button state based on validation."""
        valid_groups = [group for group in self.group_widgets if group.is_valid()]
        self.ok_btn.setEnabled(len(valid_groups) > 0)

    def accept(self):
        """Collect data and prepare for processing mode."""
        self.result_data = {
            'asset_scope': self.asset_scope_edit.text().strip() or "ASSET",
            'groups': []
        }

        for group_widget in self.group_widgets:
            group_data = group_widget.get_group_data()
            if group_data:
                self.result_data['groups'].append(group_data)

        if not self.result_data['groups']:
            QtW.QMessageBox.warning(self, "Warning", "At least one group must contain valid file paths.")
            return

        # Don't close the dialog yet - we'll use it for progress tracking
        # Just mark that we're ready to proceed
        self.ready_for_processing = True

    def reject(self):
        """Handle cancel button - close the dialog."""
        super(_AssetGroupsDialog, self).reject()

    def close_dialog(self):
        """Close the dialog when workflow is complete."""
        self.close()

    def start_processing_mode(self, total_groups):
        """Switch dialog to processing mode."""
        self.processing_mode = True
        self.total_groups = total_groups
        self.current_group = 0

        # Hide input elements
        self.asset_scope_edit.setEnabled(False)
        self.scroll_area.setVisible(False)
        self.add_group_btn.setVisible(False)
        self.instructions.setText("Building assets for your project...")

        # Show progress elements
        self.progress_widget.setVisible(True)
        self.progress_bar.setMaximum(total_groups)
        self.progress_bar.setValue(0)

        # Update buttons
        self.ok_btn.setVisible(False)
        self.cancel_btn.setText("Cancel")

        # Resize dialog for progress view - increased height for larger log display
        self.resize(600, 900)

    def update_progress(self, group_index, group_name, message=""):
        """Update progress bar and current group information."""
        self.current_group = group_index
        self.progress_bar.setValue(group_index)

        if group_index < self.total_groups:
            # Make the progress text cleaner and less repetitive
            progress_text = f"Building group {group_index + 1} of {self.total_groups}: {group_name}"
            self.current_group_label.setText(progress_text)
            self.progress_bar.setFormat(f"{group_index + 1}/{self.total_groups} - {group_name}")
        else:
            self.current_group_label.setText("✓ Workflow completed successfully!")
            self.progress_bar.setFormat("Complete!")
            self.close_btn.setVisible(True)
            self.cancel_btn.setVisible(False)

        if message:
            self.add_log(message)

        # Process events to update UI
        QtW.QApplication.processEvents()

    def add_log(self, message):
        """Add a log message to the display."""
        # Check if user is at or near the bottom before adding new message
        scrollbar = self.log_display.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

        self.log_display.append(message)

        # Only auto-scroll to bottom if user was already at the bottom
        # This allows users to scroll up and read previous logs without being forced back down
        if was_at_bottom:
            scrollbar.setValue(scrollbar.maximum())

        QtW.QApplication.processEvents()

    def capture_houdini_output(self):
        """Context manager to capture Houdini output and display in logs."""
        return HoudiniOutputCapture(self)




class HoudiniOutputCapture:
    """Context manager to capture stdout/stderr and display in dialog."""

    def __init__(self, dialog):
        self.dialog = dialog
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.captured_output = io.StringIO()

    def __enter__(self):
        sys.stdout = self.captured_output
        sys.stderr = self.captured_output
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

        # Get captured output and display it
        output = self.captured_output.getvalue()
        if output.strip():
            self.dialog.add_log(output.strip())


class LopsAssetBuilderWorkflow:
    """
    LOPS Asset Builder Workflow - Step-by-step UI for multiple asset importing

    This class combines the functionality of lops_asset_builder_v2 with the
    step-by-step UI workflow pattern from batch_import_workflow.

    Features:
    - Interactive step-by-step asset group importing
    - Multiple asset groups with individual component builders
    - Material creation and assignment
    - Automatic network layout
    """

    def __init__(self):
        self.stage_context = None
        self.asset_groups = []  # List of asset group data
        self.merge_node = None  # Final merge node to connect all component outputs

        # UI Data storage as instance variables
        self.asset_scope = "ASSET"  # Default asset scope
        self.groups_data = []  # Raw groups data from UI
        self.ui_result = None  # Complete UI result data
        self.main_dialog = None  # Reference to the main dialog for logging

    def _log_message(self, message, severity=None):
        """
        Log a message to the unified dialog if available, otherwise print to console.

        Args:
            message (str): The message to log
            severity (hou.severityType): The severity type (Error, Warning, Message)
        """
        # Format message based on severity
        if severity == hou.severityType.Error:
            formatted_message = f"❌ ERROR: {message}"
        elif severity == hou.severityType.Warning:
            formatted_message = f"⚠️ WARNING: {message}"
        elif severity == hou.severityType.Message:
            formatted_message = f"ℹ️ INFO: {message}"
        else:
            formatted_message = message

        # Log to unified dialog if available
        if hasattr(self, 'main_dialog') and self.main_dialog and hasattr(self.main_dialog, 'add_log'):
            self.main_dialog.add_log(formatted_message)
        else:
            # Fallback to console output
            print(formatted_message)

    def _create_ui_form(self):
        """
        Create and show the asset groups UI form with integrated processing.
        Uses non-modal dialog that stays open during processing to show logs.

        Returns:
            dict or None: Complete UI result data if user submitted,
                         None if user cancelled.
        """
        self.main_dialog = _AssetGroupsDialog(hou.qt.mainWindow())

        # Show dialog non-modally
        self.main_dialog.show()

        # Wait for user to click OK or Cancel using the existing ready_for_processing flag
        self.main_dialog.ready_for_processing = False
        while not self.main_dialog.ready_for_processing and self.main_dialog.isVisible():
            QtW.QApplication.processEvents()
            import time
            time.sleep(0.01)  # Small delay to prevent busy waiting

        # Check if dialog was closed (user cancelled)
        if not self.main_dialog.isVisible():
            return None  # user cancelled

        # Store all UI data in instance variables
        self.ui_result = self.main_dialog.result_data
        self.asset_scope = self.ui_result['asset_scope']
        self.groups_data = self.ui_result['groups']

        # Extract material names for each group
        for group_data in self.groups_data:
            asset_paths = group_data['asset_paths']
            material_names = self._extract_material_names(asset_paths)
            group_data['material_names'] = material_names

        return self.ui_result

    def create_workflow(self):
        """
        Creates the LOPS Asset Builder workflow:
        1. Initialize stage context
        2. Collect asset groups via UI form
        3. Create component builder for each asset group
        4. Create merge node and connect all component outputs
        5. Create node scope wrapper
        6. Setup optional light rig pipeline
        7. Show final summary
        """
        # Step 1: Initialize stage context
        self._initialize_stage_context()

        # Step 2: Collect asset groups via UI form
        ui_result = self._create_ui_form()
        if not ui_result:
            return  # user hit Cancel

        # Step 2.5: Switch to processing mode and show progress
        if self.groups_data and hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.start_processing_mode(len(self.groups_data))
            self.main_dialog.add_log("Starting LOPS Asset Builder workflow...")
            self.main_dialog.add_log(f"Processing {len(self.groups_data)} asset groups...")

            # Process each group using stored instance data
            for i, g in enumerate(self.groups_data):
                # Check if dialog is still visible
                if not (hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible()):
                    break

                group_name = g['group_name']
                self.main_dialog.update_progress(i, group_name, f"Starting processing of group: {group_name}")

                # Capture Houdini output during group processing
                with self.main_dialog.capture_houdini_output():
                    self.main_dialog.add_log(f"Creating component builder for group: {group_name}")
                    self.main_dialog.add_log(f"  - Asset paths: {len(g['asset_paths'])} files")
                    self.main_dialog.add_log(f"  - Texture folder: {g['texture_folder'] or 'None'}")

                    nodes = self._create_component_builder_for_group(g)

                if nodes:
                    # Store group data
                    group_data = {
                        'name': g['group_name'],
                        'asset_paths': g['asset_paths'],
                        'texture_folder': g['texture_folder'],
                        'component_nodes': nodes,
                        'group_id': len(self.asset_groups) + 1
                    }
                    self.asset_groups.append(group_data)
                    if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
                        self.main_dialog.add_log(f"✓ Successfully created group: {group_name}")
                else:
                    if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
                        self.main_dialog.add_log(f"✗ Failed to create group: {group_name}")

            # Update progress to completion
            if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
                self.main_dialog.update_progress(len(self.groups_data), "", "All groups processed!")
                self.main_dialog.add_log("Group processing completed. Continuing with workflow...")

                # Keep dialog open for a moment to show completion
                QtW.QApplication.processEvents()
                import time
                time.sleep(2)

        # Step 3: Create merge node and connect all component outputs
        if self.asset_groups:
            if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
                self.main_dialog.add_log("Creating final merge node...")
                QtW.QApplication.processEvents()
            self._create_final_merge_node()
            if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
                self.main_dialog.add_log("✓ Final merge node created successfully")

        # Step 4: Layout all nodes
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("Laying out all nodes...")
            QtW.QApplication.processEvents()
        self._layout_all_nodes()
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("✓ Node layout completed")

        # Step 5: Create node scope wrapper
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("Creating node scope wrapper...")
            QtW.QApplication.processEvents()
        scope_name = self._create_node_scope()
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log(f"✓ Node scope '{scope_name}' created successfully")

        # Step 6: Setup optional light rig pipeline
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("Setting up light rig pipeline...")
            QtW.QApplication.processEvents()
        self._setup_light_rig_pipeline(scope_name)
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("✓ Light rig pipeline setup completed")

        # Step 7: Show final summary
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("Generating final summary...")
            QtW.QApplication.processEvents()
        self._show_final_summary()
        if hasattr(self, 'main_dialog') and self.main_dialog and self.main_dialog.isVisible():
            self.main_dialog.add_log("✓ LOPS Asset Builder workflow completed successfully!")
            self.main_dialog.add_log("You can now close this dialog.")

            # Keep dialog open for a moment to show completion, then close
            QtW.QApplication.processEvents()
            import time
            time.sleep(3)  # Give user time to see completion message
            # self.main_dialog.close_dialog()

        return self.stage_context

    def _extract_material_names(self, asset_paths):
        """
        Extract material names from geometry files by examining shop_materialpath
        and material:binding primitive attributes.

        Args:
            asset_paths (list): List of asset file paths to examine

        Returns:
            list: Sorted list of unique material names (basenames only)
        """
        material_names = set()

        for asset_path in asset_paths:
            asset_path = asset_path.strip()
            if not asset_path:
                continue

            try:
                # Load geometry in memory
                geo = hou.Geometry()
                geo.loadFromFile(asset_path)

                # Check for shop_materialpath primitive attribute
                shop_attrib = geo.findPrimAttrib("shop_materialpath")
                if shop_attrib:
                    for prim in geo.prims():
                        material_path = prim.stringAttribValue(shop_attrib)
                        if material_path:
                            # Extract basename from material path
                            material_name = slugify(os.path.basename(material_path))
                            if material_name:
                                material_names.add(material_name)

                # Check for material:binding primitive attribute
                binding_attrib = geo.findPrimAttrib("material:binding")
                if binding_attrib:
                    for prim in geo.prims():
                        material_path = prim.stringAttribValue(binding_attrib)
                        if material_path:
                            # Extract basename from material path
                            material_name = os.path.basename(material_path)
                            if material_name:
                                material_names.add(material_name)

            except Exception as e:
                # Skip unreadable files silently as per requirements
                continue
            print(f"Material names for {asset_path} are: {material_names}")

        return sorted(list(material_names))

    def _create_component_builder_for_group(self, asset_data):
        """
        Create a component builder for a single asset group.
        Based on the create_component_builder function from lops_asset_builder_v2.
        """
        try:
            group_name = asset_data['group_name']
            asset_paths = asset_data['asset_paths']
            texture_folder = asset_data['texture_folder']

            print(f"Processing group: {group_name}")
            print(f"Asset paths: {asset_paths}")
            print(f"Texture folder: {texture_folder}")

            # Create initial nodes
            print(f"Creating initial nodes for group: {group_name}")
            comp_geo, material_lib, comp_material, comp_out = self._create_initial_nodes(group_name)
            print(f"✓ Created nodes: {comp_geo.name()}, {material_lib.name()}, {comp_material.name()}, {comp_out.name()}")

            # Prepare imported assets
            print(f"Importing {len(asset_paths)} asset files...")
            self._prepare_imported_asset(comp_geo, asset_paths, asset_data['base_path'], comp_out, group_name)
            print(f"✓ Assets imported successfully")

            # Create materials if texture folder exists
            if texture_folder and os.path.exists(texture_folder):
                print(f"Creating materials from texture folder: {texture_folder}")
                material_count = len(asset_data.get("material_names", []))
                print(f"Expected materials: {material_count}")
                self._create_materials(
                    comp_geo,
                    texture_folder,
                    material_lib,
                    asset_data["material_names"]
                )
                print(f"✓ Materials created successfully")
            else:
                print("No texture folder found, creating default MaterialX templates")
                # Create default MaterialX templates
                self._create_mtlx_templates(comp_geo, material_lib)
                print(f"✓ Default MaterialX templates created")

            # Layout nodes
            print("Laying out nodes...")
            nodes_to_layout = [comp_geo, material_lib, comp_material, comp_out]
            self.stage_context.layoutChildren(nodes_to_layout)
            print(f"✓ Node layout completed")

            print(f"✓ Group '{group_name}' processing completed successfully")
            return {
                'comp_geo': comp_geo,
                'material_lib': material_lib,
                'comp_material': comp_material,
                'comp_out': comp_out,
                'nodes_to_layout': nodes_to_layout
            }

        except Exception as e:
            error_msg = f"Error creating component builder for group {asset_data['group_name']}: {str(e)}"
            print(f"✗ {error_msg}")
            self._log_message(error_msg, severity=hou.severityType.Error)
            return None

    def _create_initial_nodes(self, node_name):
        """Create initial nodes for the component builder setup."""
        # Create nodes for the component builder setup
        comp_geo = self.stage_context.createNode("componentgeometry", _sanitize(f"{node_name}_geo"))
        material_lib = self.stage_context.createNode("materiallibrary", _sanitize(f"{node_name}_mtl"))
        comp_material = self.stage_context.createNode("componentmaterial", _sanitize(f"{node_name}_assign"))
        comp_out = self.stage_context.createNode("componentoutput", _sanitize(node_name))

        comp_geo.parm("geovariantname").set(node_name)
        material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
        comp_material.parm("nummaterials").set(0)

        # Create auto assignment for materials
        comp_material_edit = comp_material.node("edit")
        output_node = comp_material_edit.node("output0")

        assign_material = comp_material_edit.createNode("assignmaterial", _sanitize(f"{node_name}_assign"))
        # SET PARMS
        assign_material.setParms({
            "primpattern1": "%type:Mesh",
            "matspecmethod1": 2,
            "matspecvexpr1": '"/ASSET/mtl/"+@primname;',
            "bindpurpose1": "full",
        })

        # Connect nodes
        comp_material.setInput(0, comp_geo)
        comp_material.setInput(1, material_lib)
        comp_out.setInput(0, comp_material)

        # Connect the input of assign material node to the first subnet indirect input
        assign_material.setInput(0, comp_material_edit.indirectInputs()[0])
        output_node.setInput(0, assign_material)

        return comp_geo, material_lib, comp_material, comp_out

    def _prepare_imported_asset(self, parent, asset_paths, base_path, out_node, node_name):
        """
        Prepare imported assets with switch node and transform controls.
        Assets are processed through a matchsize node for consistent positioning.
        Based on _prepare_imported_asset from lops_asset_builder_v2.
        Returns switch_node and transform_node for parameter linking.
        """
        try:
            # Set the parent node where the nodes are going to be created
            parent_sop = hou.node(parent.path() + "/sopnet/geo")
            # Get the output nodes - default, proxy and sim
            default_output = hou.node(f"{parent_sop.path()}/default")
            proxy_output = hou.node(f"{parent_sop.path()}/proxy")
            sim_output = hou.node(f"{parent_sop.path()}/simproxy")

            # Create the file nodes that import the assets
            file_nodes = []
            processed_paths = []
            switch_node = parent_sop.createNode("switch", _sanitize(f"switch_{node_name}"))

            for i, asset_path in enumerate(asset_paths):
                asset_path = asset_path.strip()
                if not asset_path:
                    continue

                # Get asset name and extension
                file_path, filename = os.path.split(asset_path)
                asset_name = filename.split(".")[0]
                extension = filename.split(".")[-1]
                if ".bgeo.sc" in filename:
                    asset_name = filename.split(".")[0]
                    extension = "bgeo.sc"

                # Store full path for parameters
                full_asset_path = asset_path
                processed_paths.append(full_asset_path)

                file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
                if extension in file_extension:
                    file_import = parent_sop.createNode("file", _sanitize(f"import_{asset_name}"))
                    parm_name = "file"
                elif extension == "abc":
                    file_import = parent_sop.createNode("alembic", _sanitize(f"import_{asset_name}"))
                    parm_name = "filename"
                else:
                    continue

                # Set parameters for main nodes
                file_import.parm(parm_name).set(asset_path)
                switch_node.setInput(i, file_import)
                file_nodes.append(file_import)

            # Create the main processing nodes
            match_size = parent_sop.createNode("matchsize", _sanitize(f"matchsize_{node_name}"))
            attrib_wrangler = parent_sop.createNode("attribwrangle", "convert_mat_to_name")
            attrib_delete = parent_sop.createNode("attribdelete", "keep_P_N_UV_NAME")
            remove_points = parent_sop.createNode("add", f"remove_points")

            # Create transform node for external control (after remove_points)
            transform_node = parent_sop.createNode("xform", _sanitize(f"transform_{node_name}"))

            match_size.setParms({
                "justify_x": 2,
                "justify_y": 1,
                "justify_z": 2,
            })

            attrib_wrangler.setParms({
                "class": 1,
                "snippet": 's@shop_materialpath = tolower(replace(s@shop_materialpath, " ", "_"));\nstring material_to_name[] = split(s@shop_materialpath,"/");\ns@name=material_to_name[-1];'

            })

            attrib_delete.setParms({
                "negate": True,
                "ptdel": "N P",
                "vtxdel": "uv",
                "primdel": "name"
            })

            remove_points.parm("remove").set(True)

            # Connect main nodes - transform node now comes after remove_points
            match_size.setInput(0, switch_node)
            attrib_wrangler.setInput(0, match_size)
            attrib_delete.setInput(0, attrib_wrangler)
            remove_points.setInput(0, attrib_delete)
            transform_node.setInput(0, remove_points)
            default_output.setInput(0, transform_node)

            # Prepare Proxy Setup
            poly_reduce = parent_sop.createNode("polyreduce::2.0", "reduce_to_5")
            attrib_colour = parent_sop.createNode("attribwrangle", "set_color")
            color_node = parent_sop.createNode("color", "unique_color")
            attrib_promote = parent_sop.createNode("attribpromote", "promote_Cd")
            attrib_delete_name = parent_sop.createNode("attribdelete", f"delete_asset_name")
            name_node = parent_sop.createNode("name", "name")
            # Set parms for proxy setup
            poly_reduce.parm("percentage").set(5)

            # Custom attribute node using the ParmTemplateGroup() for the attrib_color
            attrib_colour.parm("class").set(1)

            ptg = attrib_colour.parmTemplateGroup()

            new_string = hou.StringParmTemplate(
                name="asset_name",
                label="Asset name",
                num_components= 1,
            )

            ptg.insertAfter("class", new_string)

            attrib_colour.setParmTemplateGroup(ptg)

            # Need to grab the rootprim from the component output and paste relative reference
            relative_path = attrib_colour.relativePathTo(out_node)
            expression_parm = f'`chs("{relative_path}/rootprim")`'
            attrib_colour.setParms({
                "asset_name": expression_parm,
                "snippet": 's@asset_name = chs("asset_name");',
            })

            color_node.setParms({
                "class": 1,
                "colortype": 4,
                "rampattribute": "asset_name",
            })

            attrib_promote.setParms({
                "inname": "Cd",
                "inclass": 1,
                "outclass": 0
            })
            attrib_delete_name.parm("primdel").set("asset_name")

            name_node.parm("name1").set(expression_parm)
            # Connect proxy nodes
            poly_reduce.setInput(0, transform_node)
            attrib_colour.setInput(0, poly_reduce)
            color_node.setInput(0, attrib_colour)
            attrib_promote.setInput(0, color_node)
            attrib_delete_name.setInput(0, attrib_promote)
            proxy_output.setInput(0, attrib_delete_name)

            # Prepare the sim Setup
            python_sop = self._create_convex(parent_sop)
            # Connect sim nodes
            python_sop.setInput(0, transform_node)
            name_node.setInput(0, python_sop)
            sim_output.setInput(0, name_node)

            # Layout nodes
            parent_sop.layoutChildren()

            # Create UI parameters for multi-asset switch workflow
            # This adds controls to the componentgeometry node
            if len(processed_paths) > 1:
                # Only create multi-asset parameters if we have multiple assets
                self._create_group_parameters(parent, node_name, processed_paths, switch_node, transform_node)

            return switch_node, transform_node

        except Exception as e:
            self._log_message(f"Error preparing imported asset: {str(e)}",
                             severity=hou.severityType.Error)
            return None, None

    def _create_group_parameters(self, parent_node, node_name, asset_paths, switch_node, transform_node):
        """
        Create parameters for multi-asset switch workflow.
        Inspired by batch_import_workflow.py, this function adds UI controls
        for switching between assets and controlling transforms.

        Args:
            parent_node (hou.Node): The parent node to add parameters to
            node_name (str): Name of the asset group
            asset_paths (list): List of asset file paths
            switch_node (hou.Node): The switch node to control
            transform_node (hou.Node): The transform node to control
        """
        try:
            ptg = parent_node.parmTemplateGroup()

            # Add separator for multi-asset controls
            separator = hou.SeparatorParmTemplate(f"{node_name}_multi_sep", f"{node_name} Multi-Asset Controls")
            ptg.append(separator)

            # Add asset switch parameter
            num_assets = len(asset_paths) if asset_paths else 1
            switch_parm = hou.IntParmTemplate(
                f"{node_name}_asset_switch",
                f"Selected Asset Index",
                1,
                default_value=(0,),
                min=0,
                max=max(0, num_assets - 1),
                help=f"Switch between {num_assets} imported assets"
            )
            ptg.append(switch_parm)

            # Add transform controls folder
            transform_folder = hou.FolderParmTemplate(
                f"{node_name}_transform",
                f"Asset Transform",
                folder_type=hou.folderType.Tabs
            )

            # Translation vector parameter
            translate = hou.FloatParmTemplate(
                f"{node_name}_translate",
                "Translate",
                3,
                default_value=(0, 0, 0)
            )

            # Rotation vector parameter
            rotate = hou.FloatParmTemplate(
                f"{node_name}_rotate",
                "Rotate",
                3,
                default_value=(0, 0, 0)
            )

            # Scale vector parameter
            scale = hou.FloatParmTemplate(
                f"{node_name}_scale",
                "Scale",
                3,
                default_value=(1, 1, 1)
            )

            transform_folder.addParmTemplate(translate)
            transform_folder.addParmTemplate(rotate)
            transform_folder.addParmTemplate(scale)
            ptg.append(transform_folder)

            # Add asset information folder
            if asset_paths and len(asset_paths) > 1:
                info_folder = hou.FolderParmTemplate(
                    f"{node_name}_assets_info",
                    f"Asset Files",
                    folder_type=hou.folderType.Tabs
                )

                for i, asset_path in enumerate(asset_paths):
                    asset_info = hou.StringParmTemplate(
                        f"{node_name}_asset_file_{i}",
                        f"Asset {i+1}",
                        1,
                        default_value=(asset_path,),
                        string_type=hou.stringParmType.FileReference,
                        file_type=hou.fileType.Geometry,
                        help=f"Path to asset file {i+1}"
                    )
                    info_folder.addParmTemplate(asset_info)

                ptg.append(info_folder)

            # Apply parameters to parent node
            parent_node.setParmTemplateGroup(ptg)

            # Link nodes to parameters
            self._link_group_nodes_to_parameters(parent_node, node_name, switch_node, transform_node)

        except Exception as e:
            self._log_message(f"Error creating group parameters: {str(e)}",
                             severity=hou.severityType.Error)

    def _link_group_nodes_to_parameters(self, parent_node, node_name, switch_node, transform_node):
        """
        Link switch and transform nodes to the UI parameters.

        Args:
            parent_node (hou.Node): The parent node with parameters (componentgeometry node)
            node_name (str): Name of the asset group
            switch_node (hou.Node): The switch node to control (inside sopnet/geo)
            transform_node (hou.Node): The transform node to control (inside sopnet/geo)
        """
        try:
            # Link switch node to parameter
            # Switch node is at: /stage/componentgeometry/sopnet/geo/switch_node
            # Parameters are at: /stage/componentgeometry/
            # So we need to go up 3 levels: ../../../
            if switch_node:
                switch_node.parm("input").setExpression(f'ch("../../../{node_name}_asset_switch")')

            # Link transform node using vector parameters
            # Transform node is at: /stage/componentgeometry/sopnet/geo/transform_node
            # Parameters are at: /stage/componentgeometry/
            # So we need to go up 3 levels: ../../../
            if transform_node:
                transform_mappings = [
                    ("t", f"{node_name}_translate"),
                    ("r", f"{node_name}_rotate"),
                    ("s", f"{node_name}_scale")
                ]

                for xform_base, parent_param in transform_mappings:
                    # Link each component
                    xform_components = ["x", "y", "z"]
                    for i, component in enumerate(xform_components):
                        xform_param = f"{xform_base}{component}"
                        parent_param_name = f"{parent_param}{component}"
                        transform_node.parm(xform_param).setExpression(f'ch("../../../{parent_param_name}")')

        except Exception as e:
            self._log_message(f"Error linking nodes to parameters: {str(e)}",
                             severity=hou.severityType.Error)

    def _create_materials(self, parent, folder_textures, material_lib, expected_names):
        """
        Create materials using the tex_to_mtlx script.
        Only creates materials for names found in expected_names list.

        Args:
            parent: Parent node
            folder_textures: Path to texture folder
            material_lib: Material library node
            expected_names: List of material names to create (from geometry files)
        """
        try:
            if not os.path.exists(folder_textures):
                self._log_message(f"Texture folder does not exist: {folder_textures}",
                                 severity=hou.severityType.Warning)
                self._create_mtlx_templates(parent, material_lib)
                return False

            material_handler = tex_to_mtlx.TxToMtlx()
            stage = parent.stage()
            prims_name = self._find_prims_by_attribute(stage, UsdGeom.Mesh)
            materials_created_length = 0

            if material_handler.folder_with_textures(folder_textures):
                # Get the texture detail
                texture_list = material_handler.get_texture_details(folder_textures)
                print(texture_list)
                if texture_list and isinstance(texture_list, dict):
                    # Common data
                    common_data = {
                        'mtlTX': False,  # If you want to create TX files set to True
                        'path': material_lib.path(),
                        'node': material_lib,
                    }
                    for material_name in texture_list:
                        # Skip materials not in expected_names list
                        if material_name not in expected_names:
                            continue

                        # Fix to provide the correct path
                        path = texture_list[material_name]['FOLDER_PATH']
                        if not path.endswith("/"):
                            texture_list[material_name]['FOLDER_PATH'] = path + "/"

                        materials_created_length += 1
                        create_material = tex_to_mtlx.MtlxMaterial(
                            material_name,
                            **common_data,
                            folder_path=path,
                            texture_list=texture_list
                        )
                        create_material.create_materialx()
                    self._log_message(f"Created {materials_created_length} materials in {material_lib.path()}",
                                     severity=hou.severityType.Message)
                    return True
                else:
                    self._create_mtlx_templates(parent, material_lib)
                    self._log_message("No valid texture sets found..", severity=hou.severityType.Message)
                    return True
            else:
                self._create_mtlx_templates(parent, material_lib)
                self._log_message("No valid texture sets found in folder", severity=hou.severityType.Message)
                return True
        except Exception as e:
            self._log_message(f"Error creating materials: {str(e)}", severity=hou.severityType.Error)
            return False

    def _create_mtlx_templates(self, parent, material_lib):
        """Create MaterialX templates."""
        name = "mtlxstandard_surface"
        voptoolutils._setupMtlXBuilderSubnet(
            subnet_node=None,
            destination_node=material_lib,
            name=name,
            mask=voptoolutils.MTLX_TAB_MASK,
            folder_label="MaterialX Builder",
            render_context="mtlx"
        )
        material_lib.layoutChildren()

    def _find_prims_by_attribute(self, stage: Usd.Stage, prim_type: Type[Usd.Typed]) -> List[str]:
        """Find primitives by attribute type."""
        prims_name = set()
        for prim in stage.Traverse():
            if prim.IsA(prim_type) and "render" in str(prim.GetPath()):
                prims_name.add(prim.GetName())
        return list(prims_name)

    def _create_convex(self, parent):
        """
        Creates the Python sop node that is used to create a convex hull using Scipy
        Args:
            parent = the component geometry node where the file is imported
        Return:
            python_sop = python_sop node created
        """
        # Create the extra parms to use
        python_sop = parent.createNode("python", "convex_hull_setup")

        # Create the extra parms to use
        ptg = python_sop.parmTemplateGroup()

        # Normalize normals toggle
        normalize_toggle = hou.ToggleParmTemplate(
            name="normalize",
            label="Normalize",
            default_value=True
        )

        # Invert Normals Toggle
        flip_normals = hou.ToggleParmTemplate(
            name="flip_normals",
            label="Flip Normals",
            default_value=True
        )

        # Simplify Toggle
        simplify_toggle = hou.ToggleParmTemplate(
            name="simplify",
            label="Simplify",
            default_value=True
        )

        # Level of Detail Float
        level_detail = hou.FloatParmTemplate(
            name="level_detail",
            label="Level Detail",
            num_components=1,
            disable_when="{simplify == 0}",
            max=1
        )

        # Append to node
        ptg.append(normalize_toggle)
        ptg.append(flip_normals)
        ptg.append(simplify_toggle)
        ptg.append(level_detail)

        python_sop.setParmTemplateGroup(ptg)

        code = '''
from modules import convex_hull_utils

node = hou.pwd()
geo = node.geometry()

# Get user parms
normalize_parm = node.parm("normalize")
flip_normals_parm = node.parm("flip_normals")
simplify_parm = node.parm("simplify")
level_detail = node.parm("level_detail").eval()

# Get the points
points = [point.position() for point in geo.points()]

convex_hull_utils.create_convex_hull(geo, points, normalize_parm,flip_normals_parm, simplify_parm, level_detail)
'''
        # Prepare the Sim setup
        python_sop.parm("python").set(code)

        return python_sop

    def _create_final_merge_node(self):
        """Create a final merge node to connect all component outputs."""
        try:
            self.merge_node = self.stage_context.createNode("merge", "final_merge")

            for i, group_data in enumerate(self.asset_groups):
                comp_out = group_data['component_nodes']['comp_out']
                self.merge_node.setInput(i, comp_out)

            # Set display flag on merge node
            self.merge_node.setGenericFlag(hou.nodeFlag.Display, True)

        except Exception as e:
            self._log_message(f"Error creating final merge node: {str(e)}",
                             severity=hou.severityType.Error)

    def _layout_all_nodes(self):
        """
        Layout all nodes in the stage context with proper spacing and organization.
        This function ensures nodes are properly positioned for optimal workflow organization.
        """
        try:
            # First, layout nodes within each component builder group
            # This ensures proper spacing within each group
            for group_data in self.asset_groups:
                nodes_to_layout = group_data['component_nodes']['nodes_to_layout']
                if nodes_to_layout:
                    # Layout the specific nodes for this group
                    self.stage_context.layoutChildren(nodes_to_layout)

            # Then layout all main stage nodes for overall organization
            # This provides the final positioning for all nodes
            self.stage_context.layoutChildren()

        except Exception as e:
            self._log_message(f"Error laying out nodes: {str(e)}",
                             severity=hou.severityType.Error)

    def _initialize_stage_context(self):
        """Initialize the stage context for the workflow."""
        self.stage_context = hou.node("/stage")

    def _create_node_scope(self):
        """
        Create node scope wrapper using the asset scope name from the UI.
        Returns the scope name for use in other methods.
        """
        try:
            # Select the merge node if it exists
            if self.merge_node:
                self.merge_node.setSelected(True, clear_all_selected=True)

            # Use the asset scope name from the UI (no popup needed)
            scope_name = self.asset_scope or "ASSET"

            # Insert a Scope prim (not Xform)
            node_scope = self.stage_context.createNode("scope", f"{scope_name}_scope")
            node_scope.parm("primpath").set(f"/{scope_name}")
            node_scope.setInput(0, self.merge_node)          # merge → scope
            node_scope.setGenericFlag(hou.nodeFlag.Display, True)
            node_scope.setSelected(True, clear_all_selected=True)

            return scope_name

        except Exception as e:
            self._log_message(f"Error creating node scope: {str(e)}",
                             severity=hou.severityType.Error)
            return "ASSET"  # Return default name on error

    def _setup_light_rig_pipeline(self, scope_name):
        """
        Setup optional light rig pipeline with user prompt.
        Creates light rig, camera, and Karma render setup if user chooses to.
        Uses the external lops_light_rig_pipeline script.
        """
        # Call the external script function
        setup_light_rig_pipeline(
            stage_context=self.stage_context,
            scope_name=scope_name,
            auto_prompt=True
        )

    def _show_final_summary(self):
        """Show final summary of the workflow."""
        try:
            if not self.asset_groups:
                self._log_message("No asset groups were created.",
                                 severity=hou.severityType.Warning)
                return

            summary_text = f"LOPS Asset Builder Workflow Complete!\n\n"
            summary_text += f"Created {len(self.asset_groups)} asset groups:\n\n"

            for group_data in self.asset_groups:
                summary_text += f"• {group_data['name']}: {len(group_data['asset_paths'])} assets\n"

            if self.merge_node:
                summary_text += f"\nAll groups connected to final merge node: {self.merge_node.name()}"

            self._log_message(summary_text, severity=hou.severityType.Message)

        except Exception as e:
            self._log_message(f"Error showing summary: {str(e)}",
                             severity=hou.severityType.Error)

# Global window management
_global_workflow_window = None

def toggle_lops_asset_builder_workflow():
    """
    Toggles the LOPS Asset Builder Workflow window on/off.
    If a valid window is open, it closes it.
    If it's closed (or invalid), it opens a new one.
    """
    global _global_workflow_window

    # Check if window exists and is valid
    if _global_workflow_window and shiboken2.isValid(_global_workflow_window):
        _global_workflow_window.close()
        _global_workflow_window = None
        return

    # Create new workflow instance
    try:
        workflow = LopsAssetBuilderWorkflow()
        result = workflow.create_workflow()

        # Store reference to the main dialog if it exists
        if hasattr(workflow, 'main_dialog') and workflow.main_dialog:
            _global_workflow_window = workflow.main_dialog

        return result
    except Exception as e:
        print(f"❌ ERROR: Error in LOPS Asset Builder Workflow: {str(e)}")
        return None

def create_lops_asset_builder_workflow():
    """
    Main entry point for the LOPS Asset Builder Workflow.
    Creates and runs the step-by-step workflow for multiple asset importing.
    """
    return toggle_lops_asset_builder_workflow()

# For backwards compatibility and easy access
def main():
    """Alternative entry point."""
    return create_lops_asset_builder_workflow()


if __name__ == "__main__":
    # Testing hook - only test the UI form without triggering full build
    workflow = LopsAssetBuilderWorkflow()

    result = workflow._create_ui_form()
    if result:
        print("SUCCESS: UI Form completed!")
        print()
        print("Data stored in instance variables:")
        print(f"  Asset Builder: '{workflow.asset_scope}'")
        print(f"  Number of Groups: {len(workflow.groups_data)}")
        print()
        print("Detailed Groups Data:")
        for i, group in enumerate(workflow.groups_data, 1):
            print(f"  Group {i}: {group['group_name']}")
            print(f"    Paths: {len(group['asset_paths'])} files")
            for j, path in enumerate(group['asset_paths'], 1):
                print(f"      {j}. {path}")
            print(f"    Materials folder: {group['texture_folder']}")
            print(f"    Base path: {group['base_path']}")
            print(f"    Material names: {group['material_names']}")
            if group['material_names']:
                print(f"      ✓ SUCCESS: Found {len(group['material_names'])} material names!")
                for k, mat_name in enumerate(group['material_names'], 1):
                    print(f"        {k}. '{mat_name}'")
            else:
                print(f"      ℹ INFO: No material names found in geometry files")
            print()

        print("Instance Variable Access Test:")
        print(f"  workflow.asset_scope = '{workflow.asset_scope}'")
        print(f"  workflow.groups_data contains {len(workflow.groups_data)} groups")
        print(f"  workflow.ui_result = {workflow.ui_result}")
        print()
        print("✓ All data is accessible and modifiable through instance variables!")
    else:
        print("UI Form Test - User cancelled")
        print(f"Instance variables after cancellation:")
        print(f"  workflow.asset_scope = '{workflow.asset_scope}'")
        print(f"  workflow.groups_data = {workflow.groups_data}")
        print(f"  workflow.ui_result = {workflow.ui_result}")
