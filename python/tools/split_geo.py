import hou
from modules.misc_utils import _sanitize
def split_geo():
    selected_node = hou.selectedNodes()
    obj = hou.node("obj")

    if not selected_node:
        hou.ui.displayMessage("no node is selected")
        raise ValueError("no node is selected")

    selected_node = selected_node[0]
    parent_node = selected_node.parent()
    parent_node_path = parent_node.path()
    geo_info = selected_node.geometry()

    unique_values = set()

    script_type = hou.ui.displayMessage("Please choose handle this script with primitives or points",
                                        buttons=("Primitives", "Points"))

    is_primitives = False

    if script_type == 0:
        button_pressed, attribute_name = hou.ui.readInput(
            "Provide the attribute's name to split the geometry.",
            buttons=("OK", "Cancel")
        )

        if button_pressed == 1 and not attribute_name:
            hou.ui.displayMessage("No attribute provided.Try again")
            raise ValueError("No attribute provided.")

        attribute_split = geo_info.findPrimAttrib(attribute_name)

        if not attribute_split:
            hou.ui.displayMessage(f"No specified attribute - {attribute_name} - does not exist")
            raise ValueError(f"The specified attribute - {attribute_name} - does not exist")

        is_primitives = True

        for prim in geo_info.prims():
            unique_values.add(prim.attribValue(attribute_name))
    else:
        for point in geo_info.points():
            unique_values.add(point.number())

    merge_node = parent_node.createNode('merge', node_name='mergeAll')
    node_to_layout = [selected_node]

    for index, value in enumerate(unique_values):
        blast_node = None
        null_node = None
        value = _sanitize(value)
        if is_primitives:
            blast_node = parent_node.createNode('blast', node_name=_sanitize(f"{value}_{index}"))
            blast_node.parm('group').set(f"@name={_sanitize(value)}")
            blast_node.parm('grouptype').set(4)
            null_node = parent_node.createNode("null", _sanitize(f"{value}_OUT"))
        else:
            blast_node = parent_node.createNode('blast', node_name=_sanitize(f"POINT_{value}"))
            blast_node.parm('group').set(str(value))
            blast_node.parm('grouptype').set(3)
            null_node = parent_node.createNode("null", _sanitize(f"POINT_{value}_OUT"))
        blast_node.parm('negate').set(True)
        blast_node.setInput(0, selected_node)
        null_node.setInput(0, blast_node)
        merge_node.setInput(index, null_node)
        node_to_layout.extend([blast_node, null_node])

    node_to_layout.append(merge_node)
    parent_node.layoutChildren(items=node_to_layout)
    merge_node.setDisplayFlag(True)
    merge_node.setRenderFlag(True)
