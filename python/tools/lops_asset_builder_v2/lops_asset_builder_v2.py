import os

import hou
import voptoolutils

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
import colorsys
import random
from typing import List, Type
from pxr import Usd,UsdGeom


def create_component_builder(selected_directory=None):
    '''
    Main function to create the component builder based on a provided asset
    '''

    # Get File
    if selected_directory == None:
        selected_directory = hou.ui.selectFile(title="Select the file you want to import",
                                               file_type=hou.fileType.Geometry,
                                               multiple_select=True)
    selected_directory = hou.text.expandString(selected_directory)
    path, filename = os.path.split(selected_directory.split(";")[0])

    try:
        print("rock and roll")
        if os.path.exists(path):
            # Define context
            stage_context = hou.node("/stage")
            # Get the path and filename and the folder with the texturesRR
            node_name = _get_stage_node_name(filename)
            folder_textures = os.path.join(path, "maps").replace(os.sep, "/")
            comp_geo, material_lib, comp_material, comp_out = _create_inital_nodes(stage_context, node_name)
            # Nodes to layout
            nodes_to_layout = [comp_geo, material_lib, comp_material, comp_out]
            stage_context.layoutChildren(nodes_to_layout)

             # Prepare imported geo
            _prepare_imported_asset(comp_geo, selected_directory, path, comp_out, node_name)

            # Create the materials using the text_to_mtlx script
            _create_materials(comp_geo,folder_textures, material_lib, )

            # Sticky note creation
            create_organized_net_note(f"Asset {node_name.upper()}", nodes_to_layout,hou.Vector2(0, 5))
            # Select the Component Output
            comp_out.setSelected(True, clear_all_selected=True)


            # Create light rig
            light_rig_nodes_to_layout, merge_node = lops_light_rig.create_three_point_light()
            # Light Rig Nodes to layout
            create_organized_net_note("Light Rig", light_rig_nodes_to_layout, hou.Vector2(-1, 0))
            # Set Display Flag
            comp_out.setGenericFlag(hou.nodeFlag.Display, True)
            # Create Camera Node
            camera_render = stage_context.createNode('camera','camera_render')
            camera_render.setInput(0,merge_node)
            # Create Python Script
            camera_python_script = create_camera_lookdev(stage_context, node_name)
            # Connect script
            camera_python_script.setInput(0, camera_render)

            # Create Karma nodes
            karma_settings,usdrender_rop = create_karma_nodes(stage_context)
            karma_settings.setInput(0, camera_python_script)
            usdrender_rop.setInput(0, karma_settings)
            # Karma Nodes to layout
            karma_nodes = [camera_render,camera_python_script,karma_settings,usdrender_rop]
            stage_context.layoutChildren(items=karma_nodes)
            create_organized_net_note("Camera Render", karma_nodes, hou.Vector2(0, -6))

    except Exception as e:
        hou.ui.displayMessage(f"An error happened in create component builder: {str(e)}",
                              severity=hou.severityType.Error)

def _create_inital_nodes(stage_context, node_name: str = "asset_builder"):
    # Create nodes for the component builder setup
    comp_geo = stage_context.createNode("componentgeometry", f"{node_name}_geo")
    material_lib = stage_context.createNode("materiallibrary", f"{node_name}_mtl")
    comp_material = stage_context.createNode("componentmaterial", f"{node_name}_assign")
    comp_out = stage_context.createNode("componentoutput", node_name)

    comp_geo.parm("geovariantname").set(node_name)
    material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
    comp_material.parm("nummaterials").set(0)

    # Create auto assigment for materials
    comp_material_edit = comp_material.node("edit")
    output_node = comp_material_edit.node("output0")

    assign_material = comp_material_edit.createNode("assignmaterial", f"{node_name}_assign")
    # SET PARMS
    assign_material.setParms({
        "primpattern1": "%type:Mesh",
        "matspecmethod1": 2,
        "matspecvexpr1": '"/ASSET/mtl/"+@primname;',
        "bindpurpose1": "full",
    })

    # Connect nodes
    comp_material.setInput(0, comp_geo)
    comp_material.setInput(1, material_lib)
    comp_out.setInput(0, comp_material)

    # Connect the input of assign material node to the first subnet indirect input
    assign_material.setInput(0, comp_material_edit.indirectInputs()[0])
    output_node.setInput(0, assign_material)

    # Nodes to layout
    return comp_geo, material_lib, comp_material, comp_out


