"""Reusable UI components for LOPS Asset Builder Workflow."""

import os
from typing import List, Optional
from PySide2 import QtCore, QtGui, QtWidgets as QtW

# Handle both relative and absolute imports for flexibility
try:
    # Try relative imports first (when imported as part of package)
    from ..config.constants import (
        WIDGET_MARGINS, WIDGET_SPACING, PATH_LAYOUT_SPACING,
        MINIMUM_PATH_EDIT_WIDTH, BROWSE_BUTTON_WIDTH, DELETE_BUTTON_WIDTH,
        DELETE_BUTTON_STYLE, DEFAULT_PLACEHOLDER_TEXT, MAX_SCROLL_AREA_HEIGHT
    )
    from ..utils.file_operations import FileDialogHelper
    from ..models.data_model import AssetGroup, AssetPath
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config.constants import (
        WIDGET_MARGINS, WIDGET_SPACING, PATH_LAYOUT_SPACING,
        MINIMUM_PATH_EDIT_WIDTH, BROWSE_BUTTON_WIDTH, DELETE_BUTTON_WIDTH,
        DELETE_BUTTON_STYLE, DEFAULT_PLACEHOLDER_TEXT, MAX_SCROLL_AREA_HEIGHT
    )
    from utils.file_operations import FileDialogHelper
    from models.data_model import AssetGroup, AssetPath


class PathRow(QtW.QWidget):
    """Editable geometry-file path row widget."""

    # Signals
    path_changed = QtCore.Signal(str)  # Emitted when path changes
    delete_requested = QtCore.Signal()  # Emitted when delete is requested

    def __init__(self, parent=None):
        super(PathRow, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QtW.QHBoxLayout(self)
        layout.setContentsMargins(*WIDGET_MARGINS)
        layout.setSpacing(WIDGET_SPACING)

        # Path input field with better text handling
        self.path_edit = QtW.QLineEdit()
        self.path_edit.setPlaceholderText(DEFAULT_PLACEHOLDER_TEXT["file_path"])
        self.path_edit.setText("")  # Ensure empty by default
        self.path_edit.setMinimumWidth(MINIMUM_PATH_EDIT_WIDTH)

        # Set font size for better readability
        font = self.path_edit.font()
        font.setPointSize(9)
        self.path_edit.setFont(font)

        # Enable text eliding for long paths
        self.path_edit.setToolTip("Full path will be shown in tooltip")

        # Connect signal
        self.path_edit.textChanged.connect(self._on_path_changed)

        # Browse button
        self.browse_btn = QtW.QPushButton("Browse...")
        self.browse_btn.setMinimumWidth(BROWSE_BUTTON_WIDTH[0])
        self.browse_btn.setMaximumWidth(BROWSE_BUTTON_WIDTH[1])
        self.browse_btn.clicked.connect(self.browse_file)

        # Delete button
        self.delete_btn = QtW.QPushButton("✖")
        self.delete_btn.setMinimumWidth(DELETE_BUTTON_WIDTH[0])
        self.delete_btn.setMaximumWidth(DELETE_BUTTON_WIDTH[1])
        self.delete_btn.setToolTip("Delete this row")
        self.delete_btn.setStyleSheet(DELETE_BUTTON_STYLE)
        self.delete_btn.clicked.connect(self.delete_row)

        # Add widgets to layout
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.delete_btn)

    def browse_file(self):
        """Open file browser to select a geometry file."""
        file_path = FileDialogHelper.get_single_geometry_file(
            parent=self,
            title="Select Geometry File"
        )

        if file_path:
            self.set_path(file_path)

    def delete_row(self):
        """Request deletion of this row."""
        self.delete_requested.emit()

    def get_path(self) -> str:
        """Get the current file path."""
        return self.path_edit.text().strip()

    def set_path(self, path: str):
        """Set the file path with proper text eliding and tooltip."""
        self.path_edit.setText(path)

        # Set full path as tooltip for long paths
        if path:
            self.path_edit.setToolTip(f"Full path: {path}")

            # If path is long, move cursor to end to show filename
            if len(path) > 50:
                self.path_edit.setCursorPosition(len(path))
        else:
            self.path_edit.setToolTip("Full path will be shown in tooltip")

    def _on_path_changed(self, text: str):
        """Handle path text changes."""
        self.path_changed.emit(text)


