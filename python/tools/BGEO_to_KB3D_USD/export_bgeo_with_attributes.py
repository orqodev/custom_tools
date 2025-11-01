"""
Export BGEO with KB3D Attributes - Helper Script

This script helps you export geometry from Houdini to BGEO.SC files
with the proper attributes needed for BGEO_to_KB3D_USD conversion.

Usage in Houdini Python Shell:
    exec(open('/home/tushita/houdini21.0/custom_tools/scripts/python/tools/material_tools/BGEO_to_KB3D_USD/export_bgeo_with_attributes.py').read())

Author: Custom Tools
Date: 2025-10-28
"""

import hou
import os


def export_geo_with_kb3d_attributes(
    source_node_path,
    output_folder,
    asset_name,
    part_name='main',
    default_material=None
):
    """
    Export geometry from a SOP node to BGEO.SC with KB3D attributes.

    Args:
        source_node_path: Path to SOP node with geometry (e.g., '/obj/geo1/output')
        output_folder: Where to save BGEO files
        asset_name: Value for kb3d_asset attribute
        part_name: Value for kb3d_part attribute
        default_material: Default material name (if shop_materialpath missing)

    Returns:
        Path to exported BGEO file
    """
    # Get source node
    source_node = hou.node(source_node_path)
    if not source_node:
        raise ValueError(f"Node not found: {source_node_path}")

    # Get geometry
    geo = source_node.geometry()
    if not geo:
        raise ValueError(f"No geometry in node: {source_node_path}")

    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Prepare output path
    output_file = os.path.join(output_folder, f'{asset_name}_{part_name}.bgeo.sc')

    # Check if kb3d attributes exist, add if missing
    needs_attributes = False

    # Check kb3d_asset
    if not geo.findPrimAttrib('kb3d_asset'):
        needs_attributes = True
        print(f"Adding kb3d_asset attribute: {asset_name}")

    # Check kb3d_part
    if not geo.findPrimAttrib('kb3d_part'):
        needs_attributes = True
        print(f"Adding kb3d_part attribute: {part_name}")

    # Check shop_materialpath
    if not geo.findPrimAttrib('shop_materialpath') and default_material:
        needs_attributes = True
        print(f"Adding shop_materialpath attribute: {default_material}")

    if needs_attributes:
        # Create wrangle node to add attributes
        parent = source_node.parent()
        wrangle = parent.createNode('attribwrangle', f'add_kb3d_attrs_{part_name}')
        wrangle.setInput(0, source_node)

        # Build VEX code
        vex_code = []
        vex_code.append(f's@kb3d_asset = "{asset_name}";')
        vex_code.append(f's@kb3d_part = "{part_name}";')

        if default_material:
            vex_code.append(f's@shop_materialpath = "/shop/materials/{default_material}";')

        wrangle.parm('snippet').set('\n'.join(vex_code))
        wrangle.parm('class').set(1)  # Run over primitives

        # Use wrangle output for export
        export_node = wrangle
    else:
        export_node = source_node

    # Create ROP Geometry Output node
    rop = export_node.parent().createNode('rop_geometry', f'export_{part_name}')
    rop.parm('soppath').set(export_node.path())
    rop.parm('sopoutput').set(output_file)

    # Save to disk
    print(f"Exporting to: {output_file}")
    rop.parm('execute').pressButton()

    # Cleanup temporary nodes
    if needs_attributes:
        wrangle.destroy()
    rop.destroy()

    print(f"✓ Exported: {output_file}")
    return output_file


def export_multiple_parts(
    parts_config,
    output_folder,
    asset_name
):
    """
    Export multiple parts for a single asset.

    Args:
        parts_config: List of dicts:
            [
                {
                    'node': '/obj/geo1/foundation',
                    'part': 'Foundation',
                    'material': 'Concrete'
                },
                {
                    'node': '/obj/geo1/walls',
                    'part': 'Walls',
                    'material': 'Metal'
                }
            ]
        output_folder: Where to save files
        asset_name: Asset name for all parts

    Returns:
        List of exported file paths
    """
    exported_files = []

    for part_config in parts_config:
        try:
            output_file = export_geo_with_kb3d_attributes(
                source_node_path=part_config['node'],
                output_folder=output_folder,
                asset_name=asset_name,
                part_name=part_config['part'],
                default_material=part_config.get('material')
            )
            exported_files.append(output_file)
        except Exception as e:
            print(f"✗ Failed to export {part_config['part']}: {e}")

    return exported_files


def interactive_export():
    """
    Interactive export - prompts user for selections.
    """
    # Get selected nodes
    selected = hou.selectedNodes()

    if not selected:
        print("Error: No nodes selected. Please select SOP nodes to export.")
        return

    # Ask for asset name
    asset_name = hou.ui.readInput("Asset Name", buttons=("OK", "Cancel"), title="KB3D Export")[1]
    if not asset_name:
        print("Cancelled")
        return

    # Ask for output folder
    output_folder = hou.ui.selectFile(
        title="Select Output Folder",
        file_type=hou.fileType.Directory
    )
    if not output_folder:
        print("Cancelled")
        return

    output_folder = hou.text.expandString(output_folder)

    # Export each selected node as a part
    for i, node in enumerate(selected):
        part_name = node.name()

        # Try to get material from geometry
        geo = node.geometry()
        material = None
        if geo:
            mat_attrib = geo.findPrimAttrib('shop_materialpath')
            if mat_attrib and geo.prims():
                mat_path = geo.prims()[0].attribValue('shop_materialpath')
                if mat_path:
                    material = mat_path.split('/')[-1]

        if not material:
            # Ask user
            material = hou.ui.readInput(
                f"Material for {part_name}",
                buttons=("OK", "Skip"),
                initial_contents="DefaultMaterial",
                title=f"Part: {part_name}"
            )[1]

        try:
            export_geo_with_kb3d_attributes(
                source_node_path=node.path(),
                output_folder=output_folder,
                asset_name=asset_name,
                part_name=part_name,
                default_material=material if material else None
            )
        except Exception as e:
            print(f"✗ Failed to export {part_name}: {e}")

    print(f"\n✓ Export complete! Files saved to: {output_folder}")
    print(f"\nNext step: Run BGEO_to_KB3D_USD converter:")
    print(f"  from tools.material_tools.BGEO_to_KB3D_USD import convert_bgeo_to_usd")
    print(f"  convert_bgeo_to_usd('{output_folder}', '/output/usd')")


# Example usage
if __name__ == '__main__':
    print("="*60)
    print("KB3D BGEO Export Helper")
    print("="*60)
    print("\nUsage:")
    print("  1. Select SOP nodes to export")
    print("  2. Run: interactive_export()")
    print("\nOr use programmatically:")
    print("  export_geo_with_kb3d_attributes(")
    print("      '/obj/geo1/output',")
    print("      '/tmp/bgeo',")
    print("      'MyAsset',")
    print("      'PartName',")
    print("      'MaterialName'")
    print("  )")
    print("="*60)
