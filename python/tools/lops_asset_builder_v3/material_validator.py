"""
Material Validator - Validate materials and warn about missing textures

Checks if geometry files have material assignments that can't be satisfied
by the available texture folders, and provides detailed warnings to users.
"""

import os
from typing import List, Dict, Set, Tuple
import hou
from modules.misc_utils import slugify, MaterialNamingConfig
from tools.lops_asset_builder_v3.texture_variant_detector import TextureVariantDetector


class MaterialValidationResult:
    """Result of material validation."""

    def __init__(self):
        self.materials_expected: Set[str] = set()  # Materials found in geometry
        self.materials_available: Set[str] = set()  # Materials found in textures
        self.materials_missing: Set[str] = set()    # Expected but not available
        self.has_warnings: bool = False
        self.warnings: List[str] = []
        self.info: List[str] = []

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
        self.has_warnings = True

    def add_info(self, message: str):
        """Add an info message."""
        self.info.append(message)

    def get_summary(self) -> str:
        """Get a formatted summary of validation results."""
        lines = []
        lines.append("=" * 70)
        lines.append("MATERIAL VALIDATION REPORT")
        lines.append("=" * 70)

        # Statistics
        lines.append(f"\nMaterials expected (from geometry): {len(self.materials_expected)}")
        lines.append(f"Materials available (from textures): {len(self.materials_available)}")
        lines.append(f"Materials missing: {len(self.materials_missing)}")

        # Missing materials detail
        if self.materials_missing:
            lines.append(f"\n⚠️  MISSING MATERIALS ({len(self.materials_missing)}):")
            for mat in sorted(self.materials_missing):
                lines.append(f"   ❌ {mat}")

        # Available materials
        if self.materials_available:
            lines.append(f"\n✓ AVAILABLE MATERIALS ({len(self.materials_available)}):")
            for mat in sorted(self.materials_available):
                lines.append(f"   ✓ {mat}")

        # Warnings
        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"   • {warning}")

        # Info
        if self.info:
            lines.append(f"\nℹ️  INFORMATION:")
            for info in self.info:
                lines.append(f"   • {info}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)

    def get_html_summary(self) -> str:
        """Get HTML formatted summary for Qt dialogs."""
        lines = []
        lines.append("<h3>Material Validation Report</h3>")

        # Statistics
        lines.append("<table border='0' cellpadding='3'>")
        lines.append(f"<tr><td><b>Materials expected:</b></td><td>{len(self.materials_expected)}</td></tr>")
        lines.append(f"<tr><td><b>Materials available:</b></td><td>{len(self.materials_available)}</td></tr>")
        lines.append(f"<tr><td><b>Materials missing:</b></td><td style='color: red;'><b>{len(self.materials_missing)}</b></td></tr>")
        lines.append("</table>")

        # Missing materials
        if self.materials_missing:
            lines.append(f"<h4 style='color: orange;'>⚠️ Missing Materials ({len(self.materials_missing)}):</h4>")
            lines.append("<ul style='color: red;'>")
            for mat in sorted(self.materials_missing):
                lines.append(f"<li><b>{mat}</b></li>")
            lines.append("</ul>")

        # Warnings
        if self.warnings:
            lines.append(f"<h4 style='color: orange;'>⚠️ Warnings:</h4>")
            lines.append("<ul>")
            for warning in self.warnings:
                lines.append(f"<li>{warning}</li>")
            lines.append("</ul>")

        return "".join(lines)


def extract_material_names_from_geometry(asset_paths: List[str], lowercase: bool = False) -> Set[str]:
    """
    Extract material names from geometry files.

    Args:
        asset_paths: List of geometry file paths
        lowercase: If True, convert material names to lowercase

    Returns:
        Set of material names found in geometry
    """
    material_names = set()

    for asset_path in asset_paths:
        asset_path = asset_path.strip()
        if not asset_path or not os.path.exists(asset_path):
            continue

        try:
            # Load geometry
            geo = hou.Geometry()
            geo.loadFromFile(asset_path)

            # Check shop_materialpath
            shop_attrib = geo.findPrimAttrib("shop_materialpath")
            if shop_attrib:
                for prim in geo.prims():
                    material_path = prim.stringAttribValue(shop_attrib)
                    if material_path:
                        # Extract and clean material name
                        material_name = os.path.basename(material_path)
                        if lowercase:
                            material_name = material_name.lower().replace(" ", "_")
                        else:
                            material_name = material_name.replace(" ", "_")
                        material_name = slugify(material_name, lowercase=lowercase)
                        material_name = material_name.strip("_")  # Remove trailing underscores
                        if material_name:
                            material_names.add(material_name)

            # Check material:binding
            binding_attrib = geo.findPrimAttrib("material:binding")
            if binding_attrib:
                for prim in geo.prims():
                    material_path = prim.stringAttribValue(binding_attrib)
                    if material_path:
                        material_name = os.path.basename(material_path)
                        if lowercase:
                            material_name = material_name.lower().replace(" ", "_")
                        else:
                            material_name = material_name.replace(" ", "_")
                        material_name = slugify(material_name, lowercase=lowercase)
                        material_name = material_name.strip("_")
                        if material_name:
                            material_names.add(material_name)

        except Exception as e:
            # Skip files that can't be read
            continue

    return material_names


def find_available_materials_in_textures(texture_folder: str, lowercase: bool = False) -> Set[str]:
    """
    Scan texture folder to find available material sets.

    A material set is identified by finding texture files with common prefixes.

    Args:
        texture_folder: Path to texture folder
        lowercase: If True, convert material names to lowercase

    Returns:
        Set of material names that can be created from textures
    """
    if not os.path.exists(texture_folder):
        return set()

    material_names = set()

    # Texture suffixes that identify material maps
    texture_suffixes = [
        'basecolor', 'base_color', 'diffuse', 'albedo',
        'normal', 'normal_gl', 'normal_dx',
        'roughness', 'metallic', 'metalness',
        'ao', 'ambient_occlusion', 'ambientocclusion',
        'height', 'displacement', 'bump',
        'opacity', 'alpha', 'transmission',
        'emission', 'emissive'
    ]

    # Walk through all subdirectories
    for root, dirs, files in os.walk(texture_folder):
        texture_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.tx'))]

        if not texture_files:
            continue

        # Extract material names by removing texture suffixes
        for texture_file in texture_files:
            if lowercase:
                basename = os.path.splitext(texture_file)[0].lower()
            else:
                basename = os.path.splitext(texture_file)[0]

            # Try to identify material name by removing known suffixes
            material_name = None
            for suffix in texture_suffixes:
                if basename.lower().endswith(f"_{suffix}"):
                    material_name = basename[:-len(suffix)-1]
                    break
                elif basename.lower().endswith(suffix):
                    material_name = basename[:-len(suffix)]
                    break

            if material_name:
                material_name = slugify(material_name, lowercase=lowercase).strip("_")
                if material_name:
                    material_names.add(material_name)

    return material_names


def validate_materials(
    asset_paths: List[str],
    texture_folder: str,
    texture_variants: List[str] = None,
    lowercase: bool = False,
    naming_config: MaterialNamingConfig = None
) -> MaterialValidationResult:
    """
    Validate that geometry materials can be satisfied by available textures.

    Args:
        asset_paths: List of geometry file paths
        texture_folder: Path to main texture folder
        texture_variants: Optional list of texture variant folders (e.g., ["4k", "2k"])
        lowercase: If True, convert material names to lowercase (deprecated, use naming_config)
        naming_config: Material naming configuration (preferred over lowercase param)

    Returns:
        MaterialValidationResult with detailed validation info
    """
    # Use naming_config if provided, otherwise create from lowercase param
    if naming_config is None:
        naming_config = MaterialNamingConfig.from_ui(lowercase=lowercase)

    result = MaterialValidationResult()

    # Extract expected materials from geometry
    result.add_info(f"Scanning {len(asset_paths)} geometry file(s)...")
    result.materials_expected = extract_material_names_from_geometry(asset_paths, lowercase=naming_config.lowercase)

    if not result.materials_expected:
        result.add_warning("No material assignments found in geometry files")
        result.add_info("Geometry has no shop_materialpath or material:binding attributes")
        return result

    # Find available materials in textures
    if not os.path.exists(texture_folder):
        result.add_warning(f"Texture folder does not exist: {texture_folder}")
        result.add_warning("Template materials will be created instead")
        result.materials_missing = result.materials_expected.copy()
        return result

    # Scan main texture folder
    result.add_info(f"Scanning texture folder: {texture_folder}")
    result.materials_available = find_available_materials_in_textures(texture_folder, lowercase=naming_config.lowercase)

    # Intelligently detect variant folders if not provided
    if not texture_variants:
        detector = TextureVariantDetector()
        detected_variants = detector.detect_variants(texture_folder)
        if detected_variants:
            result.add_info(f"Auto-detected {len(detected_variants)} texture variant folder(s)")
            for variant in detected_variants:
                result.add_info(f"  Found variant: {variant.folder_name} ({variant.variant_key})")
            texture_variants = [v.folder_name for v in detected_variants]

    # Scan variant folders
    if texture_variants:
        for variant in texture_variants:
            # Handle both folder names and full paths
            if os.path.isabs(variant):
                variant_path = variant
            else:
                variant_path = os.path.join(texture_folder, variant)

            if os.path.exists(variant_path) and os.path.isdir(variant_path):
                result.add_info(f"Scanning variant folder: {os.path.basename(variant_path)}")
                variant_materials = find_available_materials_in_textures(variant_path, lowercase=naming_config.lowercase)
                result.materials_available.update(variant_materials)

    # Identify missing materials
    result.materials_missing = result.materials_expected - result.materials_available

    # Generate warnings
    if result.materials_missing:
        result.add_warning(f"{len(result.materials_missing)} material(s) referenced in geometry have no matching textures")
        result.add_warning("Missing materials will use fallback template shaders")

        if len(result.materials_missing) <= 10:
            for mat in sorted(result.materials_missing):
                result.add_warning(f"  Missing: {mat}")

    # Generate info messages
    if result.materials_available:
        result.add_info(f"Found {len(result.materials_available)} material set(s) in textures")
        result.add_info(f"{len(result.materials_expected - result.materials_missing)} material(s) will be created successfully")

    return result


def validate_and_warn_user(
    asset_paths: List[str],
    texture_folder: str,
    texture_variants: List[str] = None,
    show_dialog: bool = True,
    lowercase: bool = False,
    naming_config: MaterialNamingConfig = None
) -> Tuple[MaterialValidationResult, bool]:
    """
    Validate materials and optionally show warning dialog to user.

    Args:
        asset_paths: List of geometry file paths
        texture_folder: Path to texture folder
        texture_variants: Optional list of texture variant folders
        show_dialog: If True, show Qt warning dialog when issues found
        lowercase: If True, convert material names to lowercase (deprecated, use naming_config)
        naming_config: Material naming configuration (preferred over lowercase param)

    Returns:
        Tuple of (MaterialValidationResult, user_wants_to_continue)
    """
    # Use naming_config if provided, otherwise create from lowercase param
    if naming_config is None:
        naming_config = MaterialNamingConfig.from_ui(lowercase=lowercase)

    result = validate_materials(asset_paths, texture_folder, texture_variants, naming_config=naming_config)

    # Print to console
    print(result.get_summary())

    # Show dialog if requested and there are warnings
    if show_dialog and result.has_warnings:
        try:
            from PySide6 import QtWidgets

            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Material Validation Warning")
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)

            msg_box.setText(
                f"<b>⚠️ Material validation found {len(result.materials_missing)} missing material(s)</b>"
            )

            msg_box.setInformativeText(
                "Some materials referenced in geometry don't have matching texture files.\n"
                "These materials will use fallback template shaders.\n\n"
                "Do you want to continue?"
            )

            msg_box.setDetailedText(result.get_summary())

            msg_box.setStandardButtons(
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)

            response = msg_box.exec_()
            user_continues = (response == QtWidgets.QMessageBox.Yes)

            return result, user_continues

        except Exception as e:
            print(f"Warning: Could not show validation dialog: {e}")
            return result, True

    return result, True


# Example usage
if __name__ == "__main__":
    # Test validation
    test_assets = [
        "/path/to/asset.abc"
    ]
    test_textures = "/path/to/textures"

    result = validate_materials(test_assets, test_textures)
    print(result.get_summary())
