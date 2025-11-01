"""
KB3D Assembly Cloner - Extract transforms from original and apply to cloned parts

Reads original KB3D assembly USD, extracts all part transforms,
and creates new assembly USD that references your cloned parts with same transforms.
"""

import os
import re
from typing import Dict, List, Tuple
from pxr import Usd, UsdGeom, Gf


def clone_kb3d_assembly_with_transforms(
    original_assembly_usd: str,
    cloned_parts_folder: str,
    models_base: str,
    output_assembly_name: str = None
) -> str:
    """
    Clone KB3D assembly by extracting transforms from original and applying to new parts.

    Args:
        original_assembly_usd: Path to original KB3D assembly USD (e.g. KB3D_MTM_BldgLgCommsArray_A.usd)
        cloned_parts_folder: Folder with your cloned part subfolders
        models_base: Base Models folder where assembly will be created
        output_assembly_name: Name for output assembly (defaults to same as original)

    Returns:
        Path to created assembly USD
    """
    print(f"\n{'='*70}")
    print(f"KB3D Assembly Cloner")
    print(f"{'='*70}")
    print(f"Original: {original_assembly_usd}")
    print(f"Parts: {cloned_parts_folder}")
    print(f"Output: {models_base}")
    print()

    # Extract asset name from original if not provided
    if output_assembly_name is None:
        output_assembly_name = os.path.splitext(os.path.basename(original_assembly_usd))[0]

    # Step 1: Extract transforms from original assembly
    print("Step 1: Extracting transforms from original assembly...")
    transforms = _extract_transforms_from_assembly(original_assembly_usd)
    print(f"  Found {len(transforms)} part instances")
    print()

    # Step 2: Scan cloned parts
    print("Step 2: Scanning cloned parts...")
    available_parts = _scan_cloned_parts(cloned_parts_folder)
    print(f"  Found {len(available_parts)} part types")
    print()

    # Step 3: Match transforms to available parts
    print("Step 3: Matching transforms to available parts...")
    matched_instances = _match_transforms_to_parts(transforms, available_parts, cloned_parts_folder)
    print(f"  Matched {len(matched_instances)} instances")
    print()

    # Step 4: Create individual part USD assets in Models
    print("Step 4: Creating part USD assets in Models...")
    part_assets = _create_part_usd_assets(available_parts, cloned_parts_folder, models_base)
    print()

    # Step 5: Create assembly USD
    print("Step 5: Creating assembly USD...")
    assembly_path = _create_assembly_with_transforms(
        output_assembly_name,
        models_base,
        matched_instances,
        part_assets
    )
    print()

    print(f"{'='*70}")
    print(f"Assembly Created Successfully!")
    print(f"{'='*70}")
    print(f"Assembly: {assembly_path}")
    print(f"Parts: {len(part_assets)} unique types")
    print(f"Instances: {len(matched_instances)} total instances")
    print()

    return assembly_path


def _extract_transforms_from_assembly(usd_path: str) -> Dict:
    """Extract all part transforms from original assembly USD."""
    stage = Usd.Stage.Open(usd_path)
    if not stage:
        print(f"ERROR: Could not open USD: {usd_path}")
        return {}

    transforms = {}

    # Get default prim
    default_prim = stage.GetDefaultPrim()
    if not default_prim:
        print("ERROR: No default prim in USD")
        return {}

    # Recursively find all prims with references and transforms
    def _extract_prim_info(prim, parent_path=""):
        if not prim.IsValid():
            return

        prim_name = prim.GetName()
        full_path = f"{parent_path}/{prim_name}" if parent_path else prim_name

        # Check if this prim has a reference
        refs = prim.GetPrimStack()
        has_reference = False
        ref_path = None

        for spec in refs:
            if spec.referenceList.prependedItems:
                has_reference = True
                ref_path = spec.referenceList.prependedItems[0].assetPath
                break

        if has_reference:
            # Extract transform
            xformable = UsdGeom.Xformable(prim)
            if xformable:
                # Get local transform
                local_xform = xformable.GetLocalTransformation()

                # Decompose into translate, rotate, scale
                translate = local_xform.ExtractTranslation()
                rotation = local_xform.ExtractRotation()
                rotation_xyz = rotation.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())

                # Extract scale by removing rotation and translation
                scale_matrix = Gf.Matrix4d(1.0)
                scale_matrix.SetTranslateOnly(Gf.Vec3d(0))
                scale_matrix.SetRotateOnly(Gf.Rotation())

                # Simple scale extraction from diagonal
                scale = Gf.Vec3d(
                    Gf.Vec3d(local_xform[0][0], local_xform[0][1], local_xform[0][2]).GetLength(),
                    Gf.Vec3d(local_xform[1][0], local_xform[1][1], local_xform[1][2]).GetLength(),
                    Gf.Vec3d(local_xform[2][0], local_xform[2][1], local_xform[2][2]).GetLength()
                )

                # Determine part type from reference or prim name
                part_type = _extract_part_type_from_name(prim_name, ref_path)

                transforms[full_path] = {
                    'prim_name': prim_name,
                    'part_type': part_type,
                    'reference': ref_path,
                    'translate': (translate[0], translate[1], translate[2]),
                    'rotate': (rotation_xyz[0], rotation_xyz[1], rotation_xyz[2]),
                    'scale': (scale[0], scale[1], scale[2]),
                    'local_matrix': local_xform
                }

        # Recurse into children
        for child in prim.GetChildren():
            _extract_prim_info(child, full_path)

    _extract_prim_info(default_prim)

    return transforms


