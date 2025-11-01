"""
BGEO Analyzer - Analyze BGEO.SC files and extract KB3D asset structure

This module reads BGEO.SC files and analyzes the attributes to understand:
- kb3d_part: The part name within an asset
- kb3d_asset: The asset this part belongs to
- shop_materialpath: Material assignments for geometry

It groups geometry by asset and part to reconstruct the KB3D hierarchy.

Author: Custom Tools
Date: 2025-10-28
"""

import hou
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import os


class BGEOAnalyzer:
    """Analyzes BGEO.SC files to extract KB3D asset structure."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset analyzer state."""
        self.assets = defaultdict(lambda: defaultdict(list))
        self.materials = defaultdict(set)
        self.transforms = {}
        self.bounds = {}

    def analyze_file(self, bgeo_path: str) -> Dict:
        """
        Analyze a single BGEO.SC file.

        Args:
            bgeo_path: Path to BGEO.SC file

        Returns:
            Dictionary with analysis results:
            {
                'success': bool,
                'asset': str,  # kb3d_asset value
                'parts': {part_name: geo_data},
                'materials': set of material names,
                'bounds': [min, max] vectors,
                'error': str (if failed)
            }
        """
        if not os.path.exists(bgeo_path):
            return {
                'success': False,
                'error': f'File not found: {bgeo_path}'
            }

        try:
            # Load geometry
            geo = hou.Geometry()
            geo.loadFromFile(bgeo_path)

            # Get attribute values
            asset_name = self._get_asset_name(geo)
            parts_data = self._analyze_parts(geo)
            materials = self._extract_materials(geo)
            bounds = self._calculate_bounds(geo)

            return {
                'success': True,
                'asset': asset_name,
                'parts': parts_data,
                'materials': materials,
                'bounds': bounds,
                'file': bgeo_path
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to analyze {bgeo_path}: {str(e)}'
            }

    def analyze_folder(self, folder_path: str, pattern: str = '*.bgeo.sc') -> Dict:
        """
        Analyze all BGEO.SC files in a folder.

        Args:
            folder_path: Path to folder containing BGEO.SC files
            pattern: File pattern to match (default: *.bgeo.sc)

        Returns:
            Dictionary with grouped results:
            {
                'success': bool,
                'assets': {
                    'AssetName': {
                        'parts': {
                            'PartName': {
                                'file': path,
                                'geometry': hou.Geometry,
                                'materials': set,
                                'bounds': [min, max]
                            }
                        },
                        'all_materials': set of all materials used,
                        'bounds': overall bounds
                    }
                },
                'files_processed': int,
                'errors': list of error messages
            }
        """
        self.reset()

        if not os.path.exists(folder_path):
            return {
                'success': False,
                'error': f'Folder not found: {folder_path}'
            }

        # Find all BGEO.SC files
        import glob
        bgeo_files = glob.glob(os.path.join(folder_path, pattern))

        if not bgeo_files:
            return {
                'success': False,
                'error': f'No BGEO files found in {folder_path} matching {pattern}'
            }

        assets_data = defaultdict(lambda: {
            'parts': {},
            'all_materials': set(),
            'bounds': None
        })

        errors = []
        processed = 0

        for bgeo_file in bgeo_files:
            result = self.analyze_file(bgeo_file)

            if result['success']:
                asset_name = result['asset']

                # Store part data
                for part_name, part_data in result['parts'].items():
                    assets_data[asset_name]['parts'][part_name] = {
                        'file': bgeo_file,
                        'geometry': part_data['geometry'],
                        'materials': part_data['materials'],
                        'bounds': part_data['bounds']
                    }

                # Accumulate materials
                assets_data[asset_name]['all_materials'].update(result['materials'])

                # Update bounds
                if assets_data[asset_name]['bounds'] is None:
                    assets_data[asset_name]['bounds'] = result['bounds']
                else:
                    assets_data[asset_name]['bounds'] = self._merge_bounds(
                        assets_data[asset_name]['bounds'],
                        result['bounds']
                    )

                processed += 1
            else:
                errors.append(result['error'])

        return {
            'success': processed > 0,
            'assets': dict(assets_data),
            'files_processed': processed,
            'errors': errors
        }

    def _get_asset_name(self, geo: hou.Geometry) -> str:
        """Extract kb3d_asset attribute value."""
        # Try point attribute first
        asset_attrib = geo.findPointAttrib('kb3d_asset')
        if asset_attrib:
            # Get first point's value
            if geo.points():
                return geo.points()[0].attribValue('kb3d_asset')

        # Try primitive attribute
        asset_attrib = geo.findPrimAttrib('kb3d_asset')
        if asset_attrib:
            if geo.prims():
                return geo.prims()[0].attribValue('kb3d_asset')

        # Try detail attribute
        asset_attrib = geo.findGlobalAttrib('kb3d_asset')
        if asset_attrib:
            return geo.attribValue('kb3d_asset')

        # Fallback to "Unknown"
        return "Unknown_Asset"

    def _analyze_parts(self, geo: hou.Geometry) -> Dict:
        """
        Analyze geometry parts based on kb3d_part attribute.

        Returns:
            {part_name: {'geometry': hou.Geometry, 'materials': set, 'bounds': [min, max]}}
        """
        parts = defaultdict(lambda: {
            'geometry': hou.Geometry(),
            'materials': set(),
            'bounds': None
        })

        # Check if kb3d_part attribute exists
        part_attrib = geo.findPrimAttrib('kb3d_part')

        if not part_attrib:
            # No parts defined - treat entire geo as single part
            part_name = "main"
            parts[part_name]['geometry'] = geo
            parts[part_name]['materials'] = self._extract_materials(geo)
            parts[part_name]['bounds'] = self._calculate_bounds(geo)
            return dict(parts)

        # Group primitives by part name
        prim_groups = defaultdict(list)
        for prim in geo.prims():
            part_name = prim.attribValue('kb3d_part')
            prim_groups[part_name].append(prim)

        # Create geometry for each part
        for part_name, prims in prim_groups.items():
            part_geo = hou.Geometry()

            # Copy primitives to new geometry
            for prim in prims:
                # This is simplified - in production you'd need to handle points properly
                part_geo.merge(hou.Geometry([prim]))

            parts[part_name]['geometry'] = part_geo
            parts[part_name]['materials'] = self._extract_materials_from_prims(prims)
            parts[part_name]['bounds'] = self._calculate_bounds(part_geo)

        return dict(parts)

    def _extract_materials(self, geo: hou.Geometry) -> set:
        """Extract unique material names from shop_materialpath attribute."""
        materials = set()

        # Check primitive attribute
        mat_attrib = geo.findPrimAttrib('shop_materialpath')
        if mat_attrib:
            for prim in geo.prims():
                mat_path = prim.attribValue('shop_materialpath')
                if mat_path:
                    # Extract material name from path
                    # e.g., "/shop/materials/MyMaterial" -> "MyMaterial"
                    mat_name = mat_path.split('/')[-1]
                    materials.add(mat_name)

        return materials

    def _extract_materials_from_prims(self, prims: List) -> set:
        """Extract materials from a list of primitives."""
        materials = set()

        for prim in prims:
            mat_attrib = prim.attribValue('shop_materialpath')
            if mat_attrib:
                mat_name = mat_attrib.split('/')[-1]
                materials.add(mat_name)

        return materials

    def _calculate_bounds(self, geo: hou.Geometry) -> Tuple[hou.Vector3, hou.Vector3]:
        """Calculate bounding box of geometry."""
        if not geo.prims():
            return (hou.Vector3(0, 0, 0), hou.Vector3(0, 0, 0))

        bbox = geo.boundingBox()
        return (bbox.minvec(), bbox.maxvec())

    def _merge_bounds(self, bounds1: Tuple, bounds2: Tuple) -> Tuple:
        """Merge two bounding boxes."""
        min1, max1 = bounds1
        min2, max2 = bounds2

        merged_min = hou.Vector3(
            min(min1.x(), min2.x()),
            min(min1.y(), min2.y()),
            min(min1.z(), min2.z())
        )

        merged_max = hou.Vector3(
            max(max1.x(), max2.x()),
            max(max1.y(), max2.y()),
            max(max1.z(), max2.z())
        )

        return (merged_min, merged_max)

    def get_asset_summary(self, assets_data: Dict) -> str:
        """Generate human-readable summary of analyzed assets."""
        lines = []
        lines.append("="*60)
        lines.append("BGEO ANALYSIS SUMMARY")
        lines.append("="*60)

        for asset_name, asset_data in assets_data.items():
            lines.append(f"\nAsset: {asset_name}")
            lines.append(f"  Parts: {len(asset_data['parts'])}")
            lines.append(f"  Materials: {len(asset_data['all_materials'])}")

            if asset_data['all_materials']:
                lines.append(f"    - {', '.join(sorted(asset_data['all_materials']))}")

            lines.append(f"  Part Details:")
            for part_name, part_data in asset_data['parts'].items():
                lines.append(f"    - {part_name}:")
                lines.append(f"        File: {os.path.basename(part_data['file'])}")
                lines.append(f"        Prims: {len(part_data['geometry'].prims())}")
                lines.append(f"        Materials: {', '.join(sorted(part_data['materials']))}")

        lines.append("\n" + "="*60)
        return "\n".join(lines)


# Convenience functions
def analyze_bgeo_file(bgeo_path: str) -> Dict:
    """Analyze a single BGEO.SC file."""
    analyzer = BGEOAnalyzer()
    return analyzer.analyze_file(bgeo_path)


def analyze_bgeo_folder(folder_path: str, pattern: str = '*.bgeo.sc') -> Dict:
    """Analyze all BGEO.SC files in a folder."""
    analyzer = BGEOAnalyzer()
    return analyzer.analyze_folder(folder_path, pattern)


def print_bgeo_analysis(folder_path: str):
    """Analyze and print summary of BGEO files in folder."""
    analyzer = BGEOAnalyzer()
    result = analyzer.analyze_folder(folder_path)

    if result['success']:
        print(analyzer.get_asset_summary(result['assets']))
        print(f"\nFiles processed: {result['files_processed']}")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print(f"Analysis failed: {result.get('error', 'Unknown error')}")
