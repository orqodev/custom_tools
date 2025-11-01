"""
Asset Library Builder - USD Asset Library Pipeline

A comprehensive tool for building production-ready USD asset libraries with:
- Proper payload/geometry/material structure
- Texture resolution variants (jpg1k, jpg2k, png4k)
- Automatic instanceable detection
- Material library with MaterialX shaders
- Batch processing workflows

Main Components:
    - asset_builder.py: Core builder that creates USD structure from parts
    - asset_builder_ui.py: PySide6 UI for interactive building
    - asset_builder_shelf.py: Houdini shelf tool integration

Usage:
    From Python Shell:
        from tools.asset_library_builder import show_ui
        show_ui()

    Or programmatically:
        from tools.asset_library_builder.asset_builder import build_from_parts

        build_from_parts(
            parts_folder="/path/to/parts",
            asset_name="MyAsset",
            models_folder="/path/to/Models",
            materials_folder="/path/to/Materials"
        )
"""

__version__ = "1.1.0"  # Now uses mesh names directly as material names (no conversion)
__author__ = "Custom Tools"

# Convenience imports
from .asset_builder_ui import show_ui

__all__ = ["show_ui"]