def _extract_part_type_from_name(prim_name: str, ref_path: str) -> str:
    """
    Extract base part type from prim name or reference path.

    Examples:
        "KB3D_MTM_BldgLgCommsArray_A_SmallModuleD_002" -> "SmallModuleD"
        "SatelliteArmA" -> "SatelliteArmA"
    """
    # Try to find pattern like PartName_### at end
    match = re.search(r'([A-Za-z]+[A-Z]?)_?\d*$', prim_name)
    if match:
        return match.group(1)

    # Fall back to full prim name
    return prim_name


def _scan_cloned_parts(parts_folder: str) -> Dict[str, str]:
    """
    Scan cloned parts folder and return dict of {part_type: folder_path}.

    Returns dict like: {'SmallModuleD': '/path/to/SmallModuleD', ...}
    """
    parts = {}

    if not os.path.isdir(parts_folder):
        print(f"ERROR: Parts folder not found: {parts_folder}")
        return parts

    for item in os.listdir(parts_folder):
        item_path = os.path.join(parts_folder, item)
        if os.path.isdir(item_path):
            # Check if it has geo.usda or geo.usd
            if os.path.exists(os.path.join(item_path, 'geo.usda')) or \
               os.path.exists(os.path.join(item_path, 'geo.usd')):
                parts[item] = item_path

    return parts


def _match_transforms_to_parts(
    transforms: Dict,
    available_parts: Dict[str, str],
    parts_folder: str
) -> List[Dict]:
    """Match extracted transforms to available part folders."""
    matched = []

    for full_path, xform_data in transforms.items():
        part_type = xform_data['part_type']

        # Try exact match first
        if part_type in available_parts:
            matched.append({
                'instance_name': xform_data['prim_name'],
                'part_type': part_type,
                'part_folder': available_parts[part_type],
                'translate': xform_data['translate'],
                'rotate': xform_data['rotate'],
                'scale': xform_data['scale']
            })
            continue

        # Try fuzzy match (e.g., SmallModuleD might be in available_parts as SmallModuleA)
        # Look for parts that start with similar prefix
        base_name = re.sub(r'[A-Z]$', '', part_type)  # Remove trailing letter
        matches = [p for p in available_parts.keys() if p.startswith(base_name)]

        if matches:
            # Use first match
            matched_part = matches[0]
            matched.append({
                'instance_name': xform_data['prim_name'],
                'part_type': matched_part,
                'part_folder': available_parts[matched_part],
                'translate': xform_data['translate'],
                'rotate': xform_data['rotate'],
                'scale': xform_data['scale']
            })
        else:
            print(f"  WARNING: No match for part type '{part_type}'")

    return matched


def _create_part_usd_assets(
    available_parts: Dict[str, str],
    parts_folder: str,
    models_base: str
) -> Dict[str, str]:
    """
    Create individual part USD assets in Models folder.

    Returns dict: {part_type: path_to_usd}
    """
    import shutil

    part_assets = {}

    for part_type, source_folder in available_parts.items():
        # Create output folder in Models
        output_folder = os.path.join(models_base, part_type)
        os.makedirs(output_folder, exist_ok=True)

        # Copy geo.usd/geo.usda
        geo_src = None
        if os.path.exists(os.path.join(source_folder, 'geo.usda')):
            geo_src = os.path.join(source_folder, 'geo.usda')
            geo_ext = '.usda'
        elif os.path.exists(os.path.join(source_folder, 'geo.usd')):
            geo_src = os.path.join(source_folder, 'geo.usd')
            geo_ext = '.usd'

        if geo_src:
            geo_dst = os.path.join(output_folder, f'geo{geo_ext}')
            shutil.copy2(geo_src, geo_dst)

        # Copy mtl if exists
        for mtl_name in ['mtl.usda', 'mtl.usd']:
            mtl_src = os.path.join(source_folder, mtl_name)
            if os.path.exists(mtl_src):
                shutil.copy2(mtl_src, os.path.join(output_folder, mtl_name))
                break

        # Create payload.usd
        payload_path = os.path.join(output_folder, 'payload.usd')
        _create_simple_payload(payload_path, part_type)

        # Create main part USD
        part_usd = os.path.join(output_folder, f'{part_type}.usd')
        _create_simple_part_usd(part_usd, part_type)

        part_assets[part_type] = part_usd
        print(f"  Created: {part_type}")

    return part_assets