def _create_group_parameters(parent_node, node_name, asset_paths, switch_node, transform_node):
    """
    Create parameters for multi-asset switch workflow.
    Inspired by batch_import_workflow.py, this function adds UI controls
    for switching between assets and controlling transforms.

    Args:
        parent_node (hou.Node): The parent node to add parameters to
        node_name (str): Name of the asset group
        asset_paths (list): List of asset file paths
        switch_node (hou.Node): The switch node to control
        transform_node (hou.Node): The transform node to control
    """
    try:
        ptg = parent_node.parmTemplateGroup()

        # Add separator for multi-asset controls
        separator = hou.SeparatorParmTemplate(f"{node_name}_multi_sep", f"{node_name} Multi-Asset Controls")
        ptg.append(separator)

        # Add asset switch parameter
        num_assets = len(asset_paths) if asset_paths else 1
        switch_parm = hou.IntParmTemplate(
            f"{node_name}_asset_switch",
            f"Selected Asset Index",
            1,
            default_value=(0,),
            min=0,
            max=max(0, num_assets - 1),
            help=f"Switch between {num_assets} imported assets"
        )
        ptg.append(switch_parm)

        # Add transform controls folder
        transform_folder = hou.FolderParmTemplate(
            f"{node_name}_transform", 
            f"Asset Transform", 
            folder_type=hou.folderType.Tabs
        )

        # Translation vector parameter
        translate = hou.FloatParmTemplate(
            f"{node_name}_translate", 
            "Translate", 
            3, 
            default_value=(0, 0, 0)
        )

        # Rotation vector parameter  
        rotate = hou.FloatParmTemplate(
            f"{node_name}_rotate", 
            "Rotate", 
            3, 
            default_value=(0, 0, 0)
        )

        # Scale vector parameter
        scale = hou.FloatParmTemplate(
            f"{node_name}_scale", 
            "Scale", 
            3, 
            default_value=(1, 1, 1)
        )

        transform_folder.addParmTemplate(translate)
        transform_folder.addParmTemplate(rotate)
        transform_folder.addParmTemplate(scale)
        ptg.append(transform_folder)

        # Add asset information folder
        if asset_paths and len(asset_paths) > 1:
            info_folder = hou.FolderParmTemplate(
                f"{node_name}_assets_info", 
                f"Asset Files", 
                folder_type=hou.folderType.Tabs
            )

            for i, asset_path in enumerate(asset_paths):
                asset_info = hou.StringParmTemplate(
                    f"{node_name}_asset_file_{i}",
                    f"Asset {i+1}",
                    1,
                    default_value=(asset_path,),
                    string_type=hou.stringParmType.FileReference,
                    file_type=hou.fileType.Geometry,
                    help=f"Path to asset file {i+1}"
                )
                info_folder.addParmTemplate(asset_info)

            ptg.append(info_folder)

        # Apply parameters to parent node
        parent_node.setParmTemplateGroup(ptg)

        # Link nodes to parameters
        _link_group_nodes_to_parameters(parent_node, node_name, switch_node, transform_node)

    except Exception as e:
        hou.ui.displayMessage(f"Error creating group parameters: {str(e)}", 
                              severity=hou.severityType.Error)


