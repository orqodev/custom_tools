"""
LOPS Asset Builder Workflow - Refactored Modular Version

This is the main entry point for the refactored LOPS Asset Builder Workflow.
The functionality has been reorganized into a modular structure for better
maintainability and extensibility.

Directory Structure:
- main.py: Main workflow logic and entry points
- models/: Data models and settings management
- ui/: User interface components and dialogs
- utils/: Utility functions for file operations and validation
- config/: Configuration constants and settings
"""

# Import the main workflow functionality from the refactored modules
from .main import (
    LopsAssetBuilderWorkflow,
    toggle_lops_asset_builder_workflow,
    create_lops_asset_builder_workflow,
    main
)

# Backward compatibility - expose the main functions at module level
def run():
    """Entry point for shelf tools - backward compatibility."""
    return toggle_lops_asset_builder_workflow()

def create_workflow():
    """Create workflow - backward compatibility."""
    return create_lops_asset_builder_workflow()

# Main entry point
if __name__ == "__main__":
    main()