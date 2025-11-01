"""
Simple script to select all nodes of the same type as first selection.

Usage - Copy one of these to Python Shell or Shelf Tool:

# Version 1: Search in current network only (recommended)
sel = hou.selectedNodes()
if sel:
    t = sel[0].type().name()
    [n.setSelected(True) for n in sel[0].parent().children() if n.type().name() == t]
    print(f"Selected all '{t}' nodes in current network")

# Version 2: Search entire scene (slower but finds all)
sel = hou.selectedNodes()
if sel:
    t = sel[0].type().name()
    c = sel[0].type().category().name()
    [n.setSelected(True) for n in hou.node("/").allSubChildren() if n.type().name() == t and n.type().category().name() == c]
    print(f"Selected all '{t}' nodes in scene")
"""

import hou

# Main function version
def select_same_type():
    """Select all nodes of same type as first selection (in current network)."""
    sel = hou.selectedNodes()
    if not sel:
        print("No nodes selected!")
        return

    node_type = sel[0].type().name()
    parent = sel[0].parent()

    matching = [n for n in parent.children() if n.type().name() == node_type]

    for node in matching:
        node.setSelected(True)

    print(f"Selected {len(matching)} nodes of type '{node_type}'")
    return len(matching)


# Run it
if __name__ == "__main__":
    select_same_type()
