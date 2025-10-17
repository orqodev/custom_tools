import hou

def create_subnet_lookdev_setup(node_name="lookdev_setup",parent_path="/stage"):
    # Initialize parent node variable.
    if locals().get("hou_parent") is None:
        hou_parent = hou.node(parent_path)

        # Code for /stage/lookdev_setup
    hou_node = hou_parent.createNode("subnet", node_name, run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-14.8262, 10.9669))
    hou_node.hide(False)
    hou_node.setSelected(True)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.LabelParmTemplate("lookdev_camera_settings", "Lookdev Camera Settings", column_labels=(["Lookdev Camera Settings"]))
    hou_parm_template.setTags({"sidefx::look": "heading"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("target", "Target Prim", 1, default_value=(["/turntable/asset"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("camera_path", "Camera Path", 1, default_value=(["/turntable/lookdev/__ThumbnailCamera__"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("use_existing_camera", "Use Existing Camera", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("existing_camera_path", "Existing Camera Path", 1, default_value=(["/turntable/lookdev/ldevCam0"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.setConditional(hou.parmCondType.DisableWhen, "{ use_existing_camera == 0 }")
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FloatParmTemplate("spin", "Spin Camera", 1, default_value=([0]), min=-180, max=180, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FloatParmTemplate("pitch", "Pitch Camera", 1, default_value=([14.4]), min=-90, max=90, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FloatParmTemplate("distance", "Distance", 1, default_value=([0]), min=-50, max=50, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.LabelParmTemplate("lookdev_animated_camera_settings", "LookDev Animated Camera Settings", column_labels=(["LookDev Animated Camera Settings"]))
    hou_parm_template.setTags({"sidefx::look": "heading"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("animate", "Animate", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.IntParmTemplate("frames", "Frames", 1, default_value=([60]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.setConditional(hou.parmCondType.DisableWhen, "{ animate == 0 }")
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.IntParmTemplate("start_frame", "Start Frame", 1, default_value=([4]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.setConditional(hou.parmCondType.DisableWhen, "{ animate == 0 }")
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.LabelParmTemplate("lookdev_refs", "LookDev Refs", column_labels=(["LookDev Refs"]))
    hou_parm_template.setTags({"sidefx::look": "heading"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("color_chart", "Color Chart", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"autoscope": "0000000000000000", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/target parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("target")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/asset")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/camera_path parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("camera_path")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/__ThumbnailCamera__")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/use_existing_camera parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("use_existing_camera")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/existing_camera_path parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("existing_camera_path")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/ldevCam0")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/spin parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("spin")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/pitch parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("pitch")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(-12.199999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/distance parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("distance")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/animate parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("animate")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/frames parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("frames")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(60)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/start_frame parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("start_frame")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(4)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}")
    hou_parm = hou_node.parm("color_chart")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    # Code to establish connections for /stage/lookdev_setup
    hou_node = hou_parent.node("lookdev_setup")
    if hou_parent.node("switch_env_lights") is not None:
        hou_node.setInput(0, hou_parent.node("switch_env_lights"), 0)
    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node

    # Code for /stage/lookdev_setup/output0
    hou_node = hou_parent.createNode("output", "output0", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.00241252, -6.87764))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/output0/outputidx parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/output0")
    hou_parm = hou_node.parm("outputidx")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/output0/modifiedprims parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/output0")
    hou_parm = hou_node.parm("modifiedprims")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`lopinputprims(\".\", 0)`")
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/assignmaterial1
    hou_node = hou_parent.createNode("assignmaterial", "assignmaterial1", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.00241252, -4.61864))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/assignmaterial1/nummaterials parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("nummaterials")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/enable1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("enable1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/primpattern1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("primpattern1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/ldevCam0/ref_grp/chrome_ball /turntable/lookdev/ldevCam0/ref_grp/color_chart /turntable/lookdev/ldevCam0/ref_grp/grey_ball")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/ispathexpression1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("ispathexpression1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matspecmethod1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matspecmethod1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("vexpr")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matspecpath1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matspecpath1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matspeccvex1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matspeccvex1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matspecvexpr1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matspecvexpr1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("\"/turntable/lookdev/mtl/\"+@primname")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/parmsovermethod1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("parmsovermethod1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/parmsovercvex1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("parmsovercvex1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/parmsovervexpr1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("parmsovervexpr1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/parmsoverexports1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("parmsoverexports1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("*")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matparentpath1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matparentpath1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/materials")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matparenttype1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matparenttype1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomScope")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/cvexbindingsfolder1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("cvexbindingsfolder1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/cvexautobind1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("cvexautobind1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/cvexbindings1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("cvexbindings1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/matbindingfolder1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("matbindingfolder1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/geosubset1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("geosubset1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindpurpose1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindpurpose1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindstrength1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindstrength1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("fallback")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindmethod1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindmethod1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("direct")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindcollectionexpand1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindcollectionexpand1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindpath1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindpath1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/assignmaterial1/bindname1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/assignmaterial1")
    hou_parm = hou_node.parm("bindname1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/lookdev_camera
    hou_node = hou_parent.createNode("pythonscript", "lookdev_camera", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.00241252, -5.74814))
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("python", "Python Code", 1, default_value=(["# Use the drop down menu to select example code snippets.\nnode = hou.pwd()\n\n# Add code to fetch node parameters and evaluate primitive patterns.\n# This should be done before calling editableStage or editableLayer.\n# paths = hou.LopSelectionRule(\"/*\").expandedPaths(node.input(0))\n\n# Add code to modify the stage.\nstage = node.editableStage()\n"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import pythonscriptmenu\n\nreturn pythonscriptmenu.buildSnippetMenu('Lop/pythonscript/python', kwargs=kwargs)", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    hou_parm_template.setTags({"editor": "1", "editorlang": "python", "editorlines": "20-50"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("maintainstate", "Maintain State", default_value=False)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("camera_folder", "LookDev Camera Settings", folder_type=hou.folderType.Simple, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "simple"})
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("target", "Target Prim", 1, default_value=(["/turntable/asset/"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("camera_path", "Camera Path", 1, default_value=(["/turntable/lookdev/ThumbnailCamera"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("use_existing_camera", "Use Existing Camera", default_value=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("existing_camera_path", "Existing Camera Path", 1, default_value=(["/cameras/camera_render"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ use_existing_camera == 0 }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("spin", "Spin Camera", 1, default_value=([0]), min=-180, max=180, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("pitch", "Pitch Camera", 1, default_value=([0]), min=-90, max=90, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("distance", "Distance", 1, default_value=([0]), min=-50, max=50, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("animated_cam_folder", "LookDev Animated Camera Settings", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
    # Code for parameter template
    hou_parm_template3 = hou.ToggleParmTemplate("animate", "Animate", default_value=False)
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.IntParmTemplate("frames", "Frames", 1, default_value=([60]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ animate == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.IntParmTemplate("start_frame", "Start Frame", 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ animate == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/lookdev_camera/python parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("python")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("\nfrom tools import lops_lookdev_camera\n\nimport importlib\n\nimportlib.reload(lops_lookdev_camera)\n\nlops_lookdev_camera.create_lookdev_camera(\"ASSET\")\n")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/lookdev_camera/maintainstate parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("maintainstate")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/lookdev_camera/camera_folder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("camera_folder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/lookdev_camera/target parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("target")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/asset")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../target\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../target\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../target\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../target\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/camera_path parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("camera_path")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/__ThumbnailCamera__")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/use_existing_camera parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("use_existing_camera")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../use_existing_camera\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../use_existing_camera\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../use_existing_camera\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../use_existing_camera\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/existing_camera_path parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("existing_camera_path")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/ldevCam0")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../existing_camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../existing_camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../existing_camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("chs(\"../existing_camera_path\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/spin parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("spin")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../spin\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../spin\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../spin\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../spin\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/pitch parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("pitch")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(-12.199999999999999)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(14.4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../pitch\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(14.4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../pitch\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(14.4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../pitch\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(14.4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../pitch\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/distance parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("distance")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../distance\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../distance\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../distance\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../distance\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/animated_cam_folder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("animated_cam_folder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/lookdev_camera/animate parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("animate")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../animate\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../animate\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../animate\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../animate\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/frames parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("frames")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(60)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(60)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../frames\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(60)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../frames\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(60)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../frames\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(60)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../frames\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/lookdev_camera/start_frame parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/lookdev_camera")
    hou_parm = hou_node.parm("start_frame")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(4)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../start_frame\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../start_frame\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../start_frame\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(4)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../start_frame\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "2")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/ldevCam0
    hou_node = hou_parent.createNode("camera", "ldevCam0", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.0291344, 2.01896))
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("sample_group3", "Frame Range/Subframes", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::header_parm": "sample_behavior"})
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("sample_behavior", "Sampling Behavior", 1, default_value=(["single"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["single","timedep","multi"]), menu_labels=(["Sample Current Frame","Sample Frame Range If Input Is Not Time Dependent","Sample Frame Range"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("sample_f", "Start/End/Inc", 3, default_value=([1, 240, 1]), default_expression=(["@fstart","@fend","@finc"]), default_expression_language=([hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ sample_behavior == single }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("sample_subframeenable", "Subframe Sampling", default_value=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("sample_subframegroup3", "Subframe Sampling", folder_type=hou.folderType.Simple, default_value=0, ends_tab_group=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ sample_subframeenable == 0 }")
    hou_parm_template2.setTags({"group_type": "simple", "sidefx::header_toggle": "sample_subframeenable"})
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("sample_shuttermode", "Shutter", 1, default_value=(["manual"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["cameraprim","manual"]), menu_labels=(["Use Camera Prim","Specify Manually"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ sample_subframeenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("sample_shutterrange", "Shutter Open/Close", 2, default_value=([-0.25, 0.25]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ sample_shuttermode == cameraprim } { sample_subframeenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("sample_cameraprim", "Camera Prim", 1, default_value=(["/cameras/camera1"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import expressionmenu\nreturn expressionmenu.buildExpressionsMenu(('Lop/primpath',))", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ sample_shuttermode == manual } { sample_subframeenable == 0 }")
    hou_parm_template3.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.IntParmTemplate("sample_count", "Samples", 1, default_value=([2]), min=2, max=10, min_is_strict=True, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ sample_subframeenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.ToggleParmTemplate("sample_includeframe", "Always Include Frame Sample", default_value=True)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ sample_subframeenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("primpattern", "Primitives", 1, default_value=(["`lopinputprims('.', 0)`"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createPrimPatternMenu(kwargs['node'], 0)", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringToggle)
    hou_parm_template.setConditional(hou.parmCondType.HideWhen, "{ createprims == on }")
    hou_parm_template.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, True)", "script_action_help": "Select primitives in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nShift-click to select using the primitive pattern editor.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "primlist"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("primpath", "Primitive Path", 1, default_value=(["/cameras/$OS"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createPrimPathMenu()", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    hou_parm_template.setConditional(hou.parmCondType.HideWhen, "{ createprims != on }")
    hou_parm_template.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.MenuParmTemplate("createprims", "Action", menu_items=(["off","on","forceedit"]), menu_labels=(["Edit","Create","Force Edit (Ignore Editable Flag)"]), default_value=1, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False, is_button_strip=False, strip_uses_icons=False)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.MenuParmTemplate("initforedit", "Initialize Parameters", menu_items=([]), menu_labels=([]), default_value=0, default_expression='donothing', default_expression_language=hou.scriptLanguage.Hscript, icon_names=([]), item_generator_script="import loputils\nreturn loputils.createInitializeParametersMenu(kwargs['node'].parm('createprims').eval(), 'Camera')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False, is_button_strip=False, strip_uses_icons=False)
    hou_parm_template.setScriptCallback("__import__('loputils').initializeParameters(kwargs['node'], kwargs['script_value'])")
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template.setTags({"script_callback": "__import__('loputils').initializeParameters(kwargs['node'], kwargs['script_value'])", "script_callback_language": "python"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.IntParmTemplate("primcount", "Primitive Count", 1, default_value=([1]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.hide(True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("primtype", "Primitive Type", 1, default_value=(["UsdGeomCamera"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createSchemaTypesMenu(True)", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.hide(True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("primkind", "Primitive Kind", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createKindsMenu(True, False)", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.hide(True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("specifier", "Primitive Specifier", 1, default_value=(["def"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createSpecifiersMenu()", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.hide(True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("classancestor", "Class Ancestor", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.setConditional(hou.parmCondType.DisableWhen, "{ specifier == class }")
    hou_parm_template.hide(True)
    hou_parm_template.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("parentprimtype", "Parent Primitive Type", 1, default_value=(["UsdGeomXform"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createParentTypesMenu()", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.hide(True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder2", "Transform", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__xformOptransform_control_6fb", "xformOp:transform", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'xform')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__xformOptransform_51a", "xformOp:transform", 1, default_value=(["append"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["append","prepend","overwriteorappend","overwriteorprepend","world","replace"]), menu_labels=(["Append","Prepend","Overwrite or Append","Overwrite or Prepend","Apply Transform in World Space","Replace All Local Transforms"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.setTags({"usdvaluetype": "xform"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.MenuParmTemplate("xOrd", "Transform Order", menu_items=(["srt","str","rst","rts","tsr","trs"]), menu_labels=(["Scale Rot Trans","Scale Trans Rot","Rot Scale Trans","Rot Trans Scale","Trans Scale Rot","Trans Rot Scale"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False, is_button_strip=False, strip_uses_icons=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.setJoinWithNext(True)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.MenuParmTemplate("rOrd", "Rotate Order", menu_items=(["xyz","xzy","yxz","yzx","zxy","zyx"]), menu_labels=(["Rx Ry Rz","Rx Rz Ry","Ry Rx Rz","Ry Rz Rx","Rz Rx Ry","Rz Ry Rx"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False, is_button_strip=False, strip_uses_icons=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.hideLabel(True)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("t", "Translate", 3, default_value=([0, 0, 0]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("r", "Rotate", 3, default_value=([0, 0, 0]), min=0, max=360, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("s", "Scale", 3, default_value=([1, 1, 1]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("shear", "Shear", 3, default_value=([0, 0, 0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("scale", "Uniform Scale", 1, default_value=([1]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("parmgroup_pivotxform2", "Pivot Transform", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.setTags({"group_type": "collapsible"})
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("p", "Pivot Translate", 3, default_value=([0, 0, 0]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("pr", "Pivot Rotate", 3, default_value=([0, 0, 0]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("folder3", "Constraints", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__xformOptransform_control_6fb == block } { xn__xformOptransform_control_6fb == none }")
    hou_parm_template2.setTags({"group_type": "collapsible"})
    # Code for parameter template
    hou_parm_template3 = hou.ToggleParmTemplate("lookatenable", "Enable Look At", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.ToggleParmTemplate("keepposition", "Keep Position", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template3.hide(True)
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("lookatposition", "Look At Position", 3, default_value=([0, 0, 0]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("lookatprim", "Look At Primitive", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template3.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template3.setTags({"editor": "0", "script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "script_callback": "", "script_callback_language": "python", "sidefx::usdpathtype": "prim"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("lookatprimpos", "Look At Primitive Position", 3, default_value=([0, 0, 0]), default_expression=(["import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[0]","import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[1]","import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[2]"]), default_expression_language=([hou.scriptLanguage.Python,hou.scriptLanguage.Python,hou.scriptLanguage.Python]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.hide(True)
    hou_parm_template3.setTags({"export_disable": "1"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("lookatprimrot", "Look At Primitive Rotation", 3, default_value=([0, 0, 0]), default_expression=(["import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[0]","import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[1]","import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[2]"]), default_expression_language=([hou.scriptLanguage.Python,hou.scriptLanguage.Python,hou.scriptLanguage.Python]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.hide(True)
    hou_parm_template3.setTags({"export_disable": "1"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("upvecmethod", "Up Vector Method", 1, default_value=(["yaxis"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["yaxis","xaxis","custom"]), menu_labels=(["Y Axis","X Axis","Custom"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("upvec", "Up Vector", 3, default_value=([0, 1, 0]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template3.setConditional(hou.parmCondType.HideWhen, "{ upvecmethod != custom }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("twist", "Twist", 1, default_value=([0]), min=-180, max=180, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ lookatenable == 0 }")
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder2_1", "View", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("projection_control", "Projection", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'token')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("projection", "Projection", 1, default_value=(["perspective"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["perspective","orthographic"]), menu_labels=(["Perspective","Orthographic"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ projection_control == block } { projection_control == none }")
    hou_parm_template2.setTags({"usdvaluetype": "token"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("clippingRange_control", "Clipping Range", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float2')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("clippingRange", "Clipping Range", 2, default_value=([1, 1e+06]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ clippingRange_control == block } { clippingRange_control == none }")
    hou_parm_template2.setTags({"usdvaluetype": "float2"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("focalLength_control", "Focal Length", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("focalLength", "Focal Length", 1, default_value=([50]), min=1, max=100, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ focalLength_control == block } { focalLength_control == none }")
    hou_parm_template2.setTags({"usdvaluename": ""})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("focalLengthConverted", "Focal Length (converted)", 1, default_value=([0]), default_expression=(["__import__('loputils').getConvertedCameraParmValue(pwd(), 'focalLength')"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.hide(True)
    hou_parm_template2.setTags({"usdcontrolparm": "focalLength_control", "usdvaluename": "focalLength", "usdvaluetype": "float"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("aperture_folder2", "Aperture", folder_type=hou.folderType.Simple, default_value=0, ends_tab_group=False)
    hou_parm_template2.setTags({"group_type": "simple"})
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("aperture", "Control Aperture", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nmenu = ['setratio', '![BUTTONS_set_or_create]Set Horizontal Aperture and Aspect Ratio']\nmenu.extend(loputils.createEditPropertiesControlMenu(kwargs, 'float'))\nreturn menu", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template3.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_parm_template3.setTags({"script_callback_language": "python", "sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("horizontalAperture_control", "Horizontal Aperture", 1, default_value=(["ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))"]), default_expression=(["ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))"]), default_expression_language=([hou.scriptLanguage.Hscript]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.hide(True)
    hou_parm_template3.hideLabel(True)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("horizontalAperture", "Horizontal Aperture", 1, default_value=([20.955]), min=1, max=100, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ horizontalAperture_control == block } { horizontalAperture_control == none }")
    hou_parm_template3.setHelp("Horizontal size of virtual camera sensor in millimeters.")
    hou_parm_template3.setTags({"usdcontrolparm": "horizontalAperture_control", "usdvaluename": ""})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("horizontalApertureConverted", "Horizontal Aperture (converted)", 1, default_value=([0]), default_expression=(["__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalAperture')"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.hide(True)
    hou_parm_template3.setTags({"usdcontrolparm": "horizontalAperture_control", "usdvaluename": "horizontalAperture", "usdvaluetype": "float"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("verticalAperture_control", "Vertical Aperture", 1, default_value=(["ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))"]), default_expression=(["ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))"]), default_expression_language=([hou.scriptLanguage.Hscript]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.hide(True)
    hou_parm_template3.hideLabel(True)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("verticalAperture", "Vertical Aperture", 1, default_value=([15.2908]), min=1, max=100, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ verticalAperture_control == block } { verticalAperture_control == none }")
    hou_parm_template3.setConditional(hou.parmCondType.HideWhen, "{ aperture == setratio }")
    hou_parm_template3.setHelp("Vertical size of virtual camera sensor in millimeters.")
    hou_parm_template3.setTags({"usdvaluename": ""})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("verticalApertureSwitch", "Vertical Aperture (switch)", 1, default_value=([0]), default_expression=(["if(!strcmp(chs(\"aperture\"), \"setratio\"), ch(\"horizontalAperture\") * ch(\"aspectratioy\") / ch(\"aspectratiox\"), ch(\"verticalAperture\"))"]), default_expression_language=([hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.hide(True)
    hou_parm_template3.setTags({"usdcontrolparm": "verticalAperture_control", "usdvaluename": ""})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("verticalApertureConverted", "Vertical Aperture (converted)", 1, default_value=([0]), default_expression=(["__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureSwitch')"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.hide(True)
    hou_parm_template3.setTags({"usdcontrolparm": "verticalAperture_control", "usdvaluename": "verticalAperture", "usdvaluetype": "float"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("aspectratio", "Aspect Ratio", 2, default_value=([16, 9]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
    hou_parm_template3.setConditional(hou.parmCondType.HideWhen, "{ aperture != setratio }")
    hou_parm_template3.setJoinWithNext(True)
    hou_parm_template3.setTags({"usdvaluename": ""})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.MenuParmTemplate("resMenu", "Choose Aspect Ratio", menu_items=([]), menu_labels=([]), default_value=0, icon_names=([]), item_generator_script="echo `pythonexprs(\"__import__('toolutils').parseDialogScriptMenu('FBaspectratios')\")`", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Mini, menu_use_token=False, is_button_strip=False, strip_uses_icons=False)
    hou_parm_template3.setConditional(hou.parmCondType.HideWhen, "{ aperture != setratio }")
    hou_parm_template3.setScriptCallback("opparm . aspectratio ( `arg(\"$script_value\", 0)` `arg(\"$script_value\", 1)` )")
    hou_parm_template3.setTags({"button_icon": "", "script_callback": "opparm . aspectratio ( `arg(\"$script_value\", 0)` `arg(\"$script_value\", 1)` )", "script_callback_language": "hscript"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FolderParmTemplate("aperture_offset_folder2", "Offsets", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template3.setTags({"group_type": "collapsible"})
    # Code for parameter template
    hou_parm_template4 = hou.StringParmTemplate("horizontalApertureOffset_control", "Horizontal Aperture Offset", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template4.setTags({"sidefx::look": "icon"})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    # Code for parameter template
    hou_parm_template4 = hou.FloatParmTemplate("horizontalApertureOffset", "Horizontal Aperture Offset", 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template4.setConditional(hou.parmCondType.DisableWhen, "{ horizontalApertureOffset_control == block } { horizontalApertureOffset_control == none }")
    hou_parm_template4.setTags({"usdvaluename": ""})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    # Code for parameter template
    hou_parm_template4 = hou.FloatParmTemplate("horizontalApertureOffsetConverted", "Horizontal Aperture Offset (converted)", 1, default_value=([0]), default_expression=(["__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalApertureOffset')"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template4.hide(True)
    hou_parm_template4.setTags({"usdcontrolparm": "horizontalApertureOffset_control", "usdvaluename": "horizontalApertureOffset", "usdvaluetype": "float"})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    # Code for parameter template
    hou_parm_template4 = hou.StringParmTemplate("verticalApertureOffset_control", "Vertical Aperture Offset", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template4.setTags({"sidefx::look": "icon"})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    # Code for parameter template
    hou_parm_template4 = hou.FloatParmTemplate("verticalApertureOffset", "Vertical Aperture Offset", 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template4.setConditional(hou.parmCondType.DisableWhen, "{ verticalApertureOffset_control == block } { verticalApertureOffset_control == none }")
    hou_parm_template4.setTags({"usdvaluename": ""})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    # Code for parameter template
    hou_parm_template4 = hou.FloatParmTemplate("verticalApertureOffsetConverted", "Vertical Aperture Offset (converted)", 1, default_value=([0]), default_expression=(["__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureOffset')"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template4.hide(True)
    hou_parm_template4.setTags({"usdcontrolparm": "verticalApertureOffset_control", "usdvaluename": "verticalApertureOffset", "usdvaluetype": "float"})
    hou_parm_template3.addParmTemplate(hou_parm_template4)
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FolderParmTemplate("viewport_folder2", "Viewport Control", folder_type=hou.folderType.Simple, default_value=0, ends_tab_group=False)
    hou_parm_template2.setTags({"group_type": "simple"})
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdiniguidescale_control_thb", "houdini:guidescale", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.FloatParmTemplate("xn__houdiniguidescale_s3a", "Scale Guide Geometry", 1, default_value=([0]), default_expression=(["1 / __import__('loputils').getMetersPerUnit(pwd())"]), default_expression_language=([hou.scriptLanguage.Python]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__houdiniguidescale_control_thb == block } { xn__houdiniguidescale_control_thb == none }")
    hou_parm_template3.setTags({"usdapischema": "HoudiniViewportGuideAPI", "usdvaluetype": "float"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdiniinviewermenu_control_2kb", "Show in Viewport Camera Menu", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'bool')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.ToggleParmTemplate("xn__houdiniinviewermenu_16a", "Show in Viewport Camera Menu", default_value=True)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__houdiniinviewermenu_control_2kb == block } { xn__houdiniinviewermenu_control_2kb == none }")
    hou_parm_template3.setTags({"usdapischema": "HoudiniViewportGuideAPI", "usdvaluetype": "bool"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdinibackgroundimage_control_ypb", "Background Image", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'bool')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdinibackgroundimage_xcb", "Background Image", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, file_type=hou.fileType.Image, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__houdinibackgroundimage_control_ypb == block } { xn__houdinibackgroundimage_control_ypb == none }")
    hou_parm_template3.setTags({"sidefx::allow_video": "1", "usdapischema": "HoudiniCameraPlateAPI", "usdvaluetype": "asset"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdiniforegroundimage_control_ypb", "Foreground Image", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'bool')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template3.setTags({"sidefx::look": "icon"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    # Code for parameter template
    hou_parm_template3 = hou.StringParmTemplate("xn__houdiniforegroundimage_xcb", "Foreground Image", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, file_type=hou.fileType.Image, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    hou_parm_template3.setConditional(hou.parmCondType.DisableWhen, "{ xn__houdiniforegroundimage_control_ypb == block } { xn__houdiniforegroundimage_control_ypb == none }")
    hou_parm_template3.setTags({"usdapischema": "HoudiniCameraPlateAPI", "usdvaluetype": "asset"})
    hou_parm_template2.addParmTemplate(hou_parm_template3)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder2_2", "Sampling", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__shutteropen_control_16a", "Shutter Open", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'double')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("xn__shutteropen_0ta", "Shutter Open", 1, default_value=([-0.25]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__shutteropen_control_16a == block } { xn__shutteropen_control_16a == none }")
    hou_parm_template2.setTags({"usdvaluetype": "double"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__shutterclose_control_o8a", "Shutter Close", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'double')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("xn__shutterclose_nva", "Shutter Close", 1, default_value=([0.25]), min=-1, max=1, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__shutterclose_control_o8a == block } { xn__shutterclose_control_o8a == none }")
    hou_parm_template2.setTags({"usdvaluetype": "double"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("focusDistance_control", "Focus Distance", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("focusDistance", "Focus Distance", 1, default_value=([5]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ focusDistance_control == block } { focusDistance_control == none }")
    hou_parm_template2.setTags({"usdvaluetype": "float"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("fStop_control", "F-Stop", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("fStop", "F-Stop", 1, default_value=([0]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ fStop_control == block } { fStop_control == none }")
    hou_parm_template2.setTags({"usdvaluetype": "float"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("exposure_control", "Exposure", 1, default_value=(["set"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("exposure", "Exposure", 1, default_value=([0]), min=-10, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ exposure_control == block } { exposure_control == none }")
    hou_parm_template2.setTags({"usdvaluetype": "float"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder2_3", "Karma", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacamerause_lensshader_control_subg", "Use Lens Shader", 1, default_value=(["none"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'bool')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("xn__karmacamerause_lensshader_rhbg", "Use Lens Shader", default_value=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacamerause_lensshader_control_subg == block } { xn__karmacamerause_lensshader_control_subg == none }")
    hou_parm_template2.setTags({"spare_category": "View", "uiscope": "None", "usdapischema": "KarmaCameraAPI", "usdvaluetype": "bool"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameramaterialbinding_control_fwbgi", "Lens Material", 1, default_value=(["none"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'relationship')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameramaterialbinding_ejbgi", "Lens Material", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacameramaterialbinding_control_fwbgi == block } { xn__karmacameramaterialbinding_control_fwbgi == none }")
    hou_parm_template2.setTags({"script_action": "\nimport loptoolutils\nloptoolutils.setupKarmaCameraLensMaterial(kwargs)\n", "script_action_help": "Create a lens shader LOP.", "script_action_icon": "VOP_kma_physicallens", "script_action_language": "python", "sidefx::usdpathtype": "prim", "spare_category": "View", "uiscope": "None", "usdapischema": "MaterialBindingAPI", "usdvaluename": "material:binding", "usdvaluetype": "relationship"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameralensshadervop_control_5sbg", "Lens Shader VOP", 1, default_value=(["none"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'string')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameralensshadervop_4fbg", "Lens Shader VOP", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacameralensshadervop_control_5sbg == block } { xn__karmacameralensshadervop_control_5sbg == none }")
    hou_parm_template2.setTags({"opfilter": "!!CUSTOM/MATERIAL!!", "oprelative": ".", "spare_category": "View", "uiscope": "None", "usdapischema": "KarmaCameraAPI", "usdvaluetype": "string"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameralensshader_89ag", "Lens Shader", 1, default_value=(["hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''"]), default_expression=(["hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''"]), default_expression_language=([hou.scriptLanguage.Python]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacameralensshader_control_9nbg == block } { xn__karmacameralensshader_control_9nbg == none }")
    hou_parm_template2.hide(True)
    hou_parm_template2.setTags({"spare_category": "View", "uiscope": "None", "usdapischema": "KarmaCameraAPI", "usdvaluetype": "string"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacamerawindow_control_rhbg", "Screen Window", 1, default_value=(["none"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float4')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("xn__karmacamerawindow_q3ag", "Screen Window", 4, default_value=([-1, 1, -1, 1]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacamerawindow_control_rhbg == block } { xn__karmacamerawindow_control_rhbg == none }")
    hou_parm_template2.setTags({"spare_category": "View", "uiscope": "None", "usdapischema": "KarmaCameraAPI", "usdvaluetype": "float4"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("xn__karmacameratint_control_iebg", "Tint", 1, default_value=(["none"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createEditPropertiesControlMenu(kwargs, 'float3')", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.ControlNextParameter)
    hou_parm_template2.setTags({"sidefx::look": "icon"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.FloatParmTemplate("xn__karmacameratint_h0ag", "Tint", 3, default_value=([1, 1, 1]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.ColorSquare, naming_scheme=hou.parmNamingScheme.RGBA)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ xn__karmacameratint_control_iebg == block } { xn__karmacameratint_control_iebg == none }")
    hou_parm_template2.setTags({"spare_category": "View", "uiscope": "None", "usdapischema": "KarmaCameraAPI", "usdvaluetype": "float3"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/ldevCam0/sample_group parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_group")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_behavior parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_behavior")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("single")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("sample_f")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 240, 1))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/sample_subframeenable parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_subframeenable")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_subframegroup parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_subframegroup")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_shuttermode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_shuttermode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("manual")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_shutterrange parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("sample_shutterrange")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-0.25, 0.25))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/ldevCam0/sample_cameraprim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_cameraprim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/cameras/camera1")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_count parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_count")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_includeframe parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_includeframe")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_group2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_group2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_subframegroup2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_subframegroup2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/primpattern parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("primpattern")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`lopinputprims('.', 0)`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/primpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("primpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/$OS")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/createprims parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("createprims")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("on")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/initforedit parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("initforedit")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("setdonothing")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/primcount parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("primcount")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/primtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("primtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomCamera")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/primkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("primkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/specifier parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("specifier")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("def")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/classancestor parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("classancestor")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/parentprimtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("parentprimtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomXform")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/folder11 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("folder11")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__xformOptransform_control_6fb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__xformOptransform_control_6fb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__xformOptransform_51a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__xformOptransform_51a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("append")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("srt")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/rOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("rOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("xyz")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/t parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("t")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-21.195911927649732, 5.4369067737199392, -7.2024401426095759))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/r parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("r")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-12.757650787986544, -98.721063950312754, 1.8241065744627468e-05))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/s parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("s")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/shear parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("shear")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/parmgroup_pivotxform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("parmgroup_pivotxform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/p parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("p")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/pr parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("pr")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/folder0 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("folder0")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/lookatenable parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("lookatenable")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/keepposition parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("keepposition")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/lookatposition parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("lookatposition")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/lookatprim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("lookatprim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/lookatprimpos parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("lookatprimpos")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractTranslates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/lookatprimrot parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("lookatprimrot")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[0]", hou.exprLanguage.Python)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[1]", hou.exprLanguage.Python)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("import loputils\nfrom pxr import Usd, UsdGeom\n\nlop_node = hou.node('.')\npath = lop_node.evalParm('lookatprim')\nif not path:\n    return 0\n\nstage = lop_node.stage()\nlook_at_prim = stage.GetPrimAtPath(path)\n\nif look_at_prim is None or not look_at_prim.IsA(UsdGeom.Imageable):\n    return 0\n\nxform = loputils.getPrimXform(lop_node, path)\n\nreturn xform.extractRotates()[2]", hou.exprLanguage.Python)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/upvecmethod parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("upvecmethod")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("yaxis")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/upvec parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("upvec")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 1, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/twist parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("twist")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/projection_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("projection_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/projection parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("projection")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("perspective")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/clippingRange_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("clippingRange_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/clippingRange parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("clippingRange")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1000000))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/ldevCam0/focalLength_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("focalLength_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/focalLength parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("focalLength")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(50)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/focalLengthConverted parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("focalLengthConverted")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.5)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'focalLength')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'focalLength')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'focalLength')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'focalLength')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/aperture_folder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("aperture_folder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/aperture parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("aperture")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("setratio")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalAperture_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalAperture_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalAperture parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalAperture")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(20.954999999999998)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalApertureConverted parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalApertureConverted")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.20954999999999999)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalAperture')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalAperture')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalAperture')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalAperture')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/verticalAperture_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalAperture_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("ifs(!strcmp(chs(\"aperture\"), \"setratio\"), \"set\", chs(\"aperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/verticalAperture parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalAperture")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(15.290800000000001)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/verticalApertureSwitch parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalApertureSwitch")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(11.787187499999998)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"aperture\"), \"setratio\"), ch(\"horizontalAperture\") * ch(\"aspectratioy\") / ch(\"aspectratiox\"), ch(\"verticalAperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"aperture\"), \"setratio\"), ch(\"horizontalAperture\") * ch(\"aspectratioy\") / ch(\"aspectratiox\"), ch(\"verticalAperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"aperture\"), \"setratio\"), ch(\"horizontalAperture\") * ch(\"aspectratioy\") / ch(\"aspectratiox\"), ch(\"verticalAperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"aperture\"), \"setratio\"), ch(\"horizontalAperture\") * ch(\"aspectratioy\") / ch(\"aspectratiox\"), ch(\"verticalAperture\"))", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/verticalApertureConverted parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalApertureConverted")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.11787187499999997)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureSwitch')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureSwitch')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureSwitch')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureSwitch')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/aspectratio parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("aspectratio")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((16, 9))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/ldevCam0/resMenu parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("resMenu")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("4 3")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/aperture_offset_folder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("aperture_offset_folder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalApertureOffset_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalApertureOffset_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalApertureOffset parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalApertureOffset")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/horizontalApertureOffsetConverted parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("horizontalApertureOffsetConverted")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'horizontalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/verticalApertureOffset_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalApertureOffset_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/verticalApertureOffset parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalApertureOffset")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/verticalApertureOffsetConverted parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("verticalApertureOffsetConverted")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("__import__('loputils').getConvertedCameraParmValue(pwd(), 'verticalApertureOffset')", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/viewport_folder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("viewport_folder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniguidescale_control_thb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniguidescale_control_thb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniguidescale_s3a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniguidescale_s3a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("1 / __import__('loputils').getMetersPerUnit(pwd())", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("1 / __import__('loputils').getMetersPerUnit(pwd())", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("1 / __import__('loputils').getMetersPerUnit(pwd())", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("1 / __import__('loputils').getMetersPerUnit(pwd())", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniinviewermenu_control_2kb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniinviewermenu_control_2kb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniinviewermenu_16a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniinviewermenu_16a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdinibackgroundimage_control_ypb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdinibackgroundimage_control_ypb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdinibackgroundimage_xcb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdinibackgroundimage_xcb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniforegroundimage_control_ypb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniforegroundimage_control_ypb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__houdiniforegroundimage_xcb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__houdiniforegroundimage_xcb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__shutteropen_control_16a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__shutteropen_control_16a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__shutteropen_0ta parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__shutteropen_0ta")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(-0.25)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__shutterclose_control_o8a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__shutterclose_control_o8a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__shutterclose_nva parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__shutterclose_nva")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.25)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/focusDistance_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("focusDistance_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/focusDistance parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("focusDistance")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(5095.7575243343272)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/fStop_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("fStop_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/fStop parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("fStop")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/exposure_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("exposure_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/exposure parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("exposure")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_group3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_group3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/sample_subframegroup3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("sample_subframegroup3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/folder21 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("folder21")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/parmgroup_pivotxform2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("parmgroup_pivotxform2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/folder3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("folder3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/aperture_folder2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("aperture_folder2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/aperture_offset_folder2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("aperture_offset_folder2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/viewport_folder2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("viewport_folder2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacamerause_lensshader_control_subg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacamerause_lensshader_control_subg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacamerause_lensshader_rhbg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacamerause_lensshader_rhbg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameramaterialbinding_control_fwbgi parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameramaterialbinding_control_fwbgi")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameramaterialbinding_ejbgi parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameramaterialbinding_ejbgi")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameralensshadervop_control_5sbg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameralensshadervop_control_5sbg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameralensshadervop_4fbg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameralensshadervop_4fbg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameralensshader_89ag parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameralensshader_89ag")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("hou.node(ch('xn__karmacameralensshadervop_4fbg')).shaderString() if hou.node(ch('xn__karmacameralensshadervop_4fbg')) != None else ''", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacamerawindow_control_rhbg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacamerawindow_control_rhbg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacamerawindow_q3ag parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("xn__karmacamerawindow_q3ag")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-1, 1, -1, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameratint_control_iebg parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm = hou_node.parm("xn__karmacameratint_control_iebg")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/ldevCam0/xn__karmacameratint_h0ag parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/ldevCam0")
    hou_parm_tuple = hou_node.parmTuple("xn__karmacameratint_h0ag")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("set_lookat", "True")
    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "2.1")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("2.1")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/grey_ball
    hou_node = hou_parent.createNode("sphere", "grey_ball", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.0291344, 0.889464))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/grey_ball/sample_group parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_group")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_behavior parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_behavior")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("single")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("sample_f")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 240, 1))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/grey_ball/sample_subframeenable parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_subframeenable")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_subframegroup parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_subframegroup")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_shuttermode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_shuttermode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("manual")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_shutterrange parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("sample_shutterrange")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-0.25, 0.25))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/grey_ball/sample_cameraprim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_cameraprim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/cameras/camera1")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_count parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_count")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/sample_includeframe parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("sample_includeframe")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/primpattern parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("primpattern")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`lopinputprims('.', 0)`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/primpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("primpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`chs(\"../ldevCam0/primpath\")`/ref_grp/$OS")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/createprims parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("createprims")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("on")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/initforedit parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("initforedit")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("setdonothing")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/createprimsgroup2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("createprimsgroup2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/primcount parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("primcount")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/primtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("primtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomSphere")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/primkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("primkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/specifier parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("specifier")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("def")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/classancestor parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("classancestor")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/parentprimtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("parentprimtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomXform")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/computeextents parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("computeextents")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/grey_ball/radius_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("radius_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/radius parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("radius")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.29999999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xn__primvarsdisplayColor_control_qmb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayColor_control_qmb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xn__primvarsdisplayColor_p8a parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("xn__primvarsdisplayColor_p8a")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/xn__primvarsdisplayOpacity_control_zpb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_control_zpb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xn__primvarsdisplayOpacity_ycb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_ycb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/doubleSided_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("doubleSided_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/doubleSided parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("doubleSided")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xn__xformOptransform_control_6fb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xn__xformOptransform_control_6fb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xn__xformOptransform_51a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xn__xformOptransform_51a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("append")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/xOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("xOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("srt")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/rOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("rOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("xyz")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/t parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("t")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-3.3100000000000001, -1.6899999999999999, -17.989999999999998))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/r parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("r")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/s parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("s")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/shear parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("shear")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/pivotxform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm = hou_node.parm("pivotxform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/grey_ball/p parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("p")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/grey_ball/pr parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/grey_ball")
    hou_parm_tuple = hou_node.parmTuple("pr")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "1.0")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("1.0")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/chrome_ball
    hou_node = hou_parent.createNode("sphere", "chrome_ball", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.0291344, -0.240036))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/chrome_ball/sample_group parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_group")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_behavior parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_behavior")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("single")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("sample_f")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 240, 1))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/chrome_ball/sample_subframeenable parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_subframeenable")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_subframegroup parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_subframegroup")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_shuttermode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_shuttermode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("manual")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_shutterrange parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("sample_shutterrange")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-0.25, 0.25))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/chrome_ball/sample_cameraprim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_cameraprim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/cameras/camera1")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_count parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_count")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/sample_includeframe parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("sample_includeframe")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/primpattern parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("primpattern")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`lopinputprims('.', 0)`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/primpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("primpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`chs(\"../ldevCam0/primpath\")`/ref_grp/$OS")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/createprims parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("createprims")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("on")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/initforedit parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("initforedit")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("setdonothing")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/createprimsgroup2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("createprimsgroup2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/primcount parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("primcount")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/primtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("primtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomSphere")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/primkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("primkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/specifier parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("specifier")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("def")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/classancestor parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("classancestor")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/parentprimtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("parentprimtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomXform")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/computeextents parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("computeextents")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"radius_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/chrome_ball/radius_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("radius_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/radius parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("radius")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.29999999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xn__primvarsdisplayColor_control_qmb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayColor_control_qmb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xn__primvarsdisplayColor_p8a parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("xn__primvarsdisplayColor_p8a")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/xn__primvarsdisplayOpacity_control_zpb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_control_zpb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xn__primvarsdisplayOpacity_ycb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_ycb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/doubleSided_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("doubleSided_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/doubleSided parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("doubleSided")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xn__xformOptransform_control_6fb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xn__xformOptransform_control_6fb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xn__xformOptransform_51a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xn__xformOptransform_51a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("append")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/xOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("xOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("srt")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/rOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("rOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("xyz")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/t parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("t")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-2.4900000000000002, -1.6899999999999999, -17.989999999999998))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/r parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("r")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/s parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("s")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/shear parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("shear")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/pivotxform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm = hou_node.parm("pivotxform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/chrome_ball/p parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("p")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/chrome_ball/pr parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/chrome_ball")
    hou_parm_tuple = hou_node.parmTuple("pr")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "1.0")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("1.0")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2
    hou_node = hou_parent.createNode("materiallibrary", "materiallibrary2", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.00241252, -3.48914))
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("genpreviewshaders", "Auto-generate Preview Surface Shaders", default_value=True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("allowparmanim", "Allow Shader Parameter Animation", default_value=False)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.ToggleParmTemplate("referencerendervars", "Reference Material Render Vars into Render Products", default_value=True)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("parentprimtype", "Parent Primitive Type", 1, default_value=(["UsdGeomScope"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createParentTypesMenu()", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.StringParmTemplate("matpathprefix", "Material Path Prefix", 1, default_value=(["/materials/"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("tabmenufolder", "Tab Menu", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible"})
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["*builder parameter constant rampparm collect null subnet subnetconnector suboutput subinput genericshader"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"spare_category": "Tab Menu"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.SeparatorParmTemplate("geometrygroup")
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("fillgroup2", "Fill", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::header_parm": "fillmaterials"})
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("matnet", "Material Network", 1, default_value=(["."]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"opfilter": "!!CUSTOM/MATERIAL!!", "oprelative": "."})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("containerpath", "Container Path", 1, default_value=(["/materials/"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ButtonParmTemplate("fillmaterials", "Auto-fill Materials")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("materials", "Number of Materials", folder_type=hou.folderType.MultiparmBlock, default_value=1, ends_tab_group=False)
    hou_parm_template.setTags({"multistartoffset": "1"})
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("enable#", "Enable", default_value=True)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("matflag#", "Include Only VOPs with Material Flag Set", default_value=False)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ enable# == 0 }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("matnode#", "Material VOP", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.NodeReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ enable# == 0 }")
    hou_parm_template2.setTags({"opfilter": "!!CUSTOM/MATERIAL!!", "oprelative": "."})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("matpath#", "Material Path", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ enable# == 0 }")
    hou_parm_template2.setTags({"script_action": "import loputils\nkwargs['ctrl'] = True\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "prim"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("assign#", "Assign to Geometry", default_value=True)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ enable# == 0 }")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("geopath#", "Geometry Path", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="import loputils\nreturn loputils.createPrimPatternMenu(kwargs['node'], 0)", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringToggle)
    hou_parm_template2.setConditional(hou.parmCondType.DisableWhen, "{ enable# == 0 } { assign# == 0 }")
    hou_parm_template2.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, True, allowinstanceproxies=True)", "script_action_help": "Select primitives in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.\nShift-click to select using the primitive pattern editor.\nAlt-click to toggle movement of the display flag.", "script_action_icon": "BUTTONS_reselect", "sidefx::usdpathtype": "primlist"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/materiallibrary2/genpreviewshaders parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("genpreviewshaders")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/allowparmanim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("allowparmanim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/referencerendervars parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("referencerendervars")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/parentprimtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("parentprimtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomScope")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/matpathprefix parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("matpathprefix")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/turntable/lookdev/mtl/")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/fillgroup parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("fillgroup")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/matnet parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("matnet")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(".")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/containerpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("containerpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/materials/")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/fillmaterials parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("fillmaterials")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("0")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/materials parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("materials")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/enable1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("enable1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/matflag1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("matflag1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/matnode1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("matnode1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("*")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/matpath1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("matpath1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/assign1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("assign1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/geopath1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("geopath1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/tabmenufolder parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("tabmenufolder")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/tabmenumask parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("tabmenumask")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("*builder parameter constant rampparm collect null subnet subnetconnector suboutput subinput genericshader")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/fillgroup2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2")
    hou_parm = hou_node.parm("fillgroup2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball
    hou_node = hou_parent.createNode("subnet", "chrome_ball", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-1.45251, 26.8882))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder1", "MaterialX Builder", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})
    # Code for parameter template
    hou_parm_template2 = hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=(["0","1","2"]), menu_labels=(["Never","Always","Material Flag"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression_language=([hou.scriptLanguage.Python]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["none","reference","inherit","specialize","represent"]), menu_labels=(["None","Reference","Inherit","Specialize","Represent"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1, default_value=(["/__class_mtl__/`$OS`"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"script_action": "import lopshaderutils\nlopshaderutils.selectPrimFromInputOrFile(kwargs)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"spare_category": "Tab Menu"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["mtlx"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/folder1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("folder1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/inherit_ctrl parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("inherit_ctrl")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/shader_referencetype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("shader_referencetype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/shader_baseprimpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("shader_baseprimpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/__class_mtl__/`$OS`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/tabmenumask parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("tabmenumask")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/shader_rendercontextname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("shader_rendercontextname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("mtlx")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/shader_forcechildren parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball")
    hou_parm = hou_node.parm("shader_forcechildren")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/inputs
    hou_node = hou_parent.createNode("subinput", "inputs", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-4.53993, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface
    hou_node = hou_parent.createNode("mtlxstandard_surface", "mtlxstandard_surface", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-0.2883, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/base parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("base")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/base_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("base_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0.80000000000000004, 0.80000000000000004, 0.80000000000000004))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/diffuse_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("diffuse_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/metalness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("metalness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("specular_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/specular_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_5 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_5")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.10000000000000001)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_affect_color parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_color")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/coat_affect_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_depth parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_depth")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_scatter parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_scatter")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_scatter_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_scatter_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_dispersion parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_dispersion")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/transmission_extra_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_extra_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_4 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_4")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/sheen parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/sheen_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("sheen_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/sheen_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.29999999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/subsurface parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/subsurface_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/subsurface_radius parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_radius")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/subsurface_scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/subsurface_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_7 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_7")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/emission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("emission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/emission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("emission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_6 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_6")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/thin_film_thickness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_thickness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/thin_film_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/folder0_8 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_8")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/opacity parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("opacity")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/thin_walled parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_walled")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxstandard_surface/tangent parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("tangent")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("__inputgroup_Subsurface", "collapsed")
    hou_node.setUserData("__inputgroup_Sheen", "collapsed")
    hou_node.setUserData("___toolcount___", "3")
    hou_node.setUserData("__inputgroup_Base", "collapsed")
    hou_node.setUserData("__inputgroup_Specular", "collapsed")
    hou_node.setUserData("__inputgroup_Geometry", "collapsed")
    hou_node.setUserData("__inputgroup_Emission", "collapsed")
    hou_node.setUserData("___Version___", "")
    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("__inputgroup_", "collapsed")
    hou_node.setUserData("__inputgroup_Thin Film", "collapsed")
    hou_node.setUserData("__inputgroup_Transmission", "collapsed")
    hou_node.setUserData("__inputgroup_Coat", "collapsed")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxdisplacement
    hou_node = hou_parent.createNode("mtlxdisplacement", "mtlxdisplacement", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-0.2883, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxdisplacement/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxdisplacement/displacement parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("displacement")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxdisplacement/displacement_vector3 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxdisplacement")
    hou_parm_tuple = hou_node.parmTuple("displacement_vector3")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/mtlxdisplacement/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output
    hou_node = hou_parent.createNode("subnetconnector", "surface_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(2.5236, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/surface_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.89, 0.69, 0.6]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output
    hou_node = hou_parent.createNode("subnetconnector", "displacement_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(2.5236, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/chrome_ball/displacement_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.6, 0.69, 0.89]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/chrome_ball/surface_output
    hou_node = hou_parent.node("surface_output")
    if hou_parent.node("mtlxstandard_surface") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxstandard_surface"), 0)
    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/chrome_ball/displacement_output
    hou_node = hou_parent.node("displacement_output")
    if hou_parent.node("mtlxdisplacement") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxdisplacement"), 0)

    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball
    hou_node = hou_parent.createNode("subnet", "grey_ball", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-1.45251, 25.2294))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder1", "MaterialX Builder", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})
    # Code for parameter template
    hou_parm_template2 = hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=(["0","1","2"]), menu_labels=(["Never","Always","Material Flag"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression_language=([hou.scriptLanguage.Python]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["none","reference","inherit","specialize","represent"]), menu_labels=(["None","Reference","Inherit","Specialize","Represent"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1, default_value=(["/__class_mtl__/`$OS`"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"script_action": "import lopshaderutils\nlopshaderutils.selectPrimFromInputOrFile(kwargs)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"spare_category": "Tab Menu"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["mtlx"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/folder1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("folder1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/inherit_ctrl parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("inherit_ctrl")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/shader_referencetype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("shader_referencetype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(True)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/shader_baseprimpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("shader_baseprimpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/__class_mtl__/`$OS`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/tabmenumask parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("tabmenumask")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/shader_rendercontextname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("shader_rendercontextname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("mtlx")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/shader_forcechildren parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball")
    hou_parm = hou_node.parm("shader_forcechildren")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/inputs
    hou_node = hou_parent.createNode("subinput", "inputs", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-4.53993, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface
    hou_node = hou_parent.createNode("mtlxstandard_surface", "mtlxstandard_surface", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-0.2883, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/base parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("base")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/base_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("base_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0.19, 0.19, 0.19))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/diffuse_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("diffuse_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/metalness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("metalness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("specular_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/specular_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_5 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_5")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.10000000000000001)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_affect_color parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_color")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/coat_affect_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_depth parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_depth")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_scatter parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_scatter")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_scatter_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_scatter_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_dispersion parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_dispersion")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/transmission_extra_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_extra_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_4 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_4")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/sheen parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/sheen_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("sheen_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/sheen_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.29999999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/subsurface parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/subsurface_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/subsurface_radius parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_radius")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/subsurface_scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/subsurface_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_7 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_7")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/emission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("emission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/emission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("emission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_6 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_6")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/thin_film_thickness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_thickness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/thin_film_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/folder0_8 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_8")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/opacity parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("opacity")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/thin_walled parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_walled")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxstandard_surface/tangent parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("tangent")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("__inputgroup_Subsurface", "collapsed")
    hou_node.setUserData("__inputgroup_Sheen", "collapsed")
    hou_node.setUserData("___toolcount___", "3")
    hou_node.setUserData("__inputgroup_Base", "collapsed")
    hou_node.setUserData("__inputgroup_Specular", "collapsed")
    hou_node.setUserData("__inputgroup_Geometry", "collapsed")
    hou_node.setUserData("__inputgroup_Emission", "collapsed")
    hou_node.setUserData("___Version___", "")
    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("__inputgroup_", "collapsed")
    hou_node.setUserData("__inputgroup_Thin Film", "collapsed")
    hou_node.setUserData("__inputgroup_Transmission", "collapsed")
    hou_node.setUserData("__inputgroup_Coat", "collapsed")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxdisplacement
    hou_node = hou_parent.createNode("mtlxdisplacement", "mtlxdisplacement", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-0.2883, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxdisplacement/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxdisplacement/displacement parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("displacement")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxdisplacement/displacement_vector3 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxdisplacement")
    hou_parm_tuple = hou_node.parmTuple("displacement_vector3")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/mtlxdisplacement/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/mtlxdisplacement")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output
    hou_node = hou_parent.createNode("subnetconnector", "surface_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(2.5236, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/surface_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.89, 0.69, 0.6]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output
    hou_node = hou_parent.createNode("subnetconnector", "displacement_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(2.5236, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/grey_ball/displacement_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.6, 0.69, 0.89]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___toolid___", "lops_asset_builder")
    hou_node.setUserData("___Version___", "21.0.440")
    hou_node.setUserData("___toolcount___", "3")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/grey_ball/surface_output
    hou_node = hou_parent.node("surface_output")
    if hou_parent.node("mtlxstandard_surface") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxstandard_surface"), 0)
    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/grey_ball/displacement_output
    hou_node = hou_parent.node("displacement_output")
    if hou_parent.node("mtlxdisplacement") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxdisplacement"), 0)

    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart
    hou_node = hou_parent.createNode("subnet", "color_chart", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-1.45251, 23.5505))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder1", "MaterialX Builder", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})
    # Code for parameter template
    hou_parm_template2 = hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=(["0","1","2"]), menu_labels=(["Never","Always","Material Flag"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r"]), default_expression_language=([hou.scriptLanguage.Python]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["none","reference","inherit","specialize","represent"]), menu_labels=(["None","Reference","Inherit","Specialize","Represent"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1, default_value=(["/__class_mtl__/`$OS`"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"script_action": "import lopshaderutils\nlopshaderutils.selectPrimFromInputOrFile(kwargs)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"spare_category": "Tab Menu"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["mtlx"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    hou_node.setParmTemplateGroup(hou_parm_template_group)
    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/folder1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("folder1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/inherit_ctrl parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("inherit_ctrl")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/shader_referencetype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("shader_referencetype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("inherit")
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.StringKeyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setExpression("n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm('inherit_ctrl')\nr = 'none'\nif i == 1 or (n_hasFlag and i == 2):\n    r = 'inherit'\nreturn r", hou.exprLanguage.Python)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/shader_baseprimpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("shader_baseprimpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/__class_mtl__/`$OS`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/tabmenumask parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("tabmenumask")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/shader_rendercontextname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("shader_rendercontextname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("mtlx")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/shader_forcechildren parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart")
    hou_parm = hou_node.parm("shader_forcechildren")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "21.0.440")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/inputs
    hou_node = hou_parent.createNode("subinput", "inputs", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-4.53993, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "21.0.440")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface
    hou_node = hou_parent.createNode("mtlxstandard_surface", "mtlxstandard_surface", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(8.917, 0.6466))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/base parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("base")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/base_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("base_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0.80000000000000004, 0.80000000000000004, 0.80000000000000004))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/diffuse_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("diffuse_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/metalness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("metalness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_1 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_1")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("specular_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.20000000000000001)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/specular_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("specular_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_5 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_5")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.10000000000000001)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_rotation parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_rotation")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("coat_normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_affect_color parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_color")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/coat_affect_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("coat_affect_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_depth parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_depth")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_scatter parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("transmission_scatter")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_scatter_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_scatter_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_dispersion parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_dispersion")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/transmission_extra_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("transmission_extra_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_4 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_4")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/sheen parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/sheen_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("sheen_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/sheen_roughness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("sheen_roughness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0.29999999999999999)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_3 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_3")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/subsurface parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/subsurface_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/subsurface_radius parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("subsurface_radius")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/subsurface_scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/subsurface_anisotropy parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("subsurface_anisotropy")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_7 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_7")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/emission parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("emission")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/emission_color parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("emission_color")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_6 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_6")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/thin_film_thickness parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_thickness")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/thin_film_IOR parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_film_IOR")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1.5)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/folder0_8 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("folder0_8")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/opacity parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("opacity")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/thin_walled parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm = hou_node.parm("thin_walled")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/normal parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("normal")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface/tangent parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxstandard_surface")
    hou_parm_tuple = hou_node.parmTuple("tangent")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("__inputgroup_Coat", "collapsed")
    hou_node.setUserData("__inputgroup_Subsurface", "collapsed")
    hou_node.setUserData("__inputgroup_Geometry", "collapsed")
    hou_node.setUserData("__inputgroup_Transmission", "collapsed")
    hou_node.setUserData("___Version___", "")
    hou_node.setUserData("__inputgroup_Sheen", "collapsed")
    hou_node.setUserData("__inputgroup_Emission", "collapsed")
    hou_node.setUserData("__inputgroup_Specular", "collapsed")
    hou_node.setUserData("__inputgroup_Base", "collapsed")
    hou_node.setUserData("__inputgroup_Thin Film", "collapsed")
    hou_node.setUserData("__inputgroup_", "collapsed")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxdisplacement
    hou_node = hou_parent.createNode("mtlxdisplacement", "mtlxdisplacement", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-0.2883, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxdisplacement/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxdisplacement")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("default")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxdisplacement/displacement parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxdisplacement")
    hou_parm = hou_node.parm("displacement")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxdisplacement/displacement_vector3 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxdisplacement")
    hou_parm_tuple = hou_node.parmTuple("displacement_vector3")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxdisplacement/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlxdisplacement")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output
    hou_node = hou_parent.createNode("subnetconnector", "surface_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(12.0348, 0.0376))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("surface")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/surface_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.89, 0.69, 0.6]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "21.0.440")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output
    hou_node = hou_parent.createNode("subnetconnector", "displacement_output", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(2.5236, -2.4334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/connectorkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("connectorkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("output")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmaccess parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmaccess")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmlabel parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmlabel")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("Displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("displacement")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmtypename parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmtypename")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/floatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("floatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/intdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("intdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/toggledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("toggledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/angledef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("angledef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/logfloatdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("logfloatdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/float2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float2def")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/float3def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float3def")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/vectordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("vectordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/normaldef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("normaldef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/pointdef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("pointdef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/directiondef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("directiondef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/float4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/floatm2def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("floatm2def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/float9def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float9def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 1, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/float16def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("float16def")
    hou_parm_tuple.lock((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    hou_parm_tuple.setAutoscope((False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/stringdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("stringdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/filedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("filedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/imagedef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("imagedef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/geometrydef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("geometrydef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/colordef parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("colordef")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/color4def parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm_tuple = hou_node.parmTuple("color4def")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/dictdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("dictdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/coshaderdef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("coshaderdef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/coshaderadef parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("coshaderadef")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/useasparmdefiner parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("useasparmdefiner")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output/parmuniform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/displacement_output")
    hou_parm = hou_node.parm("parmuniform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    hou_node.setColor(hou.Color([0.6, 0.69, 0.89]))
    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "21.0.440")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1
    hou_node = hou_parent.createNode("mtlximage", "mtlximage1", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(-3.083, -1.2334))
    hou_node.setDebugFlag(False)
    hou_node.setDetailLowFlag(False)
    hou_node.setDetailMediumFlag(False)
    hou_node.setDetailHighFlag(True)
    hou_node.bypass(False)
    hou_node.setCompressFlag(True)
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/signature parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("signature")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("color3")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/file parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("file")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("$HOUDINI_USER_PREF_DIR/custom_tools/misc/ACEScg_ColorChecker2005.exr")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/filecolorspace parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("filecolorspace")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/layer parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("layer")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("default")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default_color3 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("default_color3")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default_color4 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("default_color4")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default_vector2 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("default_vector2")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default_vector3 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("default_vector3")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/default_vector4 parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("default_vector4")
    hou_parm_tuple.lock((False, False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/texcoord parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm_tuple = hou_node.parmTuple("texcoord")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((90, 150))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/uaddressmode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("uaddressmode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("periodic")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/vaddressmode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("vaddressmode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("periodic")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/filtertype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("filtertype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("linear")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/framerange parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("framerange")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/frameoffset parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("frameoffset")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/materiallibrary2/color_chart/mtlximage1/frameendaction parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/materiallibrary2/color_chart/mtlximage1")
    hou_parm = hou_node.parm("frameendaction")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("constant")
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/color_chart/mtlxstandard_surface
    hou_node = hou_parent.node("mtlxstandard_surface")
    if hou_parent.node("mtlximage1") is not None:
        hou_node.setInput(1, hou_parent.node("mtlximage1"), 0)
    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/color_chart/surface_output
    hou_node = hou_parent.node("surface_output")
    if hou_parent.node("mtlxstandard_surface") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxstandard_surface"), 0)
    # Code to establish connections for /stage/lookdev_setup/materiallibrary2/color_chart/displacement_output
    hou_node = hou_parent.node("displacement_output")
    if hou_parent.node("mtlxdisplacement") is not None:
        hou_node.setInput(0, hou_parent.node("mtlxdisplacement"), 0)

    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/color_chart
    hou_node = hou_parent.createNode("cube", "color_chart", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.92401, -1.40486))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/color_chart/sample_group parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_group")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_behavior parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_behavior")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("single")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_f parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("sample_f")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 240, 1))
    hou_parm_tuple.setAutoscope((False, False, False))

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fstart", hou.exprLanguage.Hscript)
    hou_parm_tuple[0].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(240)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@fend", hou.exprLanguage.Hscript)
    hou_parm_tuple[1].setKeyframe(hou_keyframe)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("@finc", hou.exprLanguage.Hscript)
    hou_parm_tuple[2].setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/color_chart/sample_subframeenable parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_subframeenable")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_subframegroup parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_subframegroup")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_shuttermode parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_shuttermode")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("manual")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_shutterrange parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("sample_shutterrange")
    hou_parm_tuple.lock((False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((-0.25, 0.25))
    hou_parm_tuple.setAutoscope((False, False))


    # Code for /stage/lookdev_setup/color_chart/sample_cameraprim parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_cameraprim")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("/cameras/camera1")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_count parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_count")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(2)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/sample_includeframe parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("sample_includeframe")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/primpattern parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("primpattern")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`lopinputprims('.', 0)`")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/primpath parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("primpath")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`chs(\"../ldevCam0/primpath\")`/ref_grp/$OS")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/createprims parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("createprims")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("on")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/initforedit parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("initforedit")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("setdonothing")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/createprimsgroup2 parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("createprimsgroup2")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/primcount parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("primcount")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/primtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("primtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomCube")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/primkind parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("primkind")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/specifier parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("specifier")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("def")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/classancestor parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("classancestor")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/parentprimtype parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("parentprimtype")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("UsdGeomXform")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/computeextents parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("computeextents")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"size_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"size_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"size_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(0)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("if(!strcmp(chs(\"size_control\"), \"none\"), 0, 1)", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/color_chart/size_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("size_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/size parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("size")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xn__primvarsdisplayColor_control_qmb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xn__primvarsdisplayColor_control_qmb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xn__primvarsdisplayColor_p8a parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("xn__primvarsdisplayColor_p8a")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 1, 1))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/xn__primvarsdisplayOpacity_control_zpb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_control_zpb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("none")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xn__primvarsdisplayOpacity_ycb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xn__primvarsdisplayOpacity_ycb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/doubleSided_control parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("doubleSided_control")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/doubleSided parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("doubleSided")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xn__xformOptransform_control_6fb parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xn__xformOptransform_control_6fb")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("set")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xn__xformOptransform_51a parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xn__xformOptransform_51a")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("append")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/xOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("xOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("srt")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/rOrd parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("rOrd")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("xyz")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/t parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("t")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((3.1679039655687493, -1.5486793607945299, -17.989999999999998))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/r parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("r")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 180))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/s parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("s")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((1, 0.80000000000000004, 0.001))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/shear parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("shear")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/scale parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("scale")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/pivotxform parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm = hou_node.parm("pivotxform")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/color_chart/p parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("p")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    # Code for /stage/lookdev_setup/color_chart/pr parm tuple
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/color_chart")
    hou_parm_tuple = hou_node.parmTuple("pr")
    hou_parm_tuple.lock((False, False, False))
    hou_parm_tuple.deleteAllKeyframes()
    hou_parm_tuple.set((0, 0, 0))
    hou_parm_tuple.setAutoscope((False, False, False))


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    hou_node.setUserData("___Version___", "1.0")
    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("1.0")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code for /stage/lookdev_setup/switch1
    hou_node = hou_parent.createNode("switch", "switch1", run_init_scripts=False, load_contents=True, exact_type_name=True)
    hou_node.move(hou.Vector2(0.00241251, -2.46486))
    hou_node.hide(False)
    hou_node.setSelected(False)

    # Code for /stage/lookdev_setup/switch1/chooseinputbyname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("chooseinputbyname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("off")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/input parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("input")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(1)
    hou_parm.setAutoscope(False)

    # Code for first keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../color_chart\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for last keyframe.
    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../color_chart\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../color_chart\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)

    # Code for keyframe.
    hou_keyframe = hou.Keyframe()
    hou_keyframe.setTime(0)
    hou_keyframe.setValue(1)
    hou_keyframe.useValue(False)
    hou_keyframe.setSlope(0)
    hou_keyframe.useSlope(False)
    hou_keyframe.setAccel(0)
    hou_keyframe.useAccel(False)
    hou_keyframe.setExpression("ch(\"../color_chart\")", hou.exprLanguage.Hscript)
    hou_parm.setKeyframe(hou_keyframe)


    # Code for /stage/lookdev_setup/switch1/selectinputname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("selectinputname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/selectinputvalue parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("selectinputvalue")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/badinput parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("badinput")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("ignore")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/fallback parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("fallback")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set(0)
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/selectfallbackname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("selectfallbackname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("")
    hou_parm.setAutoscope(False)


    # Code for /stage/lookdev_setup/switch1/inputname parm
    if locals().get("hou_node") is None:
        hou_node = hou.node(f"/stage/{node_name}/switch1")
    hou_parm = hou_node.parm("inputname")
    hou_parm.lock(False)
    hou_parm.deleteAllKeyframes()
    hou_parm.set("`opinput(\".\", @input)`")
    hou_parm.setAutoscope(False)


    hou_node.setExpressionLanguage(hou.exprLanguage.Hscript)

    if hasattr(hou_node, "syncNodeVersionIfNeeded"):
        hou_node.syncNodeVersionIfNeeded("21.0.440")
    # Update the parent node.
    hou_parent = hou_node


    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    # Code to establish connections for /stage/lookdev_setup/output0
    hou_node = hou_parent.node("output0")
    if hou_parent.node("lookdev_camera") is not None:
        hou_node.setInput(0, hou_parent.node("lookdev_camera"), 0)
    # Code to establish connections for /stage/lookdev_setup/assignmaterial1
    hou_node = hou_parent.node("assignmaterial1")
    if hou_parent.node("materiallibrary2") is not None:
        hou_node.setInput(0, hou_parent.node("materiallibrary2"), 0)
    # Code to establish connections for /stage/lookdev_setup/lookdev_camera
    hou_node = hou_parent.node("lookdev_camera")
    if hou_parent.node("assignmaterial1") is not None:
        hou_node.setInput(0, hou_parent.node("assignmaterial1"), 0)
    # Code to establish connections for /stage/lookdev_setup/ldevCam0
    hou_node = hou_parent.node("ldevCam0")
    if len(hou_parent.indirectInputs()) > 0:
        hou_node.setInput(0, hou_parent.indirectInputs()[0])
    # Code to establish connections for /stage/lookdev_setup/grey_ball
    hou_node = hou_parent.node("grey_ball")
    if hou_parent.node("ldevCam0") is not None:
        hou_node.setInput(0, hou_parent.node("ldevCam0"), 0)
    # Code to establish connections for /stage/lookdev_setup/chrome_ball
    hou_node = hou_parent.node("chrome_ball")
    if hou_parent.node("grey_ball") is not None:
        hou_node.setInput(0, hou_parent.node("grey_ball"), 0)
    # Code to establish connections for /stage/lookdev_setup/materiallibrary2
    hou_node = hou_parent.node("materiallibrary2")
    if hou_parent.node("switch1") is not None:
        hou_node.setInput(0, hou_parent.node("switch1"), 0)
    # Code to establish connections for /stage/lookdev_setup/color_chart
    hou_node = hou_parent.node("color_chart")
    if hou_parent.node("chrome_ball") is not None:
        hou_node.setInput(0, hou_parent.node("chrome_ball"), 0)
    # Code to establish connections for /stage/lookdev_setup/switch1
    hou_node = hou_parent.node("switch1")
    if hou_parent.node("chrome_ball") is not None:
        hou_node.setInput(0, hou_parent.node("chrome_ball"), 0)
    if hou_parent.node("color_chart") is not None:
        hou_node.setInput(1, hou_parent.node("color_chart"), 0)

    # Restore the parent and current nodes.
    hou_parent = hou_parent.parent()
    hou_node = hou_node.parent()

    return hou_node


