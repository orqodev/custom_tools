import hou

### RBL KB3D Converter_v001

###SET DEFAULT VALUES, NO SPACES ALLOWED####
default_matlib_name = "Converted_Material_Library"
default_basecol_name = "basecolor"
default_metallic_name = "metallic"
default_roughness_name = "roughness"
default_normal_name = "normal"
default_displacement_name = "height"
default_emission_name = "emissive"
default_opacity_name = "opacity"
default_transmission_name = "refraction"


def run_kb3d_converter():
    """Entry point to run the KB3D converter from shelf tools.
    Wraps the original top-level script body so it can be called as a function.
    """
    #select nodes
    nodes = hou.selectedNodes()

    print("INITIALIZING KB3D CONVERTER")

    #check if arnold exists
    hpath = hou.houdiniPath()
    ar_exists = 0

    for x in hpath:
        if ("htoa" in x):
            ar_exists = 1
            print("HtoA Found")

    #setup arnold colorspace function
    def ar_colorspace_setup(input_var, cf_var, cs_var, input_num, output_num):
        color_family = input_var.path()+"/color_family"
        color_space = input_var.path()+"/color_space"
        single_channel = input_var.path()+"/single_channel"
        
        input_var.parm(color_family).set(cf_var)
        input_var.parm(color_space).set(cs_var)
        
        ar_surface.setNamedInput(input_num, ar_image, output_num)
        
        if len(output_num)==1:
            input_var.parm(single_channel).set(1)

    #setup Karma colorspace function
    def km_colorspace_setup(input_var, cs_var, input_num, output_num):
        signature = input_var.path()+"/signature"
        input_var.parm(signature).set(cs_var)
        
        km_surface.setNamedInput(input_num, km_image, output_num)
       
    #Error if nothing selected    
    if(len(nodes)==0):
        hou.ui.displayMessage("Please select nodes!")
        return
        
    #Error if parent node isn't matnet    
    topnode_path = nodes[0].parent().path()
    topnode = hou.node(topnode_path).type().name()

    if (("mat"==topnode) or ("materiallibrary" in topnode) or ("matnet"==topnode)):
        print("Parent is "+topnode)

    else:
        hou.ui.displayMessage("Selected material nodes must be directly in \na matnet, material library, or /mat context!", severity=hou.severityType.Error)
        return 
        
    #turn update mode to manual
    hou.ui.setUpdateMode(hou.updateMode.Manual)

    #create material library
    new_root = "/stage"
    mtl_lib = hou.node(new_root).createNode("materiallibrary", default_matlib_name)
    mtl_lib.parm("matpathprefix").set("/ASSET/mtl/")    

    #remap input texture names
    user_input_button, user_input_values = hou.ui.readMultiInput(
        "Set texture ID names. No Spaces Allowed!", ("Base Color:", "Metallic:", "Roughness:", "Normal:", "Displacement:", "Emission:", "Opacity:", "Refraction:"),
        initial_contents=(default_basecol_name, default_metallic_name, default_roughness_name, default_normal_name, default_displacement_name, default_emission_name, default_opacity_name, default_transmission_name),
        title="Remap Input",
        buttons=("OK", "Cancel"),
        default_choice=0, close_choice=1,
    )

    # If user cancels, do nothing
    if user_input_button == 1 or not user_input_values:
        hou.ui.setUpdateMode(hou.updateMode.AutoUpdate)
        return

    user_basecol_name = user_input_values[0]
    user_metallic_name = user_input_values[1]
    user_roughness_name = user_input_values[2]
    user_normal_name = user_input_values[3]
    user_displacement_name = user_input_values[4]
    user_emission_name = user_input_values[5]
    user_opacity_name = user_input_values[6]
    user_transmission_name = user_input_values[7]

    #define error'd materials
    error_mat = []

    #loop through each selected node
    for x in nodes:

        #set initial vars
        node = x
        path = x.path()
        root = path[:path.rfind("/")+1]
                
        pos = node.position()
        name = node.name()
        
        child = node.children()
        
        #create texture array
        textures = []
        
        #reset remap_found
        remap_found = 0
        for y in child:
            #if ("image" in y.name()):                
            if hou.nodeType(y.path()).name()=="mtlximage":
                tex_path = y.path()+"/file"
                file = hou.parm(tex_path).unexpandedString()
                textures.append(file)
                         
            if (hou.nodeType(y.path()).name()=="mtlxdisplacement"):
                disp_amount = y.parm("scale").eval()
                
            if (hou.nodeType(y.path()).name()=="mtlxremap"):
                remap_found = 1
                low_offset = y.parm("outlow").eval()
                high_offset = y.parm("outhigh").eval()    
                
        #set root to new material lib           
        if (len(textures)==0):
            error_mat.append(name)
            
        
        root=mtl_lib.path()
        
        print("Creating "+name)
        
    ###### ARNOLD SETUP #########
        if (ar_exists==1):

            #create arnold material builder
            ar = hou.node(root).createNode("arnold_materialbuilder", "arnold_"+name)
            ar.setPosition(hou.Vector2(pos[0]+4, pos[1]))
        
            ar_path = ar.path()+"/"
            ar_output = hou.node(ar.path()+"/OUT_material")
            
            #create standard surface
            ar_surface = hou.node(ar_path).createNode("standard_surface")
            ar_output.setInput(0, ar_surface, 0)
            
            for text in textures:
                #create image node
                ar_image = hou.node(ar_path).createNode("image")
                
        
                #set file path
                ar_fileparm = ar_image.path()+"/filename"
                ar_image.parm(ar_fileparm).set(text)
                
                
                #define initial inputs
                if (("_")+user_basecol_name) in text:
                    ar_colorspace_setup(ar_image, "Utility", "sRGB - Texture", "base_color", "rgba")
                    
                if (("_")+user_metallic_name) in text:
                    ar_colorspace_setup(ar_image, "ACES", "ACEScg", "metalness", "r")                  
        
                if (("_")+user_roughness_name) in text:
                    ar_colorspace_setup(ar_image, "ACES", "ACEScg", "specular_roughness", "r")
                    
                if (("_")+user_emission_name) in text:
                    ar_colorspace_setup(ar_image, "Utility", "sRGB - Texture", "emission_color", "r")
                    ar_surface.parm(ar_path+"standard_surface1/emission").set(1)
                    
                if (("_")+user_opacity_name) in text:
                    ar_colorspace_setup(ar_image, "Utility", "Raw", "opacity", "r")
                    
                if (("_")+user_transmission_name) in text:
                    ar_colorspace_setup(ar_image, "Utility", "Raw", "transmission", "r")
                
                #specialize for normal and for height    
                if (("_")+user_normal_name) in text:
                    ar_colorspace_setup(ar_image, "Utility", "Raw", "normal", "rgba") 
                    
                    #create normal node
                    ar_normal = hou.node(ar_path).createNode("normal_map")
                    
                    #connect inputs and position
                    ar_normal.setNamedInput("input", ar_image, "rgba")
                    ar_surface.setNamedInput("normal", ar_normal, "vector")
                    
                #specialize for height displacement
                if (("_")+user_displacement_name) in text:
                    ar_colorspace_setup(ar_image, "ACES", "ACEScg", "diffuse_roughness", "rgba")
                    
                    ar_surface.setInput(2, None)
                    ar_height = hou.node(ar_path).createNode("arnold::multiply", "displacement_amount")
                    
                    ar_height.parm("input2r").set(disp_amount)
                    ar_height.parm("input2g").set(disp_amount)
                    ar_height.parm("input2b").set(disp_amount)
                    
                    #if remapped
                    if (remap_found==1):
                        ar_height_offset = hou.node(ar_path).createNode("arnold::range", "displacement_remap")
                        ar_height_offset.parm("output_min").set(low_offset)
                        ar_height_offset.parm("output_max").set(high_offset)
                        
                        ar_height_offset.setNamedInput("input", ar_image, "rgba")
                        ar_height.setNamedInput("input1", ar_height_offset, "rgb")
                        ar_output.setNamedInput("displacement", ar_height, "rgb")
                        
                    else:
                        ar_height.setNamedInput("input1", ar_image, "rgba")
                        ar_output.setNamedInput("displacement", ar_height, "rgb")
                                                                                                
                #name image nodes
                nodename = text.split("/")
                node_name = nodename[-1].replace(".jpg", "")
                node_name = nodename[-1].replace(".png", "")
                ar_image.setName(node_name)
                
                print("Created Arnold "+node_name)
                
            #nicely layout arnold nodes
            ar.layoutChildren(horizontal_spacing = 2.0, vertical_spacing = 2.0)
            ar.setMaterialFlag(False)
        
    ######### END ARNOLD SETUP ####################

    ######### START KARMA SETUP ####################
        #create Karma material builder
        km = hou.node(root).createNode("subnet", "karma_"+name)
        km.setPosition(hou.Vector2(pos[0]+4, pos[1]-1.5))

        km_path = km.path()+"/"
        km_output = hou.node(km.path()+"/suboutput1")
        #hou.node(km.path()+"/subinput1").destroy()
        
    ######### START KARMA MTL BUILDER EXTRACT #############

        km.setDebugFlag(False)
        km.setDetailLowFlag(False)
        km.setDetailMediumFlag(False)
        km.setDetailHighFlag(True)
        km.bypass(False)
        km.setCompressFlag(True)
        km.hide(False)
        km.setSelected(True)
        
        hou_parm_template_group = hou.ParmTemplateGroup()
        # Code for parameter template
        hou_parm_template = hou.FolderParmTemplate("folder1", "Karma Material Builder", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
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
        hou_parm_template2.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        # Code for parameter template
        hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
        hou_parm_template.addParmTemplate(hou_parm_template2)
        # Code for parameter template
        hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["karma USD ^mtlxUsd* ^mtlxramp* ^hmtlxramp* ^hmtlxcubicramp* MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags({"spare_category": "Tab Menu"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        # Code for parameter template
        hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["kma"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        # Code for parameter template
        hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
        hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
        hou_parm_template.addParmTemplate(hou_parm_template2)
        hou_parm_template_group.append(hou_parm_template)
        km.setParmTemplateGroup(hou_parm_template_group)
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/folder1 parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("folder1")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set(0)
        hou_parm.setAutoscope(False)
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/inherit_ctrl parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("inherit_ctrl")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set(2)
        hou_parm.setAutoscope(False)
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/shader_referencetype parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("shader_referencetype")
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
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/shader_baseprimpath parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("shader_baseprimpath")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set("/__class_mtl__/`$OS`")
        hou_parm.setAutoscope(False)
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/tabmenumask parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("tabmenumask")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set("karma USD ^mtlxUsd* ^mtlxramp* ^hmtlxramp* ^hmtlxcubicramp* MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput")
        hou_parm.setAutoscope(False)
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/shader_rendercontextname parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("shader_rendercontextname")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set("kma")
        hou_parm.setAutoscope(False)
        
        
        # Code for /obj/KB3D_MTM/matnet/karmamaterial/shader_forcechildren parm 
        if locals().get("km") is None:
            km = hou.node("/obj/KB3D_MTM/matnet/karmamaterial")
        hou_parm = km.parm("shader_forcechildren")
        hou_parm.lock(False)
        hou_parm.deleteAllKeyframes()
        hou_parm.set(1)
        hou_parm.setAutoscope(False)
        
        
        km.setExpressionLanguage(hou.exprLanguage.Hscript)
        
        if hasattr(km, "syncNodeVersionIfNeeded"):
            km.syncNodeVersionIfNeeded("20.0.653")
    ####### END KARMA BUILDER EXTRACT#########            
        
        #create standard surface
        km_surface = hou.node(km_path).createNode("mtlxstandard_surface")
        
        km_output.setInput(0, km_surface, 0)
        
        for text in textures:
            #create image node
            km_image = hou.node(km_path).createNode("mtlximage")
            

            #set file path
            km_fileparm = km_image.path()+"/file"
            km_image.parm(km_fileparm).set(text)

            
            #define initial inputs
            if (("_")+user_basecol_name) in text:
                km_colorspace_setup(km_image, "color3", "base_color", "out")
                
            if (("_")+user_metallic_name) in text:
                km_colorspace_setup(km_image, "default", "metalness", "out")                  

            if (("_")+user_roughness_name) in text:
                km_colorspace_setup(km_image, "default", "specular_roughness", "out")
                
            if (("_")+user_emission_name) in text:
                km_colorspace_setup(km_image, "color3", "emission_color", "out")
                km_surface.parm(km_path+"mtlxstandard_surface1/emission").set(1)
                
            if (("_")+user_opacity_name) in text:
                km_colorspace_setup(km_image, "default", "opacity", "out")
                
            if (("_")+user_transmission_name) in text:
                km_colorspace_setup(km_image, "default", "transmission", "out")
            
            #specialize for normal and for height    
            if (("_")+user_normal_name) in text:
                km_colorspace_setup(km_image, "vector3", "normal", "out") 
                
                #create normal node
                km_normal = hou.node(km_path).createNode("mtlxnormalmap")
                
                #connect inputs and position
                km_normal.setNamedInput("in", km_image, "out")
                km_surface.setNamedInput("normal", km_normal, "out")
                
            #specialize for height displacement
            if (("_")+user_displacement_name) in text:
                km_colorspace_setup(km_image, "default", "diffuse_roughness", "out")
                
                #create displacement node and set scale
                km_surface.setInput(2, None)
                km_height = hou.node(km_path).createNode("mtlxdisplacement")
                km_height.parm("scale").set(disp_amount)
                
                if (remap_found==1):
                    #create offset node set range
                    km_height_offset = hou.node(km_path).createNode("mtlxremap")
                    km_height_offset.parm("outlow").set(low_offset)
                    km_height_offset.parm("outhigh").set(high_offset)
                    
                    #connect nodes
                    km_height_offset.setNamedInput("in", km_image, "out")
                    km_height.setNamedInput("displacement", km_height_offset, "out")
                    km_output.setInput(1, km_height, 0)
                    
                else:
                    km_height.setNamedInput("displacement", km_image, "out")
                    km_output.setInput(1, km_height, 0)
                    
                

            
            #name image nodes
            nodename = text.split("/")
            node_name = nodename[-1].replace(".jpg", "")
            node_name = nodename[-1].replace(".png", "")
            km_image.setName(node_name)
            
            print("Created Karma "+node_name)
            

        
        #create karma properties
        km_properties = hou.node(km_path).createNode("kma_material_properties")
        km_output.setInput(2, km_properties, 0)
        km_output.parm("name1").set("surface")        
        km_output.parm("name2").set("displacement")
        
        #nicely layout karma nodes
        km.layoutChildren(horizontal_spacing = 2.0, vertical_spacing = 2.0) 
        
    ######END KARMA SETUP#######

        
        #create collect node
        col = hou.node(root).createNode("collect", name)
        col.setPosition(hou.Vector2(pos[0]+8, pos[1]))
        if (ar_exists==1):
            col.setInput(0, ar, 0)
            col.setInput(1, km, 0)
        else:
            col.setInput(0, km, 0)
        
    #switch update mode to automatic
    hou.ui.setUpdateMode(hou.updateMode.AutoUpdate)

    #flag errors if nodes did not contain matx nodes
    if (len(error_mat)>0):
        error_mat_str = "\n".join(str(element) for element in error_mat)
        hou.ui.displayMessage("The node(s) below do not contain mtlx image nodes inside. \nThe following materials may be incorrect:\n\n"+error_mat_str, severity=hou.severityType.Warning)

    #layout materials
    mtl_lib.layoutChildren()
    mtl_lib.setCurrent(True, clear_all_selected=True)

