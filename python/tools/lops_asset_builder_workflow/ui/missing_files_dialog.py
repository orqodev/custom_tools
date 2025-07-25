"""Dialog for handling missing files during template loading."""

import os
from typing import List, Dict, Tuple, Optional
from PySide2 import QtCore, QtGui, QtWidgets as QtW

# Handle both relative and absolute imports for flexibility
try:
    # Try relative imports first (when imported as part of package)
    from ..utils.file_operations import FileDialogHelper
    from ..models.data_model import AssetGroup, AssetPath
except ImportError:
    # Fall back to absolute imports (when run directly)
    from tools.lops_asset_builder_workflow.utils.file_operations import FileDialogHelper
    from tools.lops_asset_builder_workflow.models.data_model import AssetGroup, AssetPath


class MissingFileItem(QtW.QWidget):
    """Widget representing a single missing file with options to handle it."""
    
    # Signals
    file_resolved = QtCore.Signal(str, str)  # old_path, new_path
    file_skipped = QtCore.Signal(str)  # old_path
    
    def __init__(self, group_name: str, file_path: str, parent=None):
        super(MissingFileItem, self).__init__(parent)
        self.group_name = group_name
        self.original_path = file_path
        self.resolved_path = None
        self.is_skipped = False
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QtW.QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Group name label
        group_label = QtW.QLabel(f"[{self.group_name}]")
        group_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        group_label.setMinimumWidth(100)
        layout.addWidget(group_label)
        
        # File path label (truncated if too long)
        file_name = os.path.basename(self.original_path)
        file_dir = os.path.dirname(self.original_path)
        if len(file_dir) > 50:
            file_dir = "..." + file_dir[-47:]
        
        self.path_label = QtW.QLabel(f"{file_dir}/{file_name}")
        self.path_label.setStyleSheet("color: #7f8c8d;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label, 1)
        
        # Status label
        self.status_label = QtW.QLabel("Missing")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.status_label.setMinimumWidth(80)
        layout.addWidget(self.status_label)
        
        # Browse button
        self.browse_btn = QtW.QPushButton("Browse...")
        self.browse_btn.setMaximumWidth(80)
        self.browse_btn.clicked.connect(self.browse_for_file)
        layout.addWidget(self.browse_btn)
        
        # Skip button
        self.skip_btn = QtW.QPushButton("Skip")
        self.skip_btn.setMaximumWidth(60)
        self.skip_btn.clicked.connect(self.skip_file)
        layout.addWidget(self.skip_btn)
    
    def browse_for_file(self):
        """Open file dialog to browse for the missing file."""
        file_path = FileDialogHelper.get_geometry_file(
            parent=self,
            title=f"Locate missing file: {os.path.basename(self.original_path)}",
            default_dir=os.path.dirname(self.original_path) if os.path.dirname(self.original_path) else None
        )
        
        if file_path:
            self.resolved_path = file_path
            self.is_skipped = False
            
            # Update UI
            self.path_label.setText(f"→ {file_path}")
            self.path_label.setStyleSheet("color: #27ae60;")
            self.status_label.setText("Resolved")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.browse_btn.setText("Change...")
            
            # Emit signal
            self.file_resolved.emit(self.original_path, file_path)
    
    def skip_file(self):
        """Skip this missing file."""
        self.is_skipped = True
        self.resolved_path = None
        
        # Update UI
        self.path_label.setStyleSheet("color: #95a5a6; text-decoration: line-through;")
        self.status_label.setText("Skipped")
        self.status_label.setStyleSheet("color: #95a5a6; font-weight: bold;")
        self.browse_btn.setEnabled(False)
        self.skip_btn.setText("Undo")
        self.skip_btn.clicked.disconnect()
        self.skip_btn.clicked.connect(self.undo_skip)
        
        # Emit signal
        self.file_skipped.emit(self.original_path)
    
    def undo_skip(self):
        """Undo the skip action."""
        self.is_skipped = False
        
        # Reset UI
        self.path_label.setStyleSheet("color: #7f8c8d;")
        self.status_label.setText("Missing")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.browse_btn.setEnabled(True)
        self.skip_btn.setText("Skip")
        self.skip_btn.clicked.disconnect()
        self.skip_btn.clicked.connect(self.skip_file)


class MissingFilesDialog(QtW.QDialog):
    """Dialog for handling missing files during template loading."""
    
    def __init__(self, missing_files: Dict[str, List[str]], parent=None):
        """Initialize the dialog.
        
        Args:
            missing_files: Dictionary mapping group names to lists of missing file paths
            parent: Parent widget
        """
        super(MissingFilesDialog, self).__init__(parent)
        self.missing_files = missing_files
        self.file_resolutions = {}  # old_path -> new_path
        self.skipped_files = set()  # set of skipped file paths
        self.setup_ui()
        self.populate_missing_files()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Missing Files Found")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)
        
        layout = QtW.QVBoxLayout(self)
        
        # Header
        header_label = QtW.QLabel("Missing Files Found in Template")
        header_font = header_label.font()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        total_missing = sum(len(files) for files in self.missing_files.values())
        description = QtW.QLabel(
            f"The template contains {total_missing} missing files. "
            f"You can browse to locate the files in their new locations, or skip files you no longer need."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #34495e; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # Scrollable area for missing files
        scroll_area = QtW.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        self.files_widget = QtW.QWidget()
        self.files_layout = QtW.QVBoxLayout(self.files_widget)
        self.files_layout.setSpacing(2)
        
        scroll_area.setWidget(self.files_widget)
        layout.addWidget(scroll_area)
        
        # Bulk actions
        bulk_layout = QtW.QHBoxLayout()
        
        self.browse_all_btn = QtW.QPushButton("Browse for All Files...")
        self.browse_all_btn.clicked.connect(self.browse_for_all_files)
        bulk_layout.addWidget(self.browse_all_btn)
        
        self.skip_all_btn = QtW.QPushButton("Skip All Missing Files")
        self.skip_all_btn.clicked.connect(self.skip_all_files)
        bulk_layout.addWidget(self.skip_all_btn)
        
        bulk_layout.addStretch()
        layout.addLayout(bulk_layout)
        
        # Status
        self.status_label = QtW.QLabel()
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Dialog buttons
        button_layout = QtW.QHBoxLayout()
        
        self.continue_btn = QtW.QPushButton("Continue with Changes")
        self.continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.continue_btn)
        
        self.cancel_btn = QtW.QPushButton("Cancel Template Loading")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Update status initially
        self.update_status()
    
    def populate_missing_files(self):
        """Populate the dialog with missing file items."""
        for group_name, file_paths in self.missing_files.items():
            # Add group separator
            if self.files_layout.count() > 0:
                separator = QtW.QFrame()
                separator.setFrameShape(QtW.QFrame.HLine)
                separator.setFrameShadow(QtW.QFrame.Sunken)
                separator.setStyleSheet("color: #bdc3c7;")
                self.files_layout.addWidget(separator)
            
            for file_path in file_paths:
                file_item = MissingFileItem(group_name, file_path, self)
                file_item.file_resolved.connect(self.on_file_resolved)
                file_item.file_skipped.connect(self.on_file_skipped)
                self.files_layout.addWidget(file_item)
        
        # Add stretch at the end
        self.files_layout.addStretch()
    
    def on_file_resolved(self, old_path: str, new_path: str):
        """Handle file resolution."""
        self.file_resolutions[old_path] = new_path
        if old_path in self.skipped_files:
            self.skipped_files.remove(old_path)
        self.update_status()
    
    def on_file_skipped(self, file_path: str):
        """Handle file skipping."""
        self.skipped_files.add(file_path)
        if file_path in self.file_resolutions:
            del self.file_resolutions[file_path]
        self.update_status()
    
    def browse_for_all_files(self):
        """Browse for a directory containing all missing files."""
        directory = QtW.QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing Missing Files",
            "",
            QtW.QFileDialog.ShowDirsOnly
        )
        
        if directory:
            # Try to find files with matching names in the selected directory
            resolved_count = 0
            
            for group_name, file_paths in self.missing_files.items():
                for file_path in file_paths:
                    if file_path not in self.file_resolutions and file_path not in self.skipped_files:
                        filename = os.path.basename(file_path)
                        potential_path = os.path.join(directory, filename)
                        
                        if os.path.exists(potential_path):
                            # Find the corresponding file item and update it
                            for i in range(self.files_layout.count()):
                                widget = self.files_layout.itemAt(i).widget()
                                if isinstance(widget, MissingFileItem) and widget.original_path == file_path:
                                    widget.browse_for_file.__func__(widget)  # Simulate browse
                                    widget.resolved_path = potential_path
                                    widget.path_label.setText(f"→ {potential_path}")
                                    widget.path_label.setStyleSheet("color: #27ae60;")
                                    widget.status_label.setText("Resolved")
                                    widget.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                                    widget.browse_btn.setText("Change...")
                                    
                                    self.file_resolutions[file_path] = potential_path
                                    resolved_count += 1
                                    break
            
            if resolved_count > 0:
                QtW.QMessageBox.information(
                    self,
                    "Files Found",
                    f"Found and resolved {resolved_count} missing files in the selected directory."
                )
            else:
                QtW.QMessageBox.information(
                    self,
                    "No Files Found",
                    "No missing files were found in the selected directory."
                )
            
            self.update_status()
    
    def skip_all_files(self):
        """Skip all missing files."""
        reply = QtW.QMessageBox.question(
            self,
            "Skip All Files",
            "Are you sure you want to skip all missing files? This will remove them from the template.",
            QtW.QMessageBox.Yes | QtW.QMessageBox.No,
            QtW.QMessageBox.No
        )
        
        if reply == QtW.QMessageBox.Yes:
            # Skip all files that aren't already resolved or skipped
            for group_name, file_paths in self.missing_files.items():
                for file_path in file_paths:
                    if file_path not in self.file_resolutions and file_path not in self.skipped_files:
                        self.skipped_files.add(file_path)
                        
                        # Update the corresponding UI item
                        for i in range(self.files_layout.count()):
                            widget = self.files_layout.itemAt(i).widget()
                            if isinstance(widget, MissingFileItem) and widget.original_path == file_path:
                                widget.skip_file()
                                break
            
            self.update_status()
    
    def update_status(self):
        """Update the status label."""
        total_missing = sum(len(files) for files in self.missing_files.values())
        resolved_count = len(self.file_resolutions)
        skipped_count = len(self.skipped_files)
        remaining_count = total_missing - resolved_count - skipped_count
        
        if remaining_count == 0:
            if resolved_count > 0 and skipped_count > 0:
                status_text = f"✓ All files handled: {resolved_count} resolved, {skipped_count} skipped"
            elif resolved_count > 0:
                status_text = f"✓ All {resolved_count} files resolved"
            else:
                status_text = f"✓ All {skipped_count} files skipped"
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            status_text = f"{remaining_count} files still need attention"
            if resolved_count > 0:
                status_text += f" ({resolved_count} resolved"
            if skipped_count > 0:
                status_text += f", {skipped_count} skipped" if resolved_count > 0 else f" ({skipped_count} skipped"
            if resolved_count > 0 or skipped_count > 0:
                status_text += ")"
            self.status_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        
        self.status_label.setText(status_text)
    
    def get_file_resolutions(self) -> Dict[str, str]:
        """Get the file path resolutions."""
        return self.file_resolutions.copy()
    
    def get_skipped_files(self) -> set:
        """Get the set of skipped files."""
        return self.skipped_files.copy()


