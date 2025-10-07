import hou
import os

def export_node_as_code(filepath=None, recurse=True):
    sel = hou.selectedNodes()
    if not sel:
        hou.ui.displayMessage("Please select a node first.", severity=hou.severityType.Error)
        raise RuntimeError("No node provided.")

    node = sel[0]

    """Export a Houdini node (and its children) as Python code, with a clickable UI message."""
    # Default save path: $HIP/<nodename>_ascode.py
    if filepath is None:
        hip = hou.expandString("$HIP")
        filepath = os.path.join(hip, f"{node.name()}_ascode.py")

    # Generate the Python recreation code
    code = node.asCode(recurse=recurse)

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Auto-generated from Houdini node: {node.path()}\n\n")
        f.write(code)

    # Build message with clickable file path
    msg = f"Node code exported successfully.\n\nFile saved at:\n{filepath}"

    # Houdini UI message with clickable link
    hou.ui.displayMessage(
        text=msg,
        buttons=("Open File", "OK"),
        severity=hou.severityType.Message,
        details="Python code file generated via asCode().",
    )

    # If user clicks "Open File"
    choice = hou.ui.displayMessage(
        text=f"Node code saved:\n\n{filepath}",
        buttons=("Open File", "OK"),
        severity=hou.severityType.Message,
    )

    if choice == 0:  # "Open File"
        try:
            os.system(f'xdg-open "{filepath}"' if os.name != "nt" else f'start "" "{filepath}"')
        except Exception as e:
            hou.ui.displayMessage(f"Could not open file:\n{e}", severity=hou.severityType.Error)

    print(f"[done] Node code exported to: {filepath}")
    return filepath

    export_node_as_code()

