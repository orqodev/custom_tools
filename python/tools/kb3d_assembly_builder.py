"""
KB3D Assembly Builder - Create assembly USD from parts

Creates KB3D-style assembly structure following Mission to Minerva pattern:
1. Individual part USD assets in Models folder (library references)
2. Main assembly USD that references parts with transform overrides

Usage:
    from tools.kb3d_assembly_builder import build_kb3d_assembly

    build_kb3d_assembly(
        parts_source_folder="/path/to/parts",
        merged_bgeo="/path/to/merged.bgeo.sc",
        models_base="/path/to/Models",
        assembly_name="KB3D_SPS_Spaceship_C"
    )
"""

import os
import re
import hou
from typing import List, Dict, Tuple, Optional

def _make_valid_prim_name(name: str) -> str:
    """
    Convert arbitrary string to a valid USD prim name:
    - Replace non [A-Za-z0-9_] with '_'
    - If starts with a digit or not [A-Za-z_], prefix '_'
    - Ensure non-empty, fallback to '_unnamed'
    Prints a warning when modified.
    """
    original = name or ""
    s = re.sub(r"[^A-Za-z0-9_]", "_", original)
    if not s:
        s = "_unnamed"
    if not (s[0].isalpha() or s[0] == "_"):
        s = "_" + s
    # Collapse consecutive underscores
    s = re.sub(r"_+", "_", s)
    if s != original:
        print(f'  WARNING: Renamed prim "{original}" -> "{s}" to satisfy USD naming rules')
    return s


def build_kb3d_assembly(
    parts_source_folder: str,
    merged_bgeo: str,
    models_base: str,
    assembly_name: str,
    materials_folder: Optional[str] = None
) -> str:
    """
    Build KB3D assembly structure from parts and merged BGEO.

    Args:
        parts_source_folder: Folder containing part subfolders (Wings, Cargo, Main)
        merged_bgeo: Path to merged BGEO file with all parts positioned
        models_base: Base Models folder where assets will be created
        assembly_name: Name for the assembly asset
        materials_folder: Optional folder with materials

    Returns:
        Path to main assembly USD file
    """
    print(f"\n{'='*60}")
    print(f"KB3D Assembly Builder")
    print(f"{'='*60}")
    print(f"Parts source: {parts_source_folder}")
    print(f"Merged BGEO: {merged_bgeo}")
    print(f"Models base: {models_base}")
    print(f"Assembly: {assembly_name}")
    print()

    # Step 1: Scan for parts
    print("Step 1: Scanning for parts...")
    parts = _scan_parts(parts_source_folder)
    if not parts:
        print("ERROR: No parts found!")
        return None

    print(f"Found {len(parts)} parts: {[p['name'] for p in parts]}")
    print()

    # Step 2: Extract transforms from merged BGEO
    print("Step 2: Extracting transforms from merged BGEO...")
    transforms = _extract_transforms_from_bgeo(merged_bgeo, parts)
    print()

    # Step 3: Create individual part USD assets in Models folder
    print("Step 3: Creating individual part USD assets...")
    part_assets = _create_part_assets(parts, models_base, materials_folder)
    print()

    # Step 4: Create main assembly USD
    print("Step 4: Creating assembly USD...")
    assembly_path = _create_assembly_usd(
        assembly_name,
        models_base,
        part_assets,
        transforms
    )
    print()

    print(f"{'='*60}")
    print(f"KB3D Assembly Created Successfully!")
    print(f"{'='*60}")
    print(f"Assembly USD: {assembly_path}")
    print()
    print("Structure:")
    print(f"  Models/")
    for part in part_assets:
        print(f"    {part['name']}/")
        print(f"      {part['name']}.usd")
    print(f"    {assembly_name}/")
    print(f"      {assembly_name}.usd  ← Load this!")
    print()

    return assembly_path


