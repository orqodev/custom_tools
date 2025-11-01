"""
KB3D USD Builder from BGEO

Simpler approach: Use your already-merged BGEO file and materials to create KB3D USD structure.

Usage:
    from tools.kb3d_from_bgeo import build_kb3d_from_bgeo

    build_kb3d_from_bgeo(
        bgeo_file="/path/to/KB3D_SPS_Spaceship_C.bgeo.sc",
        materials_folder="/path/to/Materials",
        output_folder="/path/to/output/KB3D_SPS_Spaceship_C",
        asset_name="KB3D_SPS_Spaceship_C"
    )
"""

import hou
import os
import shutil


def build_kb3d_from_bgeo(
    bgeo_file: str,
    materials_folder: str,
    output_folder: str,
    asset_name: str
) -> str:
    """
    Build KB3D USD asset from existing BGEO and materials.

    Args:
        bgeo_file: Path to merged BGEO file with all parts
        materials_folder: Path to Materials folder with mtl.usd files
        output_folder: Output folder for USD asset
        asset_name: Name for the asset

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
    print(f"Building KB3D USD Asset from BGEO: {asset_name}")
    print(f"{'='*60}")
    print(f"BGEO file: {bgeo_file}")
    print(f"Materials: {materials_folder}")
    print(f"Output: {output_folder}")
    print()

    # Step 1: Convert BGEO to USD via LOPS
    print("Step 1: Converting BGEO to geo.usd...")

    obj = hou.node('/obj')

    # Create SOP geo node with file import
    sop_geo = obj.createNode('geo', 'kb3d_bgeo_import')
    sop_geo.moveToGoodPosition()
    file_node = sop_geo.createNode('file', 'load_bgeo')
    file_node.parm('file').set(bgeo_file)
    null_out = sop_geo.createNode('null', 'OUT')
    null_out.setInput(0, file_node)
    null_out.setDisplayFlag(True)
    null_out.setRenderFlag(True)
    sop_geo.layoutChildren()

    # Create LOPS network
    lopnet = obj.createNode('lopnet', 'kb3d_to_usd')
    lopnet.moveToGoodPosition()

    # Import SOP geometry
    sop_import = lopnet.createNode('sopimport', 'import_bgeo')
    sop_import.parm('soppath').set(null_out.path())
    sop_import.parm('pathprefix').set(f'/{asset_name}')

    # USD ROP for geo
    geo_rop = lopnet.createNode('usd_rop', 'export_geo')
    geo_rop.setInput(0, sop_import)
    geo_rop.parm('lopoutput').set(geo_usd_path)
    geo_rop.parm('trange').set(0)

    lopnet.layoutChildren()

    # Execute export
    print(f"Exporting to: {geo_usd_path}")
    geo_rop.parm('execute').pressButton()

    # Clean up
    sop_geo.destroy()

    # Step 2: Copy or merge materials
    print("\nStep 2: Processing materials...")

    if materials_folder and os.path.isdir(materials_folder):
        # Look for mtl.usd files in the materials folder
        mtl_files = []
        for root, dirs, files in os.walk(materials_folder):
            for file in files:
                if file == 'mtl.usd' or file == 'mtl.usda':
                    mtl_files.append(os.path.join(root, file))

        if mtl_files:
            print(f"Found {len(mtl_files)} material USD files")
            # For now, copy the first one
            # TODO: Merge multiple material files
            shutil.copy(mtl_files[0], mtl_usd_path)
            print(f"Copied materials to: {mtl_usd_path}")
        else:
            # Create empty mtl.usd
            _create_empty_mtl(mtl_usd_path)
    else:
        _create_empty_mtl(mtl_usd_path)

    # Step 3: Create payload.usd
    print("\nStep 3: Creating payload.usd...")
    _create_payload_usd(payload_usd_path, asset_name)

    # Step 4: Create main USD
    print("\nStep 4: Creating main USD file...")
    _create_main_usd(main_usd_path, asset_name)

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

    # Clean up lopnet
    lopnet.destroy()

    return main_usd_path


def _create_empty_mtl(output_path: str):
    """Create empty mtl.usd."""
    content = f"""#usda 1.0
(
    defaultPrim = "Materials"
)

def Scope "Materials"
{{
}}
"""
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created empty mtl.usd: {output_path}")


def _create_payload_usd(output_path: str, asset_name: str):
    """Create payload.usd."""
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


def _create_main_usd(output_path: str, asset_name: str):
    """Create main USD file."""
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
        string texture_variant = "png4k"
    }}
    prepend variantSets = "texture_variant"
)
{{
    variantSet "texture_variant" = {{
        "png4k" {{

        }}
        "png2k" {{

        }}
        "png1k" {{

        }}
        "jpg4k" {{

        }}
        "jpg2k" {{

        }}
        "jpg1k" {{

        }}
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


if __name__ == "__main__":
    # Example usage
    main_usd = build_kb3d_from_bgeo(
        bgeo_file="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C.bgeo.sc",
        materials_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/Materials/",
        output_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/Models/KB3D_SPS_Spaceship_C_CLONE",
        asset_name="KB3D_SPS_Spaceship_C"
    )

    print(f"\nDone! Load in Houdini:")
    print(f"  {main_usd}")
