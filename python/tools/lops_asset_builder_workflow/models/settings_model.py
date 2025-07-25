"""Settings and configuration management for LOPS Asset Builder Workflow."""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from .data_model import WorkflowData


@dataclass
class ApplicationSettings:
    """Application-wide settings."""
    last_template_path: str = ""
    last_materials_folder: str = ""
    window_geometry: Dict[str, int] = None
    recent_templates: list = None
    auto_save_enabled: bool = True
    max_recent_templates: int = 10
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.window_geometry is None:
            self.window_geometry = {"width": 600, "height": 400, "x": -1, "y": -1}
        if self.recent_templates is None:
            self.recent_templates = []


class SettingsManager:
    """Manages application settings and template persistence."""
    
    def __init__(self, settings_file: Optional[str] = None):
        """Initialize the settings manager.
        
        Args:
            settings_file: Path to the settings file. If None, uses default location.
        """
        if settings_file is None:
            # Use a default location in the user's home directory
            home_dir = os.path.expanduser("~")
            settings_dir = os.path.join(home_dir, ".houdini_tools")
            os.makedirs(settings_dir, exist_ok=True)
            settings_file = os.path.join(settings_dir, "lops_asset_builder_settings.json")
        
        self.settings_file = settings_file
        self.settings = ApplicationSettings()
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    # Update settings with loaded data
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
            # Continue with default settings
    
    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(asdict(self.settings), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def add_recent_template(self, template_path: str) -> None:
        """Add a template to the recent templates list."""
        if template_path in self.settings.recent_templates:
            self.settings.recent_templates.remove(template_path)
        
        self.settings.recent_templates.insert(0, template_path)
        
        # Limit the number of recent templates
        if len(self.settings.recent_templates) > self.settings.max_recent_templates:
            self.settings.recent_templates = self.settings.recent_templates[:self.settings.max_recent_templates]
        
        self.save_settings()
    
    def get_recent_templates(self) -> list:
        """Get the list of recent templates, filtering out non-existent files."""
        existing_templates = [path for path in self.settings.recent_templates if os.path.exists(path)]
        
        # Update the list if some files no longer exist
        if len(existing_templates) != len(self.settings.recent_templates):
            self.settings.recent_templates = existing_templates
            self.save_settings()
        
        return existing_templates
    
    def update_window_geometry(self, width: int, height: int, x: int = -1, y: int = -1) -> None:
        """Update window geometry settings."""
        self.settings.window_geometry = {"width": width, "height": height, "x": x, "y": y}
        self.save_settings()
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get window geometry settings."""
        return self.settings.window_geometry.copy()


class TemplateManager:
    """Manages template saving and loading operations."""
    
    def __init__(self, settings_manager: Optional[SettingsManager] = None):
        """Initialize the template manager.
        
        Args:
            settings_manager: Optional settings manager for tracking recent templates.
        """
        self.settings_manager = settings_manager
    
    def save_template(self, workflow_data: WorkflowData, file_path: str) -> None:
        """Save workflow data as a template.
        
        Args:
            workflow_data: The workflow data to save.
            file_path: Path where to save the template.
            
        Raises:
            ValueError: If workflow data is invalid.
            IOError: If file cannot be written.
        """
        if not workflow_data.is_valid():
            raise ValueError("Cannot save invalid workflow data")
        
        template_data = workflow_data.to_dict()
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            # Add to recent templates if settings manager is available
            if self.settings_manager:
                self.settings_manager.add_recent_template(file_path)
                self.settings_manager.settings.last_template_path = file_path
                self.settings_manager.save_settings()
                
        except Exception as e:
            raise IOError(f"Failed to save template: {str(e)}")
    
    def load_template(self, file_path: str) -> WorkflowData:
        """Load workflow data from a template file.
        
        Args:
            file_path: Path to the template file.
            
        Returns:
            WorkflowData: The loaded workflow data.
            
        Raises:
            FileNotFoundError: If template file doesn't exist.
            ValueError: If template format is invalid.
            IOError: If file cannot be read.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                template_data = json.load(f)
            
            # Validate template data structure
            self._validate_template_data(template_data)
            
            # Get template directory for resolving relative paths
            template_dir = os.path.dirname(os.path.abspath(file_path))
            
            # Create workflow data from template with base path context
            workflow_data = WorkflowData.from_dict(template_data, base_path=template_dir)
            
            # Add to recent templates if settings manager is available
            if self.settings_manager:
                self.settings_manager.add_recent_template(file_path)
                self.settings_manager.settings.last_template_path = file_path
                self.settings_manager.save_settings()
            
            return workflow_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in template file: {str(e)}")
        except Exception as e:
            raise IOError(f"Failed to load template: {str(e)}")
    
    def _validate_template_data(self, template_data: Any) -> None:
        """Validate the structure of template data.
        
        Args:
            template_data: The data to validate.
            
        Raises:
            ValueError: If template data is invalid.
        """
        if not isinstance(template_data, dict):
            raise ValueError("Invalid template format: root must be a dictionary")
        
        if 'groups' not in template_data or not isinstance(template_data['groups'], list):
            raise ValueError("Invalid template format: 'groups' must be a list")
        
        # Validate each group
        for group_index, group_data in enumerate(template_data['groups']):
            if not isinstance(group_data, dict):
                raise ValueError(f"Invalid template format: group {group_index + 1} data must be a dictionary")
            
            if 'asset_paths' in group_data:
                paths = group_data['asset_paths']
                if not isinstance(paths, list):
                    raise ValueError(f"Invalid template format: group {group_index + 1} 'asset_paths' must be a list")
                
                for path_index, path in enumerate(paths):
                    if not isinstance(path, str):
                        raise ValueError(f"Invalid template format: group {group_index + 1} path at index {path_index} must be a string")
    
    def get_default_template_directory(self) -> str:
        """Get the default directory for templates."""
        if self.settings_manager and self.settings_manager.settings.last_template_path:
            return os.path.dirname(self.settings_manager.settings.last_template_path)
        
        # Default to user's documents or home directory
        home_dir = os.path.expanduser("~")
        documents_dir = os.path.join(home_dir, "Documents", "Houdini_Templates")
        os.makedirs(documents_dir, exist_ok=True)
        return documents_dir