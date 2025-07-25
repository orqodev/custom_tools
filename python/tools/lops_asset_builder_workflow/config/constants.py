"""Configuration constants for LOPS Asset Builder Workflow."""

# UI Constants
DEFAULT_DIALOG_WIDTH = 600
DEFAULT_DIALOG_HEIGHT = 400
PROCESSING_DIALOG_HEIGHT = 650
MAX_SCROLL_AREA_HEIGHT = 250

# File Extensions
GEOMETRY_FILE_EXTENSIONS = "Geometry Files (*.bgeo *.bgeo.sc *.abc *.obj *.fbx);;All Files (*)"
JSON_FILE_EXTENSIONS = "JSON Files (*.json);;All Files (*)"

# Default Values
DEFAULT_ASSET_SCOPE = "ASSET"
DEFAULT_GROUP_NAME_PREFIX = "group_"
DEFAULT_PLACEHOLDER_TEXT = {
    "file_path": "File path...",
    "group_name": "group_N",
    "materials_folder": "Select materials folder...",
}

# UI Styling
DELETE_BUTTON_STYLE = """
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
"""

# Layout Constants
WIDGET_MARGINS = (5, 3, 5, 3)
WIDGET_SPACING = 8
PATH_LAYOUT_SPACING = 3
MINIMUM_PATH_EDIT_WIDTH = 200
BROWSE_BUTTON_WIDTH = (80, 120)
DELETE_BUTTON_WIDTH = (30, 40)

# Progress and Logging
LOG_SCROLL_THRESHOLD = 10
PROGRESS_BAR_FORMAT = "{current}/{total} - {name}"

# Node Creation Constants
DEFAULT_NODE_SPACING = 2.0
CONVEX_HULL_TOLERANCE = 0.001

# Material Constants
MATERIAL_LIB_NAME = "MaterialLibrary"
MTLX_TEMPLATE_PREFIX = "mtlx_"

# Error Messages
ERROR_MESSAGES = {
    "invalid_template_root": "Invalid template format: root must be a dictionary",
    "invalid_groups_format": "Invalid template format: 'groups' must be a list",
    "invalid_group_data": "Invalid template format: group {index} data must be a dictionary",
    "invalid_asset_paths": "Invalid template format: group {index} 'asset_paths' must be a list",
    "invalid_path_type": "Invalid template format: group {index} path at index {path_index} must be a string",
}

# Success Messages
SUCCESS_MESSAGES = {
    "template_saved": "Template saved successfully to:\n{path}",
    "template_loaded": "Template loaded successfully from:\n{path}",
    "workflow_completed": "✓ Workflow completed successfully!",
}
