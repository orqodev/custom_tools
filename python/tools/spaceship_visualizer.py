# Enhanced Python Houdini Tool: Spaceship Visualizer with improved positioning, rotation controls, and connections

import hou
import json
import os
from typing import List, Dict, Any
from tools import spaceship_layout_generator

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

    # Part Positioning Folder
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

    # Part Rotation Folder
    rotation_folder = hou.FolderParmTemplate('rotation_folder', 'Part Rotation')
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('core_rotate', 'Core Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('wing_rotate', 'Wing Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('engine_rotate', 'Engine Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    rotation_folder.addParmTemplate(hou.FloatParmTemplate('detail_rotate', 'Detail Rotation', 3, default_value=[0.0, 0.0, 0.0]))
    parm_group.addParmTemplate(rotation_folder)

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

batch_node = hou.node(batch_import_node)

for part in layout_data:
    pt = geo.createPoint()
    pos = part.get('position', [0,0,0])
    role = part.get('role', '')

    # Apply role-specific positioning adjustments
    adjusted_pos = list(pos)
    if role == 'wing':
        # Adjust wing spread
        adjusted_pos[0] *= wing_spread
    elif role == 'engine':
        # Adjust engine offset
        adjusted_pos[2] *= engine_offset
    elif role == 'detail':
        # Adjust detail scatter
        adjusted_pos[0] *= detail_scatter
        adjusted_pos[2] *= detail_scatter

    # Apply global scale
    adjusted_pos = [p * global_scale for p in adjusted_pos]

    pt.setPosition(hou.Vector3(adjusted_pos))
    pt.setAttribValue('original_pos', hou.Vector3(pos))

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

    # === PYTHON SOP: Create Object Merge Nodes per Point ===
    load_geo_sop = geo.createNode('python', 'create_object_merges')
    load_geo_sop.setInput(0, python_sop)

    load_geo_script = """
import hou, math
node = hou.pwd()
geo_node = node.parent()
layout_geo = node.inputs()[0].geometry()

# Get rotation parameters
global_rotate = geo_node.parmTuple('global_rotate').eval()
global_translate = geo_node.parmTuple('global_translate').eval()
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

for i, pt in enumerate(layout_geo.points()):
    asset_path = pt.attribValue('asset_node')
    if not asset_path:
        continue

    role = pt.attribValue('role')

    merge_node = geo_node.createNode('object_merge', f"merge_{role}_{i}")
    merge_node.parm('objpath1').set(asset_path)
    merge_node.parm('xformtype').set(1)

    # Add transform node for positioning and rotation
    transform_node = geo_node.createNode('xform', f"transform_{role}_{i}")
    transform_node.setInput(0, merge_node)

    # Set position
    translate = pt.position()
    transform_node.parmTuple('t').set((translate[0], translate[1], translate[2]))

    # Set rotation based on role
    if role == 'core':
        transform_node.parmTuple('r').set(core_rotate)
    elif role == 'wing':
        transform_node.parmTuple('r').set(wing_rotate)
    elif role == 'engine':
        transform_node.parmTuple('r').set(engine_rotate)
    elif role == 'detail':
        transform_node.parmTuple('r').set(detail_rotate)

    merge.setNextInput(transform_node)

# Apply global transform to merged geometry
global_transform.setInput(0, merge)
node.setInput(0, global_transform)
"""
    load_geo_sop.parm('python').set(load_geo_script)

    # === CONNECTION VISUALIZATION ===
    connections_sop = geo.createNode('python', 'create_connections')
    connections_sop.setInput(0, python_sop)

    connections_script = """
import hou
node = hou.pwd()
geo = node.geometry()
geo_node = node.parent()
layout_geo = node.inputs()[0].geometry()

show_connections = geo_node.parm('show_connections').eval()
connection_thickness = geo_node.parm('connection_thickness').eval()

if show_connections:
    # Find core part
    core_pt = None
    for pt in layout_geo.points():
        if pt.attribValue('role') == 'core':
            core_pt = pt
            break

    if core_pt:
        # Create connections from core to other parts
        for pt in layout_geo.points():
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

        # Add thickness to connections if needed
        if connection_thickness > 0.01:
            # This would be handled by a polywire SOP in the node network
            pass
"""
    connections_sop.parm('python').set(connections_script)

    # Add polywire for connection thickness
    polywire = geo.createNode('polywire', 'connection_wires')
    if polywire:
        polywire.setInput(0, connections_sop)
        width_parm = polywire.parm('width')
        if width_parm:
            width_parm.setExpression('ch("../connection_thickness")')
        divisions_parm = polywire.parm('divisions')
        if divisions_parm:
            divisions_parm.set(4)

    proxy_box = geo.createNode('box', 'proxy_box')

    # Merge connections with geometry
    merge_with_connections = geo.createNode('merge', 'merge_with_connections')
    if merge_with_connections:
        merge_with_connections.setInput(0, load_geo_sop)
        if polywire:
            merge_with_connections.setInput(1, polywire)

    switch = geo.createNode('switch', 'proxy_or_real')
    if switch:
        switch.setInput(0, proxy_box)
        switch.setInput(1, merge_with_connections)
        input_parm = switch.parm('input')
        if input_parm:
            input_parm.setExpression('1 - ch("../use_proxy")')

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
