"""
Comprehensive Houdini Theme System for LOPS Asset Builder Workflow.

This module provides a centralized theming system that maintains consistent
Houdini styling across the entire application.
"""

from typing import Dict, Any
from PySide6 import QtWidgets as QtW, QtCore, QtGui


class HoudiniTheme:
    """Centralized theme system for consistent Houdini styling."""
    
    # Core Houdini Color Palette
    COLORS = {
        # Primary colors
        "background": "#000000",           # Black background
        "text": "#ffffff",                # White text
        "text_secondary": "#e0e0e0",      # Light gray text
        "text_muted": "#888888",          # Muted gray text
        
        # Accent colors
        "accent_primary": "#40E0D0",       # Turquoise
        "accent_secondary": "#7FFFD4",     # Light turquoise hover (Aquamarine)
        "accent_dark": "#20B2AA",          # Dark turquoise pressed (Light Sea Green)
        
        # Status colors
        "success": "#4CAF50",              # Consistent green
        "success_light": "#66BB6A",        # Light green hover
        "error": "#ff4444",                # Red error
        "error_light": "#ff6666",          # Light red hover
        "error_dark": "#cc0000",           # Dark red pressed
        "warning": "#ff8800",              # Orange warning
        "info": "#2196F3",                 # Blue info
        
        # UI element colors
        "border": "#333333",               # Dark gray borders
        "border_light": "#666666",         # Light gray borders
        "border_focus": "#40E0D0",         # Turquoise focus border
        "hover": "#222222",                # Dark hover background
        "hover_light": "#444444",          # Light hover background
        "disabled": "#666666",             # Disabled background
        "disabled_text": "#999999",       # Disabled text
        
        # Separator colors
        "separator": "#bdc3c7",            # Light separator
        "separator_dark": "#333333",       # Dark separator
    }
    
    # Typography
    FONTS = {
        "default_size": 12,
        "small_size": 10,
        "tiny_size": 9,                    # Added for very small buttons
        "large_size": 14,
        "header_size": 16,
        "title_size": 18,
        "monospace": "'Consolas', 'Monaco', monospace",
    }
    
    # Layout constants
    LAYOUT = {
        "border_radius": 3,
        "border_radius_large": 4,
        "padding_small": "1px 4px",        # Reduced from "2px 6px"
        "padding_medium": "2px 8px",       # Reduced from "4px 12px"
        "padding_large": "3px 10px",       # Reduced from "6px 16px"
        "padding_input": "3px",            # Reduced from "5px"
        "padding_log": "8px",              # Reduced from "10px"
        "margin_small": "3px",             # Reduced from "5px"
        "margin_medium": "6px",            # Reduced from "10px"
        "margin_label": "6px 0px",         # Reduced from "10px 0px"
        "margin_subheader": "3px 0px",     # Reduced from "5px 0px"
        "margin_zero": "0px",
        "spacing": 6,                      # Reduced from 8
        "widget_margins": (3, 2, 3, 2),   # Reduced from (5, 3, 5, 3)
        "progress_bar_height": "16px",     # Reduced from "20px"
        "progress_bar_height_small": "12px", # Reduced from "14px"
        "min_button_height": "6px",        # Reduced from "10px"
    }
    
    @classmethod
    def get_dialog_style(cls) -> str:
        """Get the base dialog stylesheet."""
        return f"""
            QDialog {{
                background-color: {cls.COLORS["background"]};
                color: {cls.COLORS["text"]};
            }}
            QLabel {{
                color: {cls.COLORS["text"]};
            }}
            QGroupBox {{
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {cls.COLORS["accent_primary"]};
                font-weight: bold;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """
    
    @classmethod
    def get_input_field_style(cls) -> str:
        """Get input field stylesheet."""
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {cls.COLORS["background"]};
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                padding: 5px;
                font-size: {cls.FONTS["default_size"]}px;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {cls.COLORS["border_focus"]};
            }}
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {cls.COLORS["disabled"]};
                color: {cls.COLORS["disabled_text"]};
                border: 1px solid {cls.COLORS["disabled"]};
            }}
        """
    
    @classmethod
    def get_primary_button_style(cls) -> str:
        """Get primary button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS["accent_primary"]};
                color: {cls.COLORS["background"]};
                font-weight: bold;
                font-size: {cls.FONTS["small_size"]}px;
                border: 1px solid {cls.COLORS["accent_primary"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                padding: {cls.LAYOUT["padding_medium"]};
                min-height: {cls.LAYOUT["min_button_height"]};
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS["accent_secondary"]};
                border: 1px solid {cls.COLORS["accent_secondary"]};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS["accent_dark"]};
                border: 1px solid {cls.COLORS["accent_dark"]};
            }}
            QPushButton:disabled {{
                background-color: {cls.COLORS["disabled"]};
                color: {cls.COLORS["disabled_text"]};
                border: 1px solid {cls.COLORS["disabled"]};
            }}
        """
    
    @classmethod
    def get_secondary_button_style(cls) -> str:
        """Get secondary button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS["border"]};
                color: {cls.COLORS["text"]};
                font-weight: bold;
                font-size: {cls.FONTS["small_size"]}px;
                border: 1px solid {cls.COLORS["border_light"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                padding: {cls.LAYOUT["padding_small"]};
                min-height: {cls.LAYOUT["min_button_height"]};
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS["hover_light"]};
                border: 1px solid {cls.COLORS["border_light"]};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS["hover"]};
                border: 1px solid {cls.COLORS["border"]};
            }}
            QPushButton:disabled {{
                background-color: {cls.COLORS["disabled"]};
                color: {cls.COLORS["disabled_text"]};
                border: 1px solid {cls.COLORS["disabled"]};
            }}
        """
    
    @classmethod
    def get_danger_button_style(cls) -> str:
        """Get danger/delete button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS["error"]};
                color: {cls.COLORS["text"]};
                font-weight: bold;
                border: 1px solid {cls.COLORS["error"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                padding: {cls.LAYOUT["padding_small"]};
                min-height: 10px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS["error_light"]};
                border: 1px solid {cls.COLORS["error_light"]};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS["error_dark"]};
                border: 1px solid {cls.COLORS["error_dark"]};
            }}
        """
    
    @classmethod
    def get_progress_bar_style(cls) -> str:
        """Get progress bar stylesheet."""
        return f"""
            QProgressBar {{
                background-color: {cls.COLORS["border"]};
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border_light"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                text-align: center;
                font-weight: bold;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {cls.COLORS["accent_primary"]};
                border-radius: 2px;
            }}
        """
    
    @classmethod
    def get_log_display_style(cls) -> str:
        """Get log display stylesheet."""
        return f"""
            QTextEdit {{
                background-color: {cls.COLORS["background"]};
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: {cls.LAYOUT["border_radius"]}px;
                padding: 10px;
                font-family: {cls.FONTS["monospace"]};
                font-size: {cls.FONTS["large_size"]}px;
            }}
        """
    
    @classmethod
    def get_validation_error_style(cls) -> str:
        """Get validation error display stylesheet."""
        return f"""
            QTextEdit {{
                background-color: {cls.COLORS["background"]};
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["error"]};
                border-radius: {cls.LAYOUT["border_radius_large"]}px;
                padding: 10px;
                font-family: {cls.FONTS["monospace"]};
                font-size: {cls.FONTS["large_size"]}px;
            }}
        """
    
    @classmethod
    def get_header_style(cls, size: str = "medium") -> str:
        """Get header label stylesheet."""
        size_map = {
            "small": cls.FONTS["large_size"],
            "medium": cls.FONTS["header_size"],
            "large": cls.FONTS["title_size"]
        }
        font_size = size_map.get(size, cls.FONTS["header_size"])
        
        return f"""
            font-size: {font_size}px;
            font-weight: bold;
            color: {cls.COLORS["accent_primary"]};
            margin-bottom: 10px;
        """
    
    @classmethod
    def get_subheader_style(cls) -> str:
        """Get subheader label stylesheet."""
        return f"""
            font-size: {cls.FONTS["large_size"]}px;
            font-weight: bold;
            color: {cls.COLORS["text"]};
            margin: 5px 0px;
        """
    
    @classmethod
    def get_status_style(cls, status: str) -> str:
        """Get status label stylesheet based on status type."""
        status_colors = {
            "success": cls.COLORS["success"],
            "error": cls.COLORS["error"],
            "warning": cls.COLORS["warning"],
            "info": cls.COLORS["text"],
            "secondary": cls.COLORS["accent_primary"],
            "muted": cls.COLORS["text_muted"],
        }
        
        color = status_colors.get(status, cls.COLORS["text"])
        style = "font-weight: bold;" if status != "info" else "font-style: italic;"
        
        return f"color: {color}; {style}"
    
    @classmethod
    def get_separator_style(cls, dark: bool = False) -> str:
        """Get separator stylesheet."""
        color = cls.COLORS["separator_dark"] if dark else cls.COLORS["separator"]
        return f"color: {color}; margin: 0px; max-height: 1px;"
    
    @classmethod
    def apply_theme_to_widget(cls, widget: QtW.QWidget, theme_type: str = "dialog"):
        """Apply theme to a widget based on its type."""
        theme_map = {
            "dialog": cls.get_dialog_style(),
            "input": cls.get_input_field_style(),
            "primary_button": cls.get_primary_button_style(),
            "secondary_button": cls.get_secondary_button_style(),
            "danger_button": cls.get_danger_button_style(),
            "progress": cls.get_progress_bar_style(),
            "log": cls.get_log_display_style(),
            "validation_error": cls.get_validation_error_style(),
        }
        
        if theme_type in theme_map:
            widget.setStyleSheet(theme_map[theme_type])
    
    @classmethod
    def create_themed_label(cls, text: str, style_type: str = "normal") -> QtW.QLabel:
        """Create a themed label with consistent styling."""
        label = QtW.QLabel(text)
        
        if style_type == "header":
            label.setStyleSheet(cls.get_header_style())
        elif style_type == "subheader":
            label.setStyleSheet(cls.get_subheader_style())
        elif style_type in ["success", "error", "warning", "info", "secondary", "muted"]:
            label.setStyleSheet(cls.get_status_style(style_type))
        else:
            label.setStyleSheet(f"color: {cls.COLORS['text']};")
        
        return label
    
    @classmethod
    def create_themed_button(cls, text: str, button_type: str = "primary") -> QtW.QPushButton:
        """Create a themed button with consistent styling."""
        button = QtW.QPushButton(text)
        cls.apply_theme_to_widget(button, f"{button_type}_button")
        return button
    
    @classmethod
    def create_themed_input(cls, placeholder: str = "") -> QtW.QLineEdit:
        """Create a themed input field with consistent styling."""
        input_field = QtW.QLineEdit()
        if placeholder:
            input_field.setPlaceholderText(placeholder)
        cls.apply_theme_to_widget(input_field, "input")
        return input_field


class HoudiniStylesheet:
    """Complete stylesheet definitions for the Houdini theme."""
    
    @staticmethod
    def get_complete_application_stylesheet() -> str:
        """Get the complete application stylesheet for consistent theming."""
        return f"""
            /* Main Application Theme */
            QMainWindow, QDialog, QWidget {{
                background-color: {HoudiniTheme.COLORS["background"]};
                color: {HoudiniTheme.COLORS["text"]};
                font-size: {HoudiniTheme.FONTS["default_size"]}px;
            }}
            
            /* Labels */
            QLabel {{
                color: {HoudiniTheme.COLORS["text"]};
            }}
            
            /* Input Fields */
            {HoudiniTheme.get_input_field_style()}
            
            /* Buttons */
            QPushButton {{
                background-color: {HoudiniTheme.COLORS["accent_primary"]};
                color: {HoudiniTheme.COLORS["background"]};
                font-weight: bold;
                border: 1px solid {HoudiniTheme.COLORS["accent_primary"]};
                border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
                padding: {HoudiniTheme.LAYOUT["padding_medium"]};
                min-height: 10px;
            }}
            QPushButton:hover {{
                background-color: {HoudiniTheme.COLORS["accent_secondary"]};
            }}
            QPushButton:pressed {{
                background-color: {HoudiniTheme.COLORS["accent_dark"]};
            }}
            QPushButton:disabled {{
                background-color: {HoudiniTheme.COLORS["disabled"]};
                color: {HoudiniTheme.COLORS["disabled_text"]};
            }}
            
            /* Progress Bars */
            {HoudiniTheme.get_progress_bar_style()}
            
            /* Group Boxes */
            QGroupBox {{
                color: {HoudiniTheme.COLORS["text"]};
                border: 1px solid {HoudiniTheme.COLORS["border"]};
                border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {HoudiniTheme.COLORS["accent_primary"]};
                font-weight: bold;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            /* Scroll Areas */
            QScrollArea {{
                background-color: {HoudiniTheme.COLORS["background"]};
                border: 1px solid {HoudiniTheme.COLORS["border"]};
                border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
            }}
            
            /* Separators */
            QFrame[frameShape="4"] {{
                color: {HoudiniTheme.COLORS["separator"]};
            }}
            
            /* Combo Boxes */
            QComboBox {{
                background-color: {HoudiniTheme.COLORS["background"]};
                color: {HoudiniTheme.COLORS["text"]};
                border: 1px solid {HoudiniTheme.COLORS["border"]};
                border-radius: {HoudiniTheme.LAYOUT["border_radius"]}px;
                padding: 5px;
            }}
            QComboBox:focus {{
                border: 2px solid {HoudiniTheme.COLORS["border_focus"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {HoudiniTheme.COLORS["text"]};
            }}
            
            /* Check Boxes */
            QCheckBox {{
                color: {HoudiniTheme.COLORS["text"]};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {HoudiniTheme.COLORS["border"]};
                border-radius: 2px;
                background-color: {HoudiniTheme.COLORS["background"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {HoudiniTheme.COLORS["accent_primary"]};
                border: 1px solid {HoudiniTheme.COLORS["accent_primary"]};
            }}
            
            /* Radio Buttons */
            QRadioButton {{
                color: {HoudiniTheme.COLORS["text"]};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {HoudiniTheme.COLORS["border"]};
                border-radius: 8px;
                background-color: {HoudiniTheme.COLORS["background"]};
            }}
            QRadioButton::indicator:checked {{
                background-color: {HoudiniTheme.COLORS["accent_primary"]};
                border: 1px solid {HoudiniTheme.COLORS["accent_primary"]};
            }}
        """