#!/usr/bin/env python
"""
Modular MaterialX Exporter

This module provides standalone MaterialX export functionality that can be used
independently or integrated into other tools. It creates MaterialX documents
directly from texture folders without requiring Houdini nodes.

Features:
    - Scan texture folder and detect material sets
    - Create MaterialX XML documents with proper node graphs
    - Support for UDIM textures
    - Standard PBR texture types (basecolor, metalness, roughness, normal, etc.)
    - Compatible with KB3D MaterialX standards

Usage:
    from tools.material_tools.materialx_exporter import MaterialXExporter

    exporter = MaterialXExporter()
    result = exporter.export_from_folder(
        texture_folder='/path/to/textures',
        output_file='/path/to/output.mtlx',
        material_name='my_material'
    )
"""

import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


class MaterialXExporter:
    """Export MaterialX documents from texture folders."""

    # Texture type configuration
    TEXTURE_TYPES = {
        'basecolor': {
            'aliases': ['basecolor', 'base_color', 'diffuse', 'albedo', 'color'],
            'mtlx_name': 'image_base_color',
            'mtlx_type': 'color3',
            'colorspace': 'srgb_texture',
            'shader_input': 'base_color'
        },
        'metalness': {
            'aliases': ['metalness', 'metallic', 'metal'],
            'mtlx_name': 'image_metalness',
            'mtlx_type': 'float',
            'colorspace': 'lin_rec709',
            'shader_input': 'metalness'
        },
        'roughness': {
            'aliases': ['roughness', 'rough'],
            'mtlx_name': 'image_specular_roughness',
            'mtlx_type': 'float',
            'colorspace': 'lin_rec709',
            'shader_input': 'specular_roughness'
        },
        'normal': {
            'aliases': ['normal', 'nor', 'nrm', 'nrml', 'norm'],
            'mtlx_name': 'image_normal',
            'mtlx_type': 'vector3',
            'colorspace': 'lin_rec709',
            'shader_input': 'normal',
            'use_normalmap': True
        },
        'opacity': {
            'aliases': ['opacity', 'alpha', 'transparency'],
            'mtlx_name': 'image_opacity',
            'mtlx_type': 'color3',
            'colorspace': 'lin_rec709',
            'shader_input': 'opacity'
        },
        'emission': {
            'aliases': ['emission', 'emissive', 'emit'],
            'mtlx_name': 'image_emission_color',
            'mtlx_type': 'color3',
            'colorspace': 'srgb_texture',
            'shader_input': 'emission_color'
        },
        'displacement': {
            'aliases': ['displacement', 'disp', 'height', 'bump'],
            'mtlx_name': 'image_displacement',
            'mtlx_type': 'float',
            'colorspace': 'lin_rec709',
            'shader_input': 'displacement'
        },
        'specular': {
            'aliases': ['specular', 'spec'],
            'mtlx_name': 'image_specular',
            'mtlx_type': 'float',
            'colorspace': 'lin_rec709',
            'shader_input': 'specular'
        },
        'transmission': {
            'aliases': ['transmission', 'trans', 'transparency'],
            'mtlx_name': 'image_transmission',
            'mtlx_type': 'float',
            'colorspace': 'lin_rec709',
            'shader_input': 'transmission'
        }
    }

    VALID_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.exr', '.tx', '.tif', '.tiff', '.rat']
    UDIM_PATTERN = re.compile(r'\.(\d{4})\.')  # Matches .1001. pattern

    def __init__(self):
        """Initialize MaterialX exporter."""
        try:
            import MaterialX as mx
            self.mx = mx
            self.available = True
        except ImportError:
            self.mx = None
            self.available = False
            print("WARNING: MaterialX library not available")

    def export_from_folder(
        self,
        texture_folder: str,
        output_file: str,
        material_name: str,
        relative_texture_path: str = None,
        detect_udim: bool = True
    ) -> Dict:
        """
        Export MaterialX document from a texture folder.

        Args:
            texture_folder: Path to folder containing textures
            output_file: Path for output .mtlx file
            material_name: Name for the material
            relative_texture_path: Relative path prefix for textures (e.g., "../../Textures/png4k/")
            detect_udim: Auto-detect UDIM textures

        Returns:
            dict: Result with success status and details
        """
        if not self.available:
            return {
                'success': False,
                'error': 'MaterialX library not available',
                'file': None
            }

        try:
            # Scan textures
            textures = self._scan_texture_folder(texture_folder, material_name)

            if not textures:
                return {
                    'success': False,
                    'error': f'No textures found in {texture_folder}',
                    'file': None
                }

            # Check for UDIM
            is_udim = False
            if detect_udim:
                for tex_info in textures.values():
                    if self.UDIM_PATTERN.search(tex_info['filename']):
                        is_udim = True
                        break

            # Create MaterialX document
            doc = self._create_materialx_document(
                material_name=material_name,
                textures=textures,
                is_udim=is_udim,
                relative_texture_path=relative_texture_path,
                texture_folder=texture_folder
            )

            # Write to file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            self.mx.writeToXmlFile(doc, output_file)

            # Verify
            if not os.path.exists(output_file) or os.path.getsize(output_file) < 100:
                return {
                    'success': False,
                    'error': 'MaterialX file not created properly',
                    'file': None
                }

            return {
                'success': True,
                'file': output_file,
                'material_name': material_name,
                'textures': list(textures.keys()),
                'is_udim': is_udim
            }

        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': f'{str(e)}\n{traceback.format_exc()}',
                'file': None
            }

    def _scan_texture_folder(self, folder: str, material_name: str) -> Dict:
        """
        Scan folder for textures matching material name.
        Uses tex_to_mtlx detection logic for consistency.

        Args:
            folder: Texture folder path
            material_name: Material name to match

        Returns:
            dict: Detected textures by type (mapped to our internal types)
        """
        if not os.path.exists(folder):
            return {}

        try:
            # Import tex_to_mtlx config for proper detection
            from tools.material_tools.TexToMtlX_V2.txmtlx_config import (
                TEXTURE_EXT, TEXTURE_TYPE, TEXTURE_TYPE_SORTED, UDIM_PATTERN, SIZE_PATTERN
            )
            from collections import defaultdict
        except ImportError:
            # Fallback to simple detection if imports fail
            return self._scan_texture_folder_simple(folder, material_name)

        # Use tex_to_mtlx detection logic
        texture_list = defaultdict(lambda: defaultdict(list))

        # Get all valid texture files
        valid_files = []
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            is_file = os.path.isfile(file_path)
            valid_extension = file.lower().endswith(tuple(TEXTURE_EXT))
            check_underscore = "_" in file
            if is_file and valid_extension and check_underscore:
                valid_files.append(file)

        # Process files
        for file in valid_files:
            split_text = os.path.splitext(file)[0]
            split_text = split_text.split("_")
            mat_name = split_text[0]

            # Find the texture type
            texture_type = None
            for tx_type in TEXTURE_TYPE:
                for tx in split_text[1:]:
                    if tx.lower() == tx_type:
                        texture_type = tx_type
                        index = split_text.index(tx)
                        mat_name = '_'.join(split_text[:index])
                        break

            if not texture_type:
                continue

            # Clean material name but PRESERVE CASING
            clean_name = mat_name.replace(' ', '_').replace('-', '_')

            # Only include textures for this material (case-insensitive match)
            if clean_name.lower() != material_name.lower():
                continue

            # Update texture list
            texture_list[clean_name][texture_type].append(file)

        # Convert to our format
        textures = {}
        if material_name.lower() in [k.lower() for k in texture_list.keys()]:
            mat_key = [k for k in texture_list.keys() if k.lower() == material_name.lower()][0]
            mat_textures = texture_list[mat_key]

            # Map tex_to_mtlx texture types to our types
            type_mapping = self._map_texture_types(TEXTURE_TYPE_SORTED)

            for tex_type_key, filenames in mat_textures.items():
                if isinstance(filenames, list) and filenames:
                    # Find which of our types this maps to
                    our_type = type_mapping.get(tex_type_key)
                    if our_type and our_type not in textures:
                        textures[our_type] = {
                            'filename': filenames[0],  # Use first file
                            'filepath': os.path.join(folder, filenames[0]),
                            'type': our_type
                        }

        return textures

    def _scan_texture_folder_simple(self, folder: str, material_name: str) -> Dict:
        """Fallback simple texture scanning."""
        textures = {}
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if not os.path.isfile(filepath):
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in self.VALID_EXTENSIONS:
                continue
            base_name = os.path.splitext(filename)[0]
            if not base_name.lower().startswith(material_name.lower()):
                continue
            tex_type = self._detect_texture_type(filename)
            if tex_type and tex_type not in textures:
                textures[tex_type] = {
                    'filename': filename,
                    'filepath': filepath,
                    'type': tex_type
                }
        return textures

    def _map_texture_types(self, texture_type_sorted: Dict) -> Dict:
        """
        Map tex_to_mtlx texture type keys to our internal types.

        Args:
            texture_type_sorted: TEXTURE_TYPE_SORTED from config

        Returns:
            dict: Mapping from tx_to_mtlx keys to our keys
        """
        # Map tex_to_mtlx keys to our keys
        mapping = {}
        for key, aliases in texture_type_sorted.items():
            if 'color' in key.lower():
                mapping_key = 'basecolor'
            elif 'metal' in key.lower():
                mapping_key = 'metalness'
            elif 'rough' in key.lower():
                mapping_key = 'roughness'
            elif 'normal' in key.lower():
                mapping_key = 'normal'
            elif 'alpha' in key.lower():
                mapping_key = 'opacity'
            elif 'emm' in key.lower() or 'emission' in key.lower():
                mapping_key = 'emission'
            elif 'disp' in key.lower():
                mapping_key = 'displacement'
            elif 'spec' in key.lower():
                mapping_key = 'specular'
            elif 'trans' in key.lower():
                mapping_key = 'transmission'
            else:
                continue

            # Map each alias to our type
            for alias in aliases:
                mapping[alias] = mapping_key

        return mapping

    def _detect_texture_type(self, filename: str) -> Optional[str]:
        """
        Detect texture type from filename.

        Args:
            filename: Texture filename

        Returns:
            str: Detected texture type key, or None
        """
        filename_lower = filename.lower()

        # Remove UDIM pattern for detection
        filename_lower = self.UDIM_PATTERN.sub('.', filename_lower)

        # Split by underscores to find type keyword
        parts = os.path.splitext(filename_lower)[0].split('_')

        # Check each part against aliases
        for part in parts:
            for tex_type, config in self.TEXTURE_TYPES.items():
                if part in config['aliases']:
                    return tex_type

        return None

    def _create_materialx_document(
        self,
        material_name: str,
        textures: Dict,
        is_udim: bool,
        relative_texture_path: Optional[str],
        texture_folder: str
    ):
        """
        Create MaterialX document with node graph and shader.

        Args:
            material_name: Name for the material
            textures: Detected textures dictionary
            is_udim: Whether textures use UDIM
            relative_texture_path: Relative path prefix for textures
            texture_folder: Source texture folder

        Returns:
            MaterialX document
        """
        # Create document
        doc = self.mx.createDocument()
        doc.setVersionString("1.38")
        doc.setColorSpace("lin_rec709")

        # Create node graph (keep original material name casing)
        nodegraph_name = f"NG_{material_name}"
        nodegraph = doc.addNodeGraph(nodegraph_name)

        # Track created nodes for shader connections
        created_nodes = {}

        # Create texture nodes
        for tex_type, tex_info in textures.items():
            config = self.TEXTURE_TYPES[tex_type]

            # Create image node
            img_node = nodegraph.addNode(
                "image",
                config['mtlx_name'],
                config['mtlx_type']
            )

            # Set file path
            file_path = self._get_texture_path(
                tex_info['filename'],
                relative_texture_path,
                texture_folder,
                is_udim
            )

            file_param = img_node.addInput("file", "filename")
            file_param.setValueString(file_path)
            file_param.setAttribute("colorspace", config['colorspace'])

            # Add output
            output_name = f"{config['mtlx_name']}_output"
            nodegraph.addOutput(output_name, config['mtlx_type']).setNodeName(config['mtlx_name'])

            created_nodes[tex_type] = {
                'node_name': config['mtlx_name'],
                'output_name': output_name,
                'config': config
            }

        # Handle normal map (needs normalmap node)
        if 'normal' in created_nodes:
            normal_info = created_nodes['normal']

            # Create normalmap node
            normalmap = nodegraph.addNode("normalmap", "normalmap", "vector3")
            nm_in = normalmap.addInput("in", "vector3")
            nm_in.setNodeName(normal_info['node_name'])

            nm_scale = normalmap.addInput("scale", "float")
            nm_scale.setValue(1.0)

            # Update output
            normalmap_output = nodegraph.addOutput("normalmap_output", "vector3")
            normalmap_output.setNodeName("normalmap")

            # Update created_nodes to point to normalmap output
            created_nodes['normal']['output_name'] = 'normalmap_output'

        # Create standard_surface shader (keep original material name casing)
        surf_shader_name = f"SR_{material_name}"
        surf_shader = doc.addNode("standard_surface", surf_shader_name, "surfaceshader")

        # Connect textures to shader
        for tex_type, node_info in created_nodes.items():
            config = node_info['config']
            shader_input_name = config['shader_input']

            # Skip if this uses normalmap (already handled above)
            if config.get('use_normalmap') and tex_type == 'normal':
                shader_input_name = 'normal'

            shader_input = surf_shader.addInput(
                shader_input_name,
                config['mtlx_type']
            )
            shader_input.setNodeGraphString(nodegraph_name)
            shader_input.setOutputString(node_info['output_name'])

        # Add standard defaults
        if 'specular_IOR' not in [inp.getName() for inp in surf_shader.getInputs()]:
            ior_input = surf_shader.addInput('specular_IOR', 'float')
            ior_input.setValue(1.45)

        if 'transmission' not in [inp.getName() for inp in surf_shader.getInputs()]:
            trans_input = surf_shader.addInput('transmission', 'float')
            trans_input.setValue(0.0)

        if 'emission' in created_nodes and 'emission' not in [inp.getName() for inp in surf_shader.getInputs()]:
            emission_input = surf_shader.addInput('emission', 'float')
            emission_input.setValue(1.0)

        # Create material (keep original material name casing)
        mtlx_mat = doc.addMaterial(material_name)
        shader_input = mtlx_mat.addInput("surfaceshader", "surfaceshader")
        shader_input.setNodeName(surf_shader_name)

        return doc

    def _get_texture_path(
        self,
        filename: str,
        relative_path: Optional[str],
        texture_folder: str,
        is_udim: bool
    ) -> str:
        """
        Get texture path for MaterialX (handle UDIM and relative paths).

        Args:
            filename: Texture filename
            relative_path: Optional relative path prefix
            texture_folder: Source texture folder
            is_udim: Whether to convert to UDIM format

        Returns:
            str: Path for MaterialX file input
        """
        # Handle UDIM conversion
        if is_udim:
            filename = self.UDIM_PATTERN.sub('.<UDIM>.', filename)

        # Use relative path if provided
        if relative_path:
            if not relative_path.endswith('/'):
                relative_path += '/'
            return f"{relative_path}{filename}"

        # Otherwise use filename only
        return filename


def export_materialx_from_textures(
    texture_folder: str,
    output_file: str,
    material_name: str,
    **kwargs
) -> Dict:
    """
    Convenience function to export MaterialX from texture folder.

    Args:
        texture_folder: Path to texture folder
        output_file: Output .mtlx file path
        material_name: Material name
        **kwargs: Additional arguments for MaterialXExporter.export_from_folder

    Returns:
        dict: Export result
    """
    exporter = MaterialXExporter()
    return exporter.export_from_folder(
        texture_folder=texture_folder,
        output_file=output_file,
        material_name=material_name,
        **kwargs
    )


# Example usage
if __name__ == '__main__':
    # Example: Export MaterialX from texture folder
    result = export_materialx_from_textures(
        texture_folder='/path/to/textures',
        output_file='/path/to/output.mtlx',
        material_name='MyMaterial',
        relative_texture_path='../../Textures/png4k/'
    )

    if result['success']:
        print(f"MaterialX created: {result['file']}")
        print(f"Textures: {result['textures']}")
        print(f"UDIM: {result['is_udim']}")
    else:
        print(f"Error: {result['error']}")
