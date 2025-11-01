"""
Quick Merge Selected Nodes

One-line script to merge selected LOP nodes.

Usage in Houdini Python Shell or Shelf Tool:
    1. Select LOP nodes
    2. Run:
       execfile('/home/tushita/houdini21.0/custom_tools/scripts/python/merge_selected_quick.py')

Or as a shelf button:
    import sys
    sys.path.insert(0, '/home/tushita/houdini21.0/custom_tools/scripts/python')
    from tools.merge_selected_lops import merge_selected_nodes
    merge_selected_nodes()
"""

import sys
import hou

sys.path.insert(0, '/home/tushita/houdini21.0/custom_tools/scripts/python')

from tools.merge_selected_lops import merge_selected_nodes

# Run the merge
if __name__ == "__main__":
    merge_selected_nodes()
