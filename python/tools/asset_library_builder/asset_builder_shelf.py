"""
Shelf Tool Integration for Asset Library Builder

This module provides the entry point for the Houdini shelf tool.
Add this to your shelf tool script:

    from tools.asset_library_builder.asset_builder_shelf import run
    run()
"""

def run():
    """Launch the Asset Library Builder UI."""
    from tools.asset_library_builder import show_ui
    show_ui()


if __name__ == "__main__":
    run()
