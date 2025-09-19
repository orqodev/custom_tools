import hou

def show_node_inputs():
    # Get selected nodes
    sel = hou.selectedNodes()
    if not sel:
        hou.ui.displayMessage("Please select a node first.")
        return

    node = sel[0]
    inputs = node.inputNames()

    msg_lines = [f"Node: {node.path()}"]
    msg_lines.append(f"Total inputs: {len(inputs)}")
    for i, name in enumerate(inputs):
        msg_lines.append(f"Input {i}: {name}")

    msg = "\n".join(msg_lines)

    # Print to shell and show popup
    print(msg)
    hou.ui.displayMessage(msg)

