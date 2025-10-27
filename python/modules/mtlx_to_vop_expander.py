"""
MaterialX to VOP Expander - Convert MaterialX files to editable Houdini VOP networks

This module provides functionality to read MaterialX (.mtlx) files and expand them
into native Houdini VOP shader networks within a materiallibrary node.

Instead of importing closed USD materials, this creates fully editable shader networks
that you can modify in Houdini.
"""

import hou
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from modules.misc_utils import _sanitize, slugify


class MaterialXToVOPExpander:
    """
    Expands MaterialX files into editable Houdini VOP networks.
    """

    def __init__(self, material_library: Optional[hou.LopNode] = None):
        """
        Initialize the MaterialX expander.

        Args:
            material_library (hou.LopNode): Optional materiallibrary node to add materials to
        """
        self.material_library = material_library
        self.created_materials = []

    def expand_mtlx_file(
        self,
        mtlx_file_path: str,
        material_library_node: Optional[hou.LopNode] = None
    ) -> List[hou.VopNode]:
        """
        Expand a MaterialX file into VOP networks.

        Args:
            mtlx_file_path (str): Path to .mtlx file
            material_library_node (hou.LopNode): Optional materiallibrary to use

        Returns:
            list: List of created material VOP networks
        """
        if not os.path.exists(mtlx_file_path):
            raise ValueError(f"MaterialX file not found: {mtlx_file_path}")

        # Use provided material library or create new one
        if material_library_node:
            self.material_library = material_library_node
        elif self.material_library is None:
            self.material_library = self._create_material_library()

        # Parse the MaterialX file
        mtlx_data = self._parse_mtlx_file(mtlx_file_path)

        # Create VOP networks for each material
        materials = []
        for material_name, material_data in mtlx_data.items():
            vop_net = self._create_vop_material(material_name, material_data, mtlx_file_path)
            if vop_net:
                materials.append(vop_net)

        return materials

    def expand_mtlx_folder(
        self,
        folder_path: str,
        material_library_node: Optional[hou.LopNode] = None,
        recursive: bool = True
    ) -> List[hou.VopNode]:
        """
        Expand all MaterialX files in a folder.

        Args:
            folder_path (str): Path to folder containing .mtlx files
            material_library_node (hou.LopNode): Optional materiallibrary to use
            recursive (bool): Search subfolders recursively

        Returns:
            list: List of created material VOP networks
        """
        if not os.path.exists(folder_path):
            raise ValueError(f"Folder not found: {folder_path}")

        # Use provided material library or create new one
        if material_library_node:
            self.material_library = material_library_node
        elif self.material_library is None:
            self.material_library = self._create_material_library()

        # Find all .mtlx files
        mtlx_files = []
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.mtlx'):
                        mtlx_files.append(os.path.join(root, file))
        else:
            mtlx_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.endswith('.mtlx')
            ]

        # Expand each file
        all_materials = []
        for mtlx_file in mtlx_files:
            try:
                materials = self.expand_mtlx_file(mtlx_file, self.material_library)
                all_materials.extend(materials)
            except Exception as e:
                print(f"Error expanding {mtlx_file}: {e}")

        return all_materials

    def _create_material_library(self) -> hou.LopNode:
        """
        Create a new materiallibrary node.

        Returns:
            hou.LopNode: The created materiallibrary node
        """
        # Find or create stage context
        obj = hou.node('/obj')
        stage = obj.node('stage')

        if stage is None:
            stage = obj.createNode('lopnet', node_name='stage')

        # Create materiallibrary
        matlib = stage.createNode('materiallibrary', node_name='expanded_materials')

        return matlib

    def _parse_mtlx_file(self, mtlx_file_path: str) -> Dict:
        """
        Parse a MaterialX XML file and extract material data.

        Args:
            mtlx_file_path (str): Path to .mtlx file

        Returns:
            dict: Material data organized by material name
        """
        tree = ET.parse(mtlx_file_path)
        root = tree.getroot()

        materials = {}

        # Find all surfacematerial nodes
        for surfacematerial in root.findall('.//surfacematerial'):
            material_name = surfacematerial.get('name', 'unnamed_material')

            material_data = {
                'name': material_name,
                'nodegraphs': {},
                'shaders': {},
                'inputs': []
            }

            # Get inputs (references to shaders)
            for input_elem in surfacematerial.findall('input'):
                input_name = input_elem.get('name')
                nodename = input_elem.get('nodename')
                material_data['inputs'].append({
                    'name': input_name,
                    'nodename': nodename
                })

            materials[material_name] = material_data

        # Parse nodegraphs (texture networks)
        for nodegraph in root.findall('.//nodegraph'):
            nodegraph_name = nodegraph.get('name')

            nodegraph_data = {
                'name': nodegraph_name,
                'nodes': [],
                'outputs': []
            }

            # Parse image nodes
            for image_node in nodegraph.findall('.//image'):
                node_name = image_node.get('name')
                node_type = image_node.get('type')

                file_input = image_node.find(".//input[@name='file']")
                file_path = file_input.get('value') if file_input is not None else ''
                colorspace = file_input.get('colorspace', 'lin_rec709') if file_input is not None else 'lin_rec709'

                nodegraph_data['nodes'].append({
                    'name': node_name,
                    'type': 'image',
                    'output_type': node_type,
                    'file': file_path,
                    'colorspace': colorspace
                })

            # Parse normalmap nodes
            for normalmap_node in nodegraph.findall('.//normalmap'):
                node_name = normalmap_node.get('name')

                in_input = normalmap_node.find(".//input[@name='in']")
                input_nodename = in_input.get('nodename') if in_input is not None else ''

                scale_input = normalmap_node.find(".//input[@name='scale']")
                scale_value = None
                if scale_input is not None:
                    scale_value = scale_input.get('value')

                nodegraph_data['nodes'].append({
                    'name': node_name,
                    'type': 'normalmap',
                    'input_node': input_nodename,
                    'scale': scale_value
                })

            # Parse outputs
            for output in nodegraph.findall('.//output'):
                output_name = output.get('name')
                output_type = output.get('type')
                nodename = output.get('nodename')

                nodegraph_data['outputs'].append({
                    'name': output_name,
                    'type': output_type,
                    'nodename': nodename
                })

            # Store nodegraph in all relevant materials
            for mat_name, mat_data in materials.items():
                mat_data['nodegraphs'][nodegraph_name] = nodegraph_data

        # Parse shader nodes (standard_surface, displacement, etc.)
        for standard_surface in root.findall('.//standard_surface'):
            shader_name = standard_surface.get('name')

            shader_data = {
                'name': shader_name,
                'type': 'standard_surface',
                'inputs': []
            }

            for input_elem in standard_surface.findall('input'):
                input_name = input_elem.get('name')
                input_type = input_elem.get('type')
                value = input_elem.get('value')
                output = input_elem.get('output')
                nodegraph = input_elem.get('nodegraph')

                shader_data['inputs'].append({
                    'name': input_name,
                    'type': input_type,
                    'value': value,
                    'output': output,
                    'nodegraph': nodegraph
                })

            # Add shader to all materials
            for mat_name, mat_data in materials.items():
                mat_data['shaders'][shader_name] = shader_data

        # Parse displacement shaders
        for displacement in root.findall('.//displacement'):
            shader_name = displacement.get('name')

            shader_data = {
                'name': shader_name,
                'type': 'displacement',
                'inputs': []
            }

            for input_elem in displacement.findall('input'):
                input_name = input_elem.get('name')
                input_type = input_elem.get('type')
                value = input_elem.get('value')
                output = input_elem.get('output')
                nodegraph = input_elem.get('nodegraph')

                shader_data['inputs'].append({
                    'name': input_name,
                    'type': input_type,
                    'value': value,
                    'output': output,
                    'nodegraph': nodegraph
                })

            # Add shader to all materials
            for mat_name, mat_data in materials.items():
                mat_data['shaders'][shader_name] = shader_data

        return materials

    def _create_vop_material(
        self,
        material_name: str,
        material_data: Dict,
        mtlx_file_path: str
    ) -> Optional[hou.VopNode]:
        """
        Create a VOP network for a material.

        This will:
        - Create a mtlxstandard_surface node
        - Create mtlximage/mtlxnormalmap nodes for textures defined in nodegraphs
        - Wire the image/normal nodes into the shader inputs (base_color, metalness, roughness, normal, etc.)

        Args:
            material_name (str): Name of the material
            material_data (dict): Parsed material data
            mtlx_file_path (str): Path to source .mtlx file for relative path resolution

        Returns:
            hou.VopNode: The created mtlxstandard_surface VOP node or None
        """
        base_dir = os.path.dirname(mtlx_file_path)
        sanitized_name = slugify(material_name)

        # Create per-material subnet (USD MaterialX Builder style)
        # Ensure unique name
        base_name = sanitized_name
        final_name = base_name
        suffix = 1
        while self.material_library.node(final_name) is not None:
            final_name = f"{base_name}_{suffix:03d}"
            suffix += 1
        mtlx_subnet = self.material_library.createNode('subnet', node_name=final_name)
        # Mark as material and prepare as MaterialX Builder-ish subnet
        try:
            mtlx_subnet.setMaterialFlag(True)
        except Exception:
            pass
        # Apply a minimal MaterialX Builder parameter set similar to TexToMtlX
        try:
            ptg = hou.ParmTemplateGroup()
            folder = hou.FolderParmTemplate(
                "folder1", "MaterialX Builder", folder_type=hou.folderType.Collapsible, default_value=0,
                ends_tab_group=False
            )
            folder.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})
            inherit = hou.IntParmTemplate(
                "inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0, max=10,
                menu_items=(['0','1','2']), menu_labels=(['Never','Always','Material Flag']), menu_use_token=False
            )
            folder.addParmTemplate(inherit)
            expr = (
                "n = hou.pwd()\n"
                "n_hasFlag = n.isMaterialFlagSet()\n"
                "i = n.evalParm('inherit_ctrl')\n"
                "r = 'none'\n"
                "if i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\n"
                "return r"
            )
            class_arc = hou.StringParmTemplate(
                "shader_referencetype", "Class Arc", 1, default_value=([expr]),
                default_expression=([expr]), default_expression_language=hou.scriptLanguage.Python,
                string_type=hou.stringParmType.Regular,
                menu_items=(['none','reference','inherit','specialize','represent']),
                menu_labels=(['None','Reference','Inherit','Specialize','Represent'])
            )
            class_arc.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
            folder.addParmTemplate(class_arc)
            baseprim = hou.StringParmTemplate(
                "shader_baseprimpath", "Class Prim Path", 1, default_value=(["/__class_mtl__/`$OS`"]),
                string_type=hou.stringParmType.Regular
            )
            baseprim.setTags({
                "script_action": "import lopshaderutils\nlopshaderutils.selectPrimFromInputOrFile(kwargs)",
                "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.",
                "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim",
                "spare_category": "Shader"
            })
            folder.addParmTemplate(baseprim)
            folder.addParmTemplate(hou.SeparatorParmTemplate("separator1"))
            tabmask = hou.StringParmTemplate(
                "tabmenumask", "Tab Menu Mask", 1,
                default_value=(["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
            )
            tabmask.setTags({"spare_category": "Tab Menu"})
            folder.addParmTemplate(tabmask)
            rctx = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["mtlx"]))
            rctx.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
            folder.addParmTemplate(rctx)
            force = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
            force.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
            folder.addParmTemplate(force)
            ptg.append(folder)
            mtlx_subnet.setParmTemplateGroup(ptg)
        except Exception:
            pass

        # Create the shader node inside the subnet
        try:
            shader_node = mtlx_subnet.createNode('mtlxstandard_surface', node_name=f"{final_name}_shader")
        except Exception:
            shader_node = mtlx_subnet.createNode('mtlxstandard_surface', node_name=f"{final_name}_shader")

        # Helper functions
        def _resolve_path(rel_or_abs: str) -> str:
            if not rel_or_abs:
                return ''
            p = rel_or_abs.replace('\\', '/')
            if os.path.isabs(p):
                return p
            # Normalize paths like ../../Textures/...
            return os.path.normpath(os.path.join(base_dir, p))

        def _safe_setparm(node: hou.Node, parm_name: str, value):
            parm = node.parm(parm_name)
            if parm is not None and value is not None:
                try:
                    parm.set(value)
                except Exception:
                    pass

        def _infer_colorspace(node_name: str, output_type: str, provided: Optional[str]) -> str:
            # If provided explicitly in .mtlx, trust that first
            if provided and len(str(provided).strip()) > 0:
                return provided
            lname = (node_name or '').lower()
            if 'base' in lname or 'albedo' in lname or 'diffuse' in lname or output_type == 'color3':
                return 'srgb_texture'
            if 'normal' in lname:
                return 'lin_rec709'
            if any(k in lname for k in ('rough', 'gloss', 'metal', 'metallic', 'height', 'disp', 'ao', 'opacity', 'mask', 'spec')):
                return 'lin_rec709'
            # Fallback consistent with TexToMtlX
            return 'lin_rec709'

        def _is_udim_path(path: str) -> bool:
            p = (path or '').lower()
            return any(tok in p for tok in ('<udim>', '$udim', '%(udim)d')) or \
                   any(part.isdigit() and len(part) == 4 and part.startswith(('1','2')) for part in os.path.basename(p).split('.'))

        def _connect_by_name(dst: hou.VopNode, input_name: str, src: hou.VopNode, src_output_index: int = 0):
            # Try to connect by named input first (if API available), fallback to index lookup
            try:
                if hasattr(dst, 'setNamedInput'):
                    dst.setNamedInput(input_name, src, src_output_index)  # type: ignore[attr-defined]
                    return True
            except Exception:
                pass
            # Try resolve input index
            try:
                if hasattr(dst, 'inputIndexOf'):
                    idx = dst.inputIndexOf(input_name)  # type: ignore[attr-defined]
                elif hasattr(dst, 'inputIndex'):
                    idx = dst.inputIndex(input_name)  # type: ignore[attr-defined]
                else:
                    idx = None
                if idx is not None and isinstance(idx, int) and idx >= 0:
                    dst.setInput(idx, src, src_output_index)
                    return True
            except Exception:
                pass
            return False

        # Build nodes from nodegraphs
        created_nodes: Dict[str, hou.VopNode] = {}
        nodegraphs = material_data.get('nodegraphs', {}) or {}

        for ng_name, ng_data in nodegraphs.items():
            # First pass: create image nodes
            for node_desc in ng_data.get('nodes', []):
                if node_desc.get('type') == 'image':
                    node_name = node_desc.get('name')
                    output_type = node_desc.get('output_type', 'color3')
                    file_path = _resolve_path(node_desc.get('file', ''))
                    provided_cs = node_desc.get('colorspace')
                    colorspace = _infer_colorspace(node_name, output_type, provided_cs)

                    hnode_name = f"{sanitized_name}_{node_name}"
                    try:
                        img_node = mtlx_subnet.createNode('mtlximage', node_name=hnode_name)
                    except Exception:
                        img_node = mtlx_subnet.createNode('mtlximage', node_name=hnode_name)

                    # Set parameters
                    _safe_setparm(img_node, 'file', file_path)
                    # Colorspace parm may differ by version; try a few common names
                    for cs_parm in ('colorspace', 'filecolorspace', 'ocio_colorspace'):
                        if img_node.parm(cs_parm):
                            _safe_setparm(img_node, cs_parm, colorspace)
                            break
                    # Best-effort UDIM toggle if such parm exists
                    if _is_udim_path(file_path):
                        for udim_parm in ('udim', 'useudim', 'enableudim', 'uselocaludim'):
                            if img_node.parm(udim_parm):
                                _safe_setparm(img_node, udim_parm, 1)
                                break

                    created_nodes[node_name] = img_node

            # Second pass: create normalmap nodes and wire their inputs
            for node_desc in ng_data.get('nodes', []):
                if node_desc.get('type') == 'normalmap':
                    node_name = node_desc.get('name')
                    input_node_name = node_desc.get('input_node')
                    scale_value = node_desc.get('scale')

                    hnode_name = f"{sanitized_name}_{node_name}"
                    try:
                        nrm_node = mtlx_subnet.createNode('mtlxnormalmap', node_name=hnode_name)
                    except Exception:
                        nrm_node = mtlx_subnet.createNode('mtlxnormalmap', node_name=hnode_name)

                    # Connect input from referenced image node if available
                    src = created_nodes.get(input_node_name)
                    if isinstance(src, hou.VopNode):
                        _connect_by_name(nrm_node, 'in', src, 0)

                    # Apply scale if provided
                    if scale_value is not None:
                        _safe_setparm(nrm_node, 'scale', scale_value)

                    created_nodes[node_name] = nrm_node

        # Wire shader inputs from shader_data definitions
        # Find a standard_surface shader entry
        std_surface = None
        for s_name, s_data in (material_data.get('shaders') or {}).items():
            if (s_data or {}).get('type') == 'standard_surface':
                std_surface = s_data
                break

        if std_surface:
            for inp in std_surface.get('inputs', []):
                inp_name = inp.get('name')
                out_name = inp.get('output')
                ng_ref = inp.get('nodegraph')
                # If the input references a nodegraph output, find the source nodename
                if out_name and ng_ref and ng_ref in nodegraphs:
                    ng_data = nodegraphs[ng_ref]
                    src_node_name = None
                    for out_desc in ng_data.get('outputs', []):
                        if out_desc.get('name') == out_name:
                            src_node_name = out_desc.get('nodename')
                            break
                    if src_node_name and src_node_name in created_nodes:
                        _connect_by_name(shader_node, inp_name, created_nodes[src_node_name], 0)
                else:
                    # If a constant value is present, set the parm if it exists
                    val = inp.get('value')
                    if val is not None:
                        _safe_setparm(shader_node, inp_name, val)

        # Optional: handle displacement
        disp_node = None
        disp_data = None
        for s_name, s_data in (material_data.get('shaders') or {}).items():
            if (s_data or {}).get('type') == 'displacement':
                disp_data = s_data
                break
        if disp_data:
            try:
                disp_node = mtlx_subnet.createNode('mtlxdisplacement', node_name=f"{sanitized_name}_displacement")
                # Connect the displacement height if provided via nodegraph
                for inp in disp_data.get('inputs', []):
                    if inp.get('name') == 'displacement':
                        out_name = inp.get('output')
                        ng_ref = inp.get('nodegraph')
                        if out_name and ng_ref and ng_ref in nodegraphs:
                            ng_data = nodegraphs[ng_ref]
                            src_node_name = None
                            for out_desc in ng_data.get('outputs', []):
                                if out_desc.get('name') == out_name:
                                    src_node_name = out_desc.get('nodename')
                                    break
                            if src_node_name and src_node_name in created_nodes:
                                _connect_by_name(disp_node, 'displacement', created_nodes[src_node_name], 0)
                    elif inp.get('name') == 'scale' and inp.get('value') is not None:
                        _safe_setparm(disp_node, 'scale', inp.get('value'))
            except Exception:
                pass

        # Ensure a proper MaterialX Builder style output exists so the subnet is a valid material
        try:
            out_node = mtlx_subnet.createNode('suboutput', node_name='OUT')
        except Exception:
            try:
                out_node = mtlx_subnet.node('OUT') or mtlx_subnet.createNode('suboutput')
            except Exception:
                out_node = None

        # Wire surface and displacement to the subnet output when possible
        try:
            if out_node is not None:
                _connect_by_name(out_node, 'surface', shader_node, 0)
                if disp_node is not None:
                    _connect_by_name(out_node, 'displacement', disp_node, 0)
        except Exception:
            pass

        # Layout for readability
        try:
            mtlx_subnet.layoutChildren()
            self.material_library.layoutChildren()
        except Exception:
            pass

        print(f"Created material subnet: {final_name} at {mtlx_subnet.path()}")

        # Record
        self.created_materials.append({'name': material_name, 'node': mtlx_subnet, 'path': mtlx_subnet.path()})
        return mtlx_subnet


