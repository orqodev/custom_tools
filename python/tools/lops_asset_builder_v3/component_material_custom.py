import hou

def _set_expr(parm, expr, lang=hou.exprLanguage.Hscript):
    if parm is None: return
    parm.setExpression(expr, language=lang)

def _set(parm, value):
    if parm is None: return
    parm.set(value)

def _get_or_create(subnet, type_name, node_name):
    n = subnet.node(node_name)
    created = False
    if n is None:
        n = subnet.createNode(type_name, node_name)
        created = True
    return n, created

def build_component_material_custom(parent_path="/stage",
                                    node_name="component_material_custom",
                                    replace_existing=False):
    parent = hou.node(parent_path)
    if not parent:
        raise RuntimeError(f"Parent path not found: {parent_path}")

    # (Re)create subnet
    subnet = parent.node(node_name)
    if subnet and replace_existing:
        subnet.destroy()
        subnet = None
    if not subnet:
        subnet = parent.createNode("subnet", node_name)

    # Ensure 2 inputs visible on the subnet
    try:
        subnet.setUserData("mininputs", "2")
        subnet.setUserData("maxinputs", "4")
    except Exception:
        pass

    # ------------------------
    # Subnet spare parameters
    # ------------------------
    ptg = hou.ParmTemplateGroup()
    ptg.addParmTemplate(hou.StringParmTemplate("variantset",   "Variant Set", 1, default_value=("mtl",)))
    ptg.addParmTemplate(hou.StringParmTemplate("variantname",  "Variant Name Default", 1, default_value=("$OS",)))
    ptg.addParmTemplate(hou.SeparatorParmTemplate("sepparm"))

    primpattern = hou.StringParmTemplate("primpattern1", "Primitives", 1, default_value=("%type:Mesh",))
    primpattern.setTags({
        "script_action":"import loputils\nloputils.selectPrimsInParm(kwargs, True, allowinstanceproxies=True)",
        "script_action_help":"Select primitives in the Scene Viewer or Scene Graph Tree pane.",
        "script_action_icon":"BUTTONS_reselect",
        "sidefx::usdpathtype":"primlist"
    })
    ptg.addParmTemplate(primpattern)

    matspecvexpr = hou.StringParmTemplate("matspecvexpr1", "Vexpression", 1,
                                          default_value=('chs("asset_path")+"mtl/"+@primname;',))
    matspecvexpr.setTags({"editor":"1","editorlang":"vex","editorlines":"5-20"})
    ptg.addParmTemplate(matspecvexpr)

    ptg.addParmTemplate(hou.StringParmTemplate("bindpurpose1", "Purpose", 1, default_value=(["full"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l -a assign_material bindpurpose1", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Normal))
    ptg.addParmTemplate(hou.MenuParmTemplate("bindstrength1", "Strength", menu_items=(["fallback","strong","weak"]), menu_labels=(["Default","Stronger than Descendants","Weaker than Descendants"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False, is_button_strip=False, strip_uses_icons=False))
    subnet.setParmTemplateGroup(ptg)

    # --------------
    # Internal nodes (get-or-create; no second variant block)
    # --------------
    assign,   _ = _get_or_create(subnet, "assignmaterial",             "assign_material")
    ref2,     _ = _get_or_create(subnet, "reference::2.0",             "reference2")
    v_end1,   _ = _get_or_create(subnet, "addvariant",                 "variantblock_end1")
    v_begin1, _ = _get_or_create(subnet, "begincontextoptionsblock",   "variantblock_begin1")
    cfg,      _ = _get_or_create(subnet, "configurelayer",             "mtl_var01")
    setvar,   _ = _get_or_create(subnet, "setvariant",                 "setvariant1")
    out,  out_created = _get_or_create(subnet, "output",               "output0")

    # If output0 already existed, just select it (don’t recreate)
    if not out_created:
        out.setSelected(True, clear_all_selected=True)

    # -------------
    # Param values
    # -------------
    # reference2
    _set(ref2.parm("primpath"), "/ASSET/")
    _set(ref2.parm("refprimpath"), "/ASSET/")
    _set(ref2.parm("enable"), 1)
    _set(ref2.parm("input_group"), 1)
    _set(ref2.parm("createprims"), "on")
    _set(ref2.parm("reftype"), "file")
    _set(ref2.parm("instanceable"), 0)
    _set(ref2.parm("files_group"), 1)
    _set(ref2.parm("num_files"), 0)
    _set(ref2.parm("primkind"), "__automatic__")
    _set(ref2.parm("parentprimtype"), "UsdGeomXform")
    _set(ref2.parm("handlemissingfiles"), "error")
    _set(ref2.parm("preop"), "none")
    _set(ref2.parm("refeditop"), "prependfront")

    # assign_material
    ptg = assign.parmTemplateGroup()
    parm_template = hou.StringParmTemplate("asset_path","Asset Path", 1, default_value=('',))
    ptg.insertBefore("nummaterials", parm_template)
    assign.setParmTemplateGroup(ptg)
    _set_expr(assign.parm("asset_path"), 'chs("../reference2/primpath")')
    _set(assign.parm("nummaterials"), 1)
    _set(assign.parm("enable1"), 1)
    _set_expr(assign.parm("primpattern1"), 'chs("../primpattern1")')
    _set(assign.parm("ispathexpression1"), 0)
    _set(assign.parm("matspecmethod1"), "vexpr")
    _set_expr(assign.parm("matspecvexpr1"), 'chs("../matspecvexpr1")')
    _set(assign.parm("parmsovermethod1"), "none")
    _set(assign.parm("matparentpath1"), "/materials")
    _set(assign.parm("matparenttype1"), "UsdGeomScope")
    _set(assign.parm("cvexautobind1"), 1)
    _set(assign.parm("matbindingfolder1"), 1)
    _set(assign.parm("geosubset1"), 0)
    _set_expr(assign.parm("bindpurpose1"), 'chs("../bindpurpose1")')
    _set_expr(assign.parm("bindstrength1"), 'ch("../bindstrength1")')
    _set(assign.parm("bindmethod1"), "direct")
    _set_expr(assign.parm("asset_path"), 'chs("../reference2/primpath")')

    # variant loop (begin/end 1)
    _set(v_begin1.parm("layerbreak"), 1)

    _set(v_end1.parm("primpath"), "/ASSET")
    _set(v_end1.parm("sourceprim"), 0)
    _set_expr(v_end1.parm("sourceprimpath"), 'lopinputprim(".", 0)')
    _set(v_end1.parm("checkopinions"), 1)
    _set(v_end1.parm("parentprimtype"), "UsdGeomXform")
    _set(v_end1.parm("createoptionsblock"), 1)
    _set_expr(v_end1.parm("variantset"), 'chs("../variantset")')
    _set(v_end1.parm("variantsetstrength"), "prependfront")
    _set_expr(v_end1.parm("variantprimpath"), 'ifs(ch("sourceprim"), chs("sourceprimpath"), chs("primpath"))')
    _set_expr(v_end1.parm("variantname"), 'chs("../variantname")')
    _set(v_end1.parm("setvariantselection"), 1)

    # configure layer
    _set(cfg.parm("setsavepath"), 1)
    _set(cfg.parm("setinputlayerexplicit"), 1)
    _set(cfg.parm("setstagemetadata"), 1)
    _set(cfg.parm("savepath"), './data/`$HIPNAME`/mtl_`chs("../variantname")`.usd')

    # setvariant
    _set(setvar.parm("num_variants"), 1)
    _set(setvar.parm("enable1"), 1)
    _set_expr(setvar.parm("primpattern1"), 'lopinputprims(".", 0)')
    _set(setvar.parm("variantsetuseindex1"), 0)
    _set_expr(setvar.parm("variantset1"), 'chs("../variantblock_end1/variantset")')
    _set(setvar.parm("variantsetindex1"), 0)
    _set(setvar.parm("variantnameuseindex1"), 0)
    _set_expr(setvar.parm("variantname1"), 'chs("../variantblock_end1/variantname")')
    _set(setvar.parm("variantnameindex1"), 0)

    # output
    _set_expr(out.parm("outputidx"), 'max(opdigits("."),0)')
    _set_expr(out.parm("modifiedprims"), 'lopinputprims(".", 0)')

    # -------------
    # Connections
    # -------------
    # Internal graph
    ref2.setInput(0, v_begin1)   # 0 <- subnet input 0 (via v_begin1)
    ref2.setInput(1, cfg)        # 1 <- subnet input 1 (via cfg)
    assign.setInput(0, ref2)
    v_end1.setInput(1, assign)
    v_end1.setInput(2, v_begin1)
    setvar.setInput(0, v_end1)
    out.setInput(0, setvar)

    # External subnet inputs → internal nodes
    sub_inputs = subnet.indirectInputs()
    if len(sub_inputs) > 0:
        v_begin1.setInput(0, sub_inputs[0])   # subnet Input 0 → variantblock_begin1
        v_end1.setInput(0, sub_inputs[0])     # also feed Input 0 into end (your original pattern)
    if len(sub_inputs) > 1:
        cfg.setInput(0, sub_inputs[1])        # subnet Input 1 → configurelayer

    subnet.layoutChildren()

    # Defaults on subnet spare parms
    _set(subnet.parm("variantset"), "mtl")
    _set(subnet.parm("variantname"), "$OS")
    _set(subnet.parm("primpattern1"), "%type:Mesh")
    _set(subnet.parm("matspecvexpr1"), 'chs("asset_path")+"mtl/"+@primname;')
    _set(subnet.parm("bindpurpose1"), "full")
    _set(subnet.parm("bindstrength1"), "fallback")

    return subnet

