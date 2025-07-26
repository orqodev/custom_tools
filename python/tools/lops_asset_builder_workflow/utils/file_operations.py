"""File operations utilities for LOPS Asset Builder Workflow."""

import os
import json
from typing import List, Optional, Tuple
from PySide2 import QtWidgets as QtW


class FileDialogHelper:
    """Helper class for file dialog operations."""
    
    @staticmethod
    def get_geometry_files(parent: Optional[QtW.QWidget] = None, 
                          title: str = "Select Geometry Files",
                          default_dir: Optional[str] = None) -> List[str]:
        """Open file dialog to select multiple geometry files.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            default_dir: Default directory to start browsing from.
            
        Returns:
            List of selected file paths.
        """
        from ..config.constants import GEOMETRY_FILE_EXTENSIONS
        
        # Use default directory if provided, otherwise use empty string
        start_dir = default_dir if default_dir and os.path.exists(default_dir) else ""
        
        file_paths, _ = QtW.QFileDialog.getOpenFileNames(
            parent,
            title,
            start_dir,
            GEOMETRY_FILE_EXTENSIONS
        )
        return file_paths or []
    
    @staticmethod
    def get_single_geometry_file(parent: Optional[QtW.QWidget] = None,
                                title: str = "Select Geometry File",
                                default_dir: Optional[str] = None) -> Optional[str]:
        """Open file dialog to select a single geometry file.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            default_dir: Default directory to start browsing from.
            
        Returns:
            Selected file path or None if cancelled.
        """
        from ..config.constants import GEOMETRY_FILE_EXTENSIONS
        
        # Use default directory if provided, otherwise use empty string
        start_dir = default_dir if default_dir and os.path.exists(default_dir) else ""
        
        file_path, _ = QtW.QFileDialog.getOpenFileName(
            parent,
            title,
            start_dir,
            GEOMETRY_FILE_EXTENSIONS
        )
        return file_path if file_path else None
    
    @staticmethod
    def get_geometry_file(parent: Optional[QtW.QWidget] = None,
                         title: str = "Select Geometry File",
                         default_dir: Optional[str] = None) -> Optional[str]:
        """Open file dialog to select a single geometry file with default directory support.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            default_dir: Default directory to start browsing from.
            
        Returns:
            Selected file path or None if cancelled.
        """
        from ..config.constants import GEOMETRY_FILE_EXTENSIONS
        
        # Use default directory if provided, otherwise use empty string
        start_dir = default_dir if default_dir and os.path.exists(default_dir) else ""
        
        file_path, _ = QtW.QFileDialog.getOpenFileName(
            parent,
            title,
            start_dir,
            GEOMETRY_FILE_EXTENSIONS
        )
        return file_path if file_path else None
    
    @staticmethod
    def get_folder(parent: Optional[QtW.QWidget] = None,
                   title: str = "Select Folder",
                   default_dir: Optional[str] = None) -> Optional[str]:
        """Open folder dialog to select a directory.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            default_dir: Default directory to start browsing from.
            
        Returns:
            Selected folder path or None if cancelled.
        """
        # Use default directory if provided, otherwise use empty string
        start_dir = default_dir if default_dir and os.path.exists(default_dir) else ""
        
        folder_path = QtW.QFileDialog.getExistingDirectory(
            parent,
            title,
            start_dir
        )
        return folder_path if folder_path else None
    
    @staticmethod
    def get_json_file_for_saving(parent: Optional[QtW.QWidget] = None,
                                 title: str = "Save Template",
                                 default_name: str = "template.json") -> Optional[str]:
        """Open file dialog to save a JSON file.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            default_name: Default filename.
            
        Returns:
            Selected file path or None if cancelled.
        """
        from ..config.constants import JSON_FILE_EXTENSIONS
        
        file_path, _ = QtW.QFileDialog.getSaveFileName(
            parent,
            title,
            default_name,
            JSON_FILE_EXTENSIONS
        )
        return file_path if file_path else None
    
    @staticmethod
    def get_json_file_for_loading(parent: Optional[QtW.QWidget] = None,
                                 title: str = "Load Template") -> Optional[str]:
        """Open file dialog to load a JSON file.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.
            
        Returns:
            Selected file path or None if cancelled.
        """
        from ..config.constants import JSON_FILE_EXTENSIONS
        
        file_path, _ = QtW.QFileDialog.getOpenFileName(
            parent,
            title,
            "",
            JSON_FILE_EXTENSIONS
        )
        return file_path if file_path else None


