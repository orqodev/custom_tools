# Enhanced Python Houdini Tool: Spaceship Visualizer with improved positioning, rotation controls, and connections

import hou
import json
import os
from typing import List, Dict, Any
from tools import spaceship_layout_generator

def create_dynamic_asset_parameters(json_path):
    """Create individual transform parameters for each asset based on JSON layout"""
    try:
        if not os.path.exists(json_path):
            return []

        with open(json_path, 'r') as f:
            layout_data = json.load(f)

        asset_parameters = []

        for i, part in enumerate(layout_data):
            name = part.get('name', f'part_{i}')
            role = part.get('role', 'unknown')

            # Translation parameters
            translate_parm = hou.FloatParmTemplate(f'asset_{i}_translate', f'{name} Translate', 3, default_value=[0.0, 0.0, 0.0])
            translate_parm.setMinValue(-100.0)
            translate_parm.setMaxValue(100.0)
            asset_parameters.append(translate_parm)

            # Rotation parameters
            rotate_parm = hou.FloatParmTemplate(f'asset_{i}_rotate', f'{name} Rotate', 3, default_value=[0.0, 0.0, 0.0])
            rotate_parm.setMinValue(-360.0)
            rotate_parm.setMaxValue(360.0)
            asset_parameters.append(rotate_parm)

            # Scale parameters
            scale_parm = hou.FloatParmTemplate(f'asset_{i}_scale', f'{name} Scale', 3, default_value=[1.0, 1.0, 1.0])
            scale_parm.setMinValue(0.1)
            scale_parm.setMaxValue(10.0)
            asset_parameters.append(scale_parm)

            # Uniform scale parameter
            uniform_scale_parm = hou.FloatParmTemplate(f'asset_{i}_uniform_scale', f'{name} Uniform Scale', 1, default_value=[1.0])
            uniform_scale_parm.setMinValue(0.1)
            uniform_scale_parm.setMaxValue(10.0)
            asset_parameters.append(uniform_scale_parm)

            # Enable/disable parameter
            enable_parm = hou.ToggleParmTemplate(f'asset_{i}_enable', f'{name} Enable', default_value=True)
            asset_parameters.append(enable_parm)

        return asset_parameters
    except Exception as e:
        print(f"Error creating dynamic parameters: {e}")
        return []

def refresh_asset_parameters(**kwargs):
    """Callback function to refresh individual asset parameters when JSON layout changes"""
    try:
        node = kwargs.get('node')
        if not node:
            return

        # Get current JSON path
        json_path_parm = node.parm('json_path')
        if not json_path_parm:
            print("JSON path parameter not found")
            return

        json_path = hou.expandString(json_path_parm.eval())

        # Get current parameter template group
        parm_group = node.parmTemplateGroup()

        # Remove existing individual asset parameters
        params_to_remove = []
        for parm_template in parm_group.parmTemplates():
            if parm_template.name().startswith('asset_') and ('_translate' in parm_template.name() or '_rotate' in parm_template.name() or '_scale' in parm_template.name() or '_uniform_scale' in parm_template.name() or '_enable' in parm_template.name()):
                params_to_remove.append(parm_template)

        for param in params_to_remove:
            try:
                parm_group.remove(param)
            except Exception as e:
                print(f"Warning: Could not remove parameter {param.name()}: {e}")

        # Create new asset parameters
        asset_parameters = create_dynamic_asset_parameters(json_path)

        if asset_parameters:
            # Add all individual asset parameters to the root level
            for asset_param in asset_parameters:
                parm_group.addParmTemplate(asset_param)

        # Apply updated parameter template group
        node.setParmTemplateGroup(parm_group)

        print(f"Refreshed asset parameters for {len(asset_parameters)} parameters")

    except Exception as e:
        print(f"Error refreshing asset parameters: {e}")