def _link_group_nodes_to_parameters(parent_node, node_name, switch_node, transform_node):
    """
    Link switch and transform nodes to the UI parameters.

    Args:
        parent_node (hou.Node): The parent node with parameters (componentgeometry node)
        node_name (str): Name of the asset group
        switch_node (hou.Node): The switch node to control (inside sopnet/geo)
        transform_node (hou.Node): The transform node to control (inside sopnet/geo)
    """
    try:
        # Link switch node to parameter
        # Switch node is at: /stage/componentgeometry/sopnet/geo/switch_node
        # Parameters are at: /stage/componentgeometry/
        # So we need to go up 3 levels: ../../../
        if switch_node:
            switch_node.parm("input").setExpression(f'ch("../../../{node_name}_asset_switch")')

        # Link transform node using vector parameters
        # Transform node is at: /stage/componentgeometry/sopnet/geo/transform_node
        # Parameters are at: /stage/componentgeometry/
        # So we need to go up 3 levels: ../../../
        if transform_node:
            transform_mappings = [
                ("t", f"{node_name}_translate"),
                ("r", f"{node_name}_rotate"),
                ("s", f"{node_name}_scale")
            ]

            for xform_base, parent_param in transform_mappings:
                # Link each component
                xform_components = ["x", "y", "z"]
                for i, component in enumerate(xform_components):
                    xform_param = f"{xform_base}{component}"
                    parent_param_name = f"{parent_param}{component}"
                    transform_node.parm(xform_param).setExpression(f'ch("../../../{parent_param_name}")')

    except Exception as e:
        hou.ui.displayMessage(f"Error linking nodes to parameters: {str(e)}", 
                              severity=hou.severityType.Error)


