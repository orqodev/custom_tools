# Batch Import Workflow

A comprehensive Houdini workflow for batch importing multiple geometry assets with dynamic switching and transform controls.

## Overview

This workflow creates a Geo node containing a subnetwork that provides:
- Batch file selection and import
- Dynamic UI generation for asset paths
- File nodes for each imported asset
- Switch node for asset selection
- Transform controls
- Parameter export to parent level

## Features

### Core Functionality
- **Geo Node Creation**: Creates a main geometry node to contain the workflow
- **Subnetwork**: Contains all the import logic and nodes
- **Batch Import Button**: Runs file selection dialog to import multiple assets
- **Dynamic UI**: Generates UI fields based on number of selected assets
- **File Nodes**: Creates individual file nodes for each asset path
- **Switch Node**: Merges all file nodes with switching capability
- **Transform Node**: Provides translation, rotation, and scale controls
- **Output Connection**: Connects everything to a final output node

### Parameter Export
- **Asset Switch Control**: Exported to parent geo node for easy access
- **Transform Controls**: All transform parameters (tx, ty, tz, rx, ry, rz, sx, sy, sz) exported to parent
- **Parameter Linking**: Automatic linking between parent and subnet parameters

### Supported File Types
- .abc (Alembic)
- .bgeo, .bgeo.sc (Houdini geometry)
- .obj (Wavefront OBJ)
- .fbx (FBX)
- .usd, .usda, .usdc (USD)

## Usage

### Creating the Workflow

```python
from batch_import_workflow import create_batch_import_workflow

# Create the complete workflow
geo_node = create_batch_import_workflow()
```

### Using the Workflow

#### Automatic Import (New Feature)
When you create the workflow, it will **automatically prompt you to select files** for import. This populates the asset path fields immediately upon creation.

1. **Create Workflow**: Run `create_batch_import_workflow()` - this will automatically open a file selection dialog
2. **Select Files**: Choose multiple geometry files in the initial dialog
3. **Workflow Ready**: The asset paths are automatically populated and ready to use

#### Manual Import (Additional Files)
You can also add more files manually after the initial creation:

1. **Run Batch Importer**: Click the "Run Batch Importer" button in the subnetwork to add more files
2. **Select Additional Files**: Choose additional geometry files in the file dialog
3. **Adjust Paths**: Modify the number of asset paths if needed

#### Using the Assets
4. **Switch Assets**: Use the "Asset Switch" parameter to change between imported assets
5. **Transform Assets**: Use the transform parameters to position, rotate, and scale
6. **Parent Controls**: Access switch and transform controls from the parent geo node

### Workflow Structure

```
batch_import_workflow (Geo Node)
├── asset_importer (Subnet)
│   ├── file_1, file_2, ... (File Nodes)
│   ├── asset_switch_node (Switch Node)
│   ├── transform_node (Transform Node)
│   └── OUTPUT (Output Node)
└── Exported Parameters
    ├── asset_switch_control
    └── asset_transform folder
        ├── asset_tx, asset_ty, asset_tz
        ├── asset_rx, asset_ry, asset_rz
        └── asset_sx, asset_sy, asset_sz
```

## Implementation Details

### Class Structure

#### BatchImportWorkflow
Main class that handles the workflow creation:
- `create_workflow()`: Main method to create the complete workflow
- `_create_geo_node()`: Creates the parent geometry node
- `_create_subnetwork()`: Creates the internal subnetwork
- `_add_ui_parameters()`: Adds all UI parameters to the subnetwork
- `_add_python_module()`: Adds Python callback functions
- `_create_internal_network()`: Creates the initial internal structure
- `_export_parameters_to_parent()`: Exports parameters to parent level
- `_link_parameters_to_parent()`: Links subnet parameters to parent parameters

### Python Module Functions

The subnetwork contains embedded Python functions:

#### `run_batch_import()`
- Opens file selection dialog
- Updates number of asset paths
- Populates asset path parameters
- Creates file nodes

#### `update_asset_paths()`
- Dynamically updates asset path parameters
- Adjusts switch parameter range
- Rebuilds UI based on number of paths

#### `update_file_nodes()`
- Creates file nodes for each asset path
- Positions nodes in the network
- Updates switch node connections

#### `update_switch_node(file_nodes)`
- Creates or updates the switch node
- Connects all file nodes as inputs
- Updates transform node connection

#### `update_transform_node(input_node)`
- Creates transform node with parameter links
- Links to parent transform parameters
- Updates output node connection

#### `update_output_node(input_node)`
- Creates final output node
- Sets display and render flags

#### `update_switch()`
- Updates switch node input based on parameter

## Testing

Run the test script to verify the workflow:

```python
from test_workflow import test_workflow_creation

# Run all tests
test_workflow_creation()
```

The test verifies:
- Geo node creation
- Subnetwork creation
- Parameter creation
- Output node creation
- Parameter export
- Parameter linking

## Requirements

- Houdini 18.0 or later
- Python 3.7+
- Access to Houdini Python API (hou module)

## File Structure

```
batch_import_workflow/
├── __init__.py
├── batch_import_workflow.py    # Main workflow implementation
├── test_workflow.py           # Test script
└── README.md                  # This documentation
```

## Integration with Existing Tools

This workflow integrates concepts from:
- `batch_importer.py`: Basic batch import functionality
- `batch_importer_with_analyze.py`: Enhanced features and analysis

## Future Enhancements

Potential improvements:
- Material assignment integration
- Automatic asset analysis and classification
- Grid layout options for imported assets
- Custom file type handlers
- Asset preview functionality
- Batch processing options

## Error Handling

The workflow includes error handling for:
- Invalid file paths
- Missing parameters
- Node creation failures
- Parameter linking issues

## License

This tool is part of the custom Houdini tools collection.