def expand_mtlx_file(
    mtlx_file_path: str,
    material_library_node: Optional[hou.LopNode] = None
) -> List[hou.VopNode]:
    """
    Convenience function to expand a MaterialX file.

    Args:
        mtlx_file_path (str): Path to .mtlx file
        material_library_node (hou.LopNode): Optional materiallibrary node

    Returns:
        list: List of created material VOP networks
    """
    expander = MaterialXToVOPExpander(material_library_node)
    return expander.expand_mtlx_file(mtlx_file_path, material_library_node)


def expand_mtlx_folder(
    folder_path: str,
    material_library_node: Optional[hou.LopNode] = None,
    recursive: bool = True
) -> List[hou.VopNode]:
    """
    Convenience function to expand all MaterialX files in a folder.

    Args:
        folder_path (str): Path to folder
        material_library_node (hou.LopNode): Optional materiallibrary node
        recursive (bool): Search recursively

    Returns:
        list: List of created material VOP networks
    """
    expander = MaterialXToVOPExpander(material_library_node)
    return expander.expand_mtlx_folder(folder_path, material_library_node, recursive)


# Example usage
if __name__ == "__main__":
    # Example: Expand a single MaterialX file
    mtlx_path = "/path/to/material.mtlx"
    materials = expand_mtlx_file(mtlx_path)

    print(f"Created {len(materials)} materials")
    for mat in materials:
        print(f"  - {mat.path()}")
