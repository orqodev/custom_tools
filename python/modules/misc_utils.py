import hou
import loputils

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