class PathUtils:
    """Utility functions for path operations."""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize a file path.
        
        Args:
            path: The path to normalize.
            
        Returns:
            Normalized path.
        """
        if not path:
            return ""
        return os.path.normpath(path.strip())
    
    @staticmethod
    def get_relative_path(path: str, base_path: str) -> str:
        """Get relative path from base path.
        
        Args:
            path: The full path.
            base_path: The base path to make relative to.
            
        Returns:
            Relative path or original path if not possible.
        """
        try:
            return os.path.relpath(path, base_path)
        except ValueError:
            # Paths are on different drives (Windows) or other error
            return path
    
    @staticmethod
    def ensure_extension(path: str, extension: str) -> str:
        """Ensure a path has the specified extension.
        
        Args:
            path: The file path.
            extension: The extension to ensure (with or without dot).
            
        Returns:
            Path with the correct extension.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        if not path.lower().endswith(extension.lower()):
            path += extension
        
        return path
    
    @staticmethod
    def is_valid_geometry_file(path: str) -> bool:
        """Check if a path points to a valid geometry file.
        
        Args:
            path: The file path to check.
            
        Returns:
            True if the file exists and has a valid geometry extension.
        """
        if not os.path.isfile(path):
            return False
        
        valid_extensions = ['.bgeo', '.bgeo.sc', '.abc', '.obj', '.fbx']
        path_lower = path.lower()
        
        return any(path_lower.endswith(ext) for ext in valid_extensions)
    
    @staticmethod
    def get_common_base_path(paths: List[str]) -> str:
        """Get the common base path for a list of file paths.
        
        Args:
            paths: List of file paths.
            
        Returns:
            Common base directory path.
        """
        if not paths:
            return ""
        
        if len(paths) == 1:
            return os.path.dirname(paths[0])
        
        # Get common prefix of all paths
        common_path = os.path.commonpath([os.path.dirname(p) for p in paths])
        return common_path
    
    @staticmethod
    def split_path_and_filename(path: str) -> Tuple[str, str]:
        """Split a path into directory and filename.
        
        Args:
            path: The file path.
            
        Returns:
            Tuple of (directory, filename).
        """
        return os.path.split(path)
    
    @staticmethod
    def get_file_size_mb(path: str) -> float:
        """Get file size in megabytes.
        
        Args:
            path: The file path.
            
        Returns:
            File size in MB, or 0 if file doesn't exist.
        """
        try:
            size_bytes = os.path.getsize(path)
            return size_bytes / (1024 * 1024)  # Convert to MB
        except (OSError, IOError):
            return 0.0


class JsonUtils:
    """Utility functions for JSON operations."""
    
    @staticmethod
    def load_json_file(file_path: str) -> dict:
        """Load JSON data from a file.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            Loaded JSON data as dictionary.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file contains invalid JSON.
            IOError: If file cannot be read.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {str(e)}", e.doc, e.pos)
        except Exception as e:
            raise IOError(f"Failed to read JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def save_json_file(data: dict, file_path: str, indent: int = 2) -> None:
        """Save data to a JSON file.
        
        Args:
            data: Dictionary data to save.
            file_path: Path where to save the JSON file.
            indent: JSON indentation level.
            
        Raises:
            IOError: If file cannot be written.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to save JSON file {file_path}: {str(e)}")
    
    @staticmethod
    def validate_json_structure(data: dict, required_keys: List[str]) -> bool:
        """Validate that JSON data has required keys.
        
        Args:
            data: JSON data to validate.
            required_keys: List of required keys.
            
        Returns:
            True if all required keys are present.
        """
        if not isinstance(data, dict):
            return False
        
        return all(key in data for key in required_keys)
    
    @staticmethod
    def pretty_format_json(data: dict) -> str:
        """Format JSON data as a pretty-printed string.
        
        Args:
            data: JSON data to format.
            
        Returns:
            Pretty-formatted JSON string.
        """
        return json.dumps(data, indent=2, ensure_ascii=False)


class BackupManager:
    """Manages backup operations for templates and settings."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups. If None, uses default location.
        """
        if backup_dir is None:
            home_dir = os.path.expanduser("~")
            backup_dir = os.path.join(home_dir, ".houdini_tools", "backups")
        
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, source_file: str, backup_name: Optional[str] = None) -> str:
        """Create a backup of a file.
        
        Args:
            source_file: Path to the file to backup.
            backup_name: Optional custom backup name.
            
        Returns:
            Path to the created backup file.
            
        Raises:
            IOError: If backup cannot be created.
        """
        if not os.path.exists(source_file):
            raise IOError(f"Source file not found: {source_file}")
        
        if backup_name is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(source_file)
            name, ext = os.path.splitext(filename)
            backup_name = f"{name}_backup_{timestamp}{ext}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            import shutil
            shutil.copy2(source_file, backup_path)
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {str(e)}")
    
    def list_backups(self, pattern: Optional[str] = None) -> List[str]:
        """List available backup files.
        
        Args:
            pattern: Optional filename pattern to filter by.
            
        Returns:
            List of backup file paths.
        """
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if pattern is None or pattern in filename:
                backup_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(backup_path):
                    backups.append(backup_path)
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backups
    
    def cleanup_old_backups(self, max_backups: int = 10) -> int:
        """Remove old backup files, keeping only the most recent ones.
        
        Args:
            max_backups: Maximum number of backups to keep.
            
        Returns:
            Number of backups removed.
        """
        backups = self.list_backups()
        
        if len(backups) <= max_backups:
            return 0
        
        backups_to_remove = backups[max_backups:]
        removed_count = 0
        
        for backup_path in backups_to_remove:
            try:
                os.remove(backup_path)
                removed_count += 1
            except OSError:
                pass  # Ignore errors when removing backups
        
        return removed_count