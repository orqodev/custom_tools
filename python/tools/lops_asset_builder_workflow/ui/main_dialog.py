"""Main dialog interface for LOPS Asset Builder Workflow."""

import sys
import io
import os
from typing import List, Optional
from PySide2 import QtCore, QtGui, QtWidgets as QtW

# Handle both relative and absolute imports for flexibility
try:
    # Try relative imports first (when imported as part of package)
    from ..config.constants import (
        DEFAULT_DIALOG_WIDTH, DEFAULT_DIALOG_HEIGHT, PROCESSING_DIALOG_HEIGHT,
        DEFAULT_ASSET_SCOPE, SUCCESS_MESSAGES, ERROR_MESSAGES
    )
    from ..models.data_model import WorkflowData, ProcessingState
    from ..models.settings_model import SettingsManager, TemplateManager
    from ..utils.file_operations import FileDialogHelper
    from ..utils.validation import ValidationUtils, UIValidator
    from .components import GroupWidget, ValidationSummaryWidget, HoudiniOutputCapture
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config.constants import (
        DEFAULT_DIALOG_WIDTH, DEFAULT_DIALOG_HEIGHT, PROCESSING_DIALOG_HEIGHT,
        DEFAULT_ASSET_SCOPE, SUCCESS_MESSAGES, ERROR_MESSAGES
    )
    from models.data_model import WorkflowData, ProcessingState
    from models.settings_model import SettingsManager, TemplateManager
    from utils.file_operations import FileDialogHelper
    from utils.validation import ValidationUtils, UIValidator
    from .components import GroupWidget, ValidationSummaryWidget, HoudiniOutputCapture


