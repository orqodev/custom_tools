"""
BGEO_to_KB3D_USD - Convert BGEO.SC files to KB3D-style USD structure

A toolkit for reverse-engineering KB3D kitbash assets by converting
Houdini BGEO.SC files (from FBX exports) into the proper KB3D USD hierarchy.

Components:
    - bgeo_analyzer: Analyze BGEO files and extract asset/part structure
    - usd_component_builder: Create KB3D-style component USDs
    - usd_assembly_builder: Create KB3D-style assembly USDs
    - bgeo_to_usd_converter: Main conversion orchestrator

Features:
    - Analyzes kb3d_part, kb3d_asset, shop_materialpath attributes
    - Creates 4-file USD structure (main.usd, payload.usd, geo.usd, mtl.usd)
    - KB3D-compatible hierarchy with assemblies and components
    - Texture variant support (jpg1k, jpg2k, jpg4k, png1k, png2k, png4k)
    - Material assignment preservation
    - Transform data support

Usage:
    # Analyze BGEO files
    from tools.material_tools.BGEO_to_KB3D_USD import analyze_bgeo_folder
    result = analyze_bgeo_folder('/path/to/bgeo/files')

    # Convert to USD
    from tools.material_tools.BGEO_to_KB3D_USD import convert_bgeo_to_usd
    convert_bgeo_to_usd(
        bgeo_folder='/path/to/bgeo',
        output_folder='/path/to/output'
    )

Version: 1.0.0
Author: Custom Tools
Date: 2025-10-28
"""

__version__ = '1.0.0'
__author__ = 'Custom Tools'

# Import main classes
from .bgeo_analyzer import BGEOAnalyzer, analyze_bgeo_file, analyze_bgeo_folder, print_bgeo_analysis
from .usd_component_builder import USDComponentBuilder, create_component_from_bgeo
from .usd_assembly_builder import USDAssemblyBuilder, create_assembly_from_components

# Import converter (will create this next)
try:
    from .bgeo_to_usd_converter import BGEOtoUSDConverter, convert_bgeo_to_usd
except ImportError:
    # Not yet created
    BGEOtoUSDConverter = None
    convert_bgeo_to_usd = None

# Public API
__all__ = [
    # Classes
    'BGEOAnalyzer',
    'USDComponentBuilder',
    'USDAssemblyBuilder',
    'BGEOtoUSDConverter',

    # Functions - Analysis
    'analyze_bgeo_file',
    'analyze_bgeo_folder',
    'print_bgeo_analysis',

    # Functions - Building
    'create_component_from_bgeo',
    'create_assembly_from_components',

    # Functions - Conversion
    'convert_bgeo_to_usd',
]
