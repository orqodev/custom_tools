"""
Import KB3D BGEO Files - Helper for loading BGEO with dynamic paths

This script helps import BGEO files using kb3d_asset attribute in the path.

Usage:
    From Houdini Python Shell or Python SOP

Author: Custom Tools
Date: 2025-10-28
"""

import hou
import os


def get_kb3d_asset_from_geo(geo):
    """
    Extract kb3d_asset attribute value from geometry.

    Args:
        geo: hou.Geometry object

    Returns:
        String value of kb3d_asset or None
    """
    # Try primitive attribute
    kb3d_attrib = geo.findPrimAttrib('kb3d_asset')
    if kb3d_attrib and geo.prims():
        return geo.prims()[0].attribValue('kb3d_asset')

    # Try point attribute
    kb3d_attrib = geo.findPointAttrib('kb3d_asset')
    if kb3d_attrib and geo.points():
        return geo.points()[0].attribValue('kb3d_asset')

    # Try detail attribute
    kb3d_attrib = geo.findGlobalAttrib('kb3d_asset')
    if kb3d_attrib:
        return geo.attribValue('kb3d_asset')

    return None


def load_bgeo_by_kb3d_asset(node, base_path_template, input_geo=None):
    """
    Load BGEO file using kb3d_asset from input geometry.

    Use this in a Python SOP node.

    Args:
        node: hou.Node (use hou.pwd())
        base_path_template: Path template with @kb3d_asset@ placeholder
            Example: "/path/to/geo/@kb3d_asset@.bgeo.sc"
        input_geo: Optional input geometry. If None, uses node.geometry()

    Returns:
        Loaded geometry
    """
    # Get input geometry
    if input_geo is None:
        if node.inputs():
            input_geo = node.inputs()[0].geometry()
        else:
            raise ValueError("No input geometry available")

    # Get kb3d_asset value
    kb3d_asset = get_kb3d_asset_from_geo(input_geo)

    if not kb3d_asset:
        raise ValueError("kb3d_asset attribute not found in input geometry")

    # Build file path
    file_path = base_path_template.replace('@kb3d_asset@', kb3d_asset)
    file_path = hou.text.expandString(file_path)

    # Check if file exists
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    # Load geometry
    output_geo = node.geometry()
    output_geo.clear()
    output_geo.loadFromFile(file_path)

    print(f"Loaded: {file_path}")
    return output_geo


def create_file_node_with_kb3d_path(parent, base_path_template, input_node=None):
    """
    Create a File SOP that loads BGEO using kb3d_asset from input.

    Args:
        parent: Parent node (e.g., hou.node('/obj/geo1'))
        base_path_template: Path template with @kb3d_asset@
        input_node: Optional input node to connect

    Returns:
        Created file node
    """
    # Create Python SOP to extract kb3d_asset and store as detail attrib
    python_sop = parent.createNode('python', 'extract_kb3d_asset')

    python_code = """
import hou

node = hou.pwd()
geo = node.geometry()

# Get input geometry
if node.inputs():
    input_geo = node.inputs()[0].geometry()

    # Get kb3d_asset from input
    kb3d_asset = None

    # Try prim attribute
    kb3d_attrib = input_geo.findPrimAttrib('kb3d_asset')
    if kb3d_attrib and input_geo.prims():
        kb3d_asset = input_geo.prims()[0].attribValue('kb3d_asset')

    # Try point attribute
    if not kb3d_asset:
        kb3d_attrib = input_geo.findPointAttrib('kb3d_asset')
        if kb3d_attrib and input_geo.points():
            kb3d_asset = input_geo.points()[0].attribValue('kb3d_asset')

    # Try detail attribute
    if not kb3d_asset:
        kb3d_attrib = input_geo.findGlobalAttrib('kb3d_asset')
        if kb3d_attrib:
            kb3d_asset = input_geo.attribValue('kb3d_asset')

    if kb3d_asset:
        # Store as detail attribute
        geo.addAttrib(hou.attribType.Global, 'kb3d_asset_path', '')
        geo.setGlobalAttribValue('kb3d_asset_path', kb3d_asset)
"""

    python_sop.parm('python').set(python_code)

    if input_node:
        python_sop.setInput(0, input_node)

    # Create File SOP
    file_node = parent.createNode('file', 'load_kb3d_bgeo')
    file_node.setInput(0, python_sop)

    # Set file path using detail attribute
    file_path_expr = base_path_template.replace('@kb3d_asset@', '`detail(-1, "kb3d_asset_path", "")`')
    file_node.parm('file').set(file_path_expr)

    return file_node


# For use directly in Python SOP
def python_sop_code():
    """
    Copy this code into a Python SOP node.
    """
    code = """
import hou
import os

node = hou.pwd()
geo = node.geometry()

# Base path template
base_path = "/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/kb3d_missiontominerva.fbxobj.native/geo/@kb3d_asset@.bgeo.sc"

# Get input geometry
if node.inputs():
    input_geo = node.inputs()[0].geometry()

    # Extract kb3d_asset
    kb3d_asset = None

    # Try prim attribute
    kb3d_attrib = input_geo.findPrimAttrib('kb3d_asset')
    if kb3d_attrib and input_geo.prims():
        kb3d_asset = input_geo.prims()[0].attribValue('kb3d_asset')

    if not kb3d_asset:
        # Try point attribute
        kb3d_attrib = input_geo.findPointAttrib('kb3d_asset')
        if kb3d_attrib and input_geo.points():
            kb3d_asset = input_geo.points()[0].attribValue('kb3d_asset')

    if not kb3d_asset:
        # Try detail attribute
        kb3d_attrib = input_geo.findGlobalAttrib('kb3d_asset')
        if kb3d_attrib:
            kb3d_asset = input_geo.attribValue('kb3d_asset')

    if kb3d_asset:
        # Build file path
        file_path = base_path.replace('@kb3d_asset@', kb3d_asset)

        # Load BGEO
        if os.path.exists(file_path):
            geo.loadFromFile(file_path)
            print(f"Loaded: {file_path}")
        else:
            raise ValueError(f"File not found: {file_path}")
    else:
        raise ValueError("kb3d_asset attribute not found")
"""
    return code


# Print usage instructions
if __name__ == '__main__':
    print("="*60)
    print("KB3D BGEO Import Helper")
    print("="*60)
    print("\nMethod 1: Python SOP")
    print("  1. Create a Python SOP node")
    print("  2. Copy this code into it:")
    print()
    print(python_sop_code())
    print()
    print("\nMethod 2: File SOP with Expression")
    print("  1. Create Attribute Wrangle before File SOP")
    print("  2. Add this code:")
    print("     s@kb3d_path = s@kb3d_asset;")
    print("  3. In File SOP, set path to:")
    print("     /path/to/geo/`detail(-1, 'kb3d_path', '')`.bgeo.sc")
    print("="*60)