class AssetGroupsDialog(QtW.QDialog):
    """Main dialog for configuring asset groups and managing the workflow."""

    # Define custom signals for better communication
    processing_started = QtCore.Signal()
    processing_finished = QtCore.Signal()
    group_processed = QtCore.Signal(int, str)  # group_index, group_name
    log_message = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetGroupsDialog, self).__init__(parent)

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.template_manager = TemplateManager(self.settings_manager)

        # Initialize data
        self.workflow_data = WorkflowData()
        self.processing_state = ProcessingState()
        self.group_widgets: List[GroupWidget] = []
        self.result_data = []

        # UI state
        self.ready_for_processing = False

        # Set proper window attributes
        # Note: Removed WA_DeleteOnClose to prevent C++ object deletion during workflow
        # The dialog needs to stay alive for progress updates after initial input collection
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.setup_ui()
        self._connect_signals()
        self._restore_window_geometry()

        # Add initial group
        self.add_group_widget()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("LOPS Asset Builder - Asset Groups")
        self.setMinimumSize(DEFAULT_DIALOG_WIDTH, DEFAULT_DIALOG_HEIGHT)

        # Main layout
        main_layout = QtW.QVBoxLayout(self)

        # Instructions
        self.instructions = QtW.QLabel(
            "Configure asset groups for your LOPS workflow. Each group will be processed "
            "as a separate component with its own materials and parameters."
        )
        self.instructions.setWordWrap(True)
        main_layout.addWidget(self.instructions)

        # Asset scope
        scope_layout = QtW.QHBoxLayout()
        scope_layout.addWidget(QtW.QLabel("Asset Scope:"))
        self.asset_scope_edit = QtW.QLineEdit()
        self.asset_scope_edit.setText(DEFAULT_ASSET_SCOPE)
        self.asset_scope_edit.setPlaceholderText("Enter asset scope name...")
        self.asset_scope_edit.textChanged.connect(self.update_ok_button)
        scope_layout.addWidget(self.asset_scope_edit)
        main_layout.addLayout(scope_layout)

        # Validation summary widget
        self.validation_widget = ValidationSummaryWidget()
        main_layout.addWidget(self.validation_widget)

        # Groups section
        groups_label = QtW.QLabel("Asset Groups:")
        font = groups_label.font()
        font.setBold(True)
        groups_label.setFont(font)
        main_layout.addWidget(groups_label)

        # Scrollable area for groups
        self.scroll_area = QtW.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(300)

        self.groups_widget = QtW.QWidget()
        self.groups_layout = QtW.QVBoxLayout(self.groups_widget)
        self.groups_layout.setSpacing(10)
        self.groups_layout.addStretch(1)  # Add stretch at the end

        self.scroll_area.setWidget(self.groups_widget)
        main_layout.addWidget(self.scroll_area)

        # Add Group button
        self.add_group_btn = QtW.QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group_widget)
        main_layout.addWidget(self.add_group_btn)

        # Template buttons
        template_layout = QtW.QHBoxLayout()

        save_template_btn = QtW.QPushButton("Save Template")
        save_template_btn.clicked.connect(self.save_template)
        template_layout.addWidget(save_template_btn)

        load_template_btn = QtW.QPushButton("Load Template")
        load_template_btn.clicked.connect(self.load_template)
        template_layout.addWidget(load_template_btn)

        template_layout.addStretch()
        main_layout.addLayout(template_layout)

        # Progress section (initially hidden) - restored old style
        self.progress_widget = QtW.QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QtW.QVBoxLayout(self.progress_widget)
        progress_layout.setSpacing(2)
        progress_layout.setContentsMargins(5, 10, 5, 10)

        # Progress title
        self.progress_title = QtW.QLabel("Asset Builder Workflow")
        self.progress_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2e7d32; margin: 0px;")
        progress_layout.addWidget(self.progress_title)

        # Progress bar
        self.progress_bar = QtW.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { height: 14px; margin: 0px; }")
        progress_layout.addWidget(self.progress_bar)

        # Current group label
        self.current_group_label = QtW.QLabel("Initializing workflow...")
        self.current_group_label.setStyleSheet("font-size: 14px; margin: 0px;")
        progress_layout.addWidget(self.current_group_label)

        # Add a separator line before logs
        separator = QtW.QFrame()
        separator.setFrameShape(QtW.QFrame.HLine)
        separator.setFrameShadow(QtW.QFrame.Sunken)
        separator.setStyleSheet("color: #cccccc; margin: 0px; max-height: 1px;")
        progress_layout.addWidget(separator)

        # Log display area
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
        self.log_display.setMinimumHeight(400)
        self.log_display.setMaximumHeight(600)
        self.log_display.setPlaceholderText("Processing logs will appear here...")
        progress_layout.addWidget(self.log_display)

        main_layout.addWidget(self.progress_widget)

        # Dialog buttons
        button_layout = QtW.QHBoxLayout()

        self.ok_btn = QtW.QPushButton("Start Workflow")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QtW.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.close_btn = QtW.QPushButton("Close")
        self.close_btn.setVisible(False)
        self.close_btn.clicked.connect(self.close_dialog)
        button_layout.addWidget(self.close_btn)

        main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect internal signals."""
        self.processing_started.connect(self._on_processing_started)
        self.processing_finished.connect(self._on_processing_finished)
        self.group_processed.connect(self._on_group_processed)
        self.log_message.connect(self._on_log_message)

    def _restore_window_geometry(self):
        """Restore window geometry from settings."""
        geometry = self.settings_manager.get_window_geometry()
        if geometry["width"] > 0 and geometry["height"] > 0:
            self.resize(geometry["width"], geometry["height"])

            if geometry["x"] >= 0 and geometry["y"] >= 0:
                self.move(geometry["x"], geometry["y"])

    def _save_window_geometry(self):
        """Save current window geometry to settings."""
        geometry = self.geometry()
        self.settings_manager.update_window_geometry(
            geometry.width(), geometry.height(),
            geometry.x(), geometry.y()
        )

    def _on_log_message(self, message: str):
        """Handle log message signal."""
        self.add_log(message)

    def _on_processing_started(self):
        """Handle processing started signal."""
        pass  # Additional processing start logic can be added here

    def _on_processing_finished(self):
        """Handle processing finished signal."""
        pass  # Additional processing finish logic can be added here

    def _on_group_processed(self, group_index: int, group_name: str):
        """Handle group processed signal."""
        self.update_progress(group_index + 1, group_name)

    def _is_dialog_valid(self) -> bool:
        """Check if the dialog and its Qt objects are still valid."""
        try:
            # Check if the dialog itself is still valid
            if not hasattr(self, 'isVisible'):
                return False
            
            # Try to access a Qt property - this will raise RuntimeError if C++ object is deleted
            # Use a simple check to avoid recursion issues
            self.isVisible()
            
            # Check key UI elements that are commonly accessed
            if hasattr(self, 'asset_scope_edit'):
                self.asset_scope_edit.isVisible()
            
            return True
            
        except RuntimeError:
            # Any RuntimeError likely means Qt objects are deleted
            return False
        except (RecursionError, AttributeError):
            # Handle recursion errors and attribute errors gracefully
            return False
        except Exception:
            # For any other exception, assume dialog is invalid
            return False

    def _safe_ui_operation(self, operation):
        """Safely execute a UI operation, handling Qt object deletion gracefully."""
        try:
            if self._is_dialog_valid():
                operation()
            else:
                print("[Dialog Closed] Skipping UI operation - dialog objects deleted")
        except RuntimeError as e:
            if "Internal C++ object" in str(e) and "already deleted" in str(e):
                print(f"[Dialog Closed] UI operation failed - Qt object deleted: {str(e)}")
            else:
                # Re-raise other RuntimeErrors
                raise
        except Exception as e:
            print(f"[Dialog Error] UI operation failed: {str(e)}")

    def add_group_widget(self):
        """Add a new group widget."""
        group_widget = GroupWidget(self)
        self.group_widgets.append(group_widget)

        # Connect signals
        group_widget.group_changed.connect(self.update_ok_button)
        group_widget.remove_requested.connect(lambda: self.remove_group_widget(group_widget))
        group_widget.validation_needed.connect(self.update_ok_button)

        # Insert before the stretch
        insert_index = self.groups_layout.count() - 1
        self.groups_layout.insertWidget(insert_index, group_widget)

        # Update validation
        self.update_ok_button()

    def remove_group_widget(self, group_widget: GroupWidget):
        """Remove a group widget."""
        if group_widget in self.group_widgets and len(self.group_widgets) > 1:
            self.group_widgets.remove(group_widget)
            self.groups_layout.removeWidget(group_widget)
            group_widget.deleteLater()

            self.update_ok_button()

    def update_ok_button(self):
        """Update the OK button state based on validation."""
        # Collect current data
        asset_scope = self.asset_scope_edit.text().strip()
        groups_data = []

        for group_widget in self.group_widgets:
            group_data = group_widget.get_group_data()
            if group_data:
                groups_data.append(group_data)

        # Update workflow data
        self.workflow_data.asset_scope = asset_scope
        self.workflow_data.groups = []
        for group_data in groups_data:
            try:
                from ..models.data_model import AssetGroup
            except ImportError:
                from models.data_model import AssetGroup
            asset_group = AssetGroup.from_dict(group_data)
            self.workflow_data.add_group(asset_group)

        # Validate
        is_valid, errors = UIValidator.validate_dialog_input(asset_scope, groups_data)
        is_ready, readiness_errors = UIValidator.validate_processing_readiness(self.workflow_data)

        # Update validation summary
        validation_summary = ValidationUtils.get_validation_summary(self.workflow_data)
        self.validation_widget.update_summary(validation_summary)

        # Update button state
        self.ready_for_processing = is_valid and is_ready
        self.ok_btn.setEnabled(self.ready_for_processing)

        # Update button text based on state
        if self.ready_for_processing:
            self.ok_btn.setText("Start Workflow")
        elif is_valid:
            self.ok_btn.setText("Fix Issues to Continue")
        else:
            self.ok_btn.setText("Fix Validation Errors")

    def accept(self):
        """Handle dialog acceptance."""
        if not self.ready_for_processing:
            QtW.QMessageBox.warning(
                self,
                "Validation Error",
                "Please fix all validation errors before starting the workflow."
            )
            return

        # Collect final data
        self.result_data = []
        for group_widget in self.group_widgets:
            group_data = group_widget.get_group_data()
            if group_data:
                self.result_data.append(group_data)

        if not self.result_data:
            QtW.QMessageBox.warning(
                self,
                "No Data",
                "No valid groups found. Please add at least one group with valid asset paths."
            )
            return

        # Save window geometry
        self._save_window_geometry()

        # Call super().accept() to return control to main.py for workflow processing
        super(AssetGroupsDialog, self).accept()

    def reject(self):
        """Handle dialog rejection."""
        if self.processing_state.is_processing:
            reply = QtW.QMessageBox.question(
                self,
                "Cancel Processing",
                "Processing is in progress. Are you sure you want to cancel?",
                QtW.QMessageBox.Yes | QtW.QMessageBox.No,
                QtW.QMessageBox.No
            )

            if reply == QtW.QMessageBox.Yes:
                self.processing_state.reset()
                self._save_window_geometry()
                super(AssetGroupsDialog, self).reject()
        else:
            self._save_window_geometry()
            super(AssetGroupsDialog, self).reject()

    def close_dialog(self):
        """Close the dialog after successful processing."""
        self._save_window_geometry()
        super(AssetGroupsDialog, self).accept()

    def save_template(self):
        """Save current form data as a template."""
        try:
            # Validate data before saving
            if not self.workflow_data.is_valid():
                QtW.QMessageBox.warning(
                    self,
                    "Invalid Data",
                    "Cannot save template with invalid data. Please fix validation errors first."
                )
                return

            # Get save location
            default_dir = self.template_manager.get_default_template_directory()
            file_path = FileDialogHelper.get_json_file_for_saving(
                parent=self,
                title="Save Template",
                default_name=os.path.join(default_dir, "asset_template.json")
            )

            if file_path:
                self.template_manager.save_template(self.workflow_data, file_path)

                QtW.QMessageBox.information(
                    self,
                    "Template Saved",
                    SUCCESS_MESSAGES["template_saved"].format(path=file_path)
                )

        except Exception as e:
            QtW.QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save template:\n{str(e)}"
            )

    def load_template(self):
        """Load form data from JSON template."""
        try:
            # Get file to load
            file_path = FileDialogHelper.get_json_file_for_loading(
                parent=self,
                title="Load Template"
            )

            if not file_path:
                return

            # Load template
            workflow_data = self.template_manager.load_template(file_path)

            # Check for missing files and handle them
            try:
                from .missing_files_dialog import handle_missing_files_in_groups
            except ImportError:
                from missing_files_dialog import handle_missing_files_in_groups
            
            updated_groups, user_cancelled = handle_missing_files_in_groups(workflow_data.groups, self)
            
            if user_cancelled:
                # User cancelled the missing files dialog, don't load the template
                return
            
            # Update workflow data with resolved groups
            workflow_data.groups = updated_groups

            # Clear existing groups - use a safer approach to avoid infinite loop
            # The remove_group_widget method has a condition that prevents removing the last widget,
            # which causes an infinite loop in the while loop. We'll clear them manually.
            for group_widget in self.group_widgets[:]:  # Create a copy of the list to iterate over
                self.groups_layout.removeWidget(group_widget)
                group_widget.deleteLater()
            
            # Clear the list completely
            self.group_widgets.clear()

            # Load asset scope
            self.asset_scope_edit.setText(workflow_data.asset_scope)

            # Create groups from loaded data (now with resolved missing files)
            for asset_group in workflow_data.groups:
                group_widget = GroupWidget(self)
                group_widget.set_asset_group(asset_group)

                self.group_widgets.append(group_widget)

                # Connect signals
                group_widget.group_changed.connect(self.update_ok_button)
                group_widget.remove_requested.connect(lambda gw=group_widget: self.remove_group_widget(gw))
                group_widget.validation_needed.connect(self.update_ok_button)

                # Add to layout
                insert_index = self.groups_layout.count() - 1
                self.groups_layout.insertWidget(insert_index, group_widget)

            # Update validation
            self.update_ok_button()

            # Show success message
            if updated_groups != workflow_data.groups:
                QtW.QMessageBox.information(
                    self,
                    "Template Loaded with Changes",
                    f"Template loaded successfully from:\n{file_path}\n\n"
                    f"Some missing files were resolved or skipped during loading."
                )
            else:
                QtW.QMessageBox.information(
                    self,
                    "Template Loaded",
                    SUCCESS_MESSAGES["template_loaded"].format(path=file_path)
                )

        except Exception as e:
            QtW.QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load template:\n{str(e)}"
            )

    def start_processing_mode(self, total_groups: int):
        """Switch dialog to processing mode."""
        try:
            # Check if the dialog Qt objects are still valid
            if not self._is_dialog_valid():
                print("[Dialog Closed] Cannot start processing mode - dialog objects deleted")
                return
                
            self.processing_state.start_processing(total_groups)

            # Hide input elements - with Qt object validity checks
            self._safe_ui_operation(lambda: self.asset_scope_edit.setEnabled(False))
            self._safe_ui_operation(lambda: self.scroll_area.setVisible(False))
            self._safe_ui_operation(lambda: self.add_group_btn.setVisible(False))
            self._safe_ui_operation(lambda: self.validation_widget.setVisible(False))
            self._safe_ui_operation(lambda: self.instructions.setText("Building assets for your project..."))

            # Show progress elements - with Qt object validity checks
            self._safe_ui_operation(lambda: self.progress_widget.setVisible(True))
            self._safe_ui_operation(lambda: self.progress_bar.setMaximum(total_groups))
            self._safe_ui_operation(lambda: self.progress_bar.setValue(0))

            # Update buttons - with Qt object validity checks
            self._safe_ui_operation(lambda: self.ok_btn.setVisible(False))
            self._safe_ui_operation(lambda: self.cancel_btn.setText("Cancel"))

            # Resize dialog for progress view - with Qt object validity checks
            self._safe_ui_operation(lambda: self.resize(600, 900))

            # Emit signal - with Qt object validity checks
            self._safe_ui_operation(lambda: self.processing_started.emit())
            
        except Exception as e:
            print(f"[Dialog Error] Error in start_processing_mode: {str(e)}")
            # Continue execution even if UI updates fail

    def update_progress(self, group_index: int, group_name: str, message: str = ""):
        """Update progress bar and current group information."""
        try:
            # Check if the dialog Qt objects are still valid
            if not self._is_dialog_valid():
                print(f"[Dialog Closed] Cannot update progress - dialog objects deleted")
                return
                
            self.processing_state.update_progress(group_index, group_name, message)
            
            # Update progress bar and label directly (old style) - with Qt object validity checks
            self._safe_ui_operation(lambda: self.progress_bar.setValue(group_index))
            
            if group_index < self.processing_state.total_groups:
                # Make the progress text cleaner and less repetitive
                progress_text = f"Building group {group_index + 1} of {self.processing_state.total_groups}: {group_name}"
                self._safe_ui_operation(lambda: self.current_group_label.setText(progress_text))
                self._safe_ui_operation(lambda: self.progress_bar.setFormat(f"{group_index + 1}/{self.processing_state.total_groups} - {group_name}"))
            else:
                self._safe_ui_operation(lambda: self.current_group_label.setText("✓ Workflow completed successfully!"))
                self._safe_ui_operation(lambda: self.progress_bar.setFormat("Complete!"))
                self._safe_ui_operation(lambda: self.close_btn.setVisible(True))
                self._safe_ui_operation(lambda: self.cancel_btn.setVisible(False))

            if message:
                self.add_log(message)

            # Process events to update UI - with Qt object validity checks
            self._safe_ui_operation(lambda: QtW.QApplication.processEvents())
            
        except Exception as e:
            print(f"[Dialog Error] Error in update_progress: {str(e)}")
            # Continue execution even if UI updates fail

    def add_log(self, message: str):
        """Add a log message to the display."""
        try:
            # Check if the dialog Qt objects are still valid
            if not self._is_dialog_valid():
                print(f"[Dialog Closed] {message}")
                return
                
            # Check if user is at or near the bottom before adding new message - with Qt object validity checks
            scrollbar = None
            was_at_bottom = False
            
            def get_scroll_position():
                nonlocal scrollbar, was_at_bottom
                scrollbar = self.log_display.verticalScrollBar()
                was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
            
            self._safe_ui_operation(get_scroll_position)

            # Add the message to the log display - with Qt object validity checks
            self._safe_ui_operation(lambda: self.log_display.append(message))

            # Only auto-scroll to bottom if user was already at the bottom - with Qt object validity checks
            if was_at_bottom and scrollbar:
                self._safe_ui_operation(lambda: scrollbar.setValue(scrollbar.maximum()))

            # Process events - with Qt object validity checks
            self._safe_ui_operation(lambda: QtW.QApplication.processEvents())
            
        except Exception as e:
            # If any error occurs, fall back to console logging
            print(f"[Dialog Error] {message}")
            print(f"[Debug] Logging error: {str(e)}")

    def capture_houdini_output(self):
        """Context manager to capture Houdini output and display in logs."""
        return HoudiniOutputCapture(self)

    def get_workflow_data(self) -> WorkflowData:
        """Get the current workflow data."""
        return self.workflow_data

    def get_result_data(self) -> List[dict]:
        """Get the result data from the dialog."""
        return self.result_data

    def closeEvent(self, event):
        """Handle window close event."""
        self._save_window_geometry()
        super(AssetGroupsDialog, self).closeEvent(event)


class SettingsDialog(QtW.QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.settings_manager = settings_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("LOPS Asset Builder - Settings")
        self.setMinimumSize(400, 300)

        layout = QtW.QVBoxLayout(self)

        # Auto-save setting
        self.auto_save_check = QtW.QCheckBox("Enable auto-save")
        layout.addWidget(self.auto_save_check)

        # Max recent templates
        recent_layout = QtW.QHBoxLayout()
        recent_layout.addWidget(QtW.QLabel("Max recent templates:"))
        self.max_recent_spin = QtW.QSpinBox()
        self.max_recent_spin.setRange(1, 50)
        recent_layout.addWidget(self.max_recent_spin)
        layout.addLayout(recent_layout)

        # Recent templates list
        layout.addWidget(QtW.QLabel("Recent Templates:"))
        self.recent_list = QtW.QListWidget()
        layout.addWidget(self.recent_list)

        # Clear recent button
        clear_recent_btn = QtW.QPushButton("Clear Recent Templates")
        clear_recent_btn.clicked.connect(self.clear_recent_templates)
        layout.addWidget(clear_recent_btn)

        # Dialog buttons
        button_layout = QtW.QHBoxLayout()

        ok_btn = QtW.QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QtW.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_settings(self):
        """Load current settings into the UI."""
        settings = self.settings_manager.settings

        self.auto_save_check.setChecked(settings.auto_save_enabled)
        self.max_recent_spin.setValue(settings.max_recent_templates)

        # Load recent templates
        self.recent_list.clear()
        for template_path in self.settings_manager.get_recent_templates():
            self.recent_list.addItem(template_path)

    def accept(self):
        """Save settings and close dialog."""
        settings = self.settings_manager.settings

        settings.auto_save_enabled = self.auto_save_check.isChecked()
        settings.max_recent_templates = self.max_recent_spin.value()

        self.settings_manager.save_settings()
        super(SettingsDialog, self).accept()

    def clear_recent_templates(self):
        """Clear the recent templates list."""
        reply = QtW.QMessageBox.question(
            self,
            "Clear Recent Templates",
            "Are you sure you want to clear all recent templates?",
            QtW.QMessageBox.Yes | QtW.QMessageBox.No,
            QtW.QMessageBox.No
        )

        if reply == QtW.QMessageBox.Yes:
            self.settings_manager.settings.recent_templates.clear()
            self.settings_manager.save_settings()
            self.recent_list.clear()
