# LOPS Asset Builder Workflow - Refactored Modular Version

A step-by-step UI workflow for multiple LOPS asset importing that combines the functionality of `lops_asset_builder_v2` with the interactive workflow pattern from `batch_import_workflow`.

**This tool has been refactored into a modular structure for better maintainability, extensibility, and code organization.**

## Features

- **Interactive Step-by-Step Workflow**: User-friendly interface that guides through the asset importing process
- **Multiple Asset Groups**: Support for importing multiple groups of assets with individual component builders
- **Material Creation and Assignment**: Automatic material creation from texture folders using MaterialX
- **Automatic Network Layout**: Basic automatic layout of nodes
- **Final Merge Node**: All asset groups are connected to a final merge node for easy management
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Modular Architecture**: Refactored into a clean, maintainable modular structure

## Modular Structure

The tool has been refactored into the following modular structure:

```
lops_asset_builder_workflow/
├── __init__.py                     # Package initialization
├── lops_asset_builder_workflow.py  # Main entry point (backward compatibility)
├── main.py                         # Core workflow logic and entry points
├── README.md                       # This documentation file
├── models/
│   ├── __init__.py
│   ├── data_model.py              # Data structures and models
│   └── settings_model.py          # Configuration management
├── ui/
│   ├── __init__.py
│   ├── main_dialog.py             # Primary interface dialogs
│   ├── settings_dialog.py         # Configuration UI (placeholder)
│   └── components.py              # Reusable UI components
├── utils/
│   ├── __init__.py
│   ├── file_operations.py         # File handling utilities
│   └── validation.py              # Input validation functions
└── config/
    ├── __init__.py
    └── constants.py               # Configuration constants
```

### Architecture Benefits

- **Maintainability**: Clear separation of concerns makes the code easier to maintain
- **Extensibility**: New features can be added without affecting existing functionality
- **Testability**: Individual components can be tested independently
- **Reusability**: UI components and utilities can be reused across the application
- **Backward Compatibility**: Existing shelf tools and scripts continue to work unchanged

## Usage

### Basic Usage (Backward Compatible)

```python
# Original approach - still works
from tools.lops_asset_builder_workflow import create_lops_asset_builder_workflow

# Run the workflow
success = create_lops_asset_builder_workflow()
```

### Shelf Tool Usage (Backward Compatible)

```python
# For shelf tools - original entry point
from tools.lops_asset_builder_workflow import run
run()
```

### New Modular Usage (Recommended)

```python
# New modular approach - recommended for new code
from tools.lops_asset_builder_workflow.main import LopsAssetBuilderWorkflow

# Create workflow instance
workflow = LopsAssetBuilderWorkflow()

# Run the workflow
success = workflow.create_workflow()

# Access workflow data
if success and workflow.ui_result:
    print(f"Created {len(workflow.ui_result)} asset groups")
    for group in workflow.ui_result:
        print(f"Group: {group['group_name']} with {len(group['asset_paths'])} assets")
```

### Advanced Modular Usage

```python
# Import specific components for advanced usage
from tools.lops_asset_builder_workflow.main import LopsAssetBuilderWorkflow
from tools.lops_asset_builder_workflow.models.data_model import WorkflowData
from tools.lops_asset_builder_workflow.ui.main_dialog import AssetGroupsDialog

# Create and configure workflow
workflow = LopsAssetBuilderWorkflow()

# Access individual components
dialog = AssetGroupsDialog()
if dialog.exec_() == dialog.Accepted:
    workflow_data = dialog.get_workflow_data()
    result_data = dialog.get_result_data()

    # Process the data as needed
    print(f"Asset scope: {workflow_data.asset_scope}")
    print(f"Number of groups: {len(result_data)}")
```

## Workflow Steps

1. **Asset Group Selection**: Select geometry files for each asset group
2. **Group Naming**: Provide a name for each asset group
3. **Component Builder Creation**: Automatic creation of LOPS component builder nodes
4. **Material Processing**: Automatic material creation from texture folders (if available)
5. **Network Layout**: Basic automatic layout of nodes
6. **Iteration**: Option to add more asset groups
7. **Final Merge**: All groups connected to a final merge node
8. **Summary**: Display of created asset groups and final status

## Supported File Formats

- **FBX** (.fbx)
- **OBJ** (.obj)
- **Alembic** (.abc)
- **BGEO** (.bgeo)
- **BGEO Sequence Cache** (.bgeo.sc)

## Directory Structure

The workflow expects the following directory structure for automatic material creation:

```
asset_directory/
├── asset1.fbx
├── asset2.obj
├── asset3.bgeo
└── maps/
    ├── material1/
    │   ├── diffuse.jpg
    │   ├── normal.jpg
    │   └── roughness.jpg
    └── material2/
        ├── diffuse.jpg
        └── normal.jpg
```

## Created Nodes

For each asset group, the workflow creates:

### LOPS Nodes
- **Component Geometry**: Imports and manages geometry variants
- **Material Library**: Contains MaterialX materials
- **Component Material**: Assigns materials to geometry
- **Component Output**: Final output for the asset group

