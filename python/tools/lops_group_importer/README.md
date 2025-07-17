# LOPS Group Importer

A LOPS (Lighting/Look Development) version of the batch import workflow that allows importing multiple asset groups with material support in Houdini's Solaris context.

## Overview

The LOPS Group Importer creates a streamlined iterative workflow for batch importing multiple asset groups in the LOPS/Solaris context. Each asset group gets its own subnetwork with unique naming and parameter prefixing to avoid cross-talk between groups. All subnetworks are connected to a final merge node with full material assignment support.

## Key Features

- **LOPS/Solaris Integration**: Works natively in Houdini's `/stage` context
- **USD and Geometry Support**: Handles both USD files (.usd, .usda, .usdc) and geometry files
- **Material Assignment**: Built-in material library and assignment system
- **Iterative Workflow**: Add multiple asset groups one by one
- **Parameter Control**: Each group has its own transform, switch, and material parameters
- **No Cross-talk**: Group-prefixed parameters prevent interference between groups

## Usage

### Basic Usage

```python
# Import and run the LOPS Group Importer
from tools.lops_group_importer.lops_group_importer import create_lops_group_importer

# Create the workflow
stage_node = create_lops_group_importer()
```

### From Houdini Python Shell

```python
import sys
sys.path.append('/path/to/your/custom_tools/scripts/python')

from tools.lops_group_importer.lops_group_importer import create_lops_group_importer
create_lops_group_importer()
```

## Workflow Steps

1. **Stage Node Creation**: Enter a name for the top-level LOPS stage node
2. **Material Library**: A global material library is created automatically
3. **Asset Group Import**: For each group:
   - Select USD or geometry files (up to 10 per group)
   - Enter a group name (auto-generated from first file)
   - Assets are imported with appropriate LOPS nodes
4. **Continue or Finish**: Choose to add more groups or finish
5. **Final Assembly**: All groups are connected to a merge node
6. **Summary**: View final summary of imported groups

## Node Structure

### Main Stage Network
- **Global Material Library**: `materiallibrary` node for all materials
- **Asset Group Subnets**: One subnet per asset group
- **Merge Node**: Combines all asset groups

### Per-Group Subnet Structure
- **Reference/Import Nodes**: USD reference or SOP import nodes
- **Switch Node**: Select between assets in the group
- **Transform Node**: Position/rotate/scale the group
- **Material Assignment**: Assign materials to the group
- **Output Node**: Subnet output

## Parameters

Each asset group subnet includes:

### Group Controls
- **Switch Parameter**: Select which asset in the group to display
- **Transform Parameters**: Translate, Rotate, Scale controls
- **Material Parameters**: Enable/disable materials, material path

### Asset Information
- **USD Assets**: File path parameters for USD files
- **Geometry Assets**: SOP node path parameters for geometry

## File Type Support

### USD Files (.usd, .usda, .usdc)
- Uses `reference` nodes
- Direct USD stage integration
- Maintains USD hierarchy and materials

### Geometry Files (.obj, .fbx, .abc, etc.)
- Uses `sopimport` nodes
- Requires SOP network setup
- Converts geometry to USD

## Material Workflow

1. **Global Material Library**: Created automatically with `/ASSET/mtl/` prefix
2. **Per-Group Assignment**: Each group can have its own material path
3. **Material Toggle**: Enable/disable materials per group
4. **USD Integration**: Works with USD material workflow

## Advanced Usage

### Programmatic Control

```python
from tools.lops_group_importer.lops_group_importer import LopsGroupImporter

# Create importer instance
importer = LopsGroupImporter()

# Create workflow
stage_node = importer.create_workflow()

# Access created nodes
material_library = importer.material_library
merge_node = importer.merge_node
asset_groups = importer.asset_groups
```

### Custom Material Setup

After creating the workflow, you can:
1. Add materials to the global material library
2. Update material paths in group parameters
3. Use the material assignment nodes for custom workflows

## Comparison with SOP Batch Importer

| Feature | SOP Batch Importer | LOPS Group Importer |
|---------|-------------------|-------------------|
| Context | `/obj` (SOPs) | `/stage` (LOPS) |
| File Types | Geometry files | USD + Geometry |
| Materials | No material support | Full material workflow |
| Workflow | Geometry processing | USD/Solaris pipeline |
| Output | Merged geometry | USD stage |

## Tips and Best Practices

1. **USD Files**: Prefer USD files for better LOPS integration
2. **Material Organization**: Use consistent material naming conventions
3. **Group Naming**: Use descriptive group names for better organization
4. **File Limits**: Keep asset groups to 10 files or fewer for performance
5. **SOP Integration**: For geometry files, set up SOP networks first

## Troubleshooting

### Common Issues

1. **Missing SOP Paths**: For geometry files, ensure SOP node paths are set correctly
2. **Material Assignment**: Check material library and paths if materials don't appear
3. **USD References**: Verify USD file paths are accessible and valid
4. **Performance**: Large numbers of assets may require optimization

### Error Messages

- **"Error creating LOPS Group Importer"**: Check Houdini version and LOPS availability
- **Missing file references**: Verify file paths are correct and accessible
- **Material assignment failures**: Check material library setup and paths

## Requirements

- Houdini with Solaris/LOPS support
- Python access to Houdini API
- USD files or geometry files to import

## Version History

- **v1.0**: Initial LOPS translation of batch import workflow
- Material assignment support
- USD and geometry file support
- Iterative group creation workflow