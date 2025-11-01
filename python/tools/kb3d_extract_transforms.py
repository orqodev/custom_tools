"""
Extract transforms from merged BGEO for KB3D assembly

Analyzes merged BGEO to extract centroid/bounds for each part based on material names.
"""

import hou
import os


def extract_part_transforms_from_bgeo(bgeo_path: str, part_names: list) -> dict:
    """
    Extract transforms for each part from merged BGEO.

    Analyzes geometry and groups parts by material name to find centroids.

    Args:
        bgeo_path: Path to merged BGEO file
        part_names: List of part names to extract (e.g. ['Wings', 'Cargo', 'Main'])

    Returns:
        Dict mapping part names to transforms:
        {
            'Wings': {'translate': (x,y,z), 'bounds': ((minx,miny,minz), (maxx,maxy,maxz))},
            ...
        }
    """
    print(f"\n{'='*60}")
    print(f"Extracting Part Transforms from BGEO")
    print(f"{'='*60}")
    print(f"BGEO: {bgeo_path}")
    print(f"Parts: {part_names}")
    print()

    # Create temp geometry node
    obj = hou.node('/obj')
    temp_geo = obj.createNode('geo', 'temp_extract_xforms', run_init_scripts=False)

    try:
        # Load BGEO
        file_node = temp_geo.createNode('file', 'file1')
        file_node.parm('file').set(bgeo_path)
        file_node.cook(force=True)

        geo = file_node.geometry()

        if not geo:
            print("ERROR: Could not load geometry")
            return {}

        print(f"Loaded geometry: {geo.intrinsicValue('primitivecount')} primitives")
        print()

        # Check for shop_materialpath attribute
        shop_attrib = geo.findPrimAttrib('shop_materialpath')
        if not shop_attrib:
            print("WARNING: No shop_materialpath attribute found")
            print("Trying to split by primitive groups...")

            # Fall back to using primitive groups
            return _extract_from_groups(geo, part_names)

        # Extract transforms by material
        transforms = {}

        for part_name in part_names:
            print(f"Processing part: {part_name}")

            # Find primitives with material matching this part
            # Material paths might be like: /mat/Wings_Material or /shop/Wings
            matching_prims = []

            for prim in geo.prims():
                mat_path = prim.attribValue('shop_materialpath')
                if mat_path and part_name.lower() in mat_path.lower():
                    matching_prims.append(prim)

            if not matching_prims:
                print(f"  WARNING: No primitives found with material matching '{part_name}'")
                print(f"  Available materials:")
                materials = set()
                for prim in geo.prims():
                    mat = prim.attribValue('shop_materialpath')
                    if mat:
                        materials.add(mat)
                for mat in sorted(materials):
                    print(f"    - {mat}")
                continue

            print(f"  Found {len(matching_prims)} primitives")

            # Calculate bounds
            bbox = hou.BoundingBox()
            for prim in matching_prims:
                bbox.enlargeToContain(prim.boundingBox())

            center = bbox.center()
            transforms[part_name] = {
                'translate': (center[0], center[1], center[2]),
                'bounds': (
                    (bbox.minvec()[0], bbox.minvec()[1], bbox.minvec()[2]),
                    (bbox.maxvec()[0], bbox.maxvec()[1], bbox.maxvec()[2])
                ),
                'size': bbox.sizevec()
            }

            print(f"  Centroid: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            print(f"  Size: ({bbox.sizevec()[0]:.3f}, {bbox.sizevec()[1]:.3f}, {bbox.sizevec()[2]:.3f})")
            print()

        return transforms

    finally:
        # Clean up
        temp_geo.destroy()


def _extract_from_groups(geo, part_names):
    """Extract transforms from primitive groups if no material attribute."""
    transforms = {}

    print("\nTrying to extract from primitive groups:")
    groups = [g.name() for g in geo.primGroups()]
    print(f"Available groups: {groups}")
    print()

    for part_name in part_names:
        # Look for matching group
        matching_group = None
        for group_name in groups:
            if part_name.lower() in group_name.lower():
                matching_group = group_name
                break

        if not matching_group:
            print(f"  No group found for {part_name}")
            continue

        group = geo.findPrimGroup(matching_group)
        if not group:
            continue

        # Calculate bounds
        bbox = hou.BoundingBox()
        for prim in group.prims():
            bbox.enlargeToContain(prim.boundingBox())

        center = bbox.center()
        transforms[part_name] = {
            'translate': (center[0], center[1], center[2]),
            'bounds': (
                (bbox.minvec()[0], bbox.minvec()[1], bbox.minvec()[2]),
                (bbox.maxvec()[0], bbox.maxvec()[1], bbox.maxvec()[2])
            ),
            'size': bbox.sizevec()
        }

        print(f"  {part_name} (group: {matching_group}):")
        print(f"    Centroid: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
        print(f"    Size: ({bbox.sizevec()[0]:.3f}, {bbox.sizevec()[1]:.3f}, {bbox.sizevec()[2]:.3f})")
        print()

    return transforms


if __name__ == "__main__":
    # Test extraction
    transforms = extract_part_transforms_from_bgeo(
        bgeo_path="/media/tushita/TUSHITA_LINUX_DATA/assets/KitBash3D - Spaceships/KB3D_SPACESHIP_CLONE/geo/KB3D_SPS_Spaceship_C/KB3D_SPS_Spaceship_C.bgeo.sc",
        part_names=['Wings', 'Cargo', 'Main']
    )

    print(f"\n{'='*60}")
    print("Extracted Transforms:")
    print(f"{'='*60}")

    for part_name, xform in transforms.items():
        print(f"\n{part_name}:")
        print(f"  translate = {xform['translate']}")
        print(f"  size = {xform['size']}")
