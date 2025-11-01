#!/usr/bin/env python
"""
Select All Nodes of Same Type

Selects all nodes in the current network that match the type of the first selected node.

Usage:
    1. Select a node (or multiple nodes - only first matters)
    2. Run this script
    3. All nodes of the same type in the same parent will be selected

Example:
    - Select a 'componentoutput' node
    - Run script
    - All 'componentoutput' nodes in that network will be selected
"""

import hou


def select_all_of_same_type(search_in_parent_only=True):
    """
    Select all nodes of the same type as the first selected node.

    Args:
        search_in_parent_only: If True, only search in the same parent network.
                               If False, search entire scene.

    Returns:
        tuple: (node_type_name, number_of_nodes_selected)
    """
    # Get current selection
    selected = hou.selectedNodes()

    if not selected:
        hou.ui.displayMessage(
            "No nodes selected!\n\nPlease select at least one node first.",
            severity=hou.severityType.Warning
        )
        return None, 0

    # Get the first selected node
    first_node = selected[0]
    node_type = first_node.type().name()
    category = first_node.type().category().name()
    parent = first_node.parent()

    # Find all nodes of the same type
    if search_in_parent_only and parent:
        # Search only in the same parent network
        all_nodes = parent.children()
        search_location = parent.path()
    else:
        # Search entire scene (all nodes in same category)
        all_nodes = hou.node("/").allSubChildren()
        search_location = "entire scene"

    # Filter to matching type and category
    matching_nodes = [
        node for node in all_nodes
        if node.type().name() == node_type and node.type().category().name() == category
    ]

    if not matching_nodes:
        hou.ui.displayMessage(
            f"No nodes of type '{node_type}' found in {search_location}!",
            severity=hou.severityType.Warning
        )
        return node_type, 0

    # Select all matching nodes
    for node in matching_nodes:
        node.setSelected(True)

    # Report results
    count = len(matching_nodes)
    message = (
        f"Selected {count} node{'s' if count != 1 else ''} "
        f"of type '{node_type}' ({category})\n\n"
        f"Search location: {search_location}"
    )

    print(message)

    # Optional: Display message to user
    if count > 50:
        hou.ui.displayMessage(
            f"Selected {count} nodes of type '{node_type}'",
            severity=hou.severityType.Message
        )

    return node_type, count


def select_all_of_same_type_globally():
    """Select all nodes of same type in entire scene."""
    return select_all_of_same_type(search_in_parent_only=False)


def select_all_of_same_type_in_parent():
    """Select all nodes of same type in current network only."""
    return select_all_of_same_type(search_in_parent_only=True)


# Quick run version (searches in parent only by default)
if __name__ == "__main__":
    select_all_of_same_type_in_parent()
