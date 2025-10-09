import hou

def build_transform_camera_and_scene_node(
        parent_path="/stage",
        node_name="transform_camera_and_scene",
        primpattern="/turntable/lookdev",
        replace_existing=False
):
    parent = hou.node(parent_path)
    if not parent:
        raise RuntimeError(f"Parent not found: {parent_path}")

    node = parent.node(node_name)
    if node and replace_existing:
        node.destroy()
        node = None
    if not node:
        node = parent.createNode("xform", node_name)

    node.setExpressionLanguage(hou.exprLanguage.Hscript)

    def _set(pn, val):
        p = node.parm(pn)
        if p: p.set(val)

    def _expr(pn, expr):
        p = node.parm(pn)
        if p:
            p.deleteAllKeyframes()
            p.setExpression(expr, hou.exprLanguage.Hscript)

    # Target prims (xform uses 'primpattern'; fall back to 'primpath' if needed)
    if node.parm("primpattern"):
        _set("primpattern", primpattern)
    elif node.parm("primpath"):
        _set("primpath", primpattern)

    # Simple world-space transform
    _set("xforminworldspace", 1)
    _set("xOrd", "srt")
    _set("rOrd", "xyz")
    if node.parm("xformdescription"):
        _set("xformdescription", "$OS")

    # Zero T/S, clear shear/scale extras (nice clean slate)
    if node.parmTuple("t"): node.parmTuple("t").set((0,0,0))
    if node.parmTuple("s"): node.parmTuple("s").set((1,1,1))
    if node.parmTuple("shear"): node.parmTuple("shear").set((0,0,0))
    if node.parm("scale"): _set("scale", 1)

    # Y rotation animation: 0→360 over $FSTART→$FEND (loop-friendly, linear)
    # This is super compact and easy to read/edit later.
    _expr("ry", 'fit($F, $FSTART, $FEND, 0, 360)')

    # Layout for tidiness
    try: parent.layoutChildren()
    except: pass

    return node

def build_lights_spin_xform(
        parent_path="/stage",
        node_name="animate_lights",
        primpattern="/turntable/lights",        # all lights on the stage
        use_frame_range=True,             # True: 0→360 over $FSTART→$FEND ; False: deg/sec
        deg_per_sec=90.0,                 # used when use_frame_range=False
        replace_existing=False
):
    parent = hou.node(parent_path)
    if not parent:
        raise RuntimeError(f"Parent not found: {parent_path}")

    node = parent.node(node_name)
    if node and replace_existing:
        node.destroy(); node = None
    if not node:
        node = parent.createNode("xform", node_name)

    node.setExpressionLanguage(hou.exprLanguage.Hscript)

    def _set(pn, val):
        p = node.parm(pn)
        if p: p.set(val)

    def _expr(pn, expr):
        p = node.parm(pn)
        if p:
            p.deleteAllKeyframes()
            p.setExpression(expr, hou.exprLanguage.Hscript)

    # target the lights
    if node.parm("primpattern"):
        _set("primpattern", primpattern)
    elif node.parm("primpath"):
        _set("primpath", primpattern)

    # clean transform & world-space
    _set("xforminworldspace", 1)
    _set("xOrd", "srt")
    _set("rOrd", "xyz")
    if node.parmTuple("t"): node.parmTuple("t").set((0,0,0))
    if node.parmTuple("s"): node.parmTuple("s").set((1,1,1))
    if node.parmTuple("shear"): node.parmTuple("shear").set((0,0,0))
    if node.parm("scale"): _set("scale", 1)

    # spin in Y
    if use_frame_range:
        # 0→360 across the current frame range
        _expr("ry", 'fit($F, $FSTART, $FEND, 0, 360)')
    else:
        # degrees-per-second speed (uses $T)
        # add a spare parm so you can tweak in the UI
        ptg = node.parmTemplateGroup()
        if ptg.find("deg_per_sec") is None:
            ptg.insertAfter(ptg.find("xformdescription") or ptg.parmTemplates()[0],
                            hou.FloatParmTemplate("deg_per_sec","Degrees Per Second",1,default_value=(deg_per_sec,)))
            node.setParmTemplateGroup(ptg)
            _set("deg_per_sec", deg_per_sec)
        _expr("ry", '($T * ch("deg_per_sec"))')

    try: parent.layoutChildren()
    except: pass

    return node
