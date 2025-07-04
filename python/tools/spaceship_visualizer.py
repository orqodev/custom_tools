# Updated Python Houdini Tool: Spaceship Visualizer with batch_import support and per-point Object Merge + Real Geometry Loading

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
    geo.addSpareParmTuple(hou.StringParmTemplate('batch_import_node', 'Batch Import Node', 1, default_value=["/obj/batch_import"], string_type=hou.stringParmType.NodeReference))
    geo.addSpareParmTuple(hou.ToggleParmTemplate('use_proxy', 'Use Proxy Geometry', default_value=True))

    # === PYTHON SOP: Load Layout ===
    python_sop = geo.createNode('python', 'load_spaceship_layout')
    python_script = """
import json, os, hou
node = hou.pwd()
geo = node.geometry()
geo_node = node.parent()

json_path = geo_node.parm('json_path').eval()
batch_import_node = geo_node.parm('batch_import_node').eval()
layout_data = json.load(open(json_path))

geo.addAttrib(hou.attribType.Point, 'name', '')
geo.addAttrib(hou.attribType.Point, 'role', '')
geo.addAttrib(hou.attribType.Point, 'asset_node', '')

batch_node = hou.node(batch_import_node)

for part in layout_data:
    pt = geo.createPoint()
    pos = part.get('position', [0,0,0])
    pt.setPosition(hou.Vector3(pos))

    name = part.get('name', '')
    role = part.get('role', '')

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
import hou
node = hou.pwd()
geo_node = node.parent()
layout_geo = node.inputs()[0].geometry()

# Delete old object_merge and transform nodes
for c in geo_node.children():
    if c.type().name() in ['object_merge', 'xform', 'merge']:
        try:
            c.destroy()
        except hou.OperationFailed:
            print(f"Could not delete node: {c.path()} (may be cooking)")

merge = geo_node.createNode('merge', 'merge_parts')

for i, pt in enumerate(layout_geo.points()):
    asset_path = pt.attribValue('asset_node')
    if not asset_path:
        continue

    merge_node = geo_node.createNode('object_merge', f"merge_{i}")
    merge_node.parm('objpath1').set(asset_path)
    merge_node.parm('xformtype').set(1)

    # Add transform node for positioning
    transform_node = geo_node.createNode('xform', f"transform_{i}")
    transform_node.setInput(0, merge_node)

    translate = pt.position()
    transform_node.parmTuple('t').set((translate[0], translate[1], translate[2]))

    merge.setNextInput(transform_node)

node.setInput(0, merge)
"""
    load_geo_sop.parm('python').set(load_geo_script)

    proxy_box = geo.createNode('box', 'proxy_box')

    switch = geo.createNode('switch', 'proxy_or_real')
    switch.setInput(0, proxy_box)
    switch.setInput(1, load_geo_sop)
    switch.parm('input').setExpression('1 - ch("../use_proxy")')

    out = geo.createNode('null', 'OUT')
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
