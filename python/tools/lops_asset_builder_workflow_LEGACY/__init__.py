"""
LOPS Asset Builder Workflow

A step-by-step UI workflow for multiple LOPS asset importing that combines
the functionality of lops_asset_builder_v2 with the interactive workflow
pattern from batch_import_workflow.

Features:
- Interactive step-by-step asset group importing
- Multiple asset groups with individual component builders
- Material creation and assignment
- Organized network layout with notes
- Final merge node connecting all asset groups

Usage:
    from tools.lops_asset_builder_workflow import create_lops_asset_builder_workflow
    create_lops_asset_builder_workflow()

Or:
    from tools.lops_asset_builder_workflow.lops_asset_builder_workflow import LopsAssetBuilderWorkflow
    workflow = LopsAssetBuilderWorkflow()
    workflow.create_workflow()
"""

from .lops_asset_builder_workflow import (
    LopsAssetBuilderWorkflow,
    create_lops_asset_builder_workflow,
    main
)

__all__ = [
    'LopsAssetBuilderWorkflow',
    'create_lops_asset_builder_workflow', 
    'main'
]

__version__ = "1.4.0"
__author__ = "Custom Tools"
__description__ = "LOPS Asset Builder Workflow - Step-by-step UI for multiple asset importing"
