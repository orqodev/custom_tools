# Updated Python Houdini Tool: Spaceship Visualizer with working switch, hide roles, and rotation offset

import hou
import json
import os
from typing import List, Dict, Any
from tools import spaceship_layout_generator

def create_spaceship_visualizer():
    obj = hou.node('/obj')
    geo = obj.createNode('geo', 'spaceship_visualizer')

    # === PARAMETERS ===
    geo.addSpareParmTuple(hou.StringParmTemplate('json_path', 'JSON Path', 1, default_value=["$HIP/spaceship_layout.json"], string_type=hou.stringParmType.FileReference))
    geo.addSpareParmTuple(hou.StringParmTemplate('asset_dir', 'Asset Directory', 1, default_value=["$HIP/assets"], string_type=hou.stringParmType.FileReference))
    geo.addSpareParmTuple(hou.StringParmTemplate('batch_import_node', 'Batch Import Node', 1, default_value=["/obj/batch_import"], string_type=hou.stringParmType.NodeReference))
    geo.addSpareParmTuple(hou.ToggleParmTemplate('use_proxy', 'Use Proxy Geometry', default_value=True))
    geo.addSpareParmTuple(hou.ToggleParmTemplate('rotate_parts', 'Random Rotation', default_value=False))
    geo.addSpareParmTuple(hou.StringParmTemplate('hide_roles', 'Hide Roles (comma-separated)', 1, default_value=[""], string_type=hou.stringParmType.Regular))
    geo.addSpareParmTuple(hou.FloatParmTemplate('rotation_offset', 'Rotation Offset', 3, default_value=(0.0, 0.0, 0.0)))
    geo.addSpareParmTuple(hou.ButtonParmTemplate('generate_layout', 'Generate Spaceship Layout'))

    # === PYTHON SOP: Load Layout ===
    python_sop = geo.createNode('python', 'load_spaceship_layout')
    python_script = """
import json, os, hou, random, math
node = hou.pwd()
geo = node.geometry()
geo_node = node.parent()

# Get parameters from parent geo node
json_path_parm = geo_node.parm('json_path')
hide_roles_parm = geo_node.parm('hide_roles')
offset_parm = geo_node.parmTuple('rotation_offset')
rotate_parts_parm = geo_node.parm('rotate_parts')

if None in (json_path_parm, hide_roles_parm, offset_parm, rotate_parts_parm):
    raise hou.NodeError("Missing required parameters on parent geo node.")

json_path = json_path_parm.eval()
hide_roles = [r.strip() for r in hide_roles_parm.eval().split(',') if r.strip()]
offset = offset_parm.eval()
rotate_parts = rotate_parts_parm.eval()

layout_data = json.load(open(json_path))

# Ensure attributes exist before assignment
geo.addAttrib(hou.attribType.Point, 'name', '')
geo.addAttrib(hou.attribType.Point, 'role', '')
geo.addAttrib(hou.attribType.Point, 'size_type', '')
geo.addAttrib(hou.attribType.Point, 'scale', 1.0)
geo.addAttrib(hou.attribType.Point, 'rotation', (0.0, 0.0, 0.0))
geo.addAttrib(hou.attribType.Point, 'visible', 1)

for part in layout_data:
    pt = geo.createPoint()
    pos = part.get('position', [0,0,0])
    pt.setPosition(hou.Vector3(pos))

    name = part.get('name', '')
    role = part.get('role', '')
    size = part.get('size_type', '')

    pt.setAttribValue('name', name)
    pt.setAttribValue('role', role)
    pt.setAttribValue('size_type', size)

    scale = {'Big':3, 'Medium':2, 'Small':1}.get(size, 1)
    pt.setAttribValue('scale', scale)
    pt.setAttribValue('visible', int(role not in hide_roles))

    rx, ry, rz = 0.0, 0.0, 0.0
    if rotate_parts:
        rx, ry, rz = random.uniform(0,360), random.uniform(0,360), random.uniform(0,360)
        if role == 'wing': rx, rz = 0.0, 0.0
        if role == 'engine': ry, rx, rz = 180.0, random.uniform(-15,15), random.uniform(-15,15)
    elif role == 'engine': ry = 180.0

    rx += offset[0]; ry += offset[1]; rz += offset[2]
    pt.setAttribValue('rotation', (rx, ry, rz))
"""
    python_sop.parm('python').set(python_script)

    # === BLAST SOP: Remove Hidden ===
    blast_sop = geo.createNode('blast', 'remove_hidden')
    blast_sop.setInput(0, python_sop)
    blast_sop.parm('group').set('@visible==0')

    # === BOX SOP: Proxy ===
    box = geo.createNode('box', 'proxy_box')
    box.parmTuple('size').set((1,1,1))

    color = geo.createNode('attribwrangle', 'color_by_role')
    color.setInput(0, box)
    color.parm('snippet').set('''
if (s@role == "core") @Cd = {1,0,0};
else if (s@role == "wing") @Cd = {0,0,1};
else if (s@role == "engine") @Cd = {1,1,0};
else @Cd = {0.5,0.5,0.5};
''')

    # === SWITCH SOP: Proxy or Real ===
    switch = geo.createNode('switch', 'proxy_or_real')
    switch.setInput(0, color)
    switch.setInput(1, box)  # placeholder for real geometry or future SOP
    switch.parm('input').setExpression('1 - ch("../use_proxy")')

    # === COPY TO POINTS ===
    copy = geo.createNode('copytopoints', 'copy_to_points')
    copy.setInput(0, switch)
    copy.setInput(1, blast_sop)
    copy.parm('usepointattrib').set(1)
    copy.parm('pointattrib').set('scale')
    copy.parm('userotation').set(True)
    copy.parm('rotationattrib').set('rotation')

    # === OUT ===
    out = geo.createNode('null', 'OUT')
    out.setInput(0, copy)
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