class GroupWidget(QtW.QWidget):
    """Full Asset Group block with name, paths list, and materials."""

    # Signals
    group_changed = QtCore.Signal()  # Emitted when group data changes
    remove_requested = QtCore.Signal()  # Emitted when group removal is requested
    validation_needed = QtCore.Signal()  # Emitted when validation is needed

    def __init__(self, parent=None):
        super(GroupWidget, self).__init__(parent)
        self.path_rows: List[PathRow] = []
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QtW.QVBoxLayout(self)

        # Group frame
        group_frame = QtW.QGroupBox("Assets Group")
        group_layout = QtW.QVBoxLayout(group_frame)

        # Group name
        name_layout = QtW.QHBoxLayout()
        name_layout.addWidget(QtW.QLabel("Group Name:"))
        self.name_edit = QtW.QLineEdit()
        self.name_edit.setPlaceholderText(DEFAULT_PLACEHOLDER_TEXT["group_name"])
        self.name_edit.textChanged.connect(self._on_group_changed)
        name_layout.addWidget(self.name_edit)
        group_layout.addLayout(name_layout)

        # Asset paths section
        paths_label = QtW.QLabel("Asset Paths:")
        group_layout.addWidget(paths_label)

        # Scrollable area for paths
        scroll_area = QtW.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(MAX_SCROLL_AREA_HEIGHT)

        self.paths_widget = QtW.QWidget()
        self.paths_layout = QtW.QVBoxLayout(self.paths_widget)
        self.paths_layout.setContentsMargins(10, 5, 10, 5)
        self.paths_layout.setSpacing(PATH_LAYOUT_SPACING)

        # Add stretch at the end to push all path rows to the top
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
        self.materials_folder_edit.setPlaceholderText(DEFAULT_PLACEHOLDER_TEXT["materials_folder"])
        self.materials_folder_edit.textChanged.connect(self._on_group_changed)
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

    def add_path_row(self) -> PathRow:
        """Add a new path row."""
        path_row = PathRow(self)
        self.path_rows.append(path_row)

        # Connect signals
        path_row.path_changed.connect(self._on_group_changed)
        path_row.delete_requested.connect(lambda: self.remove_path_row(path_row))

        # Insert the new path row before the stretch item
        insert_index = self.paths_layout.count() - 1
        self.paths_layout.insertWidget(insert_index, path_row)

        # Emit validation needed signal
        self.validation_needed.emit()

        return path_row

    def add_files_bulk(self):
        """Open file dialog to select multiple geometry files and create path rows for each."""
        file_paths = FileDialogHelper.get_geometry_files(
            parent=self,
            title="Select Geometry Files"
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
                path_row = self.add_path_row()
                path_row.set_path(file_path)

            self._on_group_changed()

    def remove_path_row(self, path_row: PathRow):
        """Remove a path row."""
        if path_row in self.path_rows:
            self.path_rows.remove(path_row)
            self.paths_layout.removeWidget(path_row)
            path_row.deleteLater()

            self._on_group_changed()
            self.validation_needed.emit()

    def browse_materials_folder(self):
        """Open folder browser for materials folder."""
        folder_path = FileDialogHelper.get_folder(
            parent=self,
            title="Select Materials Folder"
        )

        if folder_path:
            self.materials_folder_edit.setText(folder_path)

    def remove_group(self):
        """Signal parent to remove this group."""
        self.remove_requested.emit()

    def get_group_data(self) -> Optional[dict]:
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

    def set_group_data(self, group_data: dict):
        """Set the group data from a dictionary."""
        # Set group name
        if 'group_name' in group_data:
            self.name_edit.setText(str(group_data['group_name']))

        # Set texture folder
        if 'texture_folder' in group_data:
            self.materials_folder_edit.setText(str(group_data['texture_folder']))

        # Clear existing paths
        for path_row in list(self.path_rows):
            self.remove_path_row(path_row)

        # Set asset paths
        if 'asset_paths' in group_data:
            paths = group_data['asset_paths']
            if isinstance(paths, list):
                for path in paths:
                    if isinstance(path, str) and path.strip():
                        path_row = self.add_path_row()
                        path_row.set_path(str(path))

    def get_asset_group(self) -> Optional[AssetGroup]:
        """Get the group data as an AssetGroup object."""
        group_data = self.get_group_data()
        if group_data:
            return AssetGroup.from_dict(group_data)
        return None

    def set_asset_group(self, asset_group: AssetGroup):
        """Set the group data from an AssetGroup object."""
        self.set_group_data(asset_group.to_dict())

    def is_valid(self) -> bool:
        """Check if group has at least one valid path."""
        return any(row.get_path() for row in self.path_rows)

    def _on_group_changed(self):
        """Handle group data changes."""
        self.group_changed.emit()


class HoudiniOutputCapture:
    """Context manager to capture stdout/stderr and display in dialog."""

    def __init__(self, dialog):
        """Initialize the output capture.

        Args:
            dialog: Dialog with add_log method to display captured output.
        """
        self.dialog = dialog
        self.old_stdout = None
        self.old_stderr = None
        self.captured_output = None

    def __enter__(self):
        """Start capturing output."""
        import sys
        import io

        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.captured_output = io.StringIO()

        sys.stdout = self.captured_output
        sys.stderr = self.captured_output

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing output and display it."""
        import sys

        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

        # Get captured output and display it
        if self.captured_output:
            output = self.captured_output.getvalue()
            if output.strip() and hasattr(self.dialog, 'add_log'):
                self.dialog.add_log(output.strip())


class ProgressWidget(QtW.QWidget):
    """Widget for displaying progress information."""

    def __init__(self, parent=None):
        super(ProgressWidget, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QtW.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Current group label with better styling
        self.current_group_label = QtW.QLabel("Ready to start...")
        self.current_group_label.setWordWrap(True)
        self.current_group_label.setAlignment(QtCore.Qt.AlignCenter)

        # Style the current group label
        label_font = self.current_group_label.font()
        label_font.setPointSize(12)
        label_font.setBold(True)
        self.current_group_label.setFont(label_font)
        self.current_group_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0px;
            }
        """)
        layout.addWidget(self.current_group_label)

        # Progress bar with enhanced styling
        self.progress_bar = QtW.QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(30)

        # Apply modern styling to progress bar
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 11px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #2980b9, stop:1 #3498db);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Log display section with better styling
        log_label = QtW.QLabel("Processing Log:")
        log_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #34495e;
                margin-top: 10px;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(log_label)

        self.log_display = QtW.QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(300)  # Reduced height for better proportions

        # Style the log display
        self.log_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.log_display)

    def set_progress(self, current: int, total: int, group_name: str = ""):
        """Set the progress values."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        if current < total:
            progress_text = f"🔧 Building group {current + 1} of {total}: {group_name}"
            self.current_group_label.setText(progress_text)

            # Use the format from constants with better styling
            try:
                # Try to import the constant
                from ..config.constants import PROGRESS_BAR_FORMAT
                progress_format = PROGRESS_BAR_FORMAT.format(
                    current=current + 1, 
                    total=total, 
                    name=group_name
                )
            except ImportError:
                # Fallback if import fails
                progress_format = f"{current + 1}/{total} - {group_name}"

            self.progress_bar.setFormat(progress_format)
        else:
            self.current_group_label.setText("✅ Workflow completed successfully!")
            self.progress_bar.setFormat("🎉 Complete!")

    def add_log_message(self, message: str):
        """Add a message to the log display."""
        try:
            # Check if the log_display Qt object is still valid
            if hasattr(self.log_display, 'isVisible') and callable(getattr(self.log_display, 'isVisible', None)):
                try:
                    # This will raise RuntimeError if C++ object is deleted
                    _ = self.log_display.isVisible()
                    
                    # Check if user is at or near the bottom before adding new message
                    scrollbar = self.log_display.verticalScrollBar()
                    was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

                    self.log_display.append(message)

                    # Only auto-scroll to bottom if user was already at the bottom
                    if was_at_bottom:
                        scrollbar.setValue(scrollbar.maximum())
                        
                except RuntimeError as e:
                    if "Internal C++ object" in str(e) and "already deleted" in str(e):
                        # Qt object is deleted, silently ignore the log message
                        # or optionally print to console
                        print(f"[Widget Closed] {message}")
                    else:
                        # Re-raise other RuntimeErrors
                        raise
            else:
                # Widget doesn't have expected Qt methods, print to console
                print(f"[Widget Invalid] {message}")
        except Exception as e:
            # If any error occurs, fall back to console logging
            print(f"[Log Widget Error] {message}")
            print(f"[Debug] Widget logging error: {str(e)}")

    def clear_log(self):
        """Clear the log display."""
        try:
            # Check if the log_display Qt object is still valid
            if hasattr(self.log_display, 'isVisible') and callable(getattr(self.log_display, 'isVisible', None)):
                try:
                    # This will raise RuntimeError if C++ object is deleted
                    _ = self.log_display.isVisible()
                    self.log_display.clear()
                except RuntimeError as e:
                    if "Internal C++ object" in str(e) and "already deleted" in str(e):
                        # Qt object is deleted, silently ignore
                        pass
                    else:
                        # Re-raise other RuntimeErrors
                        raise
        except Exception as e:
            # If any error occurs, silently ignore for clear operation
            pass

    def reset(self):
        """Reset the progress widget to initial state."""
        self.current_group_label.setText("Ready to start...")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        self.clear_log()


class ValidationSummaryWidget(QtW.QWidget):
    """Widget for displaying validation summary information."""

    def __init__(self, parent=None):
        super(ValidationSummaryWidget, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QtW.QVBoxLayout(self)

        # Summary label
        self.summary_label = QtW.QLabel("Validation Summary")
        font = self.summary_label.font()
        font.setBold(True)
        self.summary_label.setFont(font)
        layout.addWidget(self.summary_label)

        # Details text
        self.details_text = QtW.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(self.details_text)

    def update_summary(self, validation_summary: dict):
        """Update the validation summary display.

        Args:
            validation_summary: Dictionary with validation information.
        """
        is_valid = validation_summary.get("is_valid", False)
        is_ready = validation_summary.get("is_ready_for_processing", False)

        # Update summary label
        if is_valid and is_ready:
            self.summary_label.setText("✓ Ready for Processing")
            self.summary_label.setStyleSheet("color: green; font-weight: bold;")
        elif is_valid:
            self.summary_label.setText("⚠ Valid but Not Ready")
            self.summary_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.summary_label.setText("❌ Validation Errors")
            self.summary_label.setStyleSheet("color: red; font-weight: bold;")

        # Update details
        details = []
        details.append(f"Total Groups: {validation_summary.get('total_groups', 0)}")
        details.append(f"Valid Groups: {validation_summary.get('valid_groups', 0)}")
        details.append(f"Total Assets: {validation_summary.get('total_assets', 0)}")

        if validation_summary.get('groups_with_issues', 0) > 0:
            details.append(f"Groups with Issues: {validation_summary['groups_with_issues']}")

        # Add errors if any
        errors = validation_summary.get('validation_errors', [])
        readiness_errors = validation_summary.get('readiness_errors', [])

        if errors:
            details.append("\nValidation Errors:")
            for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
                details.append(f"  {i}. {error}")
            if len(errors) > 5:
                details.append(f"  ... and {len(errors) - 5} more errors")

        if readiness_errors:
            details.append("\nReadiness Issues:")
            for i, error in enumerate(readiness_errors[:3], 1):  # Show first 3 issues
                details.append(f"  {i}. {error}")
            if len(readiness_errors) > 3:
                details.append(f"  ... and {len(readiness_errors) - 3} more issues")

        self.details_text.setPlainText("\n".join(details))
