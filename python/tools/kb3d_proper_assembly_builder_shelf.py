"""
Shelf tool script for KB3D Proper Assembly Builder UI

Add this to a shelf button in Houdini:

Button Label: KB3D Assembly Builder
Button Icon: NETWORKS_lopnet
Button Script:
    from tools.kb3d_proper_assembly_builder_ui import show_ui
    show_ui()

Or paste this code directly:
"""

# For shelf button - paste this code:
SHELF_SCRIPT = """
from tools.kb3d_proper_assembly_builder_ui import show_ui
show_ui()
"""

# Alternative: Direct execution
if __name__ == "__main__":
    from tools.kb3d_proper_assembly_builder_ui import show_ui
    show_ui()