def _prepare_imported_asset(parent, selected_directory, path, out_node, node_name):
    '''

    Creates the network layout for the default, proxy and sim outputs
    Args:
        parent = node where the file needs to be imported and prepared
        name = asset's name
        extension = if we are working with FBX, ABC, OBJ, etc
        path = path where the asset is located
    Return:
        None
    '''

    print("_prepare_imported_assets")

    try:
        # Set the parent node where the nodes are going to be created
        parent = hou.node(parent.path() + "/sopnet/geo")
        # Get the ouput nodes - default, proxy and sim,
        default_output = hou.node(f"{parent.path()}/default")
        proxy_output = hou.node(f"{parent.path()}/proxy")
        sim_output = hou.node(f"{parent.path()}/simproxy")

        # Create the file nodes that imports the assets
        filenames = selected_directory.split(";")
        file_nodes = []
        asset_paths = []
        switch_node = parent.createNode("switch", f"switch_{node_name}")

        for i, filename in enumerate(filenames):
            # Get asset name and extension
            file_path, filename = os.path.split(filename.strip())
            asset_name = filename.split(".")[0]
            extension = filename.split(".")[-1]
            if ".bgeo.sc" in filename:
                asset_name = filename.split(".")[0]
                extension = "bgeo.sc"

            # Store full path for parameters
            full_asset_path = f"{file_path}/{filename}"
            asset_paths.append(full_asset_path)

            file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
            if extension in file_extension:
                file_import = parent.createNode("file", f"import_{asset_name}")
                parm_name = "file"
            elif extension == "abc":
                file_import = parent.createNode("alembic", f"import_{asset_name}")
                parm_name = "filename"
            else:
                continue

            # Set Parms for main nodes
            file_import.parm(parm_name).set(full_asset_path)
            switch_node.setInput(i, file_import)
            file_nodes.append(file_import)

        # Create transform node for external control (like in batch_import_workflow)
        transform_node = parent.createNode("xform", f"transform_{node_name}")
        transform_node.setInput(0, switch_node)

        # Create the main nodes
        match_size = parent.createNode("matchsize", f"matchsize_{node_name}")
        attrib_wrangler = parent.createNode("attribwrangle", "convert_mat_to_name")
        attrib_delete = parent.createNode("attribdelete", "keep_P_N_UV_NAME")
        remove_points = parent.createNode("add", f"remove_points")

        match_size.setParms({
            "justify_x": 0,
            "justify_y": 1,
            "justify_z": 0,
        })

        attrib_wrangler.setParms({
            "class": 1,
            "snippet": 'string material_to_name[] = split(s@shop_materialpath,"/");\ns@name=material_to_name[-1];'
        })

        attrib_delete.setParms({
            "negate": True,
            "ptdel": "N P",
            "vtxdel": "uv",
            "primdel": "name"
        })

        remove_points.parm("remove").set(True)

        # Connect Main nodes - now using transform_node instead of switch_node directly
        match_size.setInput(0, transform_node)
        attrib_wrangler.setInput(0, match_size)
        attrib_delete.setInput(0, attrib_wrangler)
        remove_points.setInput(0, attrib_delete)
        default_output.setInput(0, remove_points)

        # Prepare Proxy Setup
        poly_reduce = parent.createNode("polyreduce::2.0", "reduce_to_5")
        attrib_colour = parent.createNode("attribwrangle", "set_color")
        color_node = parent.createNode("color", "unique_color")
        attrib_promote = parent.createNode("attribpromote", "promote_Cd")
        attrib_delete_name = parent.createNode("attribdelete", f"delete_asset_name")
        name_node = parent.createNode("name", "name")
        # Set parms for proxy setup
        poly_reduce.parm("percentage").set(5)

        # Custom attribute node using the ParmTemplateGroup() for the attrib_color
        attrib_colour.parm("class").set(1)

        ptg = attrib_colour.parmTemplateGroup()

        new_string = hou.StringParmTemplate(
            name="asset_name",
            label="Asset name",
            num_components= 1,
        )

        ptg.insertAfter("class", new_string)

        attrib_colour.setParmTemplateGroup(ptg)

        # Neeed to grab the rootprim from the component output and paste relative reference
        relative_path = attrib_colour.relativePathTo(out_node)
        expression_parm = f'`chs("{relative_path}/rootprim")`'
        attrib_colour.setParms({
            "asset_name": expression_parm,
            "snippet": 's@asset_name = chs("asset_name");',
        })

        color_node.setParms({
            "class": 1,
            "colortype": 4,
            "rampattribute": "asset_name",
        })

        attrib_promote.setParms({
            "inname": "Cd",
            "inclass": 1,
            "outclass": 0
        })
        attrib_delete_name.parm("primdel").set("asset_name")

        name_node.parm("name1").set(expression_parm)
        # Connect node
        poly_reduce.setInput(0, remove_points)
        attrib_colour.setInput(0, poly_reduce)
        color_node.setInput(0, attrib_colour)
        attrib_promote.setInput(0, color_node)
        attrib_delete_name.setInput(0, attrib_promote)
        proxy_output.setInput(0, attrib_delete_name)
        # # Prepare the sim Setup
        python_sop = _create_convex(parent)
        # Connect node
        python_sop.setInput(0, remove_points)
        name_node.setInput(0, python_sop)
        sim_output.setInput(0, name_node)

        parent.layoutChildren()

        # Create UI parameters for multi-asset switch workflow
        # This adds controls to the top-level componentgeometry node
        top_level_parent = out_node.parent()  # Get the stage context
        comp_geo_node = None

        # Find the componentgeometry node to add parameters to
        for node in top_level_parent.children():
            if node.type().name() == "componentgeometry" and node_name in node.name():
                comp_geo_node = node
                break

        if comp_geo_node and len(asset_paths) > 1:
            # Only create multi-asset parameters if we have multiple assets
            _create_group_parameters(comp_geo_node, node_name, asset_paths, switch_node, transform_node)

    except Exception as e:
        hou.ui.displayMessage(f"An error happened in prepare imported assets: {str(e)}",
                              severity=hou.severityType.Error)

def create_camera_lookdev(parent,asset_name):
    '''
    Create the python sop node that is used to create the camera lookdev.
    Args:
        parent = the component geometry node where the file is imported
    Return:
        python_sop = python_sop node created
    '''
    python_sop = parent.createNode("pythonscript", "lookdev_camera")
    code = f'''
from tools import lops_lookdev_camera

import importlib

importlib.reload(lops_lookdev_camera)

lops_lookdev_camera.create_lookdev_camera("{asset_name}")
'''
    # Prepare the Sim setup
    python_sop.parm("python").set(code)
    return python_sop

