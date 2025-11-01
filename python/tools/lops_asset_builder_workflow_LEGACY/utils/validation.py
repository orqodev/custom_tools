"""Input validation utilities for LOPS Asset Builder Workflow."""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
# Handle both relative and absolute imports for flexibility
try:
    # Try relative imports first (when imported as part of package)
    from ..models.data_model import AssetGroup, WorkflowData, AssetPath
except ImportError:
    # Fall back to absolute imports (when run directly)
    from models.data_model import AssetGroup, WorkflowData, AssetPath


class PathValidator:
    """Validator for file and directory paths."""

    @staticmethod
    def is_valid_file_path(path: str) -> bool:
        """Check if a path is a valid file path format.

        Args:
            path: The path to validate.

        Returns:
            True if the path format is valid.
        """
        if not path or not isinstance(path, str):
            return False

        path = path.strip()
        if not path:
            return False

        # Check for characters that are truly invalid on most filesystems
        # Only reject characters that are actually problematic for file paths
        invalid_chars = ['<', '>', '|', '*', '?']
        if any(char in path for char in invalid_chars):
            return False

        # Remove the overly restrictive regex pattern that was rejecting valid filenames
        # Instead, just check that the path contains some valid characters and isn't empty
        # Allow common filename characters: letters, numbers, spaces, punctuation, path separators
        if len(path.strip()) == 0:
            return False

        # Check for null bytes which are truly invalid
        if '\x00' in path:
            return False

        return True

    @staticmethod
    def is_existing_file(path: str) -> bool:
        """Check if a path points to an existing file.

        Args:
            path: The path to check.

        Returns:
            True if the file exists.
        """
        return PathValidator.is_valid_file_path(path) and os.path.isfile(path)

    @staticmethod
    def is_existing_directory(path: str) -> bool:
        """Check if a path points to an existing directory.

        Args:
            path: The path to check.

        Returns:
            True if the directory exists.
        """
        return PathValidator.is_valid_file_path(path) and os.path.isdir(path)

    @staticmethod
    def is_geometry_file(path: str) -> bool:
        """Check if a path points to a geometry file.

        Args:
            path: The path to check.

        Returns:
            True if the file has a geometry extension.
        """
        if not PathValidator.is_valid_file_path(path):
            return False

        geometry_extensions = ['.bgeo', '.bgeo.sc', '.abc', '.obj', '.fbx']
        path_lower = path.lower()
        return any(path_lower.endswith(ext) for ext in geometry_extensions)

    @staticmethod
    def validate_path_list(paths: List[str]) -> Tuple[List[str], List[str]]:
        """Validate a list of paths and separate valid from invalid ones.

        Args:
            paths: List of paths to validate.

        Returns:
            Tuple of (valid_paths, invalid_paths).
        """
        valid_paths = []
        invalid_paths = []

        for path in paths:
            if PathValidator.is_valid_file_path(path):
                valid_paths.append(path)
            else:
                invalid_paths.append(path)

        return valid_paths, invalid_paths

    @staticmethod
    def get_path_validation_errors(path: str) -> List[str]:
        """Get detailed validation errors for a path.

        Args:
            path: The path to validate.

        Returns:
            List of validation error messages.
        """
        errors = []

        if not path:
            errors.append("Path is empty")
            return errors

        if not isinstance(path, str):
            errors.append("Path must be a string")
            return errors

        path = path.strip()
        if not path:
            errors.append("Path contains only whitespace")
            return errors

        # Check for invalid characters
        invalid_chars = ['<', '>', '|', '*', '?']
        found_invalid = [char for char in invalid_chars if char in path]
        if found_invalid:
            errors.append(f"Path contains invalid characters: {', '.join(found_invalid)}")

        # Check if file exists
        if not os.path.exists(path):
            errors.append("File or directory does not exist")
        elif os.path.isfile(path):
            # Check if it's a geometry file
            if not PathValidator.is_geometry_file(path):
                errors.append("File is not a supported geometry format")

        return errors