### SOP Network (inside Component Geometry)
- **File/Alembic Nodes**: Import individual assets
- **Switch Node**: Allows switching between assets with UI parameter control
- **Transform Node**: Provides transform controls with UI parameter linking
- **Match Size**: Normalizes geometry size
- **Attribute Wrangle**: Converts material paths to names
- **Attribute Delete**: Cleans up unnecessary attributes
- **Poly Reduce**: Creates proxy geometry (5% reduction)
- **Attribute Wrangle (Color)**: Sets color attributes with asset name parameter
- **Color Node**: Creates unique colors based on asset name
- **Attribute Promote**: Promotes color data from primitive to point level
- **Python SOP (Convex Hull)**: Creates convex hull geometry for simulation with custom parameters
- **Name Node**: Sets proper naming for simulation geometry

### UI Parameters (on Component Geometry node)
- **Asset Switch**: Integer parameter to switch between imported assets
- **Transform Controls**: Translate, Rotate, and Scale vector parameters
- **Asset Information**: File reference parameters showing paths to each asset

### Organization
- **Final Merge Node**: Connects all asset groups

## Error Handling

The workflow includes comprehensive error handling for:
- File selection cancellation
- Invalid file formats
- Missing texture directories
- Node creation failures
- Material creation errors
- Network layout issues

## Integration with Existing Tools

This workflow integrates with:
- **tex_to_mtlx**: For automatic MaterialX material creation
- **lops_light_rig**: For lighting setup (can be extended)
- **lops_lookdev_camera**: For camera setup (can be extended)

## Comparison with Related Tools

| Feature | lops_asset_builder_v2 | batch_import_workflow | lops_asset_builder_workflow |
|---------|----------------------|----------------------|----------------------------|
| UI Workflow | Single dialog | Step-by-step | Step-by-step |
| Multiple Groups | No | Yes (GEO) | Yes (LOPS) |
| Material Creation | Yes | No | Yes |
| Context | LOPS | GEO | LOPS |
| Asset Switching | Limited | Yes | Yes |
| Network Organization | Basic | Good | Basic |

## Future Enhancements

Potential future improvements:
- Light rig integration
- Camera setup integration
- Render node creation
- Asset parameter linking
- Batch material assignment
- Custom material templates
- Export/import workflow configurations

## Dependencies

- Houdini 20.5+
- Python 3.11+
- PySide6 (included with Houdini)
- USD/Pixar libraries (included with Houdini)

## Version History

- **v1.4.0**: Enhanced material discovery and targeted material creation
  - Added `_extract_material_names` method to discover materials referenced in geometry files
  - Enhanced material creation to only generate materials actually used by imported geometry
  - Modified `_create_materials` to accept `expected_names` parameter for targeted material creation
  - Improved efficiency by avoiding creation of unused materials
  - Materials are now discovered by examining `shop_materialpath` and `material:binding` primitive attributes
  - Each asset group now has its own targeted material library without cross-group sharing
- **v1.3.0**: Added complete proxy setup and sim output convex hull functionality
  - Implemented full proxy setup logic from lops_asset_builder.py with color attributes and asset naming
  - Added `_create_convex` method for convex hull generation with custom parameters (normalize, flip_normals, simplify, level_detail)
  - Enhanced sim output with proper convex hull geometry creation using convex_hull_utils module
  - Added attribute wrangle for color setting with asset_name parameter linked to component output rootprim
  - Added color node for unique asset colors, attribute promotion, and proper naming nodes
  - Proxy output now includes complete processing chain: poly_reduce → attrib_colour → color_node → attrib_promote → attrib_delete_name
  - Sim output now includes convex hull processing: python_sop (convex_hull) → name_node
- **v1.2.0**: Removed network note generation logic
  - Removed `_create_organized_net_note` function and all network box/sticky note creation
  - Removed `_random_color` function and related color generation logic
  - Removed unused imports (colorsys, random)
  - Simplified workflow to focus on core asset building functionality
  - Updated documentation to reflect removal of network organization features
- **v1.1.2**: Fixed AttributeError with OpNetworkBox fitAroundNodes method
  - Added defensive error handling in `_create_organized_net_note` function
  - Now tries `fitAroundContents()` first, falls back to `fitAroundNodes()` if needed
  - Handles API differences between Houdini versions gracefully
- **v1.1.1**: Improved organized network notes and layout functions inside frames
  - Enhanced `_create_organized_net_note` with nested network boxes for better organization
  - Improved node positioning with proper offset application before network box creation
  - Added structured color scheme matching lops_asset_builder_v2
  - Enhanced `_layout_all_nodes` function for better sequencing and organization
  - Nodes are now properly laid out within groups before network boxes are created
- **v1.1.0**: Enhanced component geometry with switch and parameter controls like lops_asset_builder_v2
  - Added UI parameters for asset switching and transform controls
  - Added parameter linking between UI controls and SOP nodes
  - Enhanced multi-asset workflow with proper parameter management
- **v1.0.0**: Initial release with step-by-step workflow, multiple asset groups, and material creation

## License

Part of the Custom Tools package for Houdini.
