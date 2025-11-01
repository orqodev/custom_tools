"""
Merge Selected LOP Nodes

Creates a merge node that combines all currently selected LOP nodes.

Usage:
    1. Select multiple LOP nodes in the network editor
    2. Run this script:

       In Python Shell:
       import sys
       sys.path.insert(0, '/home/tushita/houdini21.0/custom_tools/scripts/python')
       from tools.merge_selected_lops import merge_selected_nodes
       merge_selected_nodes()

    3. A merge node will be created connecting all selected nodes

Features:
    - Automatically positions merge node below selected nodes
    - Creates output null for convenience
    - Works with any LOP nodes (componentoutput, subnets, etc.)
    - Sets display and render flags on output
"""

import hou
from typing import List, Tuple, Optional


def merge_selected_nodes(merge_name: str = "merge_selected",
                        output_name: str = "OUTPUT",
                        create_output_null: bool = True) -> Tuple[Optional[hou.Node], Optional[hou.Node]]:
    """
    Merge all currently selected LOP nodes.

    Args:
        merge_name: Name for the merge node
        output_name: Name for the output null node
        create_output_null: Whether to create an output null node

    Returns:
        Tuple of (merge_node, output_null) or (merge_node, None)
    """
    # Get selected nodes
    selected = hou.selectedNodes()

    if not selected:
        hou.ui.displayMessage(
            "No nodes selected!",
            title="Merge Selected Nodes",
            severity=hou.severityType.Warning
        )
        return None, None

    # Filter to only LOP nodes
    lop_nodes = [n for n in selected if n.type().category().name() == "Lop"]

    if not lop_nodes:
        hou.ui.displayMessage(
            "No LOP nodes selected!",
            title="Merge Selected Nodes",
            severity=hou.severityType.Warning
        )
        return None, None

    if len(lop_nodes) == 1:
        response = hou.ui.displayMessage(
            f"Only 1 LOP node selected: {lop_nodes[0].name()}\n\n"
            "A merge node needs at least 2 inputs.\n\n"
            "Continue anyway (creates merge with 1 input)?",
            title="Merge Selected Nodes",
            buttons=("Yes", "Cancel"),
            severity=hou.severityType.Warning
        )
        if response == 1:  # Cancel
            return None, None

    print("=" * 60)
    print(f"MERGE SELECTED NODES")
    print("=" * 60)
    print(f"Selected LOP nodes: {len(lop_nodes)}")

    # Get parent context (should be the same for all)
    parent = lop_nodes[0].parent()

    # Check all nodes have same parent
    if not all(n.parent() == parent for n in lop_nodes):
        hou.ui.displayMessage(
            "Selected nodes must be in the same network!",
            title="Merge Selected Nodes",
            severity=hou.severityType.Error
        )
        return None, None

    # Calculate position for merge node
    positions = [n.position() for n in lop_nodes]
    min_x = min(p[0] for p in positions)
    max_x = max(p[0] for p in positions)
    max_y = max(p[1] for p in positions)  # Highest Y (closest to top)

    avg_x = sum(p[0] for p in positions) / len(positions)
    merge_pos = (avg_x, max_y - 2.0)  # Below all selected nodes

    # Create merge node
    print(f"\nCreating merge node: {merge_name}")
    merge_node = parent.createNode("merge", merge_name)
    merge_node.setPosition(merge_pos)

    # Set number of inputs
    num_inputs = len(lop_nodes)
    merge_node.parm("numconnects").set(num_inputs)

    # Connect all selected nodes
    for i, node in enumerate(lop_nodes):
        merge_node.setInput(i, node)
        print(f"  [{i}] {node.name()} -> {merge_name}")

    # Set merge node color (green)
    merge_node.setColor(hou.Color((0.3, 0.6, 0.3)))

    # Create output null if requested
    output_null = None
    if create_output_null:
        output_null = parent.createNode("null", output_name)
        output_null.setPosition((merge_pos[0], merge_pos[1] - 1.5))
        output_null.setInput(0, merge_node)

        # Set output color (gold)
        output_null.setColor(hou.Color((1.0, 0.8, 0.0)))

        # Set flags
        output_null.setDisplayFlag(True)
        output_null.setRenderFlag(True)

        print(f"\nCreated output: {output_null.name()}")
        print(f"  Display flag: ON")
        print(f"  Render flag: ON")

    # Layout to clean up wires
    try:
        nodes_to_layout = lop_nodes + [merge_node]
        if output_null:
            nodes_to_layout.append(output_null)
        parent.layoutChildren(nodes_to_layout)
    except:
        pass

    print("\n" + "=" * 60)
    print("Merge complete!")
    print("=" * 60)
    print(f"Merge node: {merge_node.path()}")
    if output_null:
        print(f"Output node: {output_null.path()}")

    # Select the output or merge
    if output_null:
        output_null.setSelected(True, clear_all_selected=True)
    else:
        merge_node.setSelected(True, clear_all_selected=True)

    return merge_node, output_null


def merge_selected_interactive():
    """
    Interactive version with a simple dialog.
    """
    # Get selected nodes first
    selected = hou.selectedNodes()
    lop_nodes = [n for n in selected if n.type().category().name() == "Lop"]

    if not lop_nodes:
        hou.ui.displayMessage(
            "Please select at least 2 LOP nodes first!",
            title="Merge Selected Nodes",
            severity=hou.severityType.Warning
        )
        return

    # Show dialog with options
    result = hou.ui.readMultiInput(
        f"Merge {len(lop_nodes)} selected LOP nodes?",
        input_labels=("Merge node name:", "Output node name (optional):"),
        initial_contents=("merge_selected", "MERGE_OUTPUT"),
        buttons=("Create", "Cancel"),
        title="Merge Selected Nodes"
    )

    if result[0] == 1:  # Cancel
        return

    merge_name = result[1][0] if result[1][0] else "merge_selected"
    output_name = result[1][1] if result[1][1] else "MERGE_OUTPUT"
    create_output = bool(output_name.strip())

    # Create merge
    merge_selected_nodes(
        merge_name=merge_name,
        output_name=output_name,
        create_output_null=create_output
    )


# Convenience aliases
merge_selected = merge_selected_nodes
merge = merge_selected_nodes


if __name__ == "__main__":
    # Run interactive version when executed directly
    merge_selected_interactive()
