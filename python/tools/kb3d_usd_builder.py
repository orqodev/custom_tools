"""
KitBash3D USD Asset Builder

Recreates KitBash3D USD asset structure from exported parts.

Structure created:
    AssetName/
        AssetName.usd       - Main file with payload and variants
        payload.usd         - References to geo.usd and mtl.usd
        geo.usd             - Combined geometry from all parts (centered with matchsize)
        mtl.usd             - MaterialX materials from textures

Workflow:
1. Import parts (Wings, Cargo, Main, etc.) from USD files
2. Apply centered matchsize to each part (ignoring original transforms)
3. Merge all parts into single geometry
4. Export geo.usd
5. Create MaterialX materials from texture folder
6. Export mtl.usd
7. Create payload.usd and main AssetName.usd

Usage:
    from tools.kb3d_usd_builder import build_kb3d_usd_asset

    build_kb3d_usd_asset(
        parts_folder="/path/to/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C",
        output_folder="/path/to/output/KB3D_SPS_Spaceship_C",
        asset_name="KB3D_SPS_Spaceship_C",
        texture_folder="/path/to/textures",
        match_size=1.0
    )
"""

import hou
import os
from typing import List, Dict, Optional, Tuple


def scan_parts_folder(parts_folder: str) -> List[Dict[str, str]]:
    """
    Scan folder for exported USD parts.

    Args:
        parts_folder: Path containing part subfolders (Wings, Cargo, Main, etc.)

    Returns:
        List of dicts with part info
    """
    parts = []

    if not os.path.isdir(parts_folder):
        return parts

    for item in os.listdir(parts_folder):
        item_path = os.path.join(parts_folder, item)

        if not os.path.isdir(item_path):
            continue

        # Look for geo files
        geo_candidates = [
            os.path.join(item_path, 'geo.usd'),
            os.path.join(item_path, 'geo.usda'),
            os.path.join(item_path, f'{item}.usd'),
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


def create_centered_geo_usd(
    parts_folder: str,
    output_geo_path: str,
    match_size: float = 1.0,
    preserve_transforms: bool = True,
    stage_node: Optional[hou.Node] = None
) -> Tuple[hou.Node, hou.Node]:
    """
    Create geo.usd from parts.

    Args:
        parts_folder: Folder containing part USD files
        output_geo_path: Output path for geo.usd
        match_size: Target size for matchsize (only used if preserve_transforms=False)
        preserve_transforms: If True, keep original transforms (for main asset).
                           If False, center all parts (for individual part assets)
        stage_node: Optional existing stage node

    Returns:
        (stage_node, output_node)
    """
    # Scan parts
    parts = scan_parts_folder(parts_folder)

    if not parts:
        raise ValueError(f"No parts found in {parts_folder}")

    print(f"Found {len(parts)} parts: {[p['name'] for p in parts]}")
    mode_str = "preserving transforms" if preserve_transforms else "centered with matchsize"
    print(f"Processing mode: {mode_str}")

    # Create SOP network for processing
    obj = hou.node('/obj')
    sop_geo = obj.createNode('geo', 'kb3d_geo_builder')
    sop_geo.moveToGoodPosition()

    # Import and process each part
    merge_inputs = []

    for part in parts:
        print(f"Processing part: {part['name']}")

        # Import USD
        usd_import = sop_geo.createNode('file', f"import_{part['name']}")
        usd_import.parm('file').set(part['geo'])

        last_node = usd_import

        # Apply matchsize ONLY if not preserving transforms
        if not preserve_transforms:
            matchsize = sop_geo.createNode('matchsize', f"matchsize_{part['name']}")
            matchsize.setInput(0, last_node)
            matchsize.parm('scale').set(match_size)
            matchsize.parm('justify').set(1)  # Center
            matchsize.parm('justifyx').set(1)
            matchsize.parm('justifyy').set(1)
            matchsize.parm('justifyz').set(1)
            last_node = matchsize

        # Add part name attribute
        attribcreate = sop_geo.createNode('attribcreate', f"partname_{part['name']}")
        attribcreate.setInput(0, last_node)
        attribcreate.parm('name1').set('kb3d_part')
        attribcreate.parm('class1').set(1)  # Primitive
        attribcreate.parm('type1').set(3)  # String
        attribcreate.parm('string1').set(part['name'])

        merge_inputs.append(attribcreate)

    # Merge all parts
    merge = sop_geo.createNode('merge', 'merge_all_parts')
    for i, node in enumerate(merge_inputs):
        merge.setInput(i, node)

    # Clean attributes
    attribdelete = sop_geo.createNode('attribdelete', 'cleanup')
    attribdelete.setInput(0, merge)
    attribdelete.parm('ptdel').set('* ^P ^N ^uv')
    attribdelete.parm('primdel').set('* ^kb3d_part')

    # Output
    output_null = sop_geo.createNode('null', 'OUTPUT_GEO')
    output_null.setInput(0, attribdelete)
    output_null.setDisplayFlag(True)
    output_null.setRenderFlag(True)

    sop_geo.layoutChildren()

    # Create ROP Geometry node to export USD
    rop_geo = sop_geo.createNode('rop_geometry', 'export_usd')
    rop_geo.parm('sopoutput').set(output_geo_path)
    rop_geo.parm('soppath').set(output_null.path())
    rop_geo.parm('trange').set(0)  # Current frame only

    sop_geo.layoutChildren()

    return sop_geo, rop_geo


def create_payload_usd(output_path: str, asset_name: str):
    """Create payload.usd file."""
    content = f"""#usda 1.0
(
    defaultPrim = "{asset_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{asset_name}" (
    kind = "component"
    prepend references = [
        @./mtl.usd@,
        @./geo.usd@
    ]
)
{{
}}
"""
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created payload.usd: {output_path}")


def create_main_usd(output_path: str, asset_name: str, texture_variants: Optional[List[str]] = None):
    """Create main AssetName.usd file."""

    # Default texture variants if not provided
    if texture_variants is None:
        texture_variants = ["png4k", "png2k", "png1k", "jpg4k", "jpg2k", "jpg1k"]

    variant_defs = "\n".join([f'        "{v}" {{\n\n        }}' for v in texture_variants])

    content = f"""#usda 1.0
(
    defaultPrim = "{asset_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{asset_name}" (
    prepend apiSchemas = ["GeomModelAPI"]
    assetInfo = {{
        dictionary kb3d = {{
            string kitDisplayName = "Custom Clone"
            string kitId = "kb3d_clone"
            string kitVersion = "1.0.0"
        }}
    }}
    prepend inherits = </__class__/{asset_name}>
    kind = "component"
    prepend payload = @./payload.usd@
    variants = {{
        string texture_variant = "{texture_variants[0]}"
    }}
    prepend variantSets = "texture_variant"
)
{{
    variantSet "texture_variant" = {{
{variant_defs}
    }}
}}

class "__class__"
{{
    class "{asset_name}"
    {{
    }}
}}
"""
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created main USD: {output_path}")


def build_kb3d_usd_asset(
    parts_folder: str,
    output_folder: str,
    asset_name: str,
    texture_folder: Optional[str] = None,
    match_size: float = 1.0,
    preserve_transforms: bool = True,
    texture_variants: Optional[List[str]] = None
) -> str:
    """
    Build complete KB3D USD asset structure from parts.

    Args:
        parts_folder: Folder containing exported parts (Wings, Cargo, Main, etc.)
        output_folder: Output folder for USD asset
        asset_name: Name for the asset
        texture_folder: Optional texture folder for MaterialX
        match_size: Target size for matchsize normalization (only if preserve_transforms=False)
        preserve_transforms: If True (default), keep original part transforms for proper assembly.
                           If False, center all parts with matchsize.
        texture_variants: Optional list of texture variant names

    Returns:
        Path to main USD file
    """
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Define output paths
    geo_usd_path = os.path.join(output_folder, 'geo.usd')
    mtl_usd_path = os.path.join(output_folder, 'mtl.usd')
    payload_usd_path = os.path.join(output_folder, 'payload.usd')
    main_usd_path = os.path.join(output_folder, f'{asset_name}.usd')

    print(f"\n{'='*60}")
    print(f"Building KB3D USD Asset: {asset_name}")
    print(f"{'='*60}")
    print(f"Parts folder: {parts_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Match size: {match_size}")
    print()

    # Step 1: Create geo.usd from parts
    print("Step 1: Creating geo.usd from parts...")
    stage_node, usd_rop = create_centered_geo_usd(
        parts_folder=parts_folder,
        output_geo_path=geo_usd_path,
        match_size=match_size,
        preserve_transforms=preserve_transforms
    )

    # Execute USD export
    print(f"Exporting to: {geo_usd_path}")
    usd_rop.parm('execute').pressButton()

    # Step 2: Create mtl.usd (MaterialX materials)
    print("\nStep 2: Creating mtl.usd...")
    if texture_folder and os.path.isdir(texture_folder):
        print(f"Texture folder: {texture_folder}")
        # TODO: Call TexToMtlX tool to create materials
        print("Note: Use TexToMtlX tool separately to create MaterialX materials")
        print(f"      Output should be saved as: {mtl_usd_path}")
    else:
        # Create empty mtl.usd
        content = f"""#usda 1.0
(
    defaultPrim = "Materials"
)

def Scope "Materials"
{{
}}
"""
        with open(mtl_usd_path, 'w') as f:
            f.write(content)
        print(f"Created empty mtl.usd: {mtl_usd_path}")

    # Step 3: Create payload.usd
    print("\nStep 3: Creating payload.usd...")
    create_payload_usd(payload_usd_path, asset_name)

    # Step 4: Create main USD file
    print("\nStep 4: Creating main USD file...")
    create_main_usd(main_usd_path, asset_name, texture_variants)

    print(f"\n{'='*60}")
    print(f"KB3D USD Asset Created Successfully!")
    print(f"{'='*60}")
    print(f"Main USD: {main_usd_path}")
    print(f"\nFiles created:")
    print(f"  - {os.path.basename(main_usd_path)}")
    print(f"  - {os.path.basename(payload_usd_path)}")
    print(f"  - {os.path.basename(geo_usd_path)}")
    print(f"  - {os.path.basename(mtl_usd_path)}")
    print()

    return main_usd_path


def build_individual_part_assets(
    parts_folder: str,
    output_base_folder: str,
    match_size: float = 1.0
) -> List[str]:
    """
    Build individual USD assets for each part (Wings, Cargo, Main, etc.)
    with centered matchsize. Use these as standalone root-level assets.

    Args:
        parts_folder: Folder containing part subfolders
        output_base_folder: Base output folder (one subfolder per part created)
        match_size: Target size for matchsize

    Returns:
        List of main USD file paths created
    """
    parts = scan_parts_folder(parts_folder)

    if not parts:
        print(f"No parts found in {parts_folder}")
        return []

    created_assets = []

    print(f"\n{'='*60}")
    print(f"Building Individual Part Assets")
    print(f"{'='*60}")
    print(f"Parts folder: {parts_folder}")
    print(f"Output base: {output_base_folder}")
    print(f"Match size: {match_size}")
    print(f"Found {len(parts)} parts: {[p['name'] for p in parts]}")
    print()

    for part in parts:
        part_name = part['name']
        part_output_folder = os.path.join(output_base_folder, part_name)

        print(f"Building part: {part_name}")

        # Create single-part folder with just this part
        # We'll pass a temporary folder with just this one part
        single_part_folder = part['path']

        try:
            # Build USD asset for this single part with centered matchsize
            main_usd = build_kb3d_usd_asset(
                parts_folder=os.path.dirname(single_part_folder),  # Parent folder
                output_folder=part_output_folder,
                asset_name=part_name,
                match_size=match_size,
                preserve_transforms=False  # Center this part!
            )

            created_assets.append(main_usd)
            print(f"  ✓ Created: {main_usd}\n")

        except Exception as e:
            print(f"  ✗ Error processing {part_name}: {e}\n")
            continue

    print(f"{'='*60}")
    print(f"Created {len(created_assets)} individual part assets")
    print(f"{'='*60}")

    return created_assets


if __name__ == "__main__":
    # Example 1: Build main combined asset (preserve transforms)
    print("\n=== Example 1: Main Combined Asset ===")
    parts_folder = "/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C"
    output_folder = "/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/output/KB3D_SPS_Spaceship_C"
    asset_name = "KB3D_SPS_Spaceship_C"

    main_usd = build_kb3d_usd_asset(
        parts_folder=parts_folder,
        output_folder=output_folder,
        asset_name=asset_name,
        match_size=1.0,
        preserve_transforms=True  # Keep original transforms!
    )

    print(f"\nDone! Load in Houdini with:")
    print(f"  Reference: {main_usd}")

    # Example 2: Build individual part assets (centered matchsize)
    print("\n\n=== Example 2: Individual Part Assets ===")
    individual_output = "/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/output/individual_parts"

    part_assets = build_individual_part_assets(
        parts_folder=parts_folder,
        output_base_folder=individual_output,
        match_size=1.0
    )

    print(f"\nCreated {len(part_assets)} individual part assets:")
    for asset in part_assets:
        print(f"  - {asset}")
