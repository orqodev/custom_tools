import hou
from modules.misc_utils import safe_node_name
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

    # Ask user if they want to sanitize attributes
    sanitize_choice = hou.ui.displayMessage(
        "Do you want to sanitize string attributes (replace spaces with underscores)?",
        buttons=("Yes", "No"),
        severity=hou.severityType.Message,
        title="Sanitize Attributes"
    )

    if sanitize_choice == 0:  # User chose "Yes"
        # Ask for comma-separated attribute names
        button_pressed, attributes_input = hou.ui.readInput(
            "Enter attribute names to sanitize (separated by commas):\nExample: name, material, shop_materialpath",
            buttons=("OK", "Cancel"),
            initial_contents="name"
        )

        if button_pressed == 0 and attributes_input.strip():  # User clicked OK and provided input
            # Parse comma-separated attributes
            attributes_list = [attr.strip() for attr in attributes_input.split(',') if attr.strip()]

            # Generate snippet code for each attribute
            snippet_lines = []
            for attr in attributes_list:
                snippet_lines.append(f's@{attr} = replace(s@{attr}, " ", "_");')

            snippet_code = '\n'.join(snippet_lines)
        else:
            # Default to name attribute if cancelled or empty
            snippet_code = 's@name = replace(s@name, " ", "_");'
    else:
        # User chose "No" - use a simple pass-through or minimal processing
        snippet_code = '// No attribute sanitization requested'

    primitive_wrangle = parent_node.createNode('attribwrangle', node_name='convert_prim_attributes')
    primitive_wrangle.parm('class').set(1)
    primitive_wrangle.parm('snippet').set(snippet_code)
    primitive_wrangle.setInput(0, selected_node)

    merge_node = parent_node.createNode('merge', node_name='mergeAll')
    node_to_layout = [selected_node,primitive_wrangle]

    for index, value in enumerate(unique_values):
        blast_node = None
        null_node = None
        value = safe_node_name(value)
        if is_primitives:
            blast_node = parent_node.createNode('blast', node_name=safe_node_name(f"{value}_{index}"))
            blast_node.parm('group').set(f"@name={safe_node_name(value)}")
            blast_node.parm('grouptype').set(4)
            null_node = parent_node.createNode("null", safe_node_name(f"{value}_OUT"))
        else:
            blast_node = parent_node.createNode('blast', node_name=safe_node_name(f"POINT_{value}"))
            blast_node.parm('group').set(str(value))
            blast_node.parm('grouptype').set(3)
            null_node = parent_node.createNode("null", safe_node_name(f"POINT_{value}_OUT"))
        blast_node.parm('negate').set(True)
        blast_node.setInput(0, primitive_wrangle)
        null_node.setInput(0, blast_node)
        merge_node.setInput(index, null_node)
        node_to_layout.extend([blast_node, null_node])

    node_to_layout.append(merge_node)
    parent_node.layoutChildren(items=node_to_layout)
    merge_node.setDisplayFlag(True)
    merge_node.setRenderFlag(True)

