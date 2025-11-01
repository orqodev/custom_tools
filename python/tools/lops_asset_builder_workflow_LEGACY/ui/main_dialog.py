"""Main dialog interface for LOPS Asset Builder Workflow."""

import sys
import io
import os
from typing import List, Optional
from PySide6 import QtCore, QtGui, QtWidgets as QtW

# Material Design support removed - using built-in Houdini theming instead

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
    from .validation_dialog import ValidationErrorDialog
    from .houdini_theme import HoudiniTheme
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
    from .validation_dialog import ValidationErrorDialog
    from houdini_theme import HoudiniTheme


class AssetGroupsDialog(QtW.QDialog):
    """Main dialog for configuring asset groups and managing the workflow."""

    # Define custom signals for better communication
    processing_started = QtCore.Signal()
    processing_finished = QtCore.Signal()
    group_processed = QtCore.Signal(int, str)  # group_index, group_name
    log_message = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetGroupsDialog, self).__init__(parent)
        
        # Material Design theming removed - using built-in Houdini theming instead

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
        
        # Apply Houdini theme to dialog
        HoudiniTheme.apply_theme_to_widget(self, "dialog")

        # Main layout
        main_layout = QtW.QVBoxLayout(self)


        # Asset scope
        scope_layout = QtW.QHBoxLayout()
        scope_layout.addWidget(HoudiniTheme.create_themed_label("Asset Scope:"))
        self.asset_scope_edit = QtW.QLineEdit()
        self.asset_scope_edit.setText(DEFAULT_ASSET_SCOPE)
        self.asset_scope_edit.setPlaceholderText("Enter asset scope name...")
        self.asset_scope_edit.textChanged.connect(self.update_ok_button)
        HoudiniTheme.apply_theme_to_widget(self.asset_scope_edit, "input")
        scope_layout.addWidget(self.asset_scope_edit)
        main_layout.addLayout(scope_layout)

        # Validation summary widget - REMOVED: Validations now only appear in popup dialogs
        # self.validation_widget = ValidationSummaryWidget()
        # main_layout.addWidget(self.validation_widget)

        # Groups section
        self.groups_label = HoudiniTheme.create_themed_label("Asset Groups:", "subheader")
        main_layout.addWidget(self.groups_label)

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
        self.add_group_btn = HoudiniTheme.create_themed_button("Add Group", "primary")
        self.add_group_btn.clicked.connect(self.add_group_widget)
        main_layout.addWidget(self.add_group_btn)

        # Template buttons
        template_layout = QtW.QHBoxLayout()

        self.save_template_btn = HoudiniTheme.create_themed_button("Save Template", "secondary")
        self.save_template_btn.clicked.connect(self.save_template)
        template_layout.addWidget(self.save_template_btn)

        self.load_template_btn = HoudiniTheme.create_themed_button("Load Template", "secondary")
        self.load_template_btn.clicked.connect(self.load_template)
        template_layout.addWidget(self.load_template_btn)

        template_layout.addStretch()
        
        # Instructions button positioned in top right
        self.instructions_btn = HoudiniTheme.create_themed_button("Instructions", "secondary")
        self.instructions_btn.clicked.connect(self.show_instructions)
        template_layout.addWidget(self.instructions_btn)
        
        main_layout.addLayout(template_layout)

        # Progress section (initially hidden) - restored old style
        self.progress_widget = QtW.QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QtW.QVBoxLayout(self.progress_widget)
        progress_layout.setSpacing(2)
        progress_layout.setContentsMargins(5, 10, 5, 10)

        # Progress title
        self.progress_title = HoudiniTheme.create_themed_label("Asset Builder Workflow", "header")
        progress_layout.addWidget(self.progress_title)

        # Progress bar
        self.progress_bar = QtW.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        HoudiniTheme.apply_theme_to_widget(self.progress_bar, "progress")
        # Apply additional progress bar styling using theme constants
        self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + f" QProgressBar {{ height: {HoudiniTheme.LAYOUT['progress_bar_height_small']}; margin: {HoudiniTheme.LAYOUT['margin_zero']}; }}")
        progress_layout.addWidget(self.progress_bar)

        # Current group label
        self.current_group_label = HoudiniTheme.create_themed_label("Initializing workflow...", "subheader")
        progress_layout.addWidget(self.current_group_label)

        # Add a separator line before logs
        separator = QtW.QFrame()
        separator.setFrameShape(QtW.QFrame.HLine)
        separator.setFrameShadow(QtW.QFrame.Sunken)
        separator.setStyleSheet(HoudiniTheme.get_separator_style(dark=True))
        progress_layout.addWidget(separator)

        # Log display area
        log_label = HoudiniTheme.create_themed_label("Workflow Logs", "subheader")
        progress_layout.addWidget(log_label)

        self.log_display = QtW.QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QtGui.QFont("Consolas", 9))
        HoudiniTheme.apply_theme_to_widget(self.log_display, "log")
        self.log_display.setMinimumHeight(400)
        self.log_display.setMaximumHeight(600)
        self.log_display.setPlaceholderText("Processing logs will appear here...")
        progress_layout.addWidget(self.log_display)

        main_layout.addWidget(self.progress_widget)

        # Dialog buttons
        button_layout = QtW.QHBoxLayout()
        
        # Add stretch to push buttons to the right (like CSS float: right)
        button_layout.addStretch()

        self.ok_btn = HoudiniTheme.create_themed_button("Start Workflow", "primary")
        self.ok_btn.setEnabled(False)
        self.ok_btn.setFixedWidth(120)  # Reduced width for compact button
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = HoudiniTheme.create_themed_button("Cancel", "secondary")
        self.cancel_btn.setFixedWidth(80)  # Reduced width for compact button
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.close_btn = HoudiniTheme.create_themed_button("Close", "primary")
        self.close_btn.setVisible(False)
        self.close_btn.setFixedWidth(80)  # Reduced width for compact button
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
        # Restore template buttons and groups label visibility after processing completes
        self._safe_ui_operation(lambda: self.groups_label.setVisible(True))
        self._safe_ui_operation(lambda: self.save_template_btn.setVisible(True))
        self._safe_ui_operation(lambda: self.load_template_btn.setVisible(True))
        self._safe_ui_operation(lambda: self.instructions_btn.setVisible(True))

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

        # Update validation summary - REMOVED: Validations now only appear in popup dialogs
        # validation_summary = ValidationUtils.get_validation_summary(self.workflow_data)
        # self.validation_widget.update_summary(validation_summary)

        # Update button state - always enable button so users can click to see validation errors
        self.ready_for_processing = is_valid and is_ready
        self.ok_btn.setEnabled(True)  # Always enabled so users can click to see validation dialogs

        # Update button text - always show "Start Workflow" as requested
        self.ok_btn.setText("Start Workflow")

    def accept(self):
        """Handle dialog acceptance - runs validation each time Start Workflow is clicked."""
        # Always run fresh validation when Start Workflow button is clicked
        # Update workflow data with current form state
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

        # Run comprehensive validation and show detailed errors if any exist
        validation_summary = ValidationUtils.get_validation_summary(self.workflow_data)
        has_errors = ValidationErrorDialog.show_validation_summary(self, validation_summary)
        
        if has_errors:
            # Validation errors were shown in popup - don't proceed with workflow
            return

        # Additional check for empty data
        if not groups_data:
            QtW.QMessageBox.warning(
                self,
                "No Data",
                "No valid groups found. Please add at least one group with valid asset paths."
            )
            return

        # Collect final data for workflow processing
        self.result_data = groups_data

        # Save window geometry
        self._save_window_geometry()

        # Call super().accept() to return control to main.py for workflow processing
        super(AssetGroupsDialog, self).accept()

    def reject(self):
        """Handle dialog rejection with improved Qt object handling."""
        try:
            # Check if dialog is still valid before proceeding
            if not self._is_dialog_valid():
                print("[Dialog Closed] Cannot reject - dialog objects deleted")
                return
            
            # Handle processing state safely
            is_processing = False
            try:
                is_processing = self.processing_state.is_processing
            except (AttributeError, RuntimeError):
                # If processing_state is invalid, assume not processing
                is_processing = False
            
            if is_processing:
                # Use a simpler approach to avoid modal dialog hanging issues
                try:
                    reply = QtW.QMessageBox.question(
                        self,
                        "Cancel Processing",
                        "Processing is in progress. Are you sure you want to cancel?",
                        QtW.QMessageBox.Yes | QtW.QMessageBox.No,
                        QtW.QMessageBox.No
                    )

                    if reply == QtW.QMessageBox.Yes:
                        # Reset processing state safely
                        try:
                            self.processing_state.reset()
                        except (AttributeError, RuntimeError):
                            pass  # Ignore if processing_state is invalid
                        
                        # Save geometry safely
                        self._safe_ui_operation(lambda: self._save_window_geometry())
                        
                        # Close dialog
                        super(AssetGroupsDialog, self).reject()
                except Exception as e:
                    print(f"[Dialog Error] Error in cancel confirmation: {str(e)}")
                    # Force close if confirmation dialog fails
                    super(AssetGroupsDialog, self).reject()
            else:
                # Not processing, safe to close immediately
                self._safe_ui_operation(lambda: self._save_window_geometry())
                super(AssetGroupsDialog, self).reject()
                
        except Exception as e:
            print(f"[Dialog Error] Error in reject method: {str(e)}")
            # Force close as last resort
            try:
                super(AssetGroupsDialog, self).reject()
            except Exception:
                # If even super().reject() fails, try to close the dialog
                try:
                    self.close()
                except Exception:
                    pass  # Give up gracefully

    def close_dialog(self):
        """Close the dialog after successful processing."""
        self._save_window_geometry()
        super(AssetGroupsDialog, self).accept()

    def show_instructions(self):
        """Show the instructions dialog."""
        instructions_dialog = InstructionsDialog(self)
        instructions_dialog.exec_()

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

            # Show success message - no validation popup for template loading
            # Validation will be handled when user clicks "Start Workflow"
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
            # self._safe_ui_operation(lambda: self.validation_widget.setVisible(False))  # REMOVED: validation widget no longer exists
            self._safe_ui_operation(lambda: self.groups_label.setVisible(False))
            self._safe_ui_operation(lambda: self.save_template_btn.setVisible(False))
            self._safe_ui_operation(lambda: self.load_template_btn.setVisible(False))
            self._safe_ui_operation(lambda: self.instructions_btn.setVisible(False))
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


