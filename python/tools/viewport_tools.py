import hou

def _scene_viewer():
    v = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if not v:
        raise RuntimeError("No Scene Viewer pane found.")
    return v

def _current_lopnode(viewer):
    """
    Return the active LOP node that produces a USD stage for the viewer.
    - If viewer.pwd() is a LOP node → use it.
    - If viewer.pwd() is /stage (a LopNetwork) → use its display LOP node.
    """
    node = viewer.pwd()
    if isinstance(node, hou.LopNode):
        return node

    # If we're sitting on /stage (a LopNetwork), pick the display LOP inside it
    if node and node.childTypeCategory() and node.childTypeCategory().name().lower() == "lop":
        dn = node.displayNode()
        if isinstance(dn, hou.LopNode):
            return dn

    raise RuntimeError("Active viewer is not in Solaris or no display LOP node is set.")

def _active_stage(viewer):
    lopnode = _current_lopnode(viewer)
    stage = lopnode.stage()
    if not stage:
        raise RuntimeError("No active USD stage on the display LOP node.")
    return stage

# unchanged: your camera prim finder
def _find_camera_prim(stage, prim_path):
    from pxr import Usd, UsdGeom, Sdf
    path = Sdf.Path(prim_path)
    prim = stage.GetPrimAtPath(path)
    if not prim or not prim.IsValid():
        return None
    if prim.GetTypeName() == "Camera" or UsdGeom.Camera(prim):
        return str(path)
    if prim.IsA(UsdGeom.Xform):
        it = Usd.PrimRange(prim, Usd.PrimAllPrimsPredicate)
        for p in it:
            if p == prim:
                continue
            if p.GetTypeName() == "Camera" or UsdGeom.Camera(p):
                return str(p.GetPath())
    return None

def set_stage_viewport_camera_from_switch(
        switch_parm_path="../switch2/input",
        cam_base="/turntable/lookdev/ldevCam"
):
    # Resolve switch param (callback-safe)
    parm = None
    try:
        import inspect
        cb_node = inspect.currentframe().f_back.f_locals.get("kwargs", {}).get("node")
        if cb_node:
            parm = cb_node.parm(switch_parm_path)
    except Exception:
        pass
    if parm is None:
        parm = hou.parm(switch_parm_path)
    if not parm:
        raise RuntimeError(f"Switch parameter not found: {switch_parm_path}")

    index = int(parm.eval())
    target_hint = f"{cam_base}{index}"

    viewer = _scene_viewer()
    stage = _active_stage(viewer)

    cam_prim_path = _find_camera_prim(stage, target_hint)
    if not cam_prim_path:
        raise RuntimeError(f"No USD Camera prim found at or under: {target_hint}")

    viewer.curViewport().setCamera(cam_prim_path)
    print(f"[viewport_tools] Stage camera set to: {cam_prim_path}")
