"""
KB3D USD Builder using Part References

Creates KB3D-style USD that REFERENCES individual part USD files (like the original).
This keeps parts modular and reusable in the library.

Usage:
    from tools.kb3d_reference_builder import build_kb3d_with_references

    build_kb3d_with_references(
        parts_base_folder="/path/to/parts/KB3D_SPS_Spaceship_C",
        output_folder="/path/to/output/KB3D_SPS_Spaceship_C",
        asset_name="KB3D_SPS_Spaceship_C"
    )
"""

import os
from typing import List, Dict


def build_kb3d_with_references(
    parts_base_folder: str,
    output_folder: str,
    asset_name: str
) -> str:
    """
    Build KB3D USD asset that references individual part USD files.

    Args:
        parts_base_folder: Folder containing part subfolders (Wings, Cargo, Main, etc.)
        output_folder: Output folder for main USD asset
        asset_name: Name for the asset

    Returns:
        Path to main USD file
    """
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Scan for parts
    parts = []
    if os.path.isdir(parts_base_folder):
        for item in os.listdir(parts_base_folder):
            item_path = os.path.join(parts_base_folder, item)
            if os.path.isdir(item_path):
                # Check if it has a main USD file
                usd_file = os.path.join(item_path, f'{item}.usd')
                if not os.path.exists(usd_file):
                    # Try geo.usd
                    usd_file = os.path.join(item_path, 'geo.usd')

                if os.path.exists(usd_file):
                    parts.append({
                        'name': item,
                        'path': item_path,
                        'usd': usd_file
                    })

    if not parts:
        print(f"No parts found in {parts_base_folder}")
        return None

    print(f"\n{'='*60}")
    print(f"Building KB3D USD Asset: {asset_name}")
    print(f"{'='*60}")
    print(f"Parts folder: {parts_base_folder}")
    print(f"Output: {output_folder}")
    print(f"Found {len(parts)} parts: {[p['name'] for p in parts]}")
    print()

    # Create paths
    payload_usd_path = os.path.join(output_folder, 'payload.usd')
    main_usd_path = os.path.join(output_folder, f'{asset_name}.usd')

    # Step 1: Create payload.usd that references all part USD files
    print("Step 1: Creating payload.usd with part references...")
    _create_payload_with_references(payload_usd_path, asset_name, parts, parts_base_folder)

    # Step 2: Create main USD
    print("\nStep 2: Creating main USD file...")
    _create_main_usd(main_usd_path, asset_name)

    print(f"\n{'='*60}")
    print(f"KB3D USD Asset Created Successfully!")
    print(f"{'='*60}")
    print(f"Main USD: {main_usd_path}")
    print(f"\nStructure:")
    print(f"  {asset_name}.usd          ← Load this!")
    print(f"  payload.usd               ← References all parts")
    print(f"  ../parts/Wings/geo.usd    ← Individual parts")
    print(f"  ../parts/Cargo/geo.usd")
    print(f"  ../parts/Main/geo.usd")
    print()

    return main_usd_path


def _create_payload_with_references(
    output_path: str,
    asset_name: str,
    parts: List[Dict],
    parts_base_folder: str
):
    """Create payload.usd that references all part USD files."""

    # Create references list
    references = []
    for part in parts:
        # Get relative path from output folder to part USD
        rel_path = os.path.relpath(part['usd'], os.path.dirname(output_path))
        # Convert to forward slashes for USD
        rel_path = rel_path.replace('\\', '/')
        references.append(f'        @./{rel_path}@</{part["name"]}>')

    references_str = ',\n'.join(references)

    content = f"""#usda 1.0
(
    defaultPrim = "{asset_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "{asset_name}" (
    kind = "component"
    prepend references = [
{references_str}
    ]
)
{{
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created payload.usd: {output_path}")
    print(f"  References {len(parts)} parts")


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
    # Build KB3D USD that references individual parts
    main_usd = build_kb3d_with_references(
        parts_base_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C",
        output_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/Models/KB3D_SPS_Spaceship_C_CLONE",
        asset_name="KB3D_SPS_Spaceship_C"
    )

    print(f"\nDone! Load in Houdini:")
    print(f"  {main_usd}")
    print(f"\nThe asset references the individual part USD files,")
    print(f"keeping them modular just like the original KB3D library!")