class GroupValidator:
    """Validator for asset groups."""

    @staticmethod
    def validate_group_name(name: str) -> Tuple[bool, List[str]]:
        """Validate a group name.

        Args:
            name: The group name to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        if not name:
            errors.append("Group name cannot be empty")
            return False, errors

        if not isinstance(name, str):
            errors.append("Group name must be a string")
            return False, errors

        name = name.strip()
        if not name:
            errors.append("Group name cannot be only whitespace")
            return False, errors

        # Check for invalid characters in group names
        if not re.match(r'^[\w\s\-_]+$', name):
            errors.append("Group name contains invalid characters (only letters, numbers, spaces, hyphens, and underscores allowed)")

        # Check length
        if len(name) > 100:
            errors.append("Group name is too long (maximum 100 characters)")

        return len(errors) == 0, errors

    @staticmethod
    def validate_asset_group(group: AssetGroup) -> Tuple[bool, List[str]]:
        """Validate an entire asset group.

        Args:
            group: The asset group to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Validate group name
        name_valid, name_errors = GroupValidator.validate_group_name(group.group_name)
        errors.extend(name_errors)

        # Validate asset paths
        if not group.asset_paths:
            errors.append("Group must have at least one asset path")
        else:
            for i, asset_path in enumerate(group.asset_paths):
                if isinstance(asset_path, AssetPath):
                    path_errors = PathValidator.get_path_validation_errors(asset_path.path)
                    if path_errors:
                        errors.extend([f"Asset path {i+1}: {error}" for error in path_errors])
                else:
                    errors.append(f"Asset path {i+1}: Invalid asset path object")

        # Validate texture folder if provided
        if group.texture_folder:
            if not PathValidator.is_valid_file_path(group.texture_folder):
                errors.append("Invalid texture folder path format")
            elif not os.path.isdir(group.texture_folder):
                errors.append("Texture folder does not exist")

        return len(errors) == 0, errors

    @staticmethod
    def validate_group_uniqueness(groups: List[AssetGroup]) -> Tuple[bool, List[str]]:
        """Validate that group names are unique.

        Args:
            groups: List of asset groups to check.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []
        seen_names = set()

        for i, group in enumerate(groups):
            name = group.group_name.strip().lower()
            if name in seen_names:
                errors.append(f"Duplicate group name: '{group.group_name}' (group {i+1})")
            else:
                seen_names.add(name)

        return len(errors) == 0, errors


class WorkflowValidator:
    """Validator for complete workflow data."""

    @staticmethod
    def validate_asset_scope(scope: str) -> Tuple[bool, List[str]]:
        """Validate asset scope.

        Args:
            scope: The asset scope to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        if not scope:
            errors.append("Asset scope cannot be empty")
            return False, errors

        if not isinstance(scope, str):
            errors.append("Asset scope must be a string")
            return False, errors

        scope = scope.strip()
        if not scope:
            errors.append("Asset scope cannot be only whitespace")
            return False, errors

        # Check for valid scope format (alphanumeric, underscores, hyphens)
        if not re.match(r'^[\w\-]+$', scope):
            errors.append("Asset scope contains invalid characters (only letters, numbers, underscores, and hyphens allowed)")

        # Check length
        if len(scope) > 50:
            errors.append("Asset scope is too long (maximum 50 characters)")

        return len(errors) == 0, errors

    @staticmethod
    def validate_workflow_data(workflow_data: WorkflowData) -> Tuple[bool, List[str]]:
        """Validate complete workflow data.

        Args:
            workflow_data: The workflow data to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Validate asset scope
        scope_valid, scope_errors = WorkflowValidator.validate_asset_scope(workflow_data.asset_scope)
        errors.extend(scope_errors)

        # Validate groups
        if not workflow_data.groups:
            errors.append("Workflow must have at least one asset group")
        else:
            # Validate each group
            for i, group in enumerate(workflow_data.groups):
                group_valid, group_errors = GroupValidator.validate_asset_group(group)
                if group_errors:
                    errors.extend([f"Group {i+1} ({group.group_name}): {error}" for error in group_errors])

            # Validate group name uniqueness
            uniqueness_valid, uniqueness_errors = GroupValidator.validate_group_uniqueness(workflow_data.groups)
            errors.extend(uniqueness_errors)

        return len(errors) == 0, errors


class TemplateValidator:
    """Validator for template data structures."""

    @staticmethod
    def validate_template_structure(template_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate the structure of template data.

        Args:
            template_data: The template data to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Check root structure
        if not isinstance(template_data, dict):
            errors.append("Template root must be a dictionary")
            return False, errors

        # Check required keys
        if 'groups' not in template_data:
            errors.append("Template must contain 'groups' key")
            return False, errors

        if not isinstance(template_data['groups'], list):
            errors.append("Template 'groups' must be a list")
            return False, errors

        # Validate asset scope if present
        if 'asset_scope' in template_data:
            scope_valid, scope_errors = WorkflowValidator.validate_asset_scope(template_data['asset_scope'])
            errors.extend(scope_errors)

        # Validate each group
        for group_index, group_data in enumerate(template_data['groups']):
            group_errors = TemplateValidator._validate_group_data(group_data, group_index + 1)
            errors.extend(group_errors)

        return len(errors) == 0, errors

    @staticmethod
    def _validate_group_data(group_data: Any, group_index: int) -> List[str]:
        """Validate individual group data in template.

        Args:
            group_data: The group data to validate.
            group_index: The group index for error messages.

        Returns:
            List of error messages.
        """
        errors = []

        if not isinstance(group_data, dict):
            errors.append(f"Group {group_index} data must be a dictionary")
            return errors

        # Validate group name
        if 'group_name' in group_data:
            name_valid, name_errors = GroupValidator.validate_group_name(group_data['group_name'])
            if name_errors:
                errors.extend([f"Group {group_index}: {error}" for error in name_errors])

        # Validate asset paths
        if 'asset_paths' in group_data:
            paths = group_data['asset_paths']
            if not isinstance(paths, list):
                errors.append(f"Group {group_index} 'asset_paths' must be a list")
            else:
                for path_index, path in enumerate(paths):
                    if not isinstance(path, str):
                        errors.append(f"Group {group_index} path at index {path_index + 1} must be a string")
                    else:
                        path_errors = PathValidator.get_path_validation_errors(path)
                        if path_errors:
                            errors.extend([f"Group {group_index} path {path_index + 1}: {error}" for error in path_errors])

        # Validate texture folder if present
        if 'texture_folder' in group_data and group_data['texture_folder']:
            texture_folder = group_data['texture_folder']
            if not isinstance(texture_folder, str):
                errors.append(f"Group {group_index} texture_folder must be a string")
            elif not PathValidator.is_valid_file_path(texture_folder):
                errors.append(f"Group {group_index} texture_folder has invalid format")

        return errors


class UIValidator:
    """Validator for UI input data."""

    @staticmethod
    def validate_dialog_input(asset_scope: str, groups_data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate input from the main dialog.

        Args:
            asset_scope: The asset scope string.
            groups_data: List of group data dictionaries.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Validate asset scope
        scope_valid, scope_errors = WorkflowValidator.validate_asset_scope(asset_scope)
        errors.extend(scope_errors)

        # Validate groups data
        if not groups_data:
            errors.append("At least one asset group is required")
        else:
            for i, group_data in enumerate(groups_data):
                group_errors = TemplateValidator._validate_group_data(group_data, i + 1)
                errors.extend(group_errors)

        return len(errors) == 0, errors

    @staticmethod
    def validate_processing_readiness(workflow_data: WorkflowData) -> Tuple[bool, List[str]]:
        """Validate that workflow data is ready for processing.

        Args:
            workflow_data: The workflow data to validate.

        Returns:
            Tuple of (is_ready, error_messages).
        """
        errors = []

        # Basic validation
        basic_valid, basic_errors = WorkflowValidator.validate_workflow_data(workflow_data)
        errors.extend(basic_errors)

        # Additional processing-specific validation
        valid_groups = workflow_data.get_valid_groups()
        if not valid_groups:
            errors.append("No valid groups found for processing")

        # Check that all groups have at least one existing file
        for i, group in enumerate(valid_groups):
            existing_files = [ap.path for ap in group.asset_paths if os.path.exists(ap.path)]
            if not existing_files:
                errors.append(f"Group {i+1} ({group.group_name}) has no existing asset files")

        return len(errors) == 0, errors


class ValidationUtils:
    """Utility functions for validation operations."""

    @staticmethod
    def format_validation_errors(errors: List[str], title: str = "Validation Errors") -> str:
        """Format validation errors for display.

        Args:
            errors: List of error messages.
            title: Title for the error list.

        Returns:
            Formatted error string.
        """
        if not errors:
            return ""

        formatted = f"{title}:\n"
        for i, error in enumerate(errors, 1):
            formatted += f"{i}. {error}\n"

        return formatted.strip()

    @staticmethod
    def get_validation_summary(workflow_data: WorkflowData) -> Dict[str, Any]:
        """Get a comprehensive validation summary.

        Args:
            workflow_data: The workflow data to analyze.

        Returns:
            Dictionary with validation summary information.
        """
        is_valid, errors = WorkflowValidator.validate_workflow_data(workflow_data)
        is_ready, readiness_errors = UIValidator.validate_processing_readiness(workflow_data)

        valid_groups = workflow_data.get_valid_groups()
        total_assets = sum(len(group.get_valid_paths()) for group in valid_groups)

        return {
            "is_valid": is_valid,
            "is_ready_for_processing": is_ready,
            "validation_errors": errors,
            "readiness_errors": readiness_errors,
            "total_groups": len(workflow_data.groups),
            "valid_groups": len(valid_groups),
            "total_assets": total_assets,
            "groups_with_issues": len([g for g in workflow_data.groups if not g.is_valid()])
        }
