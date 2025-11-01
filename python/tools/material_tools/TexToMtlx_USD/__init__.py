"""
TexToMtlx_USD - Standalone MaterialX and USD Material Exporter

A modular toolkit for converting texture folders directly to MaterialX and USD files
without requiring Houdini material library nodes.

Components:
    - materialx_exporter: Core MaterialX document creation from textures
    - usd_exporter: USD file creation with MaterialX references and variants
    - tex_to_mtlx_standalone: UI tool and batch conversion functions

Features:
    - Direct MaterialX/USD export from texture folders
    - KB3D-compatible format and structure
    - Material name casing preservation
    - UDIM texture support
    - Texture variant system (png4k, jpg2k, jpg1k, etc.)
    - Custom metadata (kit name, ID, version)
    - ASCII USD format for readability

Usage:
    # UI Tool
    from tools.material_tools.TexToMtlx_USD.tex_to_mtlx_standalone import show_standalone_converter
    show_standalone_converter()

    # Programmatic
    from tools.material_tools.TexToMtlx_USD.materialx_exporter import MaterialXExporter
    from tools.material_tools.TexToMtlx_USD.usd_exporter import USDExporter

    mtlx_exp = MaterialXExporter()
    usd_exp = USDExporter()

Documentation:
    See docs/ folder for complete guides:
    - QUICK_START.md - Quick reference
    - README_STANDALONE_MTLX.md - Complete documentation
    - INTEGRATION_GUIDE.md - Integration with tex_to_mtlx
    - KB3D_METADATA_GUIDE.md - Metadata customization

Version: 1.0.0
Author: Custom Tools
Date: 2025-10-28
"""

__version__ = '1.0.0'
__author__ = 'Custom Tools'

# Import main classes for convenience
from .materialx_exporter import MaterialXExporter, export_materialx_from_textures
from .usd_exporter import USDExporter, export_usd_material, create_kb3d_style_usd
from .tex_to_mtlx_standalone import (
    StandaloneMaterialXConverter,
    show_standalone_converter,
    convert_textures_to_materialx
)

# Public API
__all__ = [
    # Classes
    'MaterialXExporter',
    'USDExporter',
    'StandaloneMaterialXConverter',

    # Functions
    'export_materialx_from_textures',
    'export_usd_material',
    'create_kb3d_style_usd',
    'show_standalone_converter',
    'convert_textures_to_materialx',
]
