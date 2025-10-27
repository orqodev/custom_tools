"""
Asset Folder Scanner - Intelligent detection of assets, variants, and materials

This module provides functionality to scan a folder and automatically discriminate between:
- Main assets (base geometry files)
- Asset variants (files with _B, _C, etc. suffixes)
- Material texture folders (with priority based on resolution: 4k > 2k > 1k)

Designed to work with the LOPS Asset Builder workflow.
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class AssetFolderScanner:
    """
    Scans a folder structure to identify assets, variants, and material textures.

    Naming Conventions:
    - Main Asset: base_name.ext (e.g., "PropCargo.bgeo.sc")
    - Variants: base_name_SUFFIX.ext where SUFFIX is B, C, D, etc. (e.g., "PropCargo_B.bgeo.sc")
    - Materials: Folders containing texture files, prioritized by resolution markers (4k, 2k, 1k)
    """

    # Supported geometry file extensions
    GEOMETRY_EXTENSIONS = ['.usd', '.usda', '.usdc', '.abc', '.obj', '.fbx', '.bgeo', '.bgeo.sc']

    # Supported texture file extensions
    TEXTURE_EXTENSIONS = ['.jpeg', '.png', '.jpg', '.bmp', '.tif', '.tiff', '.exr', '.targa', '.rat']

    # Texture type identifiers (from tex_to_mtlx.py)
    TEXTURE_TYPES = [
        "diffuse", "diff", "albedo", "alb", "base", "col", "color", "basecolor",
        "metalness", "metal", "mlt", "met", "metallic",
        "specular", "specularity", "spec", "spc",
        "roughness", "rough", "rgh",
        "transmission", "transparency", "trans",
        "translucency", "sss",
        "emission", "emissive", "emit", "emm",
        "opacity", "opac", "alpha",
        "ambient_occlusion", "ao", "occlusion", "cavity",
        "bump", "bmp",
        "displacement", "height", "displace", "disp", "dsp", "heightmap",
        "user", "mask",
        "normal", "nor", "nrm", "nrml", "norm"
    ]

    # Resolution priority (higher number = higher priority)
    RESOLUTION_PRIORITY = {
        '16k': 5,
        '8k': 4,
        '4k': 3,
        '2k': 2,
        '1k': 1,
    }

    # Variant suffix pattern (matches _B, _C, _D, etc. at end of filename before extension)
    VARIANT_PATTERN = re.compile(r'_([A-Z])(?=\.|$)')

    # Resolution pattern (matches 1k, 2k, 4k, etc.)
    RESOLUTION_PATTERN = re.compile(r'(\d+[Kk])')

    def __init__(self, root_path: str):
        """
        Initialize the scanner with a root folder path.

        Args:
            root_path (str): Path to the root folder containing assets and materials
        """
        self.root_path = os.path.normpath(root_path)
        if not os.path.exists(self.root_path):
            raise ValueError(f"Path does not exist: {self.root_path}")

    def scan_folder(self, geo_subfolder: str = "geo", tex_subfolder: str = "tex") -> Dict:
        """
        Scan the root folder and return a structured result.

        Args:
            geo_subfolder (str): Name of subfolder containing geometry (default: "geo")
            tex_subfolder (str): Name of subfolder containing textures (default: "tex")

        Returns:
            dict: Structured data containing:
                - main_asset: Path to main asset file
                - asset_variants: List of variant asset paths
                - main_textures: Path to highest priority texture folder
                - material_variants: List of other texture folder paths
                - geometry_files: Dict mapping asset names to their file info
                - texture_folders: Dict mapping folder names to their info
        """
        result = {
            'main_asset': None,
            'asset_variants': [],
            'main_textures': None,
            'material_variants': [],
            'geometry_files': {},
            'texture_folders': {},
            'errors': []
        }

        try:
            # Scan for geometry files
            geo_path = os.path.join(self.root_path, geo_subfolder)
            if os.path.exists(geo_path):
                geo_files = self._scan_geometry_files(geo_path)
                result['geometry_files'] = geo_files

                # Identify main asset and variants
                main, variants = self._identify_main_and_variants(geo_files)
                result['main_asset'] = main
                result['asset_variants'] = variants
            else:
                result['errors'].append(f"Geometry subfolder not found: {geo_path}")

            # Scan for texture folders
            tex_path = os.path.join(self.root_path, tex_subfolder)
            if os.path.exists(tex_path):
                tex_folders = self._scan_texture_folders(tex_path)
                result['texture_folders'] = tex_folders

                # Identify main textures and material variants
                main_tex, variant_tex = self._identify_main_and_variant_textures(tex_folders)
                result['main_textures'] = main_tex
                result['material_variants'] = variant_tex
            else:
                result['errors'].append(f"Texture subfolder not found: {tex_path}")

        except Exception as e:
            result['errors'].append(f"Error scanning folder: {str(e)}")

        return result

    def _scan_geometry_files(self, geo_folder: str) -> Dict[str, Dict]:
        """
        Scan a folder for geometry files recursively.

        Args:
            geo_folder (str): Path to geometry folder

        Returns:
            dict: Mapping of base names to file info
        """
        geo_files = {}

        try:
            # Walk through all subdirectories recursively
            for root, dirs, files in os.walk(geo_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Check extension
                    is_valid = False
                    extension = None

                    # Handle .bgeo.sc specially
                    if file.endswith('.bgeo.sc'):
                        extension = '.bgeo.sc'
                        base_name = file[:-len('.bgeo.sc')]
                        is_valid = True
                    else:
                        # Check other extensions
                        for ext in self.GEOMETRY_EXTENSIONS:
                            if file.lower().endswith(ext):
                                extension = ext
                                base_name = file[:-len(ext)]
                                is_valid = True
                                break

                    if not is_valid:
                        continue

                    # Check for variant suffix
                    variant_match = self.VARIANT_PATTERN.search(base_name)
                    is_variant = variant_match is not None
                    variant_suffix = variant_match.group(1) if is_variant else None

                    # Remove variant suffix to get true base name
                    if is_variant:
                        true_base_name = base_name[:variant_match.start()]
                    else:
                        true_base_name = base_name

                    # Calculate relative path from geo_folder
                    relative_dir = os.path.relpath(root, geo_folder)
                    if relative_dir == '.':
                        relative_dir = ''

                    # Store file info
                    file_info = {
                        'path': file_path,
                        'filename': file,
                        'base_name': base_name,
                        'true_base_name': true_base_name,
                        'extension': extension,
                        'is_variant': is_variant,
                        'variant_suffix': variant_suffix,
                        'relative_dir': relative_dir,  # Track which subfolder it's in
                    }

                    # Use display name for indexing (include relative dir to avoid collisions)
                    if relative_dir:
                        display_name = f"{relative_dir}/{base_name}"
                    else:
                        display_name = base_name
                    geo_files[display_name] = file_info

        except Exception as e:
            print(f"Error scanning geometry files: {e}")

        return geo_files

    def _identify_main_and_variants(self, geo_files: Dict[str, Dict]) -> Tuple[Optional[str], List[str]]:
        """
        Identify the main asset and its variants from geometry files.

        Logic:
        - Main asset: The file without a variant suffix (or first alphabetically if multiple)
        - Variants: Files with variant suffixes that share the same base name

        Args:
            geo_files (dict): Dictionary of geometry files

        Returns:
            tuple: (main_asset_path, [variant_paths])
        """
        if not geo_files:
            return None, []

        # Group by true base name
        grouped = {}
        for name, info in geo_files.items():
            true_base = info['true_base_name']
            if true_base not in grouped:
                grouped[true_base] = []
            grouped[true_base].append(info)

        # Find the largest group (most variants)
        largest_group_key = max(grouped.keys(), key=lambda k: len(grouped[k]))
        largest_group = grouped[largest_group_key]

        # Identify main asset (file without variant suffix)
        main_asset = None
        variants = []

        for info in largest_group:
            if not info['is_variant']:
                main_asset = info['path']
            else:
                variants.append(info['path'])

        # If no main asset found, use first file alphabetically
        if main_asset is None and largest_group:
            sorted_group = sorted(largest_group, key=lambda x: x['filename'])
            main_asset = sorted_group[0]['path']
            variants = [info['path'] for info in sorted_group[1:]]

        # Sort variants alphabetically
        variants.sort()

        return main_asset, variants

    def _scan_texture_folders(self, tex_root: str) -> Dict[str, Dict]:
        """
        Scan for texture folders recursively.

        Args:
            tex_root (str): Root path to scan for textures

        Returns:
            dict: Mapping of folder paths to folder info
        """
        texture_folders = {}

        try:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(tex_root):
                # Check if this folder contains valid textures
                if self._folder_contains_textures(root, files):
                    folder_name = os.path.basename(root)
                    relative_path = os.path.relpath(root, tex_root)

                    # Detect resolution
                    resolution = self._detect_resolution(folder_name, root)
                    priority = self.RESOLUTION_PRIORITY.get(resolution, 0)

                    # Store folder info
                    folder_info = {
                        'path': root,
                        'name': folder_name,
                        'relative_path': relative_path,
                        'resolution': resolution,
                        'priority': priority,
                        'texture_count': len([f for f in files if self._is_texture_file(f)])
                    }

                    texture_folders[root] = folder_info

        except Exception as e:
            print(f"Error scanning texture folders: {e}")

        return texture_folders

    def _folder_contains_textures(self, folder_path: str, files: List[str]) -> bool:
        """
        Check if a folder contains valid texture files.

        Args:
            folder_path (str): Path to folder
            files (list): List of filenames in folder

        Returns:
            bool: True if folder contains valid textures
        """
        for file in files:
            if self._is_texture_file(file) and "_" in file:
                return True
        return False

    def _is_texture_file(self, filename: str) -> bool:
        """
        Check if a file is a valid texture file.

        Args:
            filename (str): Filename to check

        Returns:
            bool: True if file is a texture
        """
        return any(filename.lower().endswith(ext) for ext in self.TEXTURE_EXTENSIONS)

    def _detect_resolution(self, folder_name: str, folder_path: str) -> Optional[str]:
        """
        Detect resolution from folder name or path.

        Args:
            folder_name (str): Name of the folder
            folder_path (str): Full path to folder

        Returns:
            str: Resolution string (e.g., '4k', '2k') or None
        """
        # Check folder name first
        match = self.RESOLUTION_PATTERN.search(folder_name)
        if match:
            return match.group(1).lower()

        # Check parent folder names
        path_parts = folder_path.split(os.sep)
        for part in reversed(path_parts):
            match = self.RESOLUTION_PATTERN.search(part)
            if match:
                return match.group(1).lower()

        return None

    def _identify_main_and_variant_textures(self, texture_folders: Dict[str, Dict]) -> Tuple[Optional[str], List[str]]:
        """
        Identify main texture folder and material variants based on resolution priority.

        Logic:
        - Main textures: Folder with highest resolution (4k > 2k > 1k)
        - Material variants: All other texture folders

        Args:
            texture_folders (dict): Dictionary of texture folder info

        Returns:
            tuple: (main_texture_path, [variant_texture_paths])
        """
        if not texture_folders:
            return None, []

        # Sort by priority (highest first)
        sorted_folders = sorted(
            texture_folders.items(),
            key=lambda x: (x[1]['priority'], x[1]['texture_count']),
            reverse=True
        )

        # Main texture is highest priority
        main_texture = sorted_folders[0][0]

        # Rest are material variants
        material_variants = [path for path, _ in sorted_folders[1:]]

        return main_texture, material_variants


def scan_asset_folder(root_path: str, geo_subfolder: str = "geo", tex_subfolder: str = "tex") -> Dict:
    """
    Convenience function to scan an asset folder.

    Args:
        root_path (str): Path to root folder
        geo_subfolder (str): Geometry subfolder name (default: "geo")
        tex_subfolder (str): Texture subfolder name (default: "tex")

    Returns:
        dict: Structured scan results
    """
    scanner = AssetFolderScanner(root_path)
    return scanner.scan_folder(geo_subfolder, tex_subfolder)


# Example usage for testing
if __name__ == "__main__":
    import pprint

    # Test with the known path
    test_path = "/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva"

    try:
        print(f"Scanning: {test_path}\n")
        result = scan_asset_folder(test_path)

        print("=" * 60)
        print("SCAN RESULTS")
        print("=" * 60)
        pprint.pprint(result, width=120)

    except Exception as e:
        print(f"Error: {e}")
