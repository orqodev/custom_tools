import os

import hou
import voptoolutils

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
import colorsys
import random
from typing import List, Type
from pxr import Usd,UsdGeom
from modules.misc_utils import _sanitize


def create_component_builder(selected_directory=None):
    '''
    Main function to create the component builder based on a provided asset
    '''

    # Get File
    if selected_directory == None:
        selected_directory = hou.ui.selectFile(title="Select the file you want to import",
                                               file_type=hou.fileType.Geometry,
                                               multiple_select=False)
    selected_directory = hou.text.expandString(selected_directory)

    try:
        if os.path.exists(selected_directory):
            # Define context
            stage_context = hou.node("/stage")

            # Get the path and filename and the folder with the textures
            path, filename = os.path.split(selected_directory)

            # Ask user to choose texture folder path instead of hardcoding "maps"
            default_maps_folder = os.path.join(path, "maps").replace(os.sep, "/")

            # Check if default maps folder exists
            if os.path.exists(default_maps_folder):
                # Ask user if they want to use default or choose custom path
                choice = hou.ui.displayMessage(
                    f"Found default 'maps' folder at:\n{default_maps_folder}\n\nDo you want to use this folder or choose a different one?",
                    buttons=("Use Default", "Choose Different", "Cancel"),
                    severity=hou.severityType.Message,
                    default_choice=0
                )

                if choice == 0:  # Use Default
                    folder_textures = default_maps_folder
                elif choice == 1:  # Choose Different
                    custom_folder = hou.ui.selectFile(
                        title="Select folder containing textures",
                        file_type=hou.fileType.Directory,
                        multiple_select=False
                    )
                    if custom_folder:
                        folder_textures = hou.text.expandString(custom_folder)
                    else:
                        hou.ui.displayMessage("No texture folder selected. Operation cancelled.", severity=hou.severityType.Warning)
                        return
                else:  # Cancel
                    return
            else:
                # No default maps folder found, ask user to select one
                hou.ui.displayMessage(
                    f"No 'maps' folder found at:\n{default_maps_folder}\n\nPlease select the folder containing your textures.",
                    severity=hou.severityType.Message
                )
                custom_folder = hou.ui.selectFile(
                    title="Select folder containing textures",
                    file_type=hou.fileType.Directory,
                    multiple_select=False
                )
                if custom_folder:
                    folder_textures = hou.text.expandString(custom_folder)
                else:
                    hou.ui.displayMessage("No texture folder selected. Operation cancelled.", severity=hou.severityType.Warning)
                    return

            # Get asset name and extension
            asset_name = filename.split(".")[0]
            asset_extension = filename.split(".")[-1]
            if filename.endswith("bgeo.sc"):
                asset_name = filename.split(".")[0]
                asset_extension = "bgeo.sc"

            # Create nodes for the component builder setup

            comp_geo = stage_context.createNode("componentgeometry", _sanitize(f"{asset_name}_geo"))
            material_lib = stage_context.createNode("materiallibrary", _sanitize(f"{asset_name}_mtl"))
            comp_material = stage_context.createNode("componentmaterial", _sanitize(f"{asset_name}_assign"))
            comp_out = stage_context.createNode("componentoutput", _sanitize(asset_name))

            comp_geo.parm("geovariantname").set(asset_name)
            material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
            comp_material.parm("nummaterials").set(0)

            # Create auto assigment for materials
            comp_material_edit = comp_material.node("edit")
            output_node = comp_material_edit.node("output0")

            assign_material = comp_material_edit.createNode("assignmaterial", _sanitize(f"{asset_name}_assign"))
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
            nodes_to_layout = [comp_geo, material_lib, comp_material, comp_out]
            stage_context.layoutChildren(nodes_to_layout)
            # Prepare imported geo
            _prepare_imported_asset(comp_geo, asset_name, asset_extension, path, comp_out)
            # Create the materials using the text_to_mtlx script
            _create_materials(comp_geo,folder_textures, material_lib, )

            # Sticky note creation
            create_organized_net_note(f"Asset {asset_name.upper()}", nodes_to_layout,hou.Vector2(0, 5))
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
            camera_python_script = create_camera_lookdev(stage_context, asset_name)
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

def _prepare_imported_asset(parent, name, extension, path, out_node):
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

    try:
        # Set the parent node where the nodes are going to be created
        parent = hou.node(parent.path() + "/sopnet/geo")
        # Get the ouput nodes - default, proxy and sim,
        default_output = hou.node(f"{parent.path()}/default")
        proxy_output = hou.node(f"{parent.path()}/proxy")
        sim_output = hou.node(f"{parent.path()}/simproxy")

        # Create the file node that imports the asset
        file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
        if extension in file_extension:
            file_import = parent.createNode("file", _sanitize(f"import_{name}"))
            parm_name = "file"
        elif extension == "abc":
            file_import = parent.createNode("alembic", _sanitize(f"import_{name}"))
            parm_name = "filename"
        else:
            return

        # Create the main nodes
        match_size = parent.createNode("matchsize", _sanitize(f"matchsize_{name}"))
        attrib_wrangler = parent.createNode("attribwrangle", "convert_mat_to_name")
        attrib_delete = parent.createNode("attribdelete", "keep_P_N_UV_NAME")
        remove_points = parent.createNode("add", _sanitize(f"remove_points"))

        # Set Parms for main nodes
        file_import.parm(parm_name).set(f"{path}/{name}.{extension}")

        match_size.setParms({
            "justify_x": 0,
            "justify_y": 1,
            "justify_z": 0,
        })

        attrib_wrangler.setParms({
            "class": 1,
            "snippet": 's@shop_materialpath = tolower(replace(s@shop_materialpath, " ", "_"));\nstring material_to_name[] = split(s@shop_materialpath,"/");\ns@name=material_to_name[-1];'
        })

        attrib_delete.setParms({
            "negate": True,
            "ptdel": "N P",
            "vtxdel": "uv",
            "primdel": "name"
        })

        remove_points.parm("remove").set(True)

        # Connect Main nodes
        match_size.setInput(0, file_import)
        attrib_wrangler.setInput(0, match_size)
        attrib_delete.setInput(0, attrib_wrangler)
        remove_points.setInput(0, attrib_delete)
        default_output.setInput(0, remove_points)

        # Prepare Proxy Setup
        poly_reduce = parent.createNode("polyreduce::2.0", "reduce_to_5")
        attrib_colour = parent.createNode("attribwrangle", "set_color")
        color_node = parent.createNode("color", "unique_color")
        attrib_promote = parent.createNode("attribpromote", "promote_Cd")
        attrib_delete_name = parent.createNode("attribdelete", _sanitize(f"delete_asset_name"))
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
