"""
Material Name Converter - Convert mesh names to material names

Converts lowercase underscore mesh names to proper PascalCase material names:
    kb3d_mtm_metalpanelgraytrima -> KB3D_MTM_MetalPanelGrayTrimA
"""

import os
import re
from typing import Set, List, Dict


def mesh_name_to_material_name(mesh_name: str) -> str:
    """
    Convert mesh name to material name.

    Examples:
        kb3d_mtm_metalpanelgraytrima -> KB3D_MTM_MetalPanelGrayTrimA
        kb3d_mtm_metalwornfilla -> KB3D_MTM_MetalWornFillA
        kb3d_mtm_emisblue -> KB3D_MTM_EmisBlue

    Args:
        mesh_name: Lowercase mesh name with underscores

    Returns:
        PascalCase material name
    """
    # Split by underscores
    parts = mesh_name.split('_')

    # Convert each part to PascalCase
    converted_parts = []
    for part in parts:
        if not part:
            continue

        # Special cases for KB3D and MTM (keep uppercase)
        if part.lower() in ['kb3d', 'mtm']:
            converted_parts.append(part.upper())
        else:
            # Convert to PascalCase with intelligent word splitting
            converted = _smart_pascal_case(part)
            converted_parts.append(converted)

    return '_'.join(converted_parts)


def _smart_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase with intelligent word detection.

    Handles cases like:
        metalpanel -> MetalPanel
        emisblue -> EmisBlue
        graytrima -> GrayTrimA
    """
    # Common word patterns
    common_words = [
        'metal', 'panel', 'gray', 'grey', 'white', 'red', 'yellow', 'blue', 'green',
        'trim', 'worn', 'fill', 'emis', 'glass', 'concrete', 'floor', 'solar',
        'dark', 'light', 'armored', 'kapton', 'shield', 'heat', 'holo', 'colors',
        'magnetic', 'energy', 'cable', 'industrial', 'decals', 'straps', 'spots',
        'lawn', 'grass', 'leaks', 'atlas'
    ]

    # Try to match known word patterns
    result = []
    remaining = text.lower()

    while remaining:
        matched = False

        # Try to match longest words first
        for word in sorted(common_words, key=len, reverse=True):
            if remaining.startswith(word):
                result.append(word.capitalize())
                remaining = remaining[len(word):]
                matched = True
                break

        if not matched:
            # Take the next character as-is
            result.append(remaining[0].upper())
            remaining = remaining[1:]

    return ''.join(result)


def find_matching_materials(
    material_names: Set[str],
    materials_folder: str
) -> Dict[str, str]:
    """
    Find matching material folders for the given material names.

    Args:
        material_names: Set of material names to match
        materials_folder: Path to Materials folder

    Returns:
        Dict mapping material name to material folder path
    """
    matches = {}

    if not os.path.exists(materials_folder):
        print(f"WARNING: Materials folder not found: {materials_folder}")
        return matches

    # Get all available material folders
    available_materials = {}
    for item in os.listdir(materials_folder):
        item_path = os.path.join(materials_folder, item)
        if os.path.isdir(item_path):
            # Normalize name for matching (case-insensitive)
            available_materials[item.lower()] = item

    # Match each requested material
    for mat_name in material_names:
        mat_lower = mat_name.lower()

        # Try exact match first
        if mat_lower in available_materials:
            actual_name = available_materials[mat_lower]
            mat_folder = os.path.join(materials_folder, actual_name)

            # Check if material USD exists
            mat_usd = os.path.join(mat_folder, f"{actual_name}.usd")
            if os.path.exists(mat_usd):
                matches[mat_name] = actual_name
            else:
                print(f"  WARNING: Material USD not found: {mat_usd}")
        else:
            print(f"  WARNING: Material folder not found for: {mat_name}")

    return matches


def extract_mesh_names_from_usd(usd_file_path: str) -> Set[str]:
    """
    Extract all mesh/prim names from a USD file.

    Args:
        usd_file_path: Path to USD file

    Returns:
        Set of mesh names
    """
    from pxr import Usd, UsdGeom

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


# Test/Debug function
if __name__ == "__main__":
    # Test conversions
    test_names = [
        "kb3d_mtm_metalpanelgraytrima",
        "kb3d_mtm_metalwornfilla",
        "kb3d_mtm_metalpanelyellowtrima",
        "kb3d_mtm_emisblue",
        "kb3d_mtm_glassarmoredmkapton",
        "kb3d_mtm_concretegrayindustrial",
    ]

    print("Testing mesh name to material name conversion:")
    print("=" * 80)
    for name in test_names:
        converted = mesh_name_to_material_name(name)
        print(f"{name:40} -> {converted}")
