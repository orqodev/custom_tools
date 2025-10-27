#!/usr/bin/env python
"""
Export Material Library (Node-based version)

This version exports materials by reading Houdini LOP nodes directly,
rather than traversing USD prims. This is simpler and faster when materials
are stored as node subnets (like those created by tex_to_mtlx).

Each material subnet is exported to its own folder containing:
    - material_name.mtlx (MaterialX XML)
    - material_name.usd (Binary USD that references the .mtlx)

Usage:
    from tools.material_tools.export_material_library_nodes import export_material_library_nodes

    export_material_library_nodes(
        lop_node_path='/stage/materiallibrary1',
        output_dir='/output/materials'
    )

    # Or use the dialog
    from tools.material_tools.export_material_library_nodes import show_export_dialog
    show_export_dialog()
"""

import os
import hou
from pxr import Usd, UsdShade, Sdf


def export_material_library_nodes(lop_node_path, output_dir, create_mtlx=True, create_usd=True):
    """
    Export material library by reading Houdini LOP nodes directly.

    This expects materials to be stored as subnet nodes (like tex_to_mtlx creates them),
    with MaterialX shader nodes inside (mtlxstandard_surface, mtlximage, etc.).

    Args:
        lop_node_path: Path to material library LOP node (e.g., '/stage/materiallibrary1')
        output_dir: Output directory for material folders
        create_mtlx: Whether to create .mtlx files (default: True)
        create_usd: Whether to create .usd files (default: True)

    Returns:
        dict: Results with counts and file lists
    """
    output_dir = hou.text.expandString(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Get the LOP node
    lop_node = hou.node(lop_node_path)
    if not lop_node:
        raise ValueError(f"Node not found: {lop_node_path}")

    if not isinstance(lop_node, hou.LopNode):
        raise ValueError(f"Node is not a LOP: {lop_node_path}")

    # Find all subnet children (each subnet = one material)
    material_subnets = []
    for child in lop_node.children():
        if child.type().name() == 'subnet':
            material_subnets.append(child)

    if not material_subnets:
        raise ValueError(f"No material subnets found in {lop_node_path}. "
                        f"This tool expects materials as subnet nodes (like tex_to_mtlx creates).")

    print(f"\n{'='*80}")
    print(f"EXPORTING MATERIAL LIBRARY (Node-based)")
    print(f"{'='*80}")
    print(f"Source: {lop_node_path}")
    print(f"Output: {output_dir}")
    print(f"Material subnets found: {len(material_subnets)}")
    print(f"Create .mtlx: {create_mtlx}")
    print(f"Create .usd: {create_usd}")
    print(f"{'='*80}\n")

    results = {
        'success': False,
        'total': len(material_subnets),
        'exported': 0,
        'mtlx_files': [],
        'usd_files': [],
        'errors': []
    }

    # Export each material subnet
    for i, mat_subnet in enumerate(material_subnets, 1):
        mat_name = mat_subnet.name()

        print(f"[{i}/{len(material_subnets)}] Processing: {mat_name}")

        # Create material folder
        mat_folder = os.path.join(output_dir, mat_name)
        os.makedirs(mat_folder, exist_ok=True)

        try:
            # Export MaterialX
            if create_mtlx:
                mtlx_file = os.path.join(mat_folder, f"{mat_name}.mtlx")
                mtlx_success = _export_materialx_from_nodes(mat_subnet, mtlx_file, mat_name)

                if mtlx_success:
                    print(f"  ✓ MaterialX created: {mtlx_file}")
                    results['mtlx_files'].append(mtlx_file)
                else:
                    print(f"  ✗ MaterialX export failed")
                    results['errors'].append(f"{mat_name}: MaterialX export failed")
                    continue

            # Create USD reference file (binary .usd)
            if create_usd and create_mtlx:
                usd_file = os.path.join(mat_folder, f"{mat_name}.usda")
                usd_success = _create_usd_reference(usd_file, mat_name)

                if usd_success:
                    print(f"  ✓ USD created: {usd_file}")
                    results['usd_files'].append(usd_file)
                else:
                    print(f"  ✗ USD export failed")
                    results['errors'].append(f"{mat_name}: USD export failed")
                    continue

            results['exported'] += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['errors'].append(f"{mat_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'='*80}")
    print(f"EXPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Total materials: {results['total']}")
    print(f"Successfully exported: {results['exported']}")
    print(f"MaterialX files: {len(results['mtlx_files'])}")
    print(f"USD files: {len(results['usd_files'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"{'='*80}\n")

    if results['errors']:
        print("Errors:")
        for error in results['errors'][:10]:
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more")
        print()

    results['success'] = results['exported'] > 0

    # Show completion dialog
    if hou.isUIAvailable():
        if results['success']:
            msg = f"Successfully exported {results['exported']}/{results['total']} materials\n\n"
            msg += f"MaterialX files: {len(results['mtlx_files'])}\n"
            msg += f"USD files: {len(results['usd_files'])}\n\n"
            msg += f"Output directory:\n{output_dir}"

            if results['errors']:
                msg += f"\n\nWarnings: {len(results['errors'])}"

            hou.ui.displayMessage(msg, severity=hou.severityType.Message)
        else:
            hou.ui.displayMessage(
                "Export failed. Check Python console for details.",
                severity=hou.severityType.Error
            )

    return results


def _export_materialx_from_nodes(mat_subnet, mtlx_file, mat_name):
    """
    Export MaterialX by reading Houdini nodes directly.

    Args:
        mat_subnet: Material subnet node containing MaterialX nodes
        mtlx_file: Output MaterialX file path
        mat_name: Material name

    Returns:
        bool: True if successful
    """
    try:
        import MaterialX as mx

        # Create MaterialX document
        doc = mx.createDocument()
        doc.setVersionString("1.38")
        doc.setColorSpace("lin_rec709")

        # Create nodegraph
        mat_name_lower = (mat_name or "").lower()
        nodegraph_name = f"NG_{mat_name_lower}"
        nodegraph = doc.addNodeGraph(nodegraph_name)

        # Track created nodes for connections
        created_nodes = {}  # Maps Houdini node to MaterialX node name

        # Find all MaterialX nodes in the subnet
        mtlx_nodes = []
        standard_surface = None

        for node in mat_subnet.allSubChildren():
            node_type = node.type().name()

            # Find standard_surface shader
            if node_type == 'mtlxstandard_surface':
                standard_surface = node
            # Collect other MaterialX nodes
            elif node_type.startswith('mtlx'):
                mtlx_nodes.append(node)

        if not standard_surface:
            print(f"    No mtlxstandard_surface node found in {mat_subnet.name()}")
            return False

        # Process all nodes to build nodegraph
        for node in mtlx_nodes:
            _process_houdini_node(node, nodegraph, doc, created_nodes)

        # Create the standard_surface shader at document level
        surf_shader_name = f"SR_{mat_name_lower}"
        surf_shader = doc.addNode("standard_surface", surf_shader_name, "surfaceshader")

        # Connect standard_surface inputs
        _connect_standard_surface_from_nodes(standard_surface, surf_shader, nodegraph_name, created_nodes, nodegraph)

        # Create material (lowercase name inside the .mtlx to match spec)
        mtlx_mat = doc.addMaterial(mat_name_lower)
        shader_input = mtlx_mat.addInput("surfaceshader", "surfaceshader")
        shader_input.setNodeName(surf_shader_name)

        # Write MaterialX XML
        mx.writeToXmlFile(doc, mtlx_file)

        if os.path.exists(mtlx_file) and os.path.getsize(mtlx_file) > 200:
            return True
        else:
            print(f"    MaterialX file too small or not created")
            return False

    except Exception as e:
        print(f"    MaterialX export error: {e}")
        import traceback
        traceback.print_exc()
        return False


def _process_houdini_node(hou_node, nodegraph, doc, created_nodes):
    """
    Process a single Houdini MaterialX node and create corresponding MaterialX node.

    Args:
        hou_node: Houdini node
        nodegraph: MaterialX nodegraph
        doc: MaterialX document
        created_nodes: Dictionary tracking created nodes

    Returns:
        str: Name of created MaterialX node (or None)
    """
    import MaterialX as mx

    node_type = hou_node.type().name()
    node_name = hou_node.name()

    # Skip if already processed
    if hou_node in created_nodes:
        return created_nodes[hou_node]

    # Handle different node types
    if node_type in ['mtlximage', 'mtlxtiledimage']:
        # Image node
        # Determine output type based on texture type
        standard_name = _get_standard_node_name(node_name)

        # Set correct output type based on texture purpose
        name_lower = node_name.lower()
        if "metalness" in name_lower or "metallic" in name_lower:
            output_type = "float"
        elif "roughness" in name_lower:
            output_type = "float"
        elif "normal" in name_lower and "map" not in name_lower:
            output_type = "vector3"
        else:
            # Default to color3 for basecolor, emissive, opacity, etc.
            output_type = "color3"

        # Create image node
        img_node = nodegraph.addNode("image", standard_name, output_type)

        # Get file parameter
        file_parm = hou_node.parm('file')
        if file_parm:
            file_value = file_parm.evalAsString()
            if file_value:
                # Convert to relative path
                relative_path = _convert_to_relative_path(file_value)

                file_param = img_node.addInput("file", "filename")
                file_param.setValueString(relative_path)

                # Set colorspace based on texture type
                if "basecolor" in name_lower or "diffuse" in name_lower or "emissive" in name_lower or "emission" in name_lower:
                    file_param.setAttribute("colorspace", "srgb_texture")
                else:
                    # Everything else (metalness, roughness, normal, opacity, etc.)
                    file_param.setAttribute("colorspace", "lin_rec709")

        # Add output
        nodegraph.addOutput(f"{standard_name}_output", output_type).setNodeName(standard_name)

        created_nodes[hou_node] = standard_name
        return standard_name

    elif node_type == 'mtlxnormalmap':
        # Normal map node - use simple name "normalmap"
        normalmap_name = "normalmap"
        norm_node = nodegraph.addNode("normalmap", normalmap_name, "vector3")

        # Process input connection
        input_conn = hou_node.input(0)
        if input_conn:
            # Recursively process input node
            source_name = _process_houdini_node(input_conn, nodegraph, doc, created_nodes)
            if source_name:
                norm_input = norm_node.addInput("in", "vector3")
                norm_input.setNodeName(source_name)

        # Get scale parameter (default to 1 like KB3D)
        scale_parm = hou_node.parm('scale')
        scale_value = 1.0
        if scale_parm:
            scale_value = scale_parm.eval()

        # Always add scale parameter (KB3D includes it)
        scale_param = norm_node.addInput("scale", "float")
        scale_param.setValue(float(scale_value))

        # Add output
        nodegraph.addOutput(f"{normalmap_name}_output", "vector3").setNodeName(normalmap_name)

        created_nodes[hou_node] = normalmap_name
        return normalmap_name

    elif node_type == 'mtlxrange':
        # Range/color correction node - skip it and return input
        input_conn = hou_node.input(0)
        if input_conn:
            return _process_houdini_node(input_conn, nodegraph, doc, created_nodes)
        return None

    # Add more node types as needed
    return None


def _connect_standard_surface_from_nodes(standard_surface_node, mtlx_shader, nodegraph_name, created_nodes, nodegraph):
    """
    Connect standard_surface inputs by reading Houdini node connections.

    Args:
        standard_surface_node: Houdini mtlxstandard_surface node
        mtlx_shader: MaterialX standard_surface shader
        nodegraph_name: Name of the nodegraph
        created_nodes: Dictionary mapping Houdini nodes to MaterialX names
        nodegraph: The MaterialX nodegraph to add helper nodes (e.g., normalmap)
    """
    import MaterialX as mx

    # Helper: determine input type for MaterialX based on name
    def _infer_type(input_name: str, source_name: str) -> str:
        n = input_name.lower()
        s = source_name.lower()
        float_inputs = {
            'base', 'metalness', 'specular', 'specular_roughness', 'diffuse_roughness',
            'specular_ior', 'specular_anisotropy', 'specular_rotation', 'transmission',
            'transmission_depth', 'transmission_scatter_anisotropy', 'transmission_dispersion',
            'transmission_extra_roughness', 'subsurface', 'subsurface_scale', 'subsurface_anisotropy',
            'sheen', 'sheen_roughness', 'coat', 'coat_roughness', 'coat_anisotropy', 'coat_rotation',
            'coat_ior', 'coat_affect_color', 'coat_affect_roughness', 'thin_film_thickness',
            'thin_film_ior', 'emission', 'thin_walled'
        }
        if n in float_inputs:
            return 'float'
        if 'metalness' in s or 'roughness' in s:
            return 'float'
        if 'normal' in n or 'tangent' in n or 'normal' in s or 'tangent' in s:
            return 'vector3'
        # Opacity in MaterialX standard_surface is color3
        return 'color3'

    # Compatibility: fetch an input name/label for a VOP input index across Houdini versions
    def _get_input_name(node, idx: int) -> str:
        # Try list-returning API
        try:
            if hasattr(node, 'inputNames'):
                names = node.inputNames()
                if isinstance(names, (list, tuple)) and 0 <= idx < len(names):
                    if names[idx]:
                        return str(names[idx])
        except Exception:
            pass
        # Try single-name API
        try:
            if hasattr(node, 'inputName'):
                name = node.inputName(idx)
                if name:
                    return str(name)
        except Exception:
            pass
        # Some builds might expose inputLabel; use as a last resort
        try:
            if hasattr(node, 'inputLabel'):
                label = node.inputLabel(idx)
                if label:
                    return str(label)
        except Exception:
            pass
        # Fallback for mtlxstandard_surface most common inputs (index order may vary across builds)
        fallback = [
            'base', 'base_color', 'diffuse_roughness', 'metalness', 'specular',
            'specular_roughness', 'specular_IOR', 'specular_anisotropy', 'specular_rotation',
            'transmission', 'transmission_color', 'transmission_depth', 'transmission_scatter',
            'transmission_scatter_anisotropy', 'transmission_dispersion', 'transmission_extra_roughness',
            'subsurface', 'subsurface_color', 'subsurface_radius', 'subsurface_scale', 'subsurface_anisotropy',
            'sheen', 'sheen_color', 'sheen_roughness', 'coat', 'coat_color', 'coat_roughness', 'coat_anisotropy',
            'coat_rotation', 'coat_IOR', 'coat_normal', 'coat_affect_color', 'coat_affect_roughness',
            'thin_film_thickness', 'thin_film_IOR', 'emission', 'emission_color', 'opacity', 'thin_walled',
            'normal', 'tangent'
        ]
        if 0 <= idx < len(fallback):
            return fallback[idx]
        return ''

    # Iterate through all node inputs directly by index to avoid parm name mismatches
    for input_idx in range(len(standard_surface_node.inputs())):
        input_conn = standard_surface_node.input(input_idx)
        if not input_conn:
            continue
        if input_conn not in created_nodes:
            # If the upstream node wasn't processed (unsupported type), skip
            continue

        # Get Houdini input name/label via compatibility helper and derive MaterialX input name
        raw_name = _get_input_name(standard_surface_node, input_idx) or ''
        input_name = raw_name.lower().replace(' ', '_')
        if not input_name:
            continue

        source_name = created_nodes[input_conn]

        # Infer source data type from name to validate mapping
        s_lower = source_name.lower()
        if ('metalness' in s_lower) or ('metallic' in s_lower) or ('roughness' in s_lower):
            source_type = 'float'
        elif 'normal' in s_lower or 'tangent' in s_lower:
            source_type = 'vector3'
        else:
            source_type = 'color3'

        # Correct common mismatches caused by fallback input name mapping
        # 1) Emission color textures should target 'emission_color', not 'emission'
        if ('emission' in s_lower) and source_type == 'color3' and input_name != 'emission_color':
            input_name = 'emission_color'
        # 2) Base color textures should target 'base_color', not 'base'
        if input_name == 'base' and source_type == 'color3':
            input_name = 'base_color'
        # 3) Roughness textures should target 'specular_roughness'
        if 'roughness' in s_lower and input_name != 'specular_roughness':
            input_name = 'specular_roughness'
        # 4) Metalness textures should target 'metalness'
        if ('metalness' in s_lower or 'metallic' in s_lower) and input_name != 'metalness':
            input_name = 'metalness'

        # Special handling: if connecting to normal and the source is an image, insert a normalmap node
        if input_name == 'normal' and source_name.startswith('image_') and not source_name.startswith('normalmap'):
            # Try to find existing normalmap node/output
            normalmap_node = nodegraph.getNode('normalmap') if hasattr(nodegraph, 'getNode') else None
            if normalmap_node is None:
                normalmap_node = nodegraph.addNode('normalmap', 'normalmap', 'vector3')
                # Hook image into normalmap.in
                nm_in = normalmap_node.addInput('in', 'vector3')
                nm_in.setNodeName(source_name)
                # Default scale 1.0 like KB3D
                nm_scale = normalmap_node.addInput('scale', 'float')
                nm_scale.setValue(1.0)
                # Ensure there is an output on the nodegraph
                if nodegraph.getOutput('normalmap_output') is None if hasattr(nodegraph, 'getOutput') else True:
                    nodegraph.addOutput('normalmap_output', 'vector3').setNodeName('normalmap')
            # Redirect connection to normalmap output
            source_name = 'normalmap'

        input_type = _infer_type(input_name, source_name)

        # Create/connect shader input
        if not mtlx_shader.getInput(input_name):
            shader_input = mtlx_shader.addInput(input_name, input_type)
            shader_input.setNodeGraphString(nodegraph_name)
            shader_input.setOutputString(f"{source_name}_output")

    # Add common default values that KB3D uses
    # Only add if not already connected
    if not mtlx_shader.getInput('specular_IOR'):
        ior_input = mtlx_shader.addInput('specular_IOR', 'float')
        ior_input.setValue(1.45)

    if not mtlx_shader.getInput('transmission'):
        trans_input = mtlx_shader.addInput('transmission', 'float')
        trans_input.setValue(0.0)

    if not mtlx_shader.getInput('emission'):
        emission_input = mtlx_shader.addInput('emission', 'float')
        emission_input.setValue(1.0)

    # Auto-connect fallbacks: if common textures exist but the shader input wasn’t connected in Houdini, wire them by name.
    # 1) base_color
    if not mtlx_shader.getInput('base_color'):
        # search for an image node whose name suggests base color
        base_src = None
        for _hou_node, _name in created_nodes.items():
            n = _name.lower()
            if n.startswith('image_') and ('base_color' in n or 'basecolor' in n or 'albedo' in n or 'diffuse' in n):
                base_src = _name
                break
        if base_src:
            inp = mtlx_shader.addInput('base_color', 'color3')
            inp.setNodeGraphString(nodegraph_name)
            inp.setOutputString(f"{base_src}_output")

    # 2) specular_roughness
    if not mtlx_shader.getInput('specular_roughness'):
        rough_src = None
        for _hou_node, _name in created_nodes.items():
            n = _name.lower()
            if n.startswith('image_') and ('specular_roughness' in n or 'roughness' in n):
                rough_src = _name
                break
        if rough_src:
            inp = mtlx_shader.addInput('specular_roughness', 'float')
            inp.setNodeGraphString(nodegraph_name)
            inp.setOutputString(f"{rough_src}_output")

    # 3) normal via normalmap
    if not mtlx_shader.getInput('normal'):
        normal_src = None
        for _hou_node, _name in created_nodes.items():
            n = _name.lower()
            if n.startswith('image_') and ('normal' in n) and not ('normalmap' in n):
                normal_src = _name
                break
        if normal_src:
            # ensure normalmap node exists
            normalmap_node = nodegraph.getNode('normalmap') if hasattr(nodegraph, 'getNode') else None
            if normalmap_node is None:
                normalmap_node = nodegraph.addNode('normalmap', 'normalmap', 'vector3')
                nm_in = normalmap_node.addInput('in', 'vector3')
                nm_in.setNodeName(normal_src)
                nm_scale = normalmap_node.addInput('scale', 'float')
                nm_scale.setValue(1.0)
                if nodegraph.getOutput('normalmap_output') is None if hasattr(nodegraph, 'getOutput') else True:
                    nodegraph.addOutput('normalmap_output', 'vector3').setNodeName('normalmap')
            # connect shader normal
            inp = mtlx_shader.addInput('normal', 'vector3')
            inp.setNodeGraphString(nodegraph_name)
            inp.setOutputString('normalmap_output')


def _get_standard_node_name(original_name):
    """Convert Houdini node name to standard MaterialX convention."""
    name_lower = original_name.lower()

    if "basecolor" in name_lower or "diffuse" in name_lower:
        return "image_base_color"
    elif "metallic" in name_lower or "metalness" in name_lower:
        return "image_metalness"
    elif "roughness" in name_lower:
        return "image_specular_roughness"
    elif "normal" in name_lower and "map" not in name_lower:
        return "image_normal"
    elif "emissive" in name_lower or "emission" in name_lower:
        return "image_emission_color"
    elif "opacity" in name_lower or "alpha" in name_lower:
        return "image_opacity"
    else:
        return f"image_{original_name}"


def _convert_to_relative_path(absolute_path):
    """Convert absolute texture path to relative format."""
    import os

    # Remove @ symbols if present (USD path markers)
    path = absolute_path.replace("@", "")

    # Expand environment variables
    path = hou.text.expandString(path)

    # Extract filename and directory structure
    if "Textures" in path:
        # Split at Textures folder
        parts = path.split("Textures")
        if len(parts) > 1:
            # Get the part after Textures
            texture_path = "Textures" + parts[1]
            # Convert to relative path: ../../Textures/...
            return f"../../{texture_path}"

    # Fallback: just return the filename
    return os.path.basename(path)


def _create_usd_reference(usd_file, mat_name):
    """
    Create a USD file that references the external MaterialX file.
    Uses binary .usd format (not ASCII .usda).

    Args:
        usd_file: Output USD file path
        mat_name: Material name

    Returns:
        bool: True if successful
    """
    try:
        # Remove existing file if present
        if os.path.exists(usd_file):
            os.remove(usd_file)

        # Create stage in memory (avoids cache issues)
        stage = Usd.Stage.CreateInMemory()

        # Set stage metadata
        stage.SetMetadata("defaultPrim", mat_name)
        stage.SetMetadata("metersPerUnit", 1.0)
        stage.SetMetadata("upAxis", "Y")

        # Create material prim
        mat_prim = stage.DefinePrim(f"/{mat_name}", "Material")

        # Add reference to MaterialX file
        mtlx_ref_path = f"./{mat_name}.mtlx"
        mtlx_material_path = f"/MaterialX/Materials/{mat_name}"
        mat_prim.GetReferences().AddReference(mtlx_ref_path, mtlx_material_path)

        # Make instanceable
        mat_prim.SetInstanceable(True)

        # Export to file (binary .usd format)
        stage.Export(usd_file)

        return os.path.exists(usd_file) and os.path.getsize(usd_file) > 0

    except Exception as e:
        print(f"    USD creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_export_dialog():
    """Show dialog for material library export (node-based version)."""
    try:
        from PySide6 import QtWidgets, QtCore
    except ImportError:
        try:
            from PySide2 import QtWidgets, QtCore
        except ImportError:
            print("ERROR: Qt not available")
            return

    class MaterialLibraryExportDialog(QtWidgets.QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Export Material Library (Node-based)")
            self.setMinimumWidth(550)

            # Make it a modeless dialog
            self.setModal(False)
            self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

            layout = QtWidgets.QVBoxLayout(self)

            # Material library selection
            lib_layout = QtWidgets.QHBoxLayout()
            lib_layout.addWidget(QtWidgets.QLabel("Material Library:"))
            self.lib_edit = QtWidgets.QLineEdit()
            self.lib_edit.setText("/stage/materiallibrary1")
            lib_layout.addWidget(self.lib_edit, 1)

            pick_btn = QtWidgets.QPushButton("Pick...")
            pick_btn.clicked.connect(self._pick_node)
            lib_layout.addWidget(pick_btn)
            layout.addLayout(lib_layout)

            # Output directory
            dir_layout = QtWidgets.QHBoxLayout()
            dir_layout.addWidget(QtWidgets.QLabel("Output Directory:"))
            self.dir_edit = QtWidgets.QLineEdit()
            self.dir_edit.setText("$HIP/materials")
            dir_layout.addWidget(self.dir_edit, 1)

            browse_btn = QtWidgets.QPushButton("Browse...")
            browse_btn.clicked.connect(self._browse_dir)
            dir_layout.addWidget(browse_btn)
            layout.addLayout(dir_layout)

            # Options
            self.mtlx_check = QtWidgets.QCheckBox("Create .mtlx files")
            self.mtlx_check.setChecked(True)
            layout.addWidget(self.mtlx_check)

            self.usd_check = QtWidgets.QCheckBox("Create .usd files (binary)")
            self.usd_check.setChecked(True)
            layout.addWidget(self.usd_check)

            # Info
            info = QtWidgets.QLabel(
                "Exports materials by reading Houdini nodes directly.\n"
                "Expects materials as subnet nodes (like tex_to_mtlx creates).\n"
                "Creates binary .usd files (not ASCII .usda)."
            )
            info.setWordWrap(True)
            info.setStyleSheet("color: gray; font-size: 10px; margin: 10px 0;")
            layout.addWidget(info)

            # Buttons
            btn_layout = QtWidgets.QHBoxLayout()
            btn_layout.addStretch()

            export_btn = QtWidgets.QPushButton("Export")
            export_btn.clicked.connect(self._export)
            btn_layout.addWidget(export_btn)

            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(self.close)
            btn_layout.addWidget(close_btn)

            layout.addLayout(btn_layout)

        def _pick_node(self):
            self.lower()

            node_path = hou.ui.selectNode(
                title="Select Material Library",
                node_type_filter=hou.nodeTypeFilter.Lop
            )

            self.raise_()
            self.activateWindow()

            if node_path:
                self.lib_edit.setText(node_path)

        def _browse_dir(self):
            dir_path = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Output Directory"
            )
            if dir_path:
                self.dir_edit.setText(dir_path)

        def _export(self):
            lib_path = self.lib_edit.text().strip()
            output_dir = self.dir_edit.text().strip()

            if not lib_path or not output_dir:
                hou.ui.displayMessage("Please specify material library and output directory")
                return

            self.close()

            # Run export
            export_material_library_nodes(
                lop_node_path=lib_path,
                output_dir=output_dir,
                create_mtlx=self.mtlx_check.isChecked(),
                create_usd=self.usd_check.isChecked()
            )

    dialog = MaterialLibraryExportDialog(hou.ui.mainQtWindow())
    dialog.show()