def create_spaceship_visualizer():
    obj = hou.node('/obj')
    geo = obj.createNode('geo', 'spaceship_visualizer')

    # === PARAMETERS ===
    # Create parameter folders for better organization
    parm_group = hou.ParmTemplateGroup()

    # Input/Output Folder
    input_folder = hou.FolderParmTemplate('input_folder', 'Input/Output')
    input_folder.addParmTemplate(hou.StringParmTemplate('json_path', 'JSON Path', 1, default_value=["$HIP/spaceship_layout.json"], string_type=hou.stringParmType.FileReference))
    input_folder.addParmTemplate(hou.StringParmTemplate('batch_import_node', 'Batch Import Node', 1, default_value=["/obj/batch_import"], string_type=hou.stringParmType.NodeReference))
    input_folder.addParmTemplate(hou.ToggleParmTemplate('use_proxy', 'Use Proxy Geometry', default_value=True))
    refresh_button_template = hou.ButtonParmTemplate('refresh_assets', 'Refresh Asset Parameters')
    refresh_button_template.setScriptCallback('''
import hou
import json
import os

def create_dynamic_asset_parameters(json_path):
    """Create individual transform parameters for each asset based on JSON layout"""
    try:
        if not os.path.exists(json_path):
            return []

        with open(json_path, 'r') as f:
            layout_data = json.load(f)

        asset_parameters = []

        for i, part in enumerate(layout_data):
            name = part.get('name', f'part_{i}')
            role = part.get('role', 'unknown')

            # Translation parameters
            translate_parm = hou.FloatParmTemplate(f'asset_{i}_translate', f'{name} Translate', 3, default_value=[0.0, 0.0, 0.0])
            translate_parm.setMinValue(-100.0)
            translate_parm.setMaxValue(100.0)
            asset_parameters.append(translate_parm)

            # Rotation parameters
            rotate_parm = hou.FloatParmTemplate(f'asset_{i}_rotate', f'{name} Rotate', 3, default_value=[0.0, 0.0, 0.0])
            rotate_parm.setMinValue(-360.0)
            rotate_parm.setMaxValue(360.0)
            asset_parameters.append(rotate_parm)

            # Scale parameters
            scale_parm = hou.FloatParmTemplate(f'asset_{i}_scale', f'{name} Scale', 3, default_value=[1.0, 1.0, 1.0])
            scale_parm.setMinValue(0.1)
            scale_parm.setMaxValue(10.0)
            asset_parameters.append(scale_parm)

            # Uniform scale parameter
            uniform_scale_parm = hou.FloatParmTemplate(f'asset_{i}_uniform_scale', f'{name} Uniform Scale', 1, default_value=[1.0])
            uniform_scale_parm.setMinValue(0.1)
            uniform_scale_parm.setMaxValue(10.0)
            asset_parameters.append(uniform_scale_parm)

            # Enable/disable parameter
            enable_parm = hou.ToggleParmTemplate(f'asset_{i}_enable', f'{name} Enable', default_value=True)
            asset_parameters.append(enable_parm)

        return asset_parameters
    except Exception as e:
        print(f"Error creating dynamic parameters: {e}")
        return []

# Refresh asset parameters
try:
    node = kwargs['node']

    # Get current JSON path
    json_path_parm = node.parm('json_path')
    if not json_path_parm:
        print("JSON path parameter not found")
    else:
        json_path = hou.expandString(json_path_parm.eval())

        # Get current parameter template group
        parm_group = node.parmTemplateGroup()

        # Remove existing individual asset parameters
        params_to_remove = []
        for parm_template in parm_group.parmTemplates():
            if parm_template.name().startswith('asset_') and ('_translate' in parm_template.name() or '_rotate' in parm_template.name() or '_scale' in parm_template.name() or '_uniform_scale' in parm_template.name() or '_enable' in parm_template.name()):
                params_to_remove.append(parm_template)

        for param in params_to_remove:
            try:
                parm_group.remove(param)
            except Exception as e:
                print(f"Warning: Could not remove parameter {param.name()}: {e}")

        # Create new asset parameters
        asset_parameters = create_dynamic_asset_parameters(json_path)

        if asset_parameters:
            # Add all individual asset parameters to the root level
            for asset_param in asset_parameters:
                parm_group.addParmTemplate(asset_param)

        # Apply updated parameter template group
        node.setParmTemplateGroup(parm_group)

        print(f"Refreshed asset parameters for {len(asset_parameters)} parameters")

except Exception as e:
    print(f"Error refreshing asset parameters: {e}")
''')
    refresh_button_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    input_folder.addParmTemplate(refresh_button_template)
    parm_group.addParmTemplate(input_folder)

    # Global Transform Folder
    global_folder = hou.FolderParmTemplate('global_folder', 'Global Transform')
    global_scale_parm = hou.FloatParmTemplate('global_scale', 'Global Scale', 1, default_value=[1.0])
    global_scale_parm.setMinValue(0.1)
    global_scale_parm.setMaxValue(10.0)
    global_folder.addParmTemplate(global_scale_parm)
    global_folder.addParmTemplate(hou.FloatParmTemplate('global_rotate', 'Global Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    global_folder.addParmTemplate(hou.FloatParmTemplate('global_translate', 'Global Translation', 3, default_value=[0.0, 0.0, 0.0]))
    parm_group.addParmTemplate(global_folder)

    # Part Positioning Folder (kept for backward compatibility)
    positioning_folder = hou.FolderParmTemplate('positioning_folder', 'Part Positioning')
    wing_spread_parm = hou.FloatParmTemplate('wing_spread', 'Wing Spread', 1, default_value=[1.0])
    wing_spread_parm.setMinValue(0.1)
    wing_spread_parm.setMaxValue(3.0)
    positioning_folder.addParmTemplate(wing_spread_parm)
    engine_offset_parm = hou.FloatParmTemplate('engine_offset', 'Engine Offset', 1, default_value=[1.0])
    engine_offset_parm.setMinValue(0.1)
    engine_offset_parm.setMaxValue(3.0)
    positioning_folder.addParmTemplate(engine_offset_parm)
    detail_scatter_parm = hou.FloatParmTemplate('detail_scatter', 'Detail Scatter', 1, default_value=[1.0])
    detail_scatter_parm.setMinValue(0.1)
    detail_scatter_parm.setMaxValue(3.0)
    positioning_folder.addParmTemplate(detail_scatter_parm)
    parm_group.addParmTemplate(positioning_folder)

    # Part Rotation Folder (kept for backward compatibility)
    rotation_folder = hou.FolderParmTemplate('rotation_folder', 'Part Rotation')
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('core_rotate', 'Core Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('wing_rotate', 'Wing Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('engine_rotate', 'Engine Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('detail_rotate', 'Detail Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    parm_group.addParmTemplate(rotation_folder)

    # Try to create dynamic asset parameters
    json_path = "$HIP/spaceship_layout.json"
    expanded_path = hou.expandString(json_path)
    asset_parameters = create_dynamic_asset_parameters(expanded_path)

    # Add individual asset transform parameters at root level
    if asset_parameters:
        for asset_param in asset_parameters:
            parm_group.addParmTemplate(asset_param)

    # Visualization Folder
    viz_folder = hou.FolderParmTemplate('viz_folder', 'Visualization')
    viz_folder.addParmTemplate(hou.ToggleParmTemplate('show_connections', 'Show Connections', default_value=True))
    connection_thickness_parm = hou.FloatParmTemplate('connection_thickness', 'Connection Thickness', 1, default_value=[0.05])
    connection_thickness_parm.setMinValue(0.01)
    connection_thickness_parm.setMaxValue(0.2)
    viz_folder.addParmTemplate(connection_thickness_parm)
    parm_group.addParmTemplate(viz_folder)

    # Apply parameter template group
    geo.setParmTemplateGroup(parm_group)

    # === PYTHON SOP: Load Layout ===
    python_sop = geo.createNode('python', 'load_spaceship_layout')
    python_script = """
import json, os, hou, math
node = hou.pwd()
geo = node.geometry()
geo_node = node.parent()

json_path = geo_node.parm('json_path').eval()
batch_import_node = geo_node.parm('batch_import_node').eval()
layout_data = json.load(open(json_path))

# Get parameter values for positioning adjustments
wing_spread = geo_node.parm('wing_spread').eval()
engine_offset = geo_node.parm('engine_offset').eval()
detail_scatter = geo_node.parm('detail_scatter').eval()
global_scale = geo_node.parm('global_scale').eval()

geo.addAttrib(hou.attribType.Point, 'name', '')
geo.addAttrib(hou.attribType.Point, 'role', '')
geo.addAttrib(hou.attribType.Point, 'asset_node', '')
geo.addAttrib(hou.attribType.Point, 'original_pos', hou.Vector3(0.0, 0.0, 0.0))
geo.addAttrib(hou.attribType.Point, 'bounding_box', hou.Vector3(1.0, 1.0, 1.0))

batch_node = hou.node(batch_import_node)

# First pass: collect all parts and calculate bounding boxes
parts_data = []
core_part = None

for part in layout_data:
    role = part.get('role', '')
    name = part.get('name', '')

    # Estimate bounding box based on size_type and role
    size_type = part.get('size_type', 'Medium')
    if size_type == 'Big':
        bbox = hou.Vector3(4.0, 2.0, 8.0)  # Large core hull
    elif size_type == 'Medium':
        if role == 'wing':
            bbox = hou.Vector3(6.0, 1.0, 3.0)  # Wide wings
        elif role == 'engine':
            bbox = hou.Vector3(2.0, 2.0, 4.0)  # Long engines
        else:
            bbox = hou.Vector3(2.0, 2.0, 2.0)  # Default medium
    else:  # Small
        if 'antenna' in name.lower():
            bbox = hou.Vector3(0.5, 3.0, 0.5)  # Tall antenna
        else:
            bbox = hou.Vector3(1.0, 1.0, 1.0)  # Default small

    part_data = {
        'part': part,
        'role': role,
        'name': name,
        'bbox': bbox,
        'original_pos': part.get('position', [0,0,0])
    }
    parts_data.append(part_data)

    if role == 'core':
        core_part = part_data

# Second pass: calculate improved positions with attachment logic
for part_data in parts_data:
    pt = geo.createPoint()
    part = part_data['part']
    role = part_data['role']
    name = part_data['name']
    bbox = part_data['bbox']
    original_pos = part_data['original_pos']

    if role == 'core':
        # Core stays at origin
        adjusted_pos = [0, 0, 0]
    else:
        # Calculate attachment-based position
        if not core_part:
            # Fallback to original positioning if no core
            adjusted_pos = list(original_pos)
        else:
            core_bbox = core_part['bbox']

            if role == 'wing':
                # Enhanced wing positioning: Use wing root position based on core dimensions
                side = 1 if original_pos[0] >= 0 else -1
                x_pos = side * (core_bbox[0]/2 + bbox[0]/4)  # Attach at quarter point of wing
                adjusted_pos = [x_pos * wing_spread, original_pos[1], original_pos[2]]

            elif role == 'engine':
                # Enhanced engine positioning: Position relative to core's back face
                z_offset = -(core_bbox[2]/2 + bbox[2]/4)  # Attach at quarter point
                x_spacing = original_pos[0]  # Maintain lateral spacing
                adjusted_pos = [x_spacing, original_pos[1], z_offset * engine_offset]

            elif role == 'detail':
                # Enhanced detail positioning: Calculate surface normal-based positioning
                # Find closest point on core's bounding box surface
                surface_point = [original_pos[0], original_pos[1], original_pos[2]]
                for i in range(3):
                    if abs(original_pos[i]) > core_bbox[i]/2:
                        surface_point[i] = math.copysign(core_bbox[i]/2, original_pos[i])

                # Calculate offset based on part size
                offset = max(bbox[0], bbox[1], bbox[2]) * 0.5  # Half the part's size as offset

                # Calculate direction from surface point to original position
                direction = [original_pos[i] - surface_point[i] for i in range(3)]

                # Normalize direction
                length = math.sqrt(sum(d*d for d in direction))
                if length > 0:
                    direction = [d/length for d in direction]
                else:
                    direction = [1, 0, 0]  # Default direction

                # Apply surface normal-based positioning
                adjusted_pos = [surface_point[i] + direction[i] * offset * detail_scatter for i in range(3)]
            else:
                adjusted_pos = list(original_pos)

    # Apply global scale
    adjusted_pos = [p * global_scale for p in adjusted_pos]

    pt.setPosition(hou.Vector3(adjusted_pos))
    pt.setAttribValue('original_pos', hou.Vector3(original_pos))
    pt.setAttribValue('bounding_box', bbox)

    name = part.get('name', '')
    pt.setAttribValue('name', name)
    pt.setAttribValue('role', role)

    asset_path = ''
    if batch_node:
        for child in batch_node.children():
            if name in child.name():
                asset_path = child.path()
                break
    pt.setAttribValue('asset_node', asset_path)
"""
    python_sop.parm('python').set(python_script)

    # === CONNECTION VISUALIZATION ===
    connections_sop = geo.createNode('python', 'create_connections')
    connections_sop.setInput(0, python_sop)

    connections_script = """
import hou
import math
node = hou.pwd()
geo = node.geometry()
geo_node = node.parent()
layout_geo = node.inputs()[0].geometry()

show_connections = geo_node.parm('show_connections').eval()
connection_thickness = geo_node.parm('connection_thickness').eval()

# Copy input geometry to output and add connection-based positioning adjustments
for pt in layout_geo.points():
    new_pt = geo.createPoint()
    original_pos = pt.position()
    role = pt.attribValue('role')
    name = pt.attribValue('name')

    # Apply connection-based positioning adjustments
    adjusted_pos = list(original_pos)

    # Find core part for connection calculations
    core_pt = None
    for core_candidate in layout_geo.points():
        if core_candidate.attribValue('role') == 'core':
            core_pt = core_candidate
            break

    if core_pt and pt != core_pt:
        # Calculate connection-based position adjustment
        core_pos = core_pt.position()

        # Calculate distance and direction from core
        direction = [original_pos[i] - core_pos[i] for i in range(3)]
        distance = math.sqrt(sum(d*d for d in direction))

        if distance > 0:
            # Normalize direction
            direction = [d/distance for d in direction]

            # Apply connection-based spacing based on role
            if role == 'wing':
                # Wings get pulled closer to core with connection strength
                connection_strength = 0.8  # 80% of original distance
                new_distance = distance * connection_strength
            elif role == 'engine':
                # Engines maintain distance but align better
                connection_strength = 0.9  # 90% of original distance
                new_distance = distance * connection_strength
            elif role == 'detail':
                # Details get pulled significantly closer
                connection_strength = 0.6  # 60% of original distance
                new_distance = distance * connection_strength
            else:
                new_distance = distance

            # Calculate new position based on connection
            adjusted_pos = [
                core_pos[0] + direction[0] * new_distance,
                core_pos[1] + direction[1] * new_distance,
                core_pos[2] + direction[2] * new_distance
            ]

    new_pt.setPosition(hou.Vector3(adjusted_pos))
    new_pt.setAttribValue('name', name)
    new_pt.setAttribValue('role', role)
    new_pt.setAttribValue('asset_node', pt.attribValue('asset_node'))
    new_pt.setAttribValue('original_pos', pt.attribValue('original_pos'))
    new_pt.setAttribValue('bounding_box', pt.attribValue('bounding_box'))

# Create visual connections if enabled
if show_connections:
    # Find core part
    core_pt = None
    for pt in geo.points():
        if pt.attribValue('role') == 'core':
            core_pt = pt
            break

    if core_pt:
        # Create connections from core to other parts
        for pt in geo.points():
            if pt == core_pt or pt.attribValue('role') == 'core':
                continue

            # Create polyline from core to this part
            poly = geo.createPolygon()

            # Add points for the connection line
            start_pt = geo.createPoint()
            start_pt.setPosition(core_pt.position())
            poly.addVertex(start_pt)

            end_pt = geo.createPoint()
            end_pt.setPosition(pt.position())
            poly.addVertex(end_pt)
"""
    connections_sop.parm('python').set(connections_script)

    # === PYTHON SOP: Create Object Merge Nodes per Point ===
    load_geo_sop = geo.createNode('python', 'create_object_merges')
    load_geo_sop.setInput(0, connections_sop)

    load_geo_script = """
import hou, math
node = hou.pwd()
geo_node = node.parent()
layout_geo = node.inputs()[0].geometry()

# Get global transform parameters
global_rotate = geo_node.parmTuple('global_rotate').eval()
global_translate = geo_node.parmTuple('global_translate').eval()
global_scale = geo_node.parm('global_scale').eval()

# Get fallback rotation parameters for backward compatibility
core_rotate = geo_node.parmTuple('core_rotate').eval()
wing_rotate = geo_node.parmTuple('wing_rotate').eval()
engine_rotate = geo_node.parmTuple('engine_rotate').eval()
detail_rotate = geo_node.parmTuple('detail_rotate').eval()

# Delete old object_merge and transform nodes
for c in geo_node.children():
    if c.type().name() in ['object_merge', 'xform', 'merge']:
        try:
            c.destroy()
        except hou.OperationFailed:
            print(f"Could not delete node: {c.path()} (may be cooking)")

merge = geo_node.createNode('merge', 'merge_parts')

# Global transform node for entire spaceship
global_transform = geo_node.createNode('xform', 'global_transform')
global_transform.parmTuple('t').set(global_translate)
global_transform.parmTuple('r').set(global_rotate)
global_transform.parmTuple('s').set((global_scale, global_scale, global_scale))

for i, pt in enumerate(layout_geo.points()):
    asset_path = pt.attribValue('asset_node')
    if not asset_path:
        continue

    role = pt.attribValue('role')
    name = pt.attribValue('name')

    # Check if asset is enabled (individual parameter)
    enable_parm = geo_node.parm(f'asset_{i}_enable')
    if enable_parm and not enable_parm.eval():
        continue  # Skip disabled assets

    merge_node = geo_node.createNode('object_merge', f"merge_{name}_{i}")
    merge_node.parm('objpath1').set(asset_path)
    merge_node.parm('xformtype').set(1)

    # Add transform node for positioning and rotation
    transform_node = geo_node.createNode('xform', f"transform_{name}_{i}")
    transform_node.setInput(0, merge_node)

    # Get individual asset transform parameters
    individual_translate_parm = geo_node.parmTuple(f'asset_{i}_translate')
    individual_rotate_parm = geo_node.parmTuple(f'asset_{i}_rotate')
    individual_scale_parm = geo_node.parmTuple(f'asset_{i}_scale')
    individual_uniform_scale_parm = geo_node.parm(f'asset_{i}_uniform_scale')

    # Set position (base position from layout + individual offset)
    base_translate = pt.position()
    if individual_translate_parm:
        individual_offset = individual_translate_parm.eval()
        final_translate = (
            base_translate[0] + individual_offset[0],
            base_translate[1] + individual_offset[1],
            base_translate[2] + individual_offset[2]
        )
    else:
        final_translate = (base_translate[0], base_translate[1], base_translate[2])

    transform_node.parmTuple('t').set(final_translate)

    # Set rotation (individual parameter takes precedence over role-based)
    if individual_rotate_parm:
        individual_rotation = individual_rotate_parm.eval()
        transform_node.parmTuple('r').set(individual_rotation)
    else:
        # Fallback to role-based rotation for backward compatibility
        if role == 'core':
            transform_node.parmTuple('r').set(core_rotate)
        elif role == 'wing':
            transform_node.parmTuple('r').set(wing_rotate)
        elif role == 'engine':
            transform_node.parmTuple('r').set(engine_rotate)
        elif role == 'detail':
            transform_node.parmTuple('r').set(detail_rotate)

    # Set scale (individual parameter)
    if individual_scale_parm and individual_uniform_scale_parm:
        individual_scale = individual_scale_parm.eval()
        uniform_scale = individual_uniform_scale_parm.eval()
        final_scale = (
            individual_scale[0] * uniform_scale,
            individual_scale[1] * uniform_scale,
            individual_scale[2] * uniform_scale
        )
        transform_node.parmTuple('s').set(final_scale)
    elif individual_uniform_scale_parm:
        uniform_scale = individual_uniform_scale_parm.eval()
        transform_node.parmTuple('s').set((uniform_scale, uniform_scale, uniform_scale))

    merge.setNextInput(transform_node)

# Apply global transform to merged geometry
global_transform.setInput(0, merge)
node.setInput(0, global_transform)
"""
    load_geo_sop.parm('python').set(load_geo_script)

    proxy_box = geo.createNode('box', 'proxy_box')

    switch = geo.createNode('switch', 'proxy_or_real')
    if switch:
        switch.setInput(0, proxy_box)
        switch.setInput(1, load_geo_sop)
        input_parm = switch.parm('input')
        if input_parm:
            input_parm.setExpression('1 - ch("../use_proxy")')
            # Delete channels by default to allow manual control of the switch
            input_parm.deleteAllKeyframes()

    out = geo.createNode('null', 'OUT')
    if out:
        if switch:
            out.setInput(0, switch)
        out.setDisplayFlag(True)
        out.setRenderFlag(True)

    geo.layoutChildren()
    return geo

def main():
    try:
        geo = create_spaceship_visualizer()
        print(f"Spaceship visualizer created: {geo.path()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