def _scan_parts(parts_folder: str) -> List[Dict]:
    """Recursively scan for part folders and their USD files.

    A valid part folder is any directory that contains either:
    - geo.usd or geo.usda, or
    - <foldername>.usd or <foldername>.usda

    Optional files picked up if present: mtl.(usd|usda), payload.(usd|usda)
    The leaf directory name is used as the part name.
    """
    parts: List[Dict] = []

    if not os.path.isdir(parts_folder):
        print(f"ERROR: Parts folder not found: {parts_folder}")
        return parts

    seen_names = set()

    for dirpath, dirnames, filenames in os.walk(parts_folder):
        # Skip hidden directories
        if os.path.basename(dirpath).startswith('.'):
            continue

        base = os.path.basename(dirpath)
        lower_files = {f.lower() for f in filenames}

        # Find geo file
        geo_candidates = [
            'geo.usd', 'geo.usda',
            f'{base}.usd', f'{base}.usda'
        ]
        geo_path = None
        for cand in geo_candidates:
            if cand.lower() in lower_files:
                geo_path = os.path.join(dirpath, next(f for f in filenames if f.lower() == cand.lower()))
                break

        if not geo_path:
            continue  # Not a part folder

        # Optional material and payload
        mtl_path = None
        for cand in ('mtl.usd', 'mtl.usda'):
            if cand in lower_files:
                mtl_path = os.path.join(dirpath, next(f for f in filenames if f.lower() == cand))
                break

        payload_path = None
        for cand in ('payload.usd', 'payload.usda'):
            if cand in lower_files:
                payload_path = os.path.join(dirpath, next(f for f in filenames if f.lower() == cand))
                break

        # Deduplicate by part name; warn on duplicates
        if base in seen_names:
            print(f"  WARNING: Duplicate part name '{base}' at {dirpath} — skipping")
            continue

        seen_names.add(base)
        parts.append({
            'name': base,
            'source_folder': dirpath,
            'geo_usd': geo_path,
            'mtl_usd': mtl_path,
            'payload_usd': payload_path,
        })
        print(f"  Found part: {base} ({dirpath})")

    return parts


def _extract_transforms_from_bgeo(bgeo_path: str, parts: List[Dict]) -> Dict[str, Dict]:
    """
    Extract transform information for each part from merged BGEO.

    Returns dict: {part_name: {'translate': (x,y,z), 'rotate': (x,y,z), 'scale': (x,y,z)}}
    """
    transforms = {}

    # Create temporary LOPS network to analyze BGEO
    stage = hou.node('/stage')
    if stage is None:
        stage = hou.node('/obj').createNode('lopnet', 'temp_stage')

    temp_subnet = stage.createNode('subnet', 'temp_extract_transforms')

    try:
        # Import merged BGEO
        sop_import = temp_subnet.createNode('sopimport', 'import_merged')

        # Create temp SOP network with file node
        obj = hou.node('/obj')
        temp_geo = obj.createNode('geo', 'temp_geo', run_init_scripts=False)
        temp_file = temp_geo.createNode('file', 'file1')
        temp_file.parm('file').set(bgeo_path)

        sop_import.parm('soppath').set(temp_file.path())
        sop_import.parm('primpath').set('/merged')

        # Get stage
        sop_import.cook(force=True)
        usd_stage = sop_import.stage()

        if usd_stage:
            # Try to find parts by name or shop_materialpath
            merged_prim = usd_stage.GetPrimAtPath('/merged')
            if merged_prim and merged_prim.IsValid():
                # Get bounds of entire geometry
                from pxr import UsdGeom, Gf

                # For each part, try to find geometry with matching material
                for part in parts:
                    part_name = part['name']

                    # Try to compute centroid of geometry with this material
                    # This is a simplified approach - in reality we'd need to filter by material
                    bbox = UsdGeom.Imageable(merged_prim).ComputeWorldBound(0, 'default')
                    if bbox:
                        center = bbox.ComputeCentroid()
                        transforms[part_name] = {
                            'translate': (center[0], center[1], center[2]),
                            'rotate': (0, 0, 0),
                            'scale': (1, 1, 1)
                        }
                        print(f"  {part_name}: translate={center}")

        # Clean up temp SOP
        temp_geo.destroy()

    except Exception as e:
        print(f"WARNING: Could not extract transforms: {e}")
        print("Will use identity transforms")

        # Fall back to identity transforms
        for part in parts:
            transforms[part['name']] = {
                'translate': (0, 0, 0),
                'rotate': (0, 0, 0),
                'scale': (1, 1, 1)
            }

    finally:
        # Clean up temp LOPS
        temp_subnet.destroy()

    return transforms


def _create_mtl_wrapper(output_path: str, target_usd_abs_path: str) -> None:
    """Create a tiny USD layer that subLayers the actual materials file.

    This avoids copying materials and preserves all internal references/variants.
    The wrapper is always ASCII usda for readability and stability of diffs.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    except Exception:
        pass

    # Relative path from wrapper to the target materials file
    rel = os.path.relpath(target_usd_abs_path, os.path.dirname(output_path)).replace('\\', '/')

    content = f"""#usda 1.0
