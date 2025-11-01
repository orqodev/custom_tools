"""
KB3D From Parts Builder - Build KB3D assembly from individual part USD/BGEO files

This builder works with your ACTUAL data structure:
- Input: Folder with part subfolders (each containing geo.usd, payload.usd, etc.)
- Output: Proper KB3D structure (payload → geo + mtl)

Usage:
    from tools.kb3d_from_parts_builder import build_from_parts

    build_from_parts(
        parts_folder="/path/to/geo/KB3D_MTM_BldgLgCommsArray_A",
        asset_name="KB3D_MTM_BldgLgCommsArray_A",
        models_folder="/path/to/Models",
        materials_folder="/path/to/Materials"
    )
"""

import os
import hou
from typing import List, Dict, Set, Optional
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def build_from_parts(
    parts_folder: str,
    asset_name: str,
    models_folder: str,
    materials_folder: str,
    texture_variants: List[str] = None
) -> str:
    """
    Build proper KB3D assembly from individual part folders.

    Args:
        parts_folder: Folder containing part subfolders
                     (e.g., /geo/KB3D_MTM_BldgLgCommsArray_A/)
        asset_name: Name for the asset
        models_folder: Base Models folder
        materials_folder: Materials folder for material references
        texture_variants: List of texture variants (default: ["jpg1k", "jpg2k", "png4k"])

    Returns:
        Path to created payload.usd
    """
    if texture_variants is None:
        texture_variants = ["jpg1k", "jpg2k", "png4k"]

    print(f"\n{'='*80}")
    print(f"KB3D From Parts Builder")
    print(f"{'='*80}")
    print(f"Asset: {asset_name}")
    print(f"Parts: {parts_folder}")
    print(f"Models: {models_folder}")
    print(f"Materials: {materials_folder}")
    print()

    # Create asset folder
    asset_folder = os.path.join(models_folder, asset_name)
    os.makedirs(asset_folder, exist_ok=True)

    # Step 1: Scan parts folder
    print("Step 1: Scanning parts...")
    parts = _scan_parts_folder(parts_folder)
    print(f"  Found {len(parts)} parts")
    print()

    # Step 2: Scan materials from parts
    print("Step 2: Scanning materials from parts...")
    materials = _scan_materials_from_parts(parts)
    print(f"  Found {len(materials)} unique materials")
    print()

    # Step 3: Create geo.usd by merging all parts
    print("Step 3: Creating geo.usd...")
    geo_path = os.path.join(asset_folder, "geo.usd")
    _create_geo_from_parts(parts, geo_path, asset_name, parts_folder, materials)
    print(f"  Created: {geo_path}")
    print()

    # Step 4: Create mtl.usd with material references and variants
    print("Step 4: Creating mtl.usd...")
    mtl_path = os.path.join(asset_folder, "mtl.usd")
    _create_mtl_usd(mtl_path, asset_name, materials, materials_folder, texture_variants)
    print(f"  Created: {mtl_path}")
    print()

    # Step 5: Create payload.usd
    print("Step 5: Creating payload.usd...")
    payload_path = os.path.join(asset_folder, "payload.usd")
    _create_payload_usd(payload_path, asset_name)
    print(f"  Created: {payload_path}")
    print()

    # Step 6: Create main asset.usd
    print("Step 6: Creating main asset USD...")
    main_usd_path = os.path.join(asset_folder, f"{asset_name}.usd")
    _create_main_usd(main_usd_path, asset_name)
    print(f"  Created: {main_usd_path}")
    print()

    print(f"{'='*80}")
    print(f"Assembly Created Successfully!")
    print(f"{'='*80}")
    print(f"Payload: {payload_path}")
    print(f"Geo: {geo_path}")
    print(f"Mtl: {mtl_path}")
    print(f"Materials: {len(materials)}")
    print()

    return payload_path


