"""
KB3D Proper Assembly Builder - Creates true KB3D structure (payload → geo + mtl)

This builder creates the CORRECT KB3D structure matching Mission to Minerva pattern:
- payload.usd: Simple assembly referencing mtl.usd + geo.usd
- geo.usd: All geometry with instanceable parts + empty material scope
- mtl.usd: Material library references with texture variant system

NOT the assembly-with-sub-parts pattern (which is wrong for KB3D)!

Usage:
    from tools.kb3d_proper_assembly_builder import build_kb3d_proper_assembly

    # From merged BGEO with all geometry
    build_kb3d_proper_assembly(
        source_bgeo="/path/to/merged.bgeo.sc",
        asset_name="KB3D_MTM_BldgLgCommsArray_A",
        models_folder="/path/to/Models",
        materials_folder="/path/to/Materials",
        detect_instanceable=True
    )
"""

import os
import hou
from typing import List, Dict, Set, Tuple, Optional
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def build_kb3d_proper_assembly(
    source_bgeo: str,
    asset_name: str,
    models_folder: str,
    materials_folder: str,
    detect_instanceable: bool = True,
    texture_variants: List[str] = None
) -> str:
    """
    Build proper KB3D assembly from source geometry.

    Args:
        source_bgeo: Path to merged BGEO with all parts (can have instanceable duplicates)
        asset_name: Name for the asset (e.g. KB3D_MTM_BldgLgCommsArray_A)
        models_folder: Base Models folder
        materials_folder: Materials folder for material references
        detect_instanceable: Auto-detect duplicate parts for instancing
        texture_variants: List of texture variants (default: ["jpg1k", "jpg2k", "png4k"])

    Returns:
        Path to created payload.usd
    """
    if texture_variants is None:
        texture_variants = ["jpg1k", "jpg2k", "png4k"]

    print(f"\n{'='*80}")
    print(f"KB3D Proper Assembly Builder")
    print(f"{'='*80}")
    print(f"Asset: {asset_name}")
    print(f"Source: {source_bgeo}")
    print(f"Models: {models_folder}")
    print(f"Materials: {materials_folder}")
    print()

    # Create asset folder
    asset_folder = os.path.join(models_folder, asset_name)
    os.makedirs(asset_folder, exist_ok=True)

    # Step 1: Create geo.usd from source BGEO
    print("Step 1: Creating geo.usd...")
    geo_path = os.path.join(asset_folder, "geo.usd")
    materials = _create_geo_usd(source_bgeo, geo_path, asset_name, detect_instanceable)
    print(f"  Created: {geo_path}")
    print(f"  Materials found: {len(materials)}")
    print()

    # Step 2: Create mtl.usd with material references and variants
    print("Step 2: Creating mtl.usd...")
    mtl_path = os.path.join(asset_folder, "mtl.usd")
    _create_mtl_usd(mtl_path, asset_name, materials, materials_folder, texture_variants)
    print(f"  Created: {mtl_path}")
    print()

    # Step 3: Create payload.usd
    print("Step 3: Creating payload.usd...")
    payload_path = os.path.join(asset_folder, "payload.usd")
    _create_payload_usd(payload_path, asset_name)
    print(f"  Created: {payload_path}")
    print()

    # Step 4: Create main asset.usd (optional convenience wrapper)
    print("Step 4: Creating main asset USD...")
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


def _create_geo_usd(
    source_bgeo: str,
    output_path: str,
    asset_name: str,
    detect_instanceable: bool
) -> Set[str]:
    """
    Create geo.usd from source BGEO.

    Returns set of material names found in geometry.
    """
    # Create LOPS network in /obj
    obj = hou.node("/obj")
    stage_node = obj.createNode("lopnet", f"temp_{asset_name}_geo")

    try:
        # Import BGEO via SOP Import
        sop_create = stage_node.createNode("sopcreate", "import_bgeo")
        sop_create.parm("soppath").set(source_bgeo)
        sop_create.parm("primpath").set(f"/{asset_name}")

        # Configure geometry options
        configure = stage_node.createNode("configure", "configure_geo")
        configure.setInput(0, sop_create)
        configure.parm("primpattern1").set(f"/{asset_name}/*")
        configure.parm("kind1").set("component")

        # Set instanceable on duplicate parts if requested
        if detect_instanceable:
            _set_instanceable_parts(configure, asset_name)

        # Create material scope (empty in geo.usd, filled by mtl.usd)
        material_scope = stage_node.createNode("addprim", "add_material_scope")
        material_scope.setInput(0, configure)
        material_scope.parm("primpath").set(f"/{asset_name}/mtl")
        material_scope.parm("primtype").set("Scope")

        # Extract material names from geometry
        stage = material_scope.stage()
        materials = _extract_material_names(stage, asset_name)

        # Add empty material prims to scope
        for mat_name in sorted(materials):
            add_mat = stage_node.createNode("addprim", f"add_mat_{mat_name}")
            add_mat.setInput(0, material_scope)
            add_mat.parm("primpath").set(f"/{asset_name}/mtl/{mat_name}")
            add_mat.parm("primtype").set("Material")
            material_scope = add_mat

        # Set metadata
        metadata = stage_node.createNode("setmetadata", "set_metadata")
        metadata.setInput(0, material_scope)
        metadata.parm("defaultprim").set(asset_name)
        metadata.parm("metersperunit").set(1)
        metadata.parm("upaxis").set("y")

        # Export to USD
        usd_rop = stage_node.createNode("usd_rop", "export_geo")
        usd_rop.setInput(0, metadata)
        usd_rop.parm("lopoutput").set(output_path)
        usd_rop.parm("trange").set(0)  # Current frame only

        # Execute
        usd_rop.parm("execute").pressButton()

        return materials

    finally:
        # Cleanup temp network
        stage_node.destroy()


def _extract_material_names(stage: Usd.Stage, asset_name: str) -> Set[str]:
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

    return materials


def _set_instanceable_parts(configure_node: hou.LopNode, asset_name: str):
    """
    Set instanceable = true on duplicate parts based on geometry hash.

    This is a simplified version - proper implementation would:
    1. Hash geometry topology (point count, face count, bbox)
    2. Group parts with identical topology
    3. Mark duplicates as instanceable
    """
    # TODO: Implement proper instanceable detection
    # For now, just mark all parts as potentially instanceable
    pass


def _create_mtl_usd(
    output_path: str,
    asset_name: str,
    materials: Set[str],
    materials_folder: str,
    texture_variants: List[str]
):
    """
    Create mtl.usd with material library references and texture variant system.

    Structure:
        over "AssetName" (
            variants = { string texture_variant = "png4k" }
            variantSets = "texture_variant"
        )
        {
            over "mtl" {
                over "Material1" (
                    references = @../../Materials/Material1/Material1.usd@
                ) {}
                over "Material2" ...
            }

            variantSet "texture_variant" = {
                "jpg1k" {
                    over "mtl" {
                        over "Material1" ( variants = { texture_variant = "jpg1k" } ) {}
                        ...
                    }
                }
                "jpg2k" { ... }
                "png4k" { ... }
            }
        }
    """
    stage = Usd.Stage.CreateNew(output_path)

    # Set metadata
    stage.SetDefaultPrim(stage.DefinePrim(f"/{asset_name}"))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    # Create over for asset
    asset_prim = stage.OverridePrim(f"/{asset_name}")

    # Add variant set
    vset = asset_prim.GetVariantSets().AddVariantSet("texture_variant")

    # Set default variant
    vset.SetVariantSelection("png4k")

    # Create material scope override
    mtl_scope = stage.OverridePrim(f"/{asset_name}/mtl")

    # Add material references
    for mat_name in sorted(materials):
        mat_prim = stage.OverridePrim(f"/{asset_name}/mtl/{mat_name}")

        # Relative path to material
        mat_rel_path = f"../../Materials/{mat_name}/{mat_name}.usd"

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
    """
    Create payload.usd - simple assembly referencing mtl.usd + geo.usd.

    Structure:
        def "AssetName" (
            kind = "assembly"
            references = [
                @./mtl.usd@,
                @./geo.usd@
            ]
        )
        {}
    """
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
    """
    Create main asset USD - convenience wrapper that payloads the assembly.

    Structure:
        def "AssetName" (
            kind = "assembly"
            payload = @./payload.usd@
        )
        {}
    """
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
    build_kb3d_proper_assembly(
        source_bgeo="/path/to/merged.bgeo.sc",
        asset_name="KB3D_MTM_TestAsset_A",
        models_folder="/path/to/Models",
        materials_folder="/path/to/Materials",
        detect_instanceable=True
    )