(
    subLayers = [
        @{rel}@
    ]
)
"""
    with open(output_path, 'w') as f:
        f.write(content)


def _create_part_assets(
    parts: List[Dict],
    models_base: str,
    materials_folder: Optional[str]
) -> List[Dict]:
    """
    Create individual part USD assets in Models folder.

    Returns list of created assets with their paths.
    """
    part_assets = []

    # Warn if materials_folder likely points at Models (can cause empty/self-referencing mtl.usd)
    try:
        if materials_folder:
            mb = os.path.realpath(models_base)
            mf = os.path.realpath(materials_folder)
            if os.path.commonpath([mb]) == os.path.commonpath([mb, mf]):
                print("WARNING: The selected Materials Folder appears to be the Models base or inside it.\n         This can lead to self-referencing wrappers and empty materials.\n         Prefer selecting the original materials source folder (not Models).")
    except Exception:
        pass

    def _find_material_source(part_name: str, materials_folder: Optional[str], part: Dict, part_output_folder: str) -> Optional[str]:
        """Resolve the best material file to reference for a part.
        Search order:
        1) materials_folder/<part>/mtl.(usd|usda)
        2) materials_folder/Models/<part>/mtl.(usd|usda)
        3) Any folder named <part> under materials_folder that contains mtl.(usd|usda)
        4) Fallback to part['mtl_usd'] if present next to source part
        Also avoid self-referencing materials inside the output Models folder.
        """
        candidates: List[str] = []
        if materials_folder:
            # 1) Direct subfolder
            for cand in ('mtl.usd', 'mtl.usda'):
                candidates.append(os.path.join(materials_folder, part_name, cand))
            # 2) Materials folder might actually be the project root; try Materials/Models layout
            for cand in ('mtl.usd', 'mtl.usda'):
                candidates.append(os.path.join(materials_folder, 'Models', part_name, cand))
            # 3) Recursive search for a folder named <part_name> containing mtl file
            try:
                for dirpath, dirnames, filenames in os.walk(materials_folder):
                    if os.path.basename(dirpath) == part_name:
                        lower = {f.lower() for f in filenames}
                        if 'mtl.usd' in lower or 'mtl.usda' in lower:
                            # Pick .usd first
                            if 'mtl.usd' in lower:
                                fname = next(f for f in filenames if f.lower() == 'mtl.usd')
                            else:
                                fname = next(f for f in filenames if f.lower() == 'mtl.usda')
                            candidates.append(os.path.join(dirpath, fname))
                            break
            except Exception:
                pass
        # 4) Fallback next to source part
        if part.get('mtl_usd'):
            candidates.append(part['mtl_usd'])

        # Resolve first existing candidate that is not inside the output folder (to avoid self-ref)
        for path in candidates:
            if not path or not os.path.exists(path):
                continue
            try:
                out = os.path.realpath(part_output_folder)
                src = os.path.realpath(path)
                # Avoid using a file from the same output folder (self-reference)
                if os.path.commonpath([out, src]) == out:
                    print(f"    WARNING: Skipping material at {path} (inside output folder -> would self-reference)")
                    continue
            except Exception:
                pass
            return path
        return None

    for part in parts:
        part_name = part["name"]
        part_output_folder = os.path.join(models_base, part_name)
        os.makedirs(part_output_folder, exist_ok=True)

        print(f"  Creating {part_name}...")

        # Copy geo.usd to output (rename to part_name.usd for consistency)
        import shutil
        geo_output = os.path.join(part_output_folder, "geo.usd")
        shutil.copy2(part["geo_usd"], geo_output)

        # Create/prepare mtl.usd wrapper that references the source materials file
        mtl_output = None
        mtl_source = _find_material_source(part_name, materials_folder, part, part_output_folder)

        if materials_folder and not mtl_source:
            print(f"    NOTE: No materials found for '{part_name}' under provided materials folder: {materials_folder}")
        # If not found, try to fall back to source mtl (already considered inside helper)

        if mtl_source:
            mtl_output = os.path.join(part_output_folder, "mtl.usd")
            _create_mtl_wrapper(mtl_output, mtl_source)
            rel_info = os.path.relpath(mtl_source, part_output_folder).replace('\\', '/')
            print(f"    Material wrapper created: {mtl_output} -> {rel_info}")
        else:
            print(f"    No materials found for {part_name}")

        # Create payload.usd
        payload_output = os.path.join(part_output_folder, "payload.usd")
        _create_part_payload(payload_output, part_name, has_materials=(mtl_output is not None))

        # Create main part USD
        part_usd_output = os.path.join(part_output_folder, f"{part_name}.usd")
        _create_part_main_usd(part_usd_output, part_name)

        part_assets.append({
            "name": part_name,
            "folder": part_output_folder,
            "usd_path": part_usd_output,
            "has_materials": mtl_output is not None,
        })

        print(f"    Created: {part_usd_output}")

    return part_assets


def _create_part_payload(output_path: str, part_name: str, has_materials: bool):
    """Create payload.usd for individual part."""
    prim_name = _make_valid_prim_name(part_name)
    references = ['@./geo.usd@']
    if has_materials:
        references.insert(0, '@./mtl.usd@')

    references_str = ',\n        '.join(references)

    content = f"""#usda 1.0
