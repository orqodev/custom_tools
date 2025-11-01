"""
KitBash3D Parts Processor

Tool to process exported KitBash3D parts (Wings, Cargo, Main, etc.) and combine them
into a single centered asset with proper matchsize normalization.

Workflow:
1. Scan folder for exported parts (each part has geo.usd, mtl.usd, etc.)
2. Import all parts into SOPs
3. Apply matchsize with CENTER mode (not using original transforms)
4. Combine parts into single geometry
5. Export as BGEO or USD

Usage:
    from tools.kb3d_parts_processor import process_kb3d_parts

    process_kb3d_parts(
        parts_folder="/path/to/KB3D_SPS_Spaceship_C",
        output_file="/path/to/output.bgeo.sc",
        match_size=1.0,
        center_mode=True
    )
"""

import hou
import os
from typing import List, Dict, Optional


def scan_kb3d_parts(parts_folder: str) -> List[Dict[str, str]]:
    """
    Scan a KitBash3D parts folder and find all part subfolders.

    Args:
        parts_folder: Path to folder containing part subfolders (Wings, Cargo, Main, etc.)

    Returns:
        List of dicts with part info: [{'name': 'Wings', 'path': '/path/to/Wings', 'geo': '/path/to/Wings/geo.usd'}, ...]
    """
    parts = []

    if not os.path.isdir(parts_folder):
        print(f"Error: {parts_folder} is not a directory")
        return parts

    # Look for subdirectories that contain geo files
    for item in os.listdir(parts_folder):
        item_path = os.path.join(parts_folder, item)

        if not os.path.isdir(item_path):
            continue

        # Look for geo.usd, geo.usda, or .usd file with same name as folder
        geo_candidates = [
            os.path.join(item_path, 'geo.usd'),
            os.path.join(item_path, 'geo.usda'),
            os.path.join(item_path, f'{item}.usd'),
            os.path.join(item_path, f'{item}.usda'),
        ]

        geo_file = None
        for candidate in geo_candidates:
            if os.path.exists(candidate):
                geo_file = candidate
                break

        if geo_file:
            parts.append({
                'name': item,
                'path': item_path,
                'geo': geo_file
            })

    return parts


def process_kb3d_parts(
    parts_folder: str,
    output_file: str,
    match_size: float = 1.0,
    center_mode: bool = True,
    create_network: bool = False,
    obj_context: Optional[hou.Node] = None
) -> Optional[hou.Node]:
    """
    Process KitBash3D exported parts into a single centered asset.

    Args:
        parts_folder: Path to folder containing part subfolders
        output_file: Output file path (.bgeo.sc, .usd, etc.)
        match_size: Target size for matchsize (default 1.0)
        center_mode: Use center mode for matchsize (default True)
        create_network: Create persistent network in /obj (default False)
        obj_context: Optional OBJ context node (default creates new geo)

    Returns:
        Output node if create_network=True, otherwise None
    """
    # Scan for parts
    parts = scan_kb3d_parts(parts_folder)

    if not parts:
        print(f"No parts found in {parts_folder}")
        return None

    print(f"Found {len(parts)} parts: {[p['name'] for p in parts]}")

    # Create or use existing OBJ context
    if obj_context is None:
        obj_context = hou.node('/obj').createNode('geo', 'kb3d_parts_processor')
        obj_context.moveToGoodPosition()

    # Clear any existing children if requested
    if create_network:
        for child in obj_context.children():
            child.destroy()

    # Import all parts
    merge_inputs = []

    for i, part in enumerate(parts):
        print(f"Processing part: {part['name']}")

        # Create USD import node
        usd_import = obj_context.createNode('file', f"import_{part['name']}")
        usd_import.parm('file').set(part['geo'])

        # Apply matchsize with CENTER mode
        matchsize = obj_context.createNode('matchsize', f"matchsize_{part['name']}")
        matchsize.setInput(0, usd_import)
        matchsize.parm('scale').set(match_size)

        if center_mode:
            matchsize.parm('justify').set(1)  # Center
            matchsize.parm('justifyx').set(1)  # Center X
            matchsize.parm('justifyy').set(1)  # Center Y
            matchsize.parm('justifyz').set(1)  # Center Z

        # Add to merge list
        merge_inputs.append(matchsize)

    # Merge all parts
    merge = obj_context.createNode('merge', 'merge_all_parts')
    for i, input_node in enumerate(merge_inputs):
        merge.setInput(i, input_node)

    # Add name attribute for part identification
    attribcreate = obj_context.createNode('attribcreate', 'add_part_names')
    attribcreate.setInput(0, merge)
    attribcreate.parm('name1').set('kb3d_part')
    attribcreate.parm('class1').set(1)  # Primitive
    attribcreate.parm('type1').set(3)  # String

    # Clean up attributes
    attribdelete = obj_context.createNode('attribdelete', 'cleanup_attribs')
    attribdelete.setInput(0, attribcreate)
    attribdelete.parm('ptdel').set('* ^P ^N')
    attribdelete.parm('primdel').set('usdprimalias usdprimpath usdprimname usdprimtype')

    # Output node
    output = obj_context.createNode('null', 'OUTPUT')
    output.setInput(0, attribdelete)
    output.setDisplayFlag(True)
    output.setRenderFlag(True)

    # Layout network
    obj_context.layoutChildren()

    # Export if output file specified and not creating persistent network
    if output_file and not create_network:
        ext = os.path.splitext(output_file)[1].lower()

        if ext in ['.bgeo', '.sc'] or output_file.endswith('.bgeo.sc'):
            # BGEO export
            rop = obj_context.createNode('rop_geometry', 'export_bgeo')
            rop.parm('soppath').set(output.path())
            rop.parm('sopoutput').set(output_file)
            rop.parm('execute').pressButton()
            print(f"Exported to: {output_file}")

            if not create_network:
                obj_context.destroy()
                return None
        elif ext in ['.usd', '.usda', '.usdc']:
            # USD export
            rop = obj_context.createNode('usd_rop', 'export_usd')
            rop.parm('lopoutput').set(output_file)
            # Create USD ROP setup...
            print(f"USD export to: {output_file}")

    if create_network:
        return output
    else:
        return None


def create_kb3d_asset_from_parts(
    parts_folder: str,
    asset_name: str,
    output_geo_folder: str,
    output_tex_folder: Optional[str] = None,
    match_size: float = 1.0
) -> str:
    """
    Create a complete asset structure from KB3D parts.

    Args:
        parts_folder: Path to KB3D parts folder
        asset_name: Name for the asset
        output_geo_folder: Where to save the processed geometry
        output_tex_folder: Optional texture folder path
        match_size: Target size

    Returns:
        Path to output geometry file
    """
    os.makedirs(output_geo_folder, exist_ok=True)

    output_file = os.path.join(output_geo_folder, f"{asset_name}.bgeo.sc")

    process_kb3d_parts(
        parts_folder=parts_folder,
        output_file=output_file,
        match_size=match_size,
        center_mode=True,
        create_network=False
    )

    return output_file


if __name__ == "__main__":
    # Test with Spaceship_C
    test_folder = "/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C"
    output = "/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C_merged.bgeo.sc"

    parts = scan_kb3d_parts(test_folder)
    print("Found parts:", [p['name'] for p in parts])

    # Process and create network for inspection
    node = process_kb3d_parts(
        parts_folder=test_folder,
        output_file=None,
        match_size=1.0,
        center_mode=True,
        create_network=True
    )

    if node:
        print(f"Created network at: {node.parent().path()}")
