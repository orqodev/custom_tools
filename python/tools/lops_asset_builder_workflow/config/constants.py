"""Configuration constants for LOPS Asset Builder Workflow."""

# Import HoudiniTheme for centralized styling constants
try:
    from ..ui.houdini_theme import HoudiniTheme
except ImportError:
    try:
        from ui.houdini_theme import HoudiniTheme
    except ImportError:
        # Fallback HoudiniTheme for testing environments
        class HoudiniTheme:
            COLORS = {
                "background": "#000000", "text": "#ffffff", "accent_primary": "#ffd700",
                "accent_secondary": "#ffed4e", "accent_dark": "#e6c200", "success": "#4CAF50",
                "error": "#ff4444", "error_light": "#ff6666", "error_dark": "#cc0000", 
                "warning": "#ff8800", "border": "#333333", "border_light": "#666666",
                "border_focus": "#ffd700", "hover": "#222222", "hover_light": "#444444",
                "disabled": "#666666", "disabled_text": "#999999", "text_muted": "#888888"
            }
            FONTS = {"default_size": 12, "small_size": 10, "large_size": 14, "header_size": 16, "monospace": "'Consolas', 'Monaco', monospace"}
            LAYOUT = {
                "border_radius": 3, "border_radius_large": 4, "padding_input": "5px", "padding_log": "10px", "padding_medium": "8px 16px",
                "margin_label": "8px 0px", "margin_subheader": "4px 0px", "margin_zero": "0px", "progress_bar_height": "40px",
                "progress_bar_height_small": "18px", "min_button_height": "10px", "margin_small": "4px", "margin_medium": "7px"
            }

# Material CSS processor removed - using built-in Houdini theming instead
MATERIAL_CSS_AVAILABLE = False

# UI Constants
DEFAULT_DIALOG_WIDTH = 600
DEFAULT_DIALOG_HEIGHT = 400
PROCESSING_DIALOG_HEIGHT = 650
MAX_SCROLL_AREA_HEIGHT = 1000
GROUP_WIDGET_HEIGHT = 600  # Double height to measure what 2 GroupWidgets are

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

# UI Styling - Use centralized HoudiniTheme colors
# Direct reference to HoudiniTheme.COLORS to avoid duplication
THEME_COLORS = HoudiniTheme.COLORS

# Input Field Styles
INPUT_FIELD_STYLE = f"""
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text"]};
        border: 1px solid {THEME_COLORS["border"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_input"]};
        font-size: {HoudiniTheme.FONTS["default_size"]}px;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {THEME_COLORS["border_focus"]};
    }}
"""

# Log Display Style
LOG_DISPLAY_STYLE = f"""
    QTextEdit {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text"]};
        border: 1px solid {THEME_COLORS["border"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_log"]};
        font-family: {HoudiniTheme.FONTS["monospace"]};
        font-size: {HoudiniTheme.FONTS["large_size"]}px;
    }}
"""

# Dialog Styles
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text"]};
    }}
    QLabel {{
        color: {THEME_COLORS["text"]};
    }}
"""

# Button Styles
PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {THEME_COLORS["accent_primary"]};
        color: {THEME_COLORS["background"]};
        font-weight: bold;
        border: 1px solid {THEME_COLORS["accent_primary"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_medium"]};
        min-height: {HoudiniTheme.LAYOUT["min_button_height"]};
    }}
    QPushButton:hover {{
        background-color: {THEME_COLORS["accent_secondary"]};
        border: 1px solid {THEME_COLORS["accent_secondary"]};
    }}
    QPushButton:pressed {{
        background-color: {THEME_COLORS["accent_dark"]};
        border: 1px solid {THEME_COLORS["accent_dark"]};
    }}
    QPushButton:disabled {{
        background-color: {THEME_COLORS["disabled"]};
        color: {THEME_COLORS["disabled_text"]};
        border: 1px solid {THEME_COLORS["disabled"]};
    }}
"""

SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {THEME_COLORS["border"]};
        color: {THEME_COLORS["text"]};
        font-weight: bold;
        border: 1px solid {THEME_COLORS["border_light"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_medium"]};
        min-height: {HoudiniTheme.LAYOUT["min_button_height"]};
    }}
    QPushButton:hover {{
        background-color: {THEME_COLORS["hover_light"]};
        border: 1px solid {THEME_COLORS["text_muted"]};
    }}
    QPushButton:pressed {{
        background-color: {THEME_COLORS["hover"]};
        border: 1px solid {THEME_COLORS["hover_light"]};
    }}
"""

DELETE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {THEME_COLORS["error"]};
        color: {THEME_COLORS["text"]};
        font-weight: bold;
        border: 1px solid {THEME_COLORS["error"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_medium"]};
        min-height: {HoudiniTheme.LAYOUT["min_button_height"]};
    }}
    QPushButton:hover {{
        background-color: {THEME_COLORS["error_light"]};
        border: 1px solid {THEME_COLORS["error_light"]};
    }}
    QPushButton:pressed {{
        background-color: {THEME_COLORS["error_dark"]};
        border: 1px solid {THEME_COLORS["error_dark"]};
    }}
"""

# Progress Bar Style
PROGRESS_BAR_STYLE = f"""
    QProgressBar {{
        background-color: {THEME_COLORS["border"]};
        color: {THEME_COLORS["text"]};
        border: 1px solid {THEME_COLORS["border_light"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
        text-align: center;
        font-weight: bold;
        height: {HoudiniTheme.LAYOUT["progress_bar_height"]};
    }}
    QProgressBar::chunk {{
        background-color: {THEME_COLORS["accent_primary"]};
        border-radius: 2px;
    }}
"""

# Validation Error Styles
VALIDATION_ERROR_STYLE = f"""
    QTextEdit {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text"]};
        border: 1px solid {THEME_COLORS["error"]};
        border-radius: {HoudiniTheme.LAYOUT["border_radius_large"]}px;
        padding: {HoudiniTheme.LAYOUT["padding_log"]};
        font-family: {HoudiniTheme.FONTS["monospace"]};
        font-size: {HoudiniTheme.FONTS["large_size"]}px;
    }}
"""

# Status Label Styles
STATUS_LABEL_STYLES = {
    "success": f"color: {THEME_COLORS['success']}; font-weight: bold;",
    "error": f"color: {THEME_COLORS['error']}; font-weight: bold;",
    "warning": f"color: {THEME_COLORS['warning']}; font-weight: bold;",
    "info": f"color: {THEME_COLORS['text']}; font-style: italic;",
    "secondary": f"color: {THEME_COLORS['accent_primary']}; font-weight: bold;",
}

# Header Styles
HEADER_LABEL_STYLE = f"font-size: {HoudiniTheme.FONTS['header_size']}px; font-weight: bold; color: {THEME_COLORS['accent_primary']}; margin-bottom: {HoudiniTheme.LAYOUT['margin_medium']};"
SUBHEADER_LABEL_STYLE = f"font-size: {HoudiniTheme.FONTS['large_size']}px; font-weight: bold; color: {THEME_COLORS['text']}; margin: {HoudiniTheme.LAYOUT['margin_subheader']};"

# Material Design CSS Styles - Using built-in Houdini theming instead
MATERIAL_FULL_CSS = ""
MATERIAL_BUTTON_STYLE = PRIMARY_BUTTON_STYLE
MATERIAL_INPUT_STYLE = INPUT_FIELD_STYLE
MATERIAL_DIALOG_STYLE = DIALOG_STYLE

# Layout Constants
WIDGET_MARGINS = (3, 2, 3, 2)          # Reduced from (5, 3, 5, 3)
WIDGET_SPACING = 6                      # Reduced from 8
PATH_LAYOUT_SPACING = 2                 # Reduced from 3
MINIMUM_PATH_EDIT_WIDTH = 150           # Reduced from 200
BROWSE_BUTTON_WIDTH = (50, 70)          # Reduced from (80, 120)
DELETE_BUTTON_WIDTH = (20, 30)          # Reduced from (30, 40)

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
