"""Data structures for LOPS Asset Builder Workflow."""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class AssetPath:
    """Represents a single asset file path."""
    path: str
    
    def __post_init__(self):
        """Validate the path after initialization."""
        if not isinstance(self.path, str):
            raise ValueError("Path must be a string")
        self.path = self.path.strip()
    
    @property
    def filename(self) -> str:
        """Get the filename from the path."""
        return os.path.basename(self.path)
    
    @property
    def directory(self) -> str:
        """Get the directory from the path."""
        return os.path.dirname(self.path)
    
    def is_valid(self) -> bool:
        """Check if the path is valid and not empty."""
        return bool(self.path and self.path.strip())


@dataclass
class AssetGroup:
    """Represents a group of assets with associated metadata."""
    group_name: str
    asset_paths: List[AssetPath] = field(default_factory=list)
    texture_folder: str = ""
    base_path: str = ""
    material_names: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and process data after initialization."""
        if not self.group_name:
            self.group_name = "Unnamed_Group"
        
        # Ensure asset_paths are AssetPath objects
        if self.asset_paths and not isinstance(self.asset_paths[0], AssetPath):
            self.asset_paths = [AssetPath(path) if isinstance(path, str) else AssetPath(path.path if hasattr(path, 'path') else str(path)) 
                              for path in self.asset_paths]
        
        # Set base_path from first asset if not provided
        if not self.base_path and self.asset_paths:
            first_valid_path = next((ap.path for ap in self.asset_paths if ap.is_valid()), "")
            if first_valid_path:
                self.base_path = os.path.dirname(first_valid_path)
    
    def add_asset_path(self, path: str) -> None:
        """Add a new asset path to the group."""
        asset_path = AssetPath(path)
        if asset_path.is_valid():
            self.asset_paths.append(asset_path)
            
            # Update base_path if this is the first valid path
            if not self.base_path:
                self.base_path = asset_path.directory
    
    def remove_asset_path(self, path: str) -> bool:
        """Remove an asset path from the group. Returns True if removed."""
        for i, asset_path in enumerate(self.asset_paths):
            if asset_path.path == path:
                del self.asset_paths[i]
                return True
        return False
    
    def get_valid_paths(self) -> List[str]:
        """Get list of valid asset paths as strings."""
        return [ap.path for ap in self.asset_paths if ap.is_valid()]
    
    def is_valid(self) -> bool:
        """Check if the group has at least one valid asset path."""
        return any(ap.is_valid() for ap in self.asset_paths)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the group to a dictionary for serialization."""
        return {
            "group_name": self.group_name,
            "asset_paths": self.get_valid_paths(),
            "base_path": self.base_path,
            "texture_folder": self.texture_folder,
            "material_names": self.material_names.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_path: str = "") -> 'AssetGroup':
        """Create an AssetGroup from a dictionary.
        
        Args:
            data: Dictionary containing group data.
            base_path: Base path for resolving relative paths.
        """
        # Resolve asset paths relative to base_path if provided
        asset_paths = []
        for path in data.get("asset_paths", []):
            if base_path and not os.path.isabs(path):
                resolved_path = os.path.join(base_path, path)
                asset_paths.append(AssetPath(resolved_path))
            else:
                asset_paths.append(AssetPath(path))
        
        # Resolve texture folder relative to base_path if provided
        texture_folder = data.get("texture_folder", "")
        if texture_folder and base_path and not os.path.isabs(texture_folder):
            texture_folder = os.path.join(base_path, texture_folder)
        
        # Use provided base_path or the one from data
        resolved_base_path = base_path if base_path else data.get("base_path", "")
        
        return cls(
            group_name=data.get("group_name", "Unnamed_Group"),
            asset_paths=asset_paths,
            texture_folder=texture_folder,
            base_path=resolved_base_path,
            material_names=data.get("material_names", [])
        )


@dataclass
class WorkflowData:
    """Represents the complete workflow data."""
    asset_scope: str = "ASSET"
    groups: List[AssetGroup] = field(default_factory=list)
    
    def add_group(self, group: AssetGroup) -> None:
        """Add a group to the workflow."""
        if group.is_valid():
            self.groups.append(group)
    
    def remove_group(self, group: AssetGroup) -> bool:
        """Remove a group from the workflow. Returns True if removed."""
        try:
            self.groups.remove(group)
            return True
        except ValueError:
            return False
    
    def get_valid_groups(self) -> List[AssetGroup]:
        """Get list of valid groups."""
        return [group for group in self.groups if group.is_valid()]
    
    def is_valid(self) -> bool:
        """Check if the workflow has at least one valid group."""
        return any(group.is_valid() for group in self.groups)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow data to a dictionary for serialization."""
        return {
            "asset_scope": self.asset_scope,
            "groups": [group.to_dict() for group in self.get_valid_groups()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_path: str = "") -> 'WorkflowData':
        """Create WorkflowData from a dictionary.
        
        Args:
            data: Dictionary containing workflow data.
            base_path: Base path for resolving relative paths.
        """
        return cls(
            asset_scope=data.get("asset_scope", "ASSET"),
            groups=[AssetGroup.from_dict(group_data, base_path) for group_data in data.get("groups", [])]
        )


@dataclass
class ProcessingState:
    """Represents the state of workflow processing."""
    is_processing: bool = False
    current_group_index: int = 0
    total_groups: int = 0
    current_group_name: str = ""
    progress_message: str = ""
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as a percentage."""
        if self.total_groups == 0:
            return 0.0
        return (self.current_group_index / self.total_groups) * 100.0
    
    @property
    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.current_group_index >= self.total_groups
    
    def reset(self) -> None:
        """Reset the processing state."""
        self.is_processing = False
        self.current_group_index = 0
        self.total_groups = 0
        self.current_group_name = ""
        self.progress_message = ""
    
    def start_processing(self, total_groups: int) -> None:
        """Start processing with the given number of groups."""
        self.is_processing = True
        self.current_group_index = 0
        self.total_groups = total_groups
        self.current_group_name = ""
        self.progress_message = ""
    
    def update_progress(self, group_index: int, group_name: str, message: str = "") -> None:
        """Update the processing progress."""
        self.current_group_index = group_index
        self.current_group_name = group_name
        self.progress_message = message
        
        if self.is_complete:
            self.is_processing = False