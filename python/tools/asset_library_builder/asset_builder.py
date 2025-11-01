"""
Asset Library Builder - Build USD asset assemblies from individual part USD/BGEO files

This builder creates production-ready USD asset libraries:
- Input: Folder with part subfolders (each containing geo.usd, payload.usd, etc.)
- Output: Proper USD structure (payload → geo + mtl)

Usage:
    from tools.asset_library_builder.asset_builder import build_from_parts

    build_from_parts(
        parts_folder="/path/to/parts/MyAsset",
        asset_name="MyAsset",
        models_folder="/path/to/Models",
        materials_folder="/path/to/Materials"
    )
"""

import os
import hou
from typing import List, Dict, Set, Optional, Callable
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def build_from_parts(
    parts_folder: str,
    asset_name: str,
    models_folder: str,
    materials_folder: str,
    texture_variants: List[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> str:
    """
    Build proper USD assembly from individual part folders.

    Args:
        parts_folder: Folder containing part subfolders
                     (e.g., /parts/MyAsset/)
        asset_name: Name for the asset
        models_folder: Base Models folder
        materials_folder: Materials folder for material references
        texture_variants: List of texture variants (default: ["jpg1k", "jpg2k", "png4k"])
        progress_callback: Optional callback(percent: int, message: str) for progress updates

    Returns:
        Path to created payload.usd
    """
    if texture_variants is None:
        texture_variants = ["jpg1k", "jpg2k", "png4k"]

    def _report_progress(percent: int, message: str):
        """Report progress to callback and console."""
        print(message)
        if progress_callback:
            progress_callback(percent, message)

    _report_progress(0, f"\n{'='*80}")
    _report_progress(0, f"Asset Library Builder")
    _report_progress(0, f"{'='*80}")
    _report_progress(0, f"Asset: {asset_name}")
    _report_progress(0, f"Parts: {parts_folder}")
    _report_progress(0, f"Models: {models_folder}")
    _report_progress(0, f"Materials: {materials_folder}")
    _report_progress(0, "")

    # Create asset folder
    asset_folder = os.path.join(models_folder, asset_name)
    os.makedirs(asset_folder, exist_ok=True)

    # Step 1: Scan parts folder (0-10%)
    _report_progress(5, "Step 1/6: Scanning parts...")
    parts = _scan_parts_folder(parts_folder)
    _report_progress(10, f"  Found {len(parts)} parts")

    if not parts:
        raise RuntimeError(f"No parts found in folder: {parts_folder}")

    # Step 2: Scan materials from parts (10-20%)
    _report_progress(15, "Step 2/6: Scanning materials from parts...")
    materials = _scan_materials_from_parts(parts, materials_folder, progress_callback)
    _report_progress(20, f"  Found {len(materials)} unique materials")

    # Step 3: Create geo.usd by merging all parts (20-50%)
    _report_progress(25, "Step 3/6: Creating geo.usd...")
    geo_path = os.path.join(asset_folder, "geo.usd")
    _create_geo_from_parts(parts, geo_path, asset_name, parts_folder, materials, progress_callback)
    _report_progress(50, f"  Created: {geo_path}")

    # Step 4: Create mtl.usd with material references and variants (50-70%)
    _report_progress(55, "Step 4/6: Creating mtl.usd...")
    mtl_path = os.path.join(asset_folder, "mtl.usd")
    _create_mtl_usd(mtl_path, asset_name, materials, materials_folder, texture_variants, progress_callback)
    _report_progress(70, f"  Created: {mtl_path}")

    # Step 5: Create payload.usd (70-85%)
    _report_progress(75, "Step 5/6: Creating payload.usd...")
    payload_path = os.path.join(asset_folder, "payload.usd")
    _create_payload_usd(payload_path, asset_name)
    _report_progress(85, f"  Created: {payload_path}")

    # Step 6: Create main asset.usd (85-100%)
    _report_progress(90, "Step 6/6: Creating main asset USD...")
    main_usd_path = os.path.join(asset_folder, f"{asset_name}.usd")
    _create_main_usd(main_usd_path, asset_name)
    _report_progress(95, f"  Created: {main_usd_path}")

    _report_progress(100, "")
    _report_progress(100, f"{'='*80}")
    _report_progress(100, f"Assembly Created Successfully!")
    _report_progress(100, f"{'='*80}")
    _report_progress(100, f"Payload: {payload_path}")
    _report_progress(100, f"Geo: {geo_path}")
    _report_progress(100, f"Mtl: {mtl_path}")
    _report_progress(100, f"Materials: {len(materials)}")
    _report_progress(100, "")

    return payload_path


def _scan_parts_folder(parts_folder: str) -> List[Dict]:
    """
    Scan parts folder and find all part subfolders.

    Returns list of dicts with part info:
    [
        {
            'name': 'PartA',
            'folder': '/path/to/PartA',
            'geo_usd': '/path/to/PartA/geo.usd',
            'bgeo': '/path/to/PartA/PartA.bgeo.sc',
            'payload': '/path/to/PartA/payload.usd'
        },
        ...
    ]
    """
    parts = []

    if not os.path.exists(parts_folder):
        print(f"ERROR: Parts folder not found: {parts_folder}")
        return parts

    for item in os.listdir(parts_folder):
        part_path = os.path.join(parts_folder, item)

        if not os.path.isdir(part_path):
            continue

        # Check for geo files
        geo_usd = os.path.join(part_path, "geo.usd")
        geo_usda = os.path.join(part_path, "geo.usda")
        bgeo = os.path.join(part_path, f"{item}.bgeo.sc")
        bgeo_alt = os.path.join(part_path, f"{item}.bgeo")
        payload = os.path.join(part_path, "payload.usd")
        payload_alt = os.path.join(part_path, "payload.usda")

        # Prefer USD over BGEO
        geo_file = None
        if os.path.exists(geo_usd):
            geo_file = geo_usd
        elif os.path.exists(geo_usda):
            geo_file = geo_usda
        elif os.path.exists(bgeo):
            geo_file = bgeo
        elif os.path.exists(bgeo_alt):
            geo_file = bgeo_alt

        if geo_file:
            part_info = {
                'name': item,
                'folder': part_path,
                'geo_file': geo_file,
                'payload': payload if os.path.exists(payload) else (payload_alt if os.path.exists(payload_alt) else None)
            }
            parts.append(part_info)

    return sorted(parts, key=lambda p: p['name'])


def _extract_mesh_names_from_usd(usd_file_path: str) -> Set[str]:
    """
    Extract all mesh/prim names from a USD file.

    Args:
        usd_file_path: Path to USD file

    Returns:
        Set of mesh names
    """
    mesh_names = set()

    try:
        stage = Usd.Stage.Open(usd_file_path)
        if stage:
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    # Get the prim name (last component of path)
                    mesh_name = prim.GetName()
                    if mesh_name:
                        mesh_names.add(mesh_name)
    except Exception as e:
        print(f"    Warning: Could not extract mesh names from {usd_file_path}: {e}")

    return mesh_names


def _find_matching_materials(
    material_names: Set[str],
    materials_folder: str
) -> Set[str]:
    """
    Find matching material folders for the given material names.
    Uses mesh names directly as material names (no conversion).

    Args:
        material_names: Set of material names to match (from mesh names)
        materials_folder: Path to Materials folder

    Returns:
        Set of matched material names
    """
    matches = set()

    if not os.path.exists(materials_folder):
        print(f"WARNING: Materials folder not found: {materials_folder}")
        return matches

    # Get all available material folders (case-insensitive lookup)
    available_materials = {}
    for item in os.listdir(materials_folder):
        item_path = os.path.join(materials_folder, item)
        if os.path.isdir(item_path):
            # Normalize name for matching (case-insensitive)
            available_materials[item.lower()] = item

    # Match each requested material
    for mat_name in material_names:
        mat_lower = mat_name.lower()

        # Try exact match first (case-insensitive)
        if mat_lower in available_materials:
            actual_name = available_materials[mat_lower]
            mat_folder = os.path.join(materials_folder, actual_name)

            # Check if material USD exists
            mat_usd = os.path.join(mat_folder, f"{actual_name}.usd")
            if os.path.exists(mat_usd):
                matches.add(actual_name)
            else:
                print(f"  WARNING: Material USD not found: {mat_usd}")
        else:
            print(f"  WARNING: Material folder not found for: {mat_name}")

    return matches


def _scan_materials_from_parts(
    parts: List[Dict],
    materials_folder: str,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Set[str]:
    """
    Scan all part files and extract material names from mesh names.
    Uses mesh names directly as material names (no conversion).
    Matches against Materials folder (case-insensitive).
    """
    mesh_names = set()
    total = len(parts)

    # Step 1: Extract all mesh names from parts
    for i, part in enumerate(parts):
        geo_file = part['geo_file']

        # Report progress
        if progress_callback:
            percent = 10 + int((i / total) * 10)  # 10-20% range
            progress_callback(percent, f"  Scanning meshes from part {i+1}/{total}: {part['name']}")

        # Only scan USD files
        if geo_file.endswith(('.usd', '.usda', '.usdc')):
            try:
                part_mesh_names = _extract_mesh_names_from_usd(geo_file)
                mesh_names.update(part_mesh_names)
            except Exception as e:
                print(f"    Warning: Could not extract mesh names from {geo_file}: {e}")

    print(f"  Found {len(mesh_names)} unique mesh names")

    # Step 2: Match against Materials folder (use mesh names directly)
    matched_materials = _find_matching_materials(mesh_names, materials_folder)

    print(f"  Matched {len(matched_materials)} materials in library")

    # Return matched material names
    return matched_materials


def _create_geo_from_parts(
    parts: List[Dict],
    output_path: str,
    asset_name: str,
    parts_folder: str,
    materials: Set[str],
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> None:
    """
    Create geo.usd by merging all part USD/BGEO files in LOPS.
    Creates material bindings by assigning materials based on mesh names.
    Uses mesh names directly as material names (no conversion).
    """

    # Create LOPS network
    obj = hou.node("/obj")
    stage_node = obj.createNode("lopnet", f"temp_{asset_name}_geo_builder")

    try:
        # Create root prim using primitive node
        root = stage_node.createNode("primitive", "add_root")
        root.parm("primpath").set(f"/{asset_name}")
        root.parm("primtype").set("Xform")

        current_node = root
        total_parts = len(parts)

        # Import each part (20-43% progress range)
        for i, part in enumerate(parts):
            part_name = part['name']
            geo_file = part['geo_file']

            # Report progress
            if progress_callback:
                percent = 20 + int((i / total_parts) * 23)
                progress_callback(percent, f"  Importing part {i+1}/{total_parts}: {part_name}")

            # Import part geometry
            if geo_file.endswith('.bgeo') or geo_file.endswith('.bgeo.sc'):
                # Import BGEO via SOP Import
                sop_import = stage_node.createNode("sopimport", f"import_{part_name}")
                sop_import.setInput(0, current_node)
                sop_import.parm("soppath").set(geo_file)
                sop_import.parm("pathprefix").set(f"/{asset_name}")
                current_node = sop_import

            else:
                # Import USD via Reference
                ref = stage_node.createNode("reference", f"ref_{part_name}")
                ref.setInput(0, current_node)
                ref.parm("filepath1").set(geo_file)
                ref.parm("primpath1").set(f"/{asset_name}/{part_name}")
                current_node = ref

        # Create material bindings (43-45% progress)
        if progress_callback:
            progress_callback(43, "  Creating material bindings...")

        # Use assignmaterial node to bind based on prim names
        assign_mat = stage_node.createNode("assignmaterial", "bind_materials")
        assign_mat.setInput(0, current_node)

        # Build assignment rules: for each material, assign to prims with matching names
        # Since mesh names = material names (no conversion), just match directly
        assignment_rules = []
        for mat_name in sorted(materials):
            # Pattern matches any mesh with this name (case-insensitive via *)
            prim_pattern = f"*/{mat_name}"
            material_path = f"/{asset_name}/mtl/{mat_name}"

            assignment_rules.append(f"{prim_pattern} -> {material_path}")

        # Set assignment rules on the node
        if assignment_rules:
            assign_mat.parm("num_bindings").set(len(assignment_rules))
            for idx, rule in enumerate(assignment_rules, start=1):
                parts_rule = rule.split(" -> ")
                if len(parts_rule) == 2:
                    assign_mat.parm(f"primpattern{idx}").set(parts_rule[0])
                    assign_mat.parm(f"matspecpath{idx}").set(parts_rule[1])

        current_node = assign_mat

        # Create material scope (45% progress)
        if progress_callback:
            progress_callback(45, f"  Adding material scope with {len(materials)} materials")

        mtl_scope = stage_node.createNode("scope", "add_mtl_scope")
        mtl_scope.setInput(0, current_node)
        mtl_scope.parm("primpath").set(f"/{asset_name}/mtl")

        # Create individual material prims (45-48% progress)
        current_node = mtl_scope
        total_mats = len(materials)
        for i, mat_name in enumerate(sorted(materials)):
            # Sanitize material name for node name
            safe_name = mat_name.replace('-', '_').replace('.', '_')[:50]

            mat_prim = stage_node.createNode("primitive", f"mat_{safe_name}")
            mat_prim.setInput(0, current_node)

            # Check if parameter exists before setting
            primpath_parm = mat_prim.parm("primpath")
            if primpath_parm is None:
                print(f"    ERROR: primpath parameter not found on primitive node!")
                break
            primpath_parm.set(f"/{asset_name}/mtl/{mat_name}")

            primtype_parm = mat_prim.parm("primtype")
            if primtype_parm is None:
                print(f"    ERROR: primtype parameter not found on primitive node!")
                break
            primtype_parm.set("Material")

            current_node = mat_prim

        # Set metadata using configurestage (48% progress)
        if progress_callback:
            progress_callback(48, "  Configuring stage metadata")

        metadata = stage_node.createNode("configurestage", "metadata")
        metadata.setInput(0, current_node)

        # Check parameters exist
        defaultprim_parm = metadata.parm("defaultprim")
        if defaultprim_parm:
            defaultprim_parm.set(asset_name)
        else:
            print("    WARNING: defaultprim parameter not found")

        metersperunit_parm = metadata.parm("metersperunit")
        if metersperunit_parm:
            metersperunit_parm.set(1)
        else:
            print("    WARNING: metersperunit parameter not found")

        upaxis_parm = metadata.parm("upaxis")
        if upaxis_parm:
            upaxis_parm.set("y")
        else:
            print("    WARNING: upaxis parameter not found")

        # Export to USD (49-50% progress)
        if progress_callback:
            progress_callback(49, "  Exporting geo.usd...")

        usd_rop = stage_node.createNode("usd_rop", "export_geo")
        usd_rop.setInput(0, metadata)

        lopoutput_parm = usd_rop.parm("lopoutput")
        if lopoutput_parm:
            lopoutput_parm.set(output_path)
        else:
            print("    ERROR: lopoutput parameter not found on usd_rop!")
            raise RuntimeError("Cannot set output path on USD ROP")

        trange_parm = usd_rop.parm("trange")
        if trange_parm:
            trange_parm.set(0)
        else:
            print("    WARNING: trange parameter not found, using default")

        # Execute export
        execute_parm = usd_rop.parm("execute")
        if execute_parm:
            execute_parm.pressButton()
        else:
            print("    ERROR: execute button not found on usd_rop!")
            raise RuntimeError("Cannot execute USD ROP")

    finally:
        # Cleanup
        stage_node.destroy()


def _create_mtl_usd(
    output_path: str,
    asset_name: str,
    materials: Set[str],
    materials_folder: str,
    texture_variants: List[str],
    progress_callback: Optional[Callable[[int, str], None]] = None
):
    """Create mtl.usd with material library references and texture variant system."""
    if progress_callback:
        progress_callback(55, "  Creating material library structure...")

    stage = Usd.Stage.CreateNew(output_path)

    # Set metadata
    stage.SetDefaultPrim(stage.DefinePrim(f"/{asset_name}"))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    # Create over for asset
    asset_prim = stage.OverridePrim(f"/{asset_name}")

    # Add variant set
    vset = asset_prim.GetVariantSets().AddVariantSet("texture_variant")
    vset.SetVariantSelection(texture_variants[-1])  # Default to highest quality

    # Create material scope override
    mtl_scope = stage.OverridePrim(f"/{asset_name}/mtl")

    # Add material references (55-65% progress)
    total_mats = len(materials)
    for i, mat_name in enumerate(sorted(materials)):
        if progress_callback:
            percent = 55 + int((i / total_mats) * 10)
            progress_callback(percent, f"  Adding material {i+1}/{total_mats}: {mat_name}")

        mat_prim = stage.OverridePrim(f"/{asset_name}/mtl/{mat_name}")

        # Relative path to material
        mat_rel_path = f"../../Materials/{mat_name}/{mat_name}.usd"

        # Check if material exists
        mat_abs_path = os.path.join(materials_folder, mat_name, f"{mat_name}.usd")
        if not os.path.exists(mat_abs_path):
            print(f"  WARNING: Material not found: {mat_abs_path}")
            continue

        # Add reference
        mat_prim.GetReferences().AddReference(
            assetPath=mat_rel_path,
            primPath=f"/{mat_name}"
        )

    # Create texture variants (65-70% progress)
    if progress_callback:
        progress_callback(65, "  Creating texture variants...")

    for variant in texture_variants:
        vset.AddVariant(variant)
        vset.SetVariantSelection(variant)

        with vset.GetVariantEditContext():
            # Override material scope
            variant_mtl_scope = stage.OverridePrim(f"/{asset_name}/mtl")

            # Set variant on each material
            for mat_name in sorted(materials):
                variant_mat_prim = stage.OverridePrim(f"/{asset_name}/mtl/{mat_name}")

                # Set texture_variant on material
                mat_vset = variant_mat_prim.GetVariantSets().AddVariantSet("texture_variant")
                mat_vset.SetVariantSelection(variant)

    # Save
    stage.GetRootLayer().Save()


def _create_payload_usd(output_path: str, asset_name: str):
    """Create payload.usd - simple assembly referencing mtl.usd + geo.usd."""
    content = f"""#usda 1.0
(
    defaultPrim = "{asset_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{asset_name}" (
    kind = "assembly"
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


def _create_main_usd(output_path: str, asset_name: str):
    """Create main asset USD - convenience wrapper."""
    content = f"""#usda 1.0
(
    defaultPrim = "{asset_name}"
    metersPerUnit = 1
    upAxis = "Y"
)

def "{asset_name}" (
    kind = "assembly"
    prepend payload = @./payload.usd@
)
{{
}}
"""

    with open(output_path, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    # Example usage
    build_from_parts(
        parts_folder="/path/to/parts/MyAsset",
        asset_name="MyAsset",
        models_folder="/path/to/Models",
        materials_folder="/path/to/Materials"
    )