def create_karma_nodes(parent):
    '''
    Create Karma nodes and setup the default configuration
    Args:
        parent: Node parent to create the Karma nodes

    Returns:
        karma_nodes (list): list of nodes

    '''

    karma_settings = parent.createNode('karmarenderproperties', 'karmarendersettings')
    usdrender_rop = parent.createNode('usdrender_rop', 'usdrender_rop')
    karma_settings.parm('picture').set('$JOB/render/$HIPNAME.$OS.$F4.exr')
    usdrender_rop.parm('rendersettings').set('`chs("../karmarendersettings/primpath")`')
    return karma_settings, usdrender_rop

def _create_convex(parent):
    '''
    Creates the Python sop node that is used to create a convex hull using Scipy
    Args:
        parent = the component geometry node where the file is imported
    Return:
        python_sop = python_sop node created
    '''
    # Create the extra parms to use
    python_sop = parent.createNode("python", "convex_hull_setup")

    # Create the extra parms to use
    ptg = python_sop.parmTemplateGroup()

    # Normalize normals toggle
    normalize_toggle = hou.ToggleParmTemplate(
        name="normalize",
        label="Normalize",
        default_value=True
    )

    # Invert Normals Toggle
    flip_normals = hou.ToggleParmTemplate(
        name="flip_normals",
        label="Flip Normals",
        default_value=True
    )

    # Simplify Toogle
    simplify_toogle = hou.ToggleParmTemplate(
        name="simplify",
        label="Simplify",
        default_value=True
    )

    # Level of Detail Float
    level_detail = hou.FloatParmTemplate(
        name="level_detail",
        label="Level Detail",
        num_components=1,
        disable_when="{simplify == 0}",
        max=1
    )

    # Append to node
    ptg.append(normalize_toggle)
    ptg.append(flip_normals)
    ptg.append(simplify_toogle)
    ptg.append(level_detail)

    python_sop.setParmTemplateGroup(ptg)

    code = '''
from modules import convex_hull_utils

node = hou.pwd()
geo = node.geometry()

# Get user parms
normalize_parm = node.parm("normalize")
flip_normals_parm = node.parm("flip_normals")
simplify_parm = node.parm("simplify")
level_detail = node.parm("level_detail").eval()

# Get the points
points = [point.position() for point in geo.points()]

convex_hull_utils.create_convex_hull(geo, points, normalize_parm,flip_normals_parm, simplify_parm, level_detail)
'''
    # Prepare the Sim setup
    python_sop.parm("python").set(code)

    return python_sop

def _create_mtlx_templates(parent, material_lib):
    stage = parent.stage()
    prims_name = _find_prims_by_attribute(stage, UsdGeom.Mesh)
    for name in prims_name:
        voptoolutils._setupMtlXBuilderSubnet(
            subnet_node=None,
            destination_node=material_lib,
            name=name,
            mask=voptoolutils.MTLX_TAB_MASK,
            folder_label="MaterialX Builder",
            render_context="mtlx"
        )
    material_lib.layoutChildren()

