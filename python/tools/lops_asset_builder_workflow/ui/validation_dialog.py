"""Validation error dialog for displaying detailed validation errors."""

from typing import List
from PySide2 import QtCore, QtGui, QtWidgets as QtW


class ValidationErrorDialog(QtW.QDialog):
    """Dialog for displaying detailed validation errors."""

    def __init__(self, parent=None):
        super(ValidationErrorDialog, self).__init__(parent)
        
        # Set window flags to ensure it appears as a proper external dialog
        self.setWindowFlags(
            QtCore.Qt.Dialog | 
            QtCore.Qt.WindowTitleHint | 
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        
        # Ensure the dialog is modal
        self.setModal(True)
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Validation Errors")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)

        # Main layout
        main_layout = QtW.QVBoxLayout(self)

        # Title and icon
        title_layout = QtW.QHBoxLayout()
        
        # Error icon
        icon_label = QtW.QLabel()
        icon = self.style().standardIcon(QtW.QStyle.SP_MessageBoxCritical)
        icon_label.setPixmap(icon.pixmap(32, 32))
        title_layout.addWidget(icon_label)

        # Title text
        self.title_label = QtW.QLabel("Validation Errors Found")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        main_layout.addLayout(title_layout)

        # Description
        self.description_label = QtW.QLabel(
            "The following validation errors must be resolved before proceeding:"
        )
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("margin: 10px 0px; color: #666666;")
        main_layout.addWidget(self.description_label)

        # Error list
        self.error_list = QtW.QTextEdit()
        self.error_list.setReadOnly(True)
        self.error_list.setFont(QtGui.QFont("Consolas", 10))
        self.error_list.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 10px;
                color: #333333;
            }
        """)
        main_layout.addWidget(self.error_list)

        # Buttons
        button_layout = QtW.QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QtW.QPushButton("OK")
        self.ok_button.setMinimumWidth(80)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        main_layout.addLayout(button_layout)

    def set_validation_errors(self, errors: List[str], title: str = "Validation Errors"):
        """Set the validation errors to display.
        
        Args:
            errors: List of error messages to display.
            title: Title for the error dialog.
        """
        if not errors:
            self.error_list.setPlainText("No errors found.")
            return

        # Update title
        self.title_label.setText(title)
        self.setWindowTitle(title)

        # Format errors for display
        error_text = ""
        for i, error in enumerate(errors, 1):
            error_text += f"{i}. {error}\n"

        self.error_list.setPlainText(error_text.strip())

    def set_validation_summary(self, validation_summary: dict):
        """Set validation errors from a validation summary.
        
        Args:
            validation_summary: Dictionary from ValidationUtils.get_validation_summary()
        """
        all_errors = []
        
        # Add validation errors
        if validation_summary.get("validation_errors"):
            all_errors.extend(validation_summary["validation_errors"])
        
        # Add readiness errors
        if validation_summary.get("readiness_errors"):
            all_errors.extend(validation_summary["readiness_errors"])

        # Update description with summary info
        total_groups = validation_summary.get("total_groups", 0)
        valid_groups = validation_summary.get("valid_groups", 0)
        groups_with_issues = validation_summary.get("groups_with_issues", 0)
        
        description = f"Found {len(all_errors)} validation error(s) across {total_groups} group(s). "
        if groups_with_issues > 0:
            description += f"{groups_with_issues} group(s) have issues that need to be resolved."
        
        self.description_label.setText(description)
        
        # Set the errors
        self.set_validation_errors(all_errors, "Validation Errors")

    @staticmethod
    def show_validation_errors(parent, errors: List[str], title: str = "Validation Errors") -> bool:
        """Show validation errors in a dialog.
        
        Args:
            parent: Parent widget for the dialog.
            errors: List of error messages to display.
            title: Title for the error dialog.
            
        Returns:
            True if there were errors to show, False otherwise.
        """
        if not errors:
            return False

        dialog = ValidationErrorDialog(parent)
        dialog.set_validation_errors(errors, title)
        
        # Center the dialog on parent or screen
        if parent:
            dialog.move(parent.geometry().center() - dialog.rect().center())
        
        # Ensure dialog is visible and has focus
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Execute as modal dialog
        result = dialog.exec_()
        return True

    @staticmethod
    def show_validation_summary(parent, validation_summary: dict) -> bool:
        """Show validation summary in a dialog.
        
        Args:
            parent: Parent widget for the dialog.
            validation_summary: Dictionary from ValidationUtils.get_validation_summary()
            
        Returns:
            True if there were errors to show, False otherwise.
        """
        all_errors = []
        
        # Collect all errors
        if validation_summary.get("validation_errors"):
            all_errors.extend(validation_summary["validation_errors"])
        if validation_summary.get("readiness_errors"):
            all_errors.extend(validation_summary["readiness_errors"])

        if not all_errors:
            return False

        dialog = ValidationErrorDialog(parent)
        dialog.set_validation_summary(validation_summary)
        
        # Center the dialog on parent or screen
        if parent:
            dialog.move(parent.geometry().center() - dialog.rect().center())
        
        # Ensure dialog is visible and has focus
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Execute as modal dialog
        result = dialog.exec_()
        return True