"""
KB3D Reverse Engineering Tools

Tools for reverse-engineering KitBash3D USD assets to create a proper
component-based USD pipeline.

Modules:
    kb3d_usd_analyzer - Analyze USD files to extract component structure
    kb3d_geometry_converter - Convert extracted .bgeo.sc to USD components
    kb3d_assembly_generator - Generate new assemblies from components
    kb3d_pipeline_orchestrator - Batch process entire asset library
"""

from .kb3d_usd_analyzer import KB3DAnalyzer, analyze_asset, AssetMapping

__all__ = [
    'KB3DAnalyzer',
    'analyze_asset',
    'AssetMapping',
]
