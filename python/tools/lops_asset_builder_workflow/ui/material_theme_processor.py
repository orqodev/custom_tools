"""
Material CSS Template Processor for LOPS Asset Builder Workflow.

This module integrates the qt_material CSS template system with our existing
HoudiniTheme color system, allowing us to use Material Design styling while
maintaining our custom color palette.
"""

import os
import sys
import jinja2
from typing import Dict, Any, Optional

# Handle both relative and absolute imports for flexibility
try:
    from .houdini_theme import HoudiniTheme
except ImportError:
    try:
        from houdini_theme import HoudiniTheme
    except ImportError:
        # Try importing from ui module
        try:
            from ui.houdini_theme import HoudiniTheme
        except ImportError:
            # Create a minimal fallback HoudiniTheme for testing
            class HoudiniTheme:
                COLORS = {
                    'accent_primary': '#ffd700',
                    'accent_secondary': '#ffed4e', 
                    'background': '#000000',
                    'text': '#ffffff',
                    'hover_light': '#444444',
                    'border_light': '#666666',
                    'error': '#ff4444',
                    'warning': '#ff8800',
                    'success': '#4CAF50',
                }
                FONTS = {
                    'default_size': 12,
                }


class MaterialThemeProcessor:
    """Processes qt_material CSS templates with our custom theme colors."""
    
    def __init__(self):
        """Initialize the material theme processor."""
        self.template_path = self._get_template_path()
        self.template_vars = self._create_template_variables()
        
    def _get_template_path(self) -> str:
        """Get the path to the material.css.template file."""
        # Try multiple possible paths to find the template
        possible_paths = [
            # Path from current file location
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'qt-material', 'qt_material', 'material.css.template'),
            # Path from project root
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'qt-material', 'qt_material', 'material.css.template'),
            # Direct path from houdini20.5 directory
            '/home/tushita/houdini20.5/custom_tools/qt-material/qt_material/material.css.template',
            # Relative path from current working directory
            os.path.join(os.getcwd(), 'custom_tools', 'qt-material', 'qt_material', 'material.css.template'),
        ]
        
        for template_path in possible_paths:
            template_path = os.path.abspath(template_path)
            if os.path.exists(template_path):
                return template_path
        
        # If none found, return the most likely path for error reporting
        return os.path.abspath(possible_paths[0])
    
    def _create_template_variables(self) -> Dict[str, Any]:
        """Map our HoudiniTheme colors to material template variables."""
        return {
            # Primary Material Design colors mapped from our theme
            'primaryColor': HoudiniTheme.COLORS['accent_primary'],           # #40E0D0 (Turquoise)
            'primaryLightColor': HoudiniTheme.COLORS['accent_secondary'],    # #7FFFD4 (Light turquoise)
            'primaryTextColor': HoudiniTheme.COLORS['background'],           # #000000 (Black text on turquoise)
            
            # Secondary colors (backgrounds and surfaces)
            'secondaryColor': HoudiniTheme.COLORS['hover_light'],            # #444444 (Medium gray)
            'secondaryLightColor': HoudiniTheme.COLORS['border_light'],      # #666666 (Light gray)
            'secondaryDarkColor': HoudiniTheme.COLORS['background'],         # #000000 (Black background)
            'secondaryTextColor': HoudiniTheme.COLORS['text'],               # #ffffff (White text)
            
            # Status colors
            'danger': HoudiniTheme.COLORS['error'],                          # #ff4444 (Red)
            'warning': HoudiniTheme.COLORS['warning'],                       # #ff8800 (Orange)
            'success': HoudiniTheme.COLORS['success'],                       # #4CAF50 (Green)
            
            # Typography
            'font_family': 'Roboto, Arial, sans-serif',
            'font_size': HoudiniTheme.FONTS['default_size'],                 # 12
            'line_height': HoudiniTheme.FONTS['default_size'] + 8,           # 20
            
            # Material Design density scale
            'density_scale': '0',                                            # Standard density
            
            # Button shape
            'button_shape': 'default',
            
            # Platform detection
            'linux': sys.platform.startswith('linux'),
            'windows': sys.platform.startswith('win'),
            'darwin': sys.platform.startswith('darwin'),
            
            # Qt framework detection
            'pyqt5': 'PyQt5' in sys.modules,
            'pyqt6': 'PyQt6' in sys.modules,
            'pyside2': 'PySide2' in sys.modules,
            'pyside6': 'PySide6' in sys.modules,
        }
    
    def _opacity_filter(self, color: str, opacity: float = 0.5) -> str:
        """Convert hex color to rgba with opacity (Jinja2 filter)."""
        if not color.startswith('#') or len(color) != 7:
            return color
            
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f'rgba({r}, {g}, {b}, {opacity})'
        except ValueError:
            return color
    
    def _density_filter(self, value, density_scale, border=0, scale=1, density_interval=4, min_=4):
        """Apply Material Design density scaling (Jinja2 filter)."""
        if isinstance(value, str) and value.startswith('@'):
            return value[1:] * scale
            
        if value == 'unset':
            return 'unset'
            
        if isinstance(value, str):
            try:
                value = float(value.replace('px', ''))
            except ValueError:
                return value
                
        density = (value + (density_interval * int(density_scale)) - (border * 2)) * scale
        
        if density <= 0:
            density = min_
        return density
    
    def generate_material_css(self, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """Generate Material Design CSS using our theme colors."""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Material template not found at: {self.template_path}")
        
        # Prepare template variables
        template_vars = self.template_vars.copy()
        if extra_vars:
            template_vars.update(extra_vars)
        
        # Set up Jinja2 environment
        template_dir = os.path.dirname(self.template_path)
        template_name = os.path.basename(self.template_path)
        
        loader = jinja2.FileSystemLoader(template_dir)
        env = jinja2.Environment(autoescape=False, loader=loader)
        
        # Add custom filters
        env.filters['opacity'] = self._opacity_filter
        env.filters['density'] = self._density_filter
        
        # Load and render template
        template = env.get_template(template_name)
        return template.render(**template_vars)
    
    def get_material_styles(self) -> Dict[str, str]:
        """Get commonly used material styles as individual strings."""
        try:
            full_css = self.generate_material_css()
            
            # For now, return the full CSS as a single style
            # In the future, we could parse and extract specific widget styles
            return {
                'full_material_css': full_css,
                'primary_button': self._extract_button_style(full_css, 'QPushButton'),
                'input_field': self._extract_input_style(full_css),
                'dialog': self._extract_dialog_style(full_css),
            }
        except Exception as e:
            print(f"Warning: Failed to generate material styles: {e}")
            return {}
    
    def _extract_button_style(self, css: str, selector: str) -> str:
        """Extract button styles from full CSS (simplified extraction)."""
        # This is a simplified extraction - in practice, you might want more sophisticated parsing
        lines = css.split('\n')
        in_button_block = False
        button_css = []
        
        for line in lines:
            if selector in line and '{' in line:
                in_button_block = True
                button_css.append(line)
            elif in_button_block:
                button_css.append(line)
                if '}' in line and not line.strip().endswith(','):
                    break
        
        return '\n'.join(button_css) if button_css else ""
    
    def _extract_input_style(self, css: str) -> str:
        """Extract input field styles from full CSS."""
        # Look for QLineEdit, QTextEdit styles
        return self._extract_button_style(css, 'QLineEdit')
    
    def _extract_dialog_style(self, css: str) -> str:
        """Extract dialog styles from full CSS."""
        return self._extract_button_style(css, 'QDialog')


# Global instance for easy access
material_processor = MaterialThemeProcessor()


def get_material_css() -> str:
    """Get the full Material Design CSS for our theme."""
    return material_processor.generate_material_css()


def get_material_styles() -> Dict[str, str]:
    """Get Material Design styles as a dictionary."""
    return material_processor.get_material_styles()


# Convenience functions for specific styles
def get_material_button_style() -> str:
    """Get Material Design button style."""
    styles = get_material_styles()
    return styles.get('primary_button', '')


def get_material_input_style() -> str:
    """Get Material Design input field style."""
    styles = get_material_styles()
    return styles.get('input_field', '')


def get_material_dialog_style() -> str:
    """Get Material Design dialog style."""
    styles = get_material_styles()
    return styles.get('dialog', '')