class InstructionsDialog(QtW.QDialog):
    """Dialog to show tool usage instructions."""
    
    def __init__(self, parent=None):
        super(InstructionsDialog, self).__init__(parent)
        self.setWindowTitle("LOPS Asset Builder - Instructions")
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the instructions dialog UI."""
        # Apply Houdini theme to dialog
        HoudiniTheme.apply_theme_to_widget(self, "dialog")
        
        layout = QtW.QVBoxLayout(self)
        
        # Title
        title = HoudiniTheme.create_themed_label("LOPS Asset Builder Workflow - Instructions", "header")
        layout.addWidget(title)
        
        # Instructions text
        instructions_text = QtW.QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setHtml("""
        <h3>How to Use the LOPS Asset Builder Tool</h3>
        
        <h4>1. Asset Scope</h4>
        <p>Enter the asset scope name that will be used for your LOPS workflow. This typically represents the main asset or scene you're working with.</p>
        
        <h4>2. Asset Groups</h4>
        <p>Create one or more asset groups. Each group represents a collection of geometry files that will be processed together:</p>
        <ul>
            <li><b>Group Name:</b> Enter a descriptive name for the group (e.g., "buildings", "vegetation", "props")</li>
            <li><b>Asset Paths:</b> Add geometry files (.bgeo, .abc, .obj, .fbx) using the "Add Files..." button or by typing paths manually</li>
            <li><b>Materials Folder:</b> Select the folder containing materials for this group</li>
        </ul>
        
        <h4>3. Managing Groups</h4>
        <ul>
            <li>Click <b>"Add Group"</b> to create additional asset groups</li>
            <li>Click <b>"Remove Group"</b> to delete a group you no longer need</li>
            <li>Use the <b>"Add Files..."</b> button to bulk-import multiple geometry files</li>
        </ul>
        
        <h4>4. Templates</h4>
        <ul>
            <li><b>Save Template:</b> Save your current configuration for reuse</li>
            <li><b>Load Template:</b> Load a previously saved configuration</li>
        </ul>
        
        <h4>5. Processing</h4>
        <p>Once you've configured your asset groups:</p>
        <ul>
            <li>Click <b>"Start Workflow"</b> to begin processing</li>
            <li>Monitor progress in the workflow logs</li>
            <li>Each group will be processed as a separate component with its own materials and parameters</li>
        </ul>
        
        <h4>Tips</h4>
        <ul>
            <li>Organize similar assets into the same group for better workflow efficiency</li>
            <li>Ensure all geometry files are accessible and materials folders contain the required files</li>
            <li>Save templates for commonly used configurations to speed up future workflows</li>
        </ul>
        """)
        layout.addWidget(instructions_text)
        
        # Close button
        button_layout = QtW.QHBoxLayout()
        button_layout.addStretch()
        close_btn = QtW.QPushButton("Close")
        try:
            from ..config.constants import MATERIAL_BUTTON_STYLE
            close_btn.setStyleSheet(MATERIAL_BUTTON_STYLE)
        except ImportError:
            from config.constants import MATERIAL_BUTTON_STYLE
            close_btn.setStyleSheet(MATERIAL_BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)


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
        
        # Apply Houdini theme to dialog
        HoudiniTheme.apply_theme_to_widget(self, "dialog")

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
        try:
            from ..config.constants import SECONDARY_BUTTON_STYLE
            clear_recent_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        except ImportError:
            from config.constants import SECONDARY_BUTTON_STYLE
            clear_recent_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        clear_recent_btn.clicked.connect(self.clear_recent_templates)
        layout.addWidget(clear_recent_btn)

        # Dialog buttons
        button_layout = QtW.QHBoxLayout()

        ok_btn = QtW.QPushButton("OK")
        try:
            from ..config.constants import MATERIAL_BUTTON_STYLE
            ok_btn.setStyleSheet(MATERIAL_BUTTON_STYLE)
        except ImportError:
            from config.constants import MATERIAL_BUTTON_STYLE
            ok_btn.setStyleSheet(MATERIAL_BUTTON_STYLE)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QtW.QPushButton("Cancel")
        try:
            from ..config.constants import SECONDARY_BUTTON_STYLE
            cancel_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        except ImportError:
            from config.constants import SECONDARY_BUTTON_STYLE
            cancel_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
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
