import hou
import loputils
import re

def _is_in_solaris():
    ''' Checks if the current context is Stage'''
    # Get the current network editor pane
    network_editor = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)

    if network_editor.pwd().childTypeCategory().name() == "Lop":
        return True
    return False

def calculate_prim_bounds(target_node):
    '''Calculate the bounding box for a prim in solaris
    Args:
        target_node = The LOP node
    Return:
        dict : Contains the bounding box information - min, max, center, size and original bounding box
    '''

    # Get the stage
    stage = target_node.stage()

    if not stage:
        print("No USD stage found")
        return None

    # Get the target prim
    prim = stage.GetDefaultPrim()

    if not prim or not prim.IsValid():
        print(f"Invalid prim {prim}")
        return None

    # Calculate the bounding box
    bounds = loputils.computePrimWorldBounds(target_node,[prim])
    print(type(bounds))

    # Extract the bounding box information
    range3d = bounds.GetRange()
    min_point = hou.Vector3(range3d.GetMin())
    max_point = hou.Vector3(range3d.GetMax())

    center = (min_point + max_point) * 0.5
    size = max_point - min_point

    return {"min":min_point, "max":max_point, "center":center, "size":size, "bbox":bounds}

def safe_node_name(raw: str) -> str:
    """
    Replace illegal chars with underscores and make sure
    the name doesn't start with a digit.
    """
    # Keep only [A‑Z a‑z 0‑9 _]
    name = re.sub(r'[^A-Za-z0-9_]+', '_', str(raw))

    # Prepend underscore if the first char is a digit
    if name and name[0].isdigit():
        name = f"_{name}"

    return name


def _sanitize(text: str) -> str:
    """
    Replace every whitespace character (space, tab, newline, etc.)
    with a single underscore.  Collapses multiple spaces to one _.
    """
    # \W+ matches one or more non-word characters (opposite of [a-zA-Z0-9_])
    # Should use \s+ to match one or more whitespace characters instead
    return re.sub('\\s+', '_', text)


def sanitize_all_prim_string_attribs(geo: hou.Geometry):
    """
    Walk every primitive attribute that is of String type and sanitise values.
    """
    # Get all primitive attribs that store STRING data
    prim_str_attribs = [
        a for a in geo.primAttribs()
        if a.dataType() == hou.attribData.String
    ]

    if not prim_str_attribs:
        return  # nothing to do

    for prim in geo.prims():
        for attrib in prim_str_attribs:
            raw_val = prim.stringAttribValue(attrib.name())
            cleaned = _sanitize(raw_val)
            if cleaned != raw_val:
                prim.setAttribValue(attrib, cleaned)