def handle_missing_files_in_groups(groups: List[AssetGroup], parent=None) -> Tuple[List[AssetGroup], bool]:
    """Handle missing files in asset groups.
    
    Args:
        groups: List of asset groups to check for missing files
        parent: Parent widget for the dialog
    
    Returns:
        Tuple of (updated_groups, user_cancelled)
    """
    # Find missing files
    missing_files = {}
    
    for group in groups:
        group_missing = []
        for asset_path in group.asset_paths:
            if not os.path.exists(asset_path.path):
                group_missing.append(asset_path.path)
        
        # Also check texture folder
        if group.texture_folder and not os.path.exists(group.texture_folder):
            group_missing.append(group.texture_folder)
        
        if group_missing:
            missing_files[group.group_name] = group_missing
    
    # If no missing files, return original groups
    if not missing_files:
        return groups, False
    
    # Show missing files dialog
    dialog = MissingFilesDialog(missing_files, parent)
    if dialog.exec_() != QtW.QDialog.Accepted:
        return groups, True  # User cancelled
    
    # Apply resolutions and skips
    file_resolutions = dialog.get_file_resolutions()
    skipped_files = dialog.get_skipped_files()
    
    updated_groups = []
    for group in groups:
        # Create a new group with updated paths
        updated_asset_paths = []
        for asset_path in group.asset_paths:
            if asset_path.path in skipped_files:
                continue  # Skip this file
            elif asset_path.path in file_resolutions:
                # Use resolved path
                updated_asset_paths.append(AssetPath(file_resolutions[asset_path.path]))
            else:
                # Keep original path
                updated_asset_paths.append(asset_path)
        
        # Update texture folder if needed
        updated_texture_folder = group.texture_folder
        if group.texture_folder in skipped_files:
            updated_texture_folder = ""
        elif group.texture_folder in file_resolutions:
            updated_texture_folder = file_resolutions[group.texture_folder]
        
        # Create updated group
        updated_group = AssetGroup(
            group_name=group.group_name,
            asset_paths=updated_asset_paths,
            texture_folder=updated_texture_folder,
            base_path=group.base_path,
            material_names=group.material_names.copy()
        )
        
        # Only add group if it still has valid asset paths
        if updated_group.asset_paths:
            updated_groups.append(updated_group)
    
    return updated_groups, False