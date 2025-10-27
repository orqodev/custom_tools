"""
USD Material Variant Builder

Creates USD materials with texture resolution variants following the KB3D pattern.
This module can create materials similar to KB3D structure with multiple texture
resolution variants (1k, 2k, 4k in jpg/png formats).

Usage:
    from modules import usd_material_variant_builder

    builder = usd_material_variant_builder.USDMaterialVariantBuilder(
        material_name="MyMaterial",
        base_texture_path="$JOB/textures"
    )

    # Add texture variants
    builder.add_variant("png4k", "png4k")
    builder.add_variant("jpg2k", "jpg2k")

    # Create USD file
    builder.create_usd_material("/path/to/output.usda")

Based on KB3D material structure analysis.
"""

import os
from typing import Dict, List, Optional, Tuple
from pxr import Usd, UsdShade, Sdf, UsdGeom


class TextureVariant:
    """Represents a texture resolution variant."""

    def __init__(self, variant_name: str, folder_name: str, format: str = "png", resolution: str = "4k"):
        self.variant_name = variant_name  # e.g., "png4k"
        self.folder_name = folder_name    # e.g., "png4k" (subfolder in Textures/)
        self.format = format              # "png" or "jpg"
        self.resolution = resolution      # "1k", "2k", "4k"
        self.textures: Dict[str, str] = {}  # Map type -> filename


class USDMaterialVariantBuilder:
    """
    Build USD materials with texture resolution variants.

    Follows KB3D pattern:
    - MaterialX reference for shader network
    - Variant sets for texture resolutions
    - Relative texture paths
    - Class inheritance structure
    """

    def __init__(self, material_name: str, base_texture_path: str = "../../Textures"):
        """
        Initialize builder.

        Args:
            material_name: Name of the material (e.g., "MyMaterial")
            base_texture_path: Base path to textures folder (relative or absolute)
        """
        self.material_name = material_name
        self.base_texture_path = base_texture_path
        self.variants: List[TextureVariant] = []
        self.default_variant: Optional[str] = None

        # Standard PBR texture types
        self.texture_types = {
            'base_color': 'basecolor',
            'metalness': 'metallic',
            'specular_roughness': 'roughness',
            'normal': 'normal',
            'emission_color': 'emissive',
            'opacity': 'opacity',
            'displacement': 'displacement'
        }

        # Asset metadata
        self.asset_info = {}

    def add_variant(self, variant_name: str, folder_name: str,
                   format: str = "png", resolution: str = "4k",
                   is_default: bool = False) -> TextureVariant:
        """
        Add a texture resolution variant.

        Args:
            variant_name: Name for the variant (e.g., "png4k")
            folder_name: Subfolder name in Textures/ (e.g., "png4k")
            format: Image format ("png" or "jpg")
            resolution: Resolution string ("1k", "2k", "4k")
            is_default: Set as default variant

        Returns:
            TextureVariant object for further configuration
        """
        variant = TextureVariant(variant_name, folder_name, format, resolution)
        self.variants.append(variant)

        if is_default or not self.default_variant:
            self.default_variant = variant_name

        return variant

    def auto_discover_variants(self, textures_base_path: str,
                              material_base_name: str) -> int:
        """
        Auto-discover texture variants by scanning folder structure.

        Expected structure:
            textures_base_path/
                png1k/
                    material_basecolor.png
                    material_metallic.png
                jpg2k/
                    material_basecolor.jpg
                    ...

        Args:
            textures_base_path: Absolute path to textures folder
            material_base_name: Base name for texture files (e.g., "MyMaterial")

        Returns:
            Number of variants discovered
        """
        import hou

        expanded_path = hou.text.expandString(textures_base_path)

        if not os.path.isdir(expanded_path):
            print(f"Warning: Texture path does not exist: {expanded_path}")
            return 0

        discovered_count = 0

        # Scan for resolution folders
        for subfolder in os.listdir(expanded_path):
            subfolder_path = os.path.join(expanded_path, subfolder)

            if not os.path.isdir(subfolder_path):
                continue

            # Check if folder matches resolution pattern (png4k, jpg2k, etc.)
            format_match = None
            resolution_match = None

            if subfolder.startswith('png'):
                format_match = 'png'
                resolution_match = subfolder[3:]  # e.g., "4k" from "png4k"
            elif subfolder.startswith('jpg'):
                format_match = 'jpg'
                resolution_match = subfolder[3:]  # e.g., "2k" from "jpg2k"

            if not format_match or not resolution_match:
                continue

            # Check if textures exist
            test_texture = os.path.join(
                subfolder_path,
                f"{material_base_name}_basecolor.{format_match}"
            )

            if os.path.isfile(test_texture):
                variant = self.add_variant(
                    variant_name=subfolder,
                    folder_name=subfolder,
                    format=format_match,
                    resolution=resolution_match,
                    is_default=(subfolder == "png4k")  # KB3D default
                )

                # Discover all textures for this variant
                for texture_type, suffix in self.texture_types.items():
                    texture_file = f"{material_base_name}_{suffix}.{format_match}"
                    texture_path = os.path.join(subfolder_path, texture_file)

                    if os.path.isfile(texture_path):
                        variant.textures[texture_type] = texture_file

                discovered_count += 1
                print(f"Discovered variant: {subfolder} with {len(variant.textures)} textures")

        return discovered_count

    def set_asset_info(self, kit_name: str = None, kit_id: str = None,
                      kit_version: str = None):
        """
        Set asset metadata (KB3D-style).

        Args:
            kit_name: Display name for the kit
            kit_id: Unique kit identifier
            kit_version: Kit version string
        """
        if kit_name:
            self.asset_info['kitDisplayName'] = kit_name
        if kit_id:
            self.asset_info['kitId'] = kit_id
        if kit_version:
            self.asset_info['kitVersion'] = kit_version

    def create_usd_material(self, output_path: str,
                           mtlx_reference: Optional[str] = None,
                           create_class: bool = True) -> bool:
        """
        Create USD material file with texture variants.

        Args:
            output_path: Output .usda file path
            mtlx_reference: Path to MaterialX file (relative to USD file)
            create_class: Create __class__ inheritance structure (KB3D pattern)

        Returns:
            True if successful
        """
        try:
            # Create stage
            stage = Usd.Stage.CreateNew(output_path)

            # Set metadata
            stage.SetMetadata('metersPerUnit', 1.0)
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

            # Create material prim
            material_path = f"/{self.material_name}"
            material_prim = stage.DefinePrim(material_path, 'Material')
            stage.SetDefaultPrim(material_prim)

            # Add MaterialX reference if provided
            if mtlx_reference:
                if not mtlx_reference.startswith('./'):
                    mtlx_reference = f"./{mtlx_reference}"

                mtlx_ref = f"{mtlx_reference}</MaterialX/Materials/{self.material_name}>"
                references = material_prim.GetReferences()
                references.AddReference(assetPath=mtlx_ref)

            # Create class inheritance structure (KB3D pattern)
            if create_class:
                class_path = f"/__class__/{self.material_name}"
                class_prim = stage.DefinePrim("/__class__", "Scope")
                class_prim.SetSpecifier(Sdf.SpecifierClass)

                material_class_prim = stage.DefinePrim(class_path)
                material_class_prim.SetSpecifier(Sdf.SpecifierClass)

                # Add class inheritance
                inherits = material_prim.GetInherits()
                inherits.AddInherit(class_path)

            # Set as instanceable (KB3D pattern)
            material_prim.SetInstanceable(True)

            # Add asset metadata
            if self.asset_info:
                material_prim.SetAssetInfoByKey('kb3d', self.asset_info)

            # Create variant set
            if self.variants:
                variant_set = material_prim.GetVariantSets().AddVariantSet('texture_variant')

                # Set default variant
                if self.default_variant:
                    variant_set.SetVariantSelection(self.default_variant)

                # Create each variant
                for variant in self.variants:
                    variant_set.AddVariant(variant.variant_name)
                    variant_set.SetVariantSelection(variant.variant_name)

                    with variant_set.GetVariantEditContext():
                        # Create override for MaterialX node graph
                        ng_path = f"{material_path}/NG_{self.material_name}"
                        ng_prim = stage.OverridePrim(ng_path)

                        # Create image node overrides for each texture type
                        for texture_type, filename in variant.textures.items():
                            image_node_path = f"{ng_path}/image_{texture_type}"
                            image_node = stage.OverridePrim(image_node_path)

                            # Set texture path
                            texture_path = f"{self.base_texture_path}/{variant.folder_name}/{filename}"

                            # Create inputs:file attribute
                            file_attr = image_node.CreateAttribute(
                                'inputs:file',
                                Sdf.ValueTypeNames.Asset
                            )
                            file_attr.Set(Sdf.AssetPath(texture_path))

            # Save stage
            stage.GetRootLayer().Save()
            print(f"Created USD material: {output_path}")
            print(f"  Variants: {len(self.variants)}")
            print(f"  Default: {self.default_variant}")

            return True

        except Exception as e:
            print(f"Error creating USD material: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_variant_info(self) -> Dict:
        """Get information about configured variants."""
        return {
            'material_name': self.material_name,
            'default_variant': self.default_variant,
            'variant_count': len(self.variants),
            'variants': [
                {
                    'name': v.variant_name,
                    'folder': v.folder_name,
                    'format': v.format,
                    'resolution': v.resolution,
                    'texture_count': len(v.textures)
                }
                for v in self.variants
            ]
        }


def create_kb3d_style_material(material_name: str, textures_path: str,
                               output_path: str, mtlx_file: str = None) -> bool:
    """
    Convenience function to create KB3D-style material with auto-discovery.

    Args:
        material_name: Name of material
        textures_path: Path to textures folder (with png4k, jpg2k subfolders)
        output_path: Output .usda file path
        mtlx_file: Optional MaterialX filename (defaults to {material_name}.mtlx)

    Returns:
        True if successful

    Example:
        create_kb3d_style_material(
            "MyMaterial",
            "$JOB/assets/materials/MyMaterial/Textures",
            "$JOB/assets/materials/MyMaterial/MyMaterial.usda"
        )
    """
    builder = USDMaterialVariantBuilder(material_name)

    # Auto-discover variants
    variant_count = builder.auto_discover_variants(textures_path, material_name)

    if variant_count == 0:
        print(f"Warning: No texture variants discovered in {textures_path}")
        return False

    # Set MaterialX reference
    if mtlx_file is None:
        mtlx_file = f"{material_name}.mtlx"

    # Create USD file
    return builder.create_usd_material(output_path, mtlx_reference=mtlx_file)