def _create_materials(parent, folder_textures,material_lib):
    ''' Create the material using the tex_to_mtlx script
    Args:
        folder_textures: the folder where the textures are located
        material_lib: the material library where the materials will be saved
    Return:
         None
    '''
    try:
        if not os.path.exists(folder_textures):
            hou.ui.displayMessage(f"Folder does not exist {folder_textures}",
                                  severity=hou.severityType.Error)
            return False
        material_handler = tex_to_mtlx.TxToMtlx()
        stage = parent.stage()
        prims_name = _find_prims_by_attribute(stage, UsdGeom.Mesh)
        materials_created_lenght = 0
        if material_handler.folder_with_textures(folder_textures):
            # Get the texture detail
            texture_list = material_handler.get_texture_details(folder_textures)
            if texture_list and isinstance(texture_list, dict):
                # Common data
                common_data = {
                    'mtlTX':False, #If you want to create TX files set to True
                    'path': material_lib.path(),
                    'node': material_lib,
                }
                for material_name in texture_list:
                    # Fix to provide the correct path
                    path = texture_list[material_name]['FOLDER_PATH']
                    if not path.endswith("/"):
                        texture_list[material_name]['FOLDER_PATH'] = path + "/"
                    if material_name not in prims_name:
                        continue
                    else:
                        materials_created_lenght += 1
                        create_material = tex_to_mtlx.MtlxMaterial(
                            material_name,
                            **common_data,
                            folder_path = path,
                            texture_list=texture_list
                        )
                        create_material.create_materialx()
                hou.ui.displayMessage(f"Created {materials_created_lenght} materials in {material_lib.path()}", severity=hou.severityType.Message)
                return True
            else:
                _create_mtlx_templates(parent, material_lib)
                hou.ui.displayMessage("No valid textures sets found..",severity=hou.severityType.Message)
                return True
        else:
            _create_mtlx_templates(parent, material_lib)
            hou.ui.displayMessage("No valid textures sets found in folder",severity=hou.severityType.Message)
            return True
    except Exception as e:
        hou.ui.displayMessage(f"Error creating materials: {str(e)}",severity=hou.severityType.Error)
        return False

def _find_prims_by_attribute(stage: Usd.Stage, prim_type: Type[Usd.Typed]) -> List[Usd.Prim]:
    prims_name = set()
    for prim in stage.Traverse():
        if prim.IsA(prim_type) and "render" in str(prim.GetPath()):
            prims_name.add(prim.GetName())
    return list(prims_name)

def _random_color():
    ''' Generate a random color RGB values between 0 and 1'''
    red_color = random.random()
    green_color = random.random()
    blue_color = random.random()
    #Get main colour
    main_colour = hou.Color(red_color, green_color, blue_color)
    # Convert RGB to HSV
    hue, saturation, value = colorsys.rgb_to_hsv(red_color, green_color, blue_color)
    new_saturation = saturation * 0.5
    # Get the secondary colour
    sec_red, sec_green, sec_blue = colorsys.hsv_to_rgb(hue, new_saturation, value)
    secondary_colour = hou.Color(sec_red, sec_green, sec_blue)

    return (main_colour, secondary_colour)


def _get_stage_node_name(filename):
    """Ask user for the Stage node name."""
    filename = filename.split(".")[0]
    if filename.endswith("bgeo.sc"):
        filename = filename.split(".")[0]
    try:
        stage_name = hou.ui.readInput(
            "Enter name for the top-level LOPS Stage node:",
            initial_contents=filename,
            title="LOPS Group Importer - Stage Node Name"
        )
        if stage_name[0] == 0:  # User clicked OK
            return stage_name[1].strip() or filename
        else:  # User cancelled
            return filename
    except:
        return filename

def create_organized_net_note(asset_name, nodes_to_layout, offset_vector=hou.Vector2(0, 0)):
    '''
    Creates a network box and sticky note organized around selected nodes,
    with position offset to avoid overlapping groups.

    Args:
        asset_name (str): Label text for the sticky note and network box
        nodes_to_layout (list): List of nodes to include in the network box
        offset (float): Horizontal offset applied to this block
    Returns:
        None
    '''
    parent = nodes_to_layout[0].parent()

    # Colors
    background_colour = 0.189
    parent_colour = hou.Color(background_colour, background_colour, background_colour)
    child_colour, sticky_note_colour = _random_color()
    text_color = hou.Color(0.8, 0.8, 0.8)

    # Apply horizontal offset to nodes
    for node in nodes_to_layout:
        node.setPosition(node.position() + offset_vector)

    # Create network boxes
    parent_box = parent.createNetworkBox()
    child_box = parent.createNetworkBox()
    parent_box.addItem(child_box)

    for node in nodes_to_layout:
        child_box.addItem(node)

    child_box.fitAroundContents()

    # Network box settings
    parent_box.setComment(asset_name)
    parent_box.setColor(parent_colour)
    child_box.setColor(child_colour)

    parent_box.fitAroundContents()