def _create_simple_payload(output_path: str, part_name: str):
    """Create simple payload.usd for part."""
    content = f"""#usda 1.0
(
    defaultPrim = "{part_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{part_name}" (
    kind = "component"
    prepend references = [@./geo.usda@, @./mtl.usda@]
)
{{
}}
"""
    with open(output_path, 'w') as f:
        f.write(content)


def _create_simple_part_usd(output_path: str, part_name: str):
    """Create main USD for part."""
    content = f"""#usda 1.0
(
    defaultPrim = "{part_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{part_name}" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "component"
    prepend payload = @./payload.usd@
)
{{
}}
"""
    with open(output_path, 'w') as f:
        f.write(content)


def _create_assembly_with_transforms(
    assembly_name: str,
    models_base: str,
    instances: List[Dict],
    part_assets: Dict[str, str]
) -> str:
    """Create assembly USD with all part instances and transforms."""
    assembly_folder = os.path.join(models_base, assembly_name)
    os.makedirs(assembly_folder, exist_ok=True)

    # Create payload with all instances
    payload_path = os.path.join(assembly_folder, 'payload.usd')
    _write_assembly_payload(payload_path, assembly_name, instances, assembly_folder)

    # Create main assembly USD
    assembly_usd = os.path.join(assembly_folder, f'{assembly_name}.usd')
    _write_assembly_main_usd(assembly_usd, assembly_name)

    return assembly_usd


def _write_assembly_payload(
    output_path: str,
    assembly_name: str,
    instances: List[Dict],
    assembly_folder: str
):
    """Write payload.usd with all part instances."""

    # Build instance defs
    instance_defs = []

    for instance in instances:
        part_type = instance['part_type']
        instance_name = instance['instance_name']
        translate = instance['translate']
        rotate = instance['rotate']
        scale = instance['scale']

        # Get relative path to part USD
        part_usd = os.path.join(os.path.dirname(assembly_folder), part_type, f'{part_type}.usd')
        part_rel = os.path.relpath(part_usd, assembly_folder).replace('\\', '/')

        # Build xformOp list
        xform_ops = []
        instance_def = f'\n    def Xform "{instance_name}" (\n'
        instance_def += f'        kind = "component"\n'
        instance_def += f'        prepend references = @{part_rel}@\n'
        instance_def += f'    )\n    {{'

        if translate != (0, 0, 0):
            instance_def += f'\n        double3 xformOp:translate = ({translate[0]}, {translate[1]}, {translate[2]})'
            xform_ops.append('xformOp:translate')

        if rotate != (0, 0, 0):
            instance_def += f'\n        double3 xformOp:rotateXYZ = ({rotate[0]}, {rotate[1]}, {rotate[2]})'
            xform_ops.append('xformOp:rotateXYZ')

        if scale != (1, 1, 1) and scale != (0, 0, 0):
            instance_def += f'\n        double3 xformOp:scale = ({scale[0]}, {scale[1]}, {scale[2]})'
            xform_ops.append('xformOp:scale')

        if xform_ops:
            ops_str = '", "'.join(xform_ops)
            instance_def += f'\n        uniform token[] xformOpOrder = ["{ops_str}"]'

        instance_def += '\n    }'

        instance_defs.append(instance_def)

    instances_str = '\n'.join(instance_defs)

    content = f"""#usda 1.0
(
    defaultPrim = "{assembly_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "{assembly_name}" (
    kind = "assembly"
)
{{{instances_str}
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"  Wrote payload: {output_path}")
    print(f"    {len(instances)} instances")


def _write_assembly_main_usd(output_path: str, assembly_name: str):
    """Write main assembly USD."""
    content = f"""#usda 1.0
(
    defaultPrim = "{assembly_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{assembly_name}" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "assembly"
    prepend payload = @./payload.usd@
)
{{
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"  Wrote main USD: {output_path}")


if __name__ == "__main__":
    # Clone Mission to Minerva assembly
    assembly_usd = clone_kb3d_assembly_with_transforms(
        original_assembly_usd="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/Models/KB3D_MTM_BldgLgCommsArray_A/KB3D_MTM_BldgLgCommsArray_A.usd",
        cloned_parts_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/kb3d_clone/geo/KB3D_MTM_BldgLgCommsArray_A",
        models_base="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/kb3d_clone/Models",
        output_assembly_name="KB3D_MTM_BldgLgCommsArray_A"
    )

    print(f"\nDone! Load in Houdini:")
    print(f"  {assembly_usd}")