def _scan_parts_folder(parts_folder: str) -> List[Dict]:
    """
    Scan parts folder and find all part subfolders.

    Returns list of dicts with part info:
    [
        {
            'name': 'SatelliteArmE',
            'folder': '/path/to/SatelliteArmE',
            'geo_usd': '/path/to/SatelliteArmE/geo.usd',
            'bgeo': '/path/to/SatelliteArmE/SatelliteArmE.bgeo.sc',
            'payload': '/path/to/SatelliteArmE/payload.usd'
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


def _scan_materials_from_parts(parts: List[Dict]) -> Set[str]:
    """
    Scan all part files and extract material names BEFORE building.
    This avoids stage cooking issues.
    """
    materials = set()

    for part in parts:
        geo_file = part['geo_file']

        # Only scan USD files (BGEO doesn't have material info easily accessible)
        if geo_file.endswith(('.usd', '.usda', '.usdc')):
            try:
                # Open USD file directly
                stage = Usd.Stage.Open(geo_file)
                if stage:
                    # Traverse and find materials
                    for prim in stage.Traverse():
                        if prim.IsA(UsdGeom.Mesh):
                            binding_api = UsdShade.MaterialBindingAPI(prim)
                            material_binding = binding_api.GetDirectBinding()

                            if material_binding:
                                mat_path = material_binding.GetMaterialPath()
                                if mat_path:
                                    materials.add(mat_path.name)

                            # Check subsets
                            geom_mesh = UsdGeom.Mesh(prim)
                            subsets = UsdGeom.Subset.GetAllGeomSubsets(geom_mesh)
                            for subset in subsets:
                                subset_binding = UsdShade.MaterialBindingAPI(subset.GetPrim())
                                subset_material = subset_binding.GetDirectBinding()
                                if subset_material:
                                    mat_path = subset_material.GetMaterialPath()
                                    if mat_path:
                                        materials.add(mat_path.name)
            except Exception as e:
                print(f"    Warning: Could not scan materials from {geo_file}: {e}")

    return materials


def _create_geo_from_parts(
    parts: List[Dict],
    output_path: str,
    asset_name: str,
    parts_folder: str,
    materials: Set[str]
) -> None:
    """
    Create geo.usd by merging all part USD/BGEO files in LOPS.
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

        # Import each part
        for i, part in enumerate(parts):
            part_name = part['name']
            geo_file = part['geo_file']

            print(f"  Importing part {i+1}/{len(parts)}: {part_name}")

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

        # Create material scope
        mtl_scope = stage_node.createNode("scope", "add_mtl_scope")
        mtl_scope.setInput(0, current_node)
        mtl_scope.parm("primpath").set(f"/{asset_name}/mtl")

        # Materials were already scanned before this function
        print(f"  Adding {len(materials)} material prims")

        # Create individual material prims (no materiallibrary needed)
        current_node = mtl_scope
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

        # Set metadata using configurestage
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

        # Export to USD
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


def _extract_material_names_from_stage(stage: Usd.Stage, asset_name: str) -> Set[str]:
    """Extract unique material names from geometry material bindings."""
    materials = set()

    root_prim = stage.GetPrimAtPath(f"/{asset_name}")
    if not root_prim:
        return materials

    # Traverse all mesh prims
    for prim in Usd.PrimRange(root_prim):
        if prim.IsA(UsdGeom.Mesh):
            # Check for material binding
            binding_api = UsdShade.MaterialBindingAPI(prim)
            material_binding = binding_api.GetDirectBinding()

            if material_binding:
                mat_path = material_binding.GetMaterialPath()
                if mat_path:
                    mat_name = mat_path.name
                    materials.add(mat_name)

            # Also check subsets for per-face materials
            geom_mesh = UsdGeom.Mesh(prim)
            subsets = UsdGeom.Subset.GetAllGeomSubsets(geom_mesh)
            for subset in subsets:
                subset_binding = UsdShade.MaterialBindingAPI(subset.GetPrim())
                subset_material = subset_binding.GetDirectBinding()
                if subset_material:
                    mat_path = subset_material.GetMaterialPath()
                    if mat_path:
                        materials.add(mat_path.name)

    return materials


def _create_mtl_usd(
    output_path: str,
    asset_name: str,
    materials: Set[str],
    materials_folder: str,
    texture_variants: List[str]
):
    """Create mtl.usd with material library references and texture variant system."""
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

    # Add material references
    for mat_name in sorted(materials):
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

    # Create texture variants
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
        parts_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/kb3d_clone/geo/KB3D_MTM_BldgLgCommsArray_A",
        asset_name="KB3D_MTM_BldgLgCommsArray_A",
        models_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/kb3d_clone/Models",
        materials_folder="/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/Materials"
    )