(
    defaultPrim = "{prim_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{prim_name}" (
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


def _create_part_main_usd(output_path: str, part_name: str):
    """Create main USD file for individual part."""
    prim_name = _make_valid_prim_name(part_name)
    content = f"""#usda 1.0
(
    defaultPrim = "{prim_name}"
    metersPerUnit = 1
    upAxis = "Y"
)


def "{prim_name}" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "component"
    prepend payload = @./payload.usd@
)
{{
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)


def _create_assembly_usd(
    assembly_name: str,
    models_base: str,
    part_assets: List[Dict],
    transforms: Dict[str, Dict]
) -> str:
    """Create main assembly USD that references parts with transforms."""

    assembly_folder = os.path.join(models_base, assembly_name)
    os.makedirs(assembly_folder, exist_ok=True)

    # Create payload.usd with part references and transforms
    payload_path = os.path.join(assembly_folder, 'payload.usd')
    _create_assembly_payload(payload_path, assembly_name, part_assets, transforms, models_base)

    # Create main assembly USD
    assembly_usd_path = os.path.join(assembly_folder, f'{assembly_name}.usd')
    _create_assembly_main_usd(assembly_usd_path, assembly_name)

    return assembly_usd_path


def _create_assembly_payload(
    output_path: str,
    assembly_name: str,
    part_assets: List[Dict],
    transforms: Dict[str, Dict],
    models_base: str
):
    """Create payload.usd for assembly with part references and transforms."""

    asm_prim = _make_valid_prim_name(assembly_name)

    # Build part references with transforms
    part_defs = []

    for part in part_assets:
        part_name = part['name']
        part_prim = _make_valid_prim_name(part_name)

        # Get relative path from assembly folder to part payload (avoid cycles via main .usd)
        payload_abs_path = os.path.join(part['folder'], 'payload.usd')
        part_rel_path = os.path.relpath(payload_abs_path, os.path.dirname(output_path))
        part_rel_path = part_rel_path.replace('\\', '/')

        # Get transform
        xform = transforms.get(part_name, {
            'translate': (0, 0, 0),
            'rotate': (0, 0, 0),
            'scale': (1, 1, 1)
        })

        translate = xform['translate']
        rotate = xform['rotate']
        scale = xform['scale']

        # Build xformOp list
        xform_ops = []
        if translate != (0, 0, 0):
            xform_ops.append('xformOp:translate')
        if rotate != (0, 0, 0):
            xform_ops.append('xformOp:rotateXYZ')
        if scale != (1, 1, 1):
            xform_ops.append('xformOp:scale')

        # Create part def
        part_def = f"""
    def Xform "{part_prim}" (
        kind = "component"
        prepend payload = @{part_rel_path}@
    )
    {{"""

        if translate != (0, 0, 0):
            part_def += f"""
        double3 xformOp:translate = ({translate[0]}, {translate[1]}, {translate[2]})"""

        if rotate != (0, 0, 0):
            part_def += f"""
        double3 xformOp:rotateXYZ = ({rotate[0]}, {rotate[1]}, {rotate[2]})"""

        if scale != (1, 1, 1):
            part_def += f"""
        double3 xformOp:scale = ({scale[0]}, {scale[1]}, {scale[2]})"""

        if xform_ops:
            xform_ops_str = '", "'.join(xform_ops)
            part_def += f"""
        uniform token[] xformOpOrder = ["{xform_ops_str}"]"""

        part_def += """
    }"""

        part_defs.append(part_def)

    parts_str = '\n'.join(part_defs)

    content = f"""#usda 1.0
(
    defaultPrim = "{asm_prim}"
    metersPerUnit = 1
    upAxis = "Y"
)


def Xform "{asm_prim}" (
    kind = "assembly"
)
{{
{parts_str}
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"  Created assembly payload: {output_path}")


def _create_assembly_main_usd(output_path: str, assembly_name: str):
    """Create main USD file for assembly."""
    prim_name = _make_valid_prim_name(assembly_name)
    content = f"""#usda 1.0
(
    defaultPrim = "{prim_name}"
    metersPerUnit = 1
    upAxis = "Y"
)


def "{prim_name}" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "assembly"
    prepend payload = @./payload.usd@
)
{{
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"  Created assembly USD: {output_path}")


if __name__ == "__main__":
    # Build KB3D assembly from parts
    assembly_usd = build_kb3d_assembly(
        parts_source_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C",
        merged_bgeo="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C.bgeo.sc",
        models_base="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/Models",
        assembly_name="KB3D_SPS_Spaceship_C",
        materials_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/Materials"
    )

    print(f"\nDone! Load in Houdini:")
    print(f"  {assembly_usd}")
    print(f"\nThis assembly references individual parts from the Models library")
    print(f"with transform overrides, following the Mission to Minerva pattern!")
