"""
LOPS Asset Builder v2
=====================

A tool for building assets in Houdini's LOPS context with automatic material creation
and network organization.

Features:
- Automatic component creation for assets
- Material discovery and creation
- Light rig setup
- Camera and render setup
- Configurable network organization

Network Organization:
--------------------
The tool provides configurable network organization with the following features:
- Optional network boxes for visual grouping
- Category-based color coding (Asset, Light, Camera, Material, Render)
- Configurable positioning with offsets
- Automatically disabled for TOP functions to prevent issues

To configure network organization:
```python
from tools.lops_asset_builder_v2 import lops_asset_builder_v2

# Disable network boxes
lops_asset_builder_v2.configure_network_organization(create_boxes=False)

# Enable network boxes with category-based colors
lops_asset_builder_v2.configure_network_organization(create_boxes=True, use_categories=True)

# Use random colors instead of categories
lops_asset_builder_v2.configure_network_organization(use_categories=False)

# Set a default offset for all nodes
lops_asset_builder_v2.configure_network_organization(default_offset=hou.Vector2(1, 0))
```
"""

import os

import hou
import voptoolutils
from sympy import primitive

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
import colorsys
import random
from typing import List, Type, Optional, Dict, Tuple, Any
from pxr import Usd,UsdGeom
from modules.misc_utils import _sanitize, slugify
from tools.lops_asset_builder_v3.component_material_custom import build_component_material_custom
from tools.lops_asset_builder_v3.componentoutput_custom import componentoutput_custom_creation
from tools.lops_asset_builder_v3.create_transform_nodes import build_transform_camera_and_scene_node, \
    build_lights_spin_xform
from tools.lops_asset_builder_v3.subnet_lookdev_setup import create_subnet_lookdev_setup

# Global configuration for network organization
NETWORK_CONFIG = {
    "create_network_boxes": True,  # Set to False to disable network boxes
    "use_categories": True,        # Set to False to use random colors instead of category-based colors
    "default_offset": hou.Vector2(0, 0)
}


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
        if os.path.exists(path):
            # Define context
            stage_context = hou.node("/stage")
            # Get the path and filename and the folder with the texturesRR
            node_name = _get_stage_node_name(filename)

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
            comp_geo, material_lib, comp_material, comp_out = _create_inital_nodes(stage_context, node_name)

            # Nodes to layout
            nodes_to_layout = [comp_geo, material_lib, comp_material, comp_out]
            stage_context.layoutChildren(nodes_to_layout)

             # Extract material names from the asset paths
            asset_paths = selected_directory.split(";")
            material_names = _extract_material_names(asset_paths)
            print(f"Found {len(material_names)} materials in assets: {material_names}")

            # Prepare imported geo
            _prepare_imported_asset(comp_geo, selected_directory, path, comp_out, node_name)

            # Create the materials using the text_to_mtlx script with targeted material creation
            _create_materials(comp_geo, folder_textures, material_lib, material_names)

            # Sticky note creation
            create_organized_net_note(f"Asset {node_name.upper()}", nodes_to_layout,hou.Vector2(-2, 11))

            # Select the Component Output
            comp_out.setSelected(True, clear_all_selected=True)

            #Create primitive node
            primitive_node = stage_context.createNode("primitive", _sanitize(f"{node_name}_geo"))
            primitive_node.parm("primpath").set("/turntable/asset/\n/turntable/lookdev/\n/turntable/lights/")
            primitive_node.parm("parentprimtype").set("UsdGeomScope")

            #Create graftstage node asset
            graftstage_asset_node = stage_context.createNode("graftstages", "graftstage_asset")
            graftstage_asset_node.parm("primpath").set("/turntable/asset")
            graftstage_asset_node.parm("destpath").set("/")
            graftstage_asset_node.setInput(0,primitive_node)
            graftstage_asset_node.setInput(1,comp_out)

            # Create grafstages node lights
            graftstage_lights_node = stage_context.createNode("graftstages", "graftstage_lights_rig")
            graftstage_lights_node.parm("primpath").set("/turntable/lights/")
            graftstage_lights_node.parm("destpath").set("/")
            graftstage_lights_node.setInput(0,graftstage_asset_node)

            # Create light rig
            light_rig_nodes_to_layout,light_mixer = lops_light_rig.create_three_point_light()

            # Light Rig Nodes to layout
            create_organized_net_note("Light Rig", light_rig_nodes_to_layout, hou.Vector2(5, 10))

            # Hook grafstages light to lightmixer
            graftstage_lights_node.setInput(1,light_mixer)

            # Create switch to activate and deactivate lights
            switch_lights_node = stage_context.createNode("switch", "switch_lights_rig")
            switch_lights_node.setInput(0,graftstage_asset_node)
            switch_lights_node.setInput(1,graftstage_lights_node)

            # Create Subnetwork lookdev setup
            subnetwork_lookdevsetup_node = create_subnet_lookdev_setup(node_name="lookdev_setup")
            subnetwork_lookdevsetup_node.setInput(0,switch_lights_node)

            # Create switch to activate and lookdev
            switch_lookdev_setup_node = stage_context.createNode("switch", "switch_lookdev_setup")
            switch_lookdev_setup_node.setInput(0,switch_lights_node)
            switch_lookdev_setup_node.setInput(1,subnetwork_lookdevsetup_node)

            # Create grafstages node lights
            graftstage_envlights_node = stage_context.createNode("graftstages", "graftstage_envlights")
            graftstage_envlights_node.parm("primpath").set("/turntable/envlights/")
            graftstage_lights_node.parm("destpath").set("/")
            graftstage_envlights_node.setInput(0,switch_lookdev_setup_node)

            # Create Env Lights
            domelight1_node = stage_context.createNode("domelight::3.0", "domelight1")
            domelight2_node = stage_context.createNode("domelight::3.0", "domelight2")
            domelight3_node = stage_context.createNode("domelight::3.0", "domelight3")
            switch_envlights_selection_node = stage_context.createNode("switch","switch_envlights_selection")
            switch_envlights_selection_node.setInput(0,domelight1_node)
            switch_envlights_selection_node.setInput(1,domelight2_node)
            switch_envlights_selection_node.setInput(2,domelight3_node)
            envlights_nodes_to_layout = [domelight1_node,domelight2_node,domelight3_node,switch_envlights_selection_node]
            stage_context.layoutChildren(items=envlights_nodes_to_layout)
            create_organized_net_note("Env Light", envlights_nodes_to_layout, hou.Vector2(7, 6))
            graftstage_envlights_node.setInput(1,switch_envlights_selection_node)
            switch_env_lights = stage_context.createNode("switch","switch_env_lights")
            switch_env_lights.setInput(0,switch_lookdev_setup_node)
            switch_env_lights.setInput(1,graftstage_envlights_node)
            lookdev_setup_layout = [graftstage_envlights_node,switch_env_lights, switch_lookdev_setup_node,subnetwork_lookdevsetup_node,switch_lights_node,graftstage_lights_node,graftstage_asset_node,primitive_node]
            stage_context.layoutChildren(items=lookdev_setup_layout, horizontal_spacing=0.3, vertical_spacing=1.5)
            create_organized_net_note("LookDev Setup", lookdev_setup_layout, hou.Vector2(15, -5))

            # Camera and Animations
            transform_camera_and_scene_node = build_transform_camera_and_scene_node()
            transform_camera_and_scene_node.setInput(0,switch_env_lights)
            switch_transform_camera_and_scene_node = stage_context.createNode("switch","switch_transform_camera_and_scene_node")
            switch_transform_camera_and_scene_node.setInput(0,switch_env_lights)
            switch_transform_camera_and_scene_node.setInput(1,transform_camera_and_scene_node)
            transform_envlights_node = build_lights_spin_xform()
            transform_envlights_node.setInput(0,switch_transform_camera_and_scene_node)
            switch_animate_lights = stage_context.createNode("switch","switch_animate_lights")
            switch_animate_lights.setInput(0,switch_transform_camera_and_scene_node)
            switch_animate_lights.setInput(1,transform_envlights_node)
            # Create Karma nodes
            karma_settings,usdrender_rop = create_karma_nodes(stage_context)
            karma_settings.setInput(0, switch_animate_lights)
            usdrender_rop.setInput(0, karma_settings)
            # Karma Nodes to layout
            karma_nodes = [switch_transform_camera_and_scene_node,transform_camera_and_scene_node,switch_animate_lights,transform_envlights_node,karma_settings,usdrender_rop]
            stage_context.layoutChildren(items=karma_nodes,horizontal_spacing=0.25, vertical_spacing=1)
            create_organized_net_note("Camera Render", karma_nodes, hou.Vector2(0, -6))

    except Exception as e:
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error: An error happened in create component builder: {str(e)}")

def _create_inital_nodes(stage_context, node_name: str = "asset_builder"):
    # Create nodes for the component builder setup
    comp_geo = stage_context.createNode("componentgeometry", _sanitize(f"{node_name}_geo"))
    material_lib = stage_context.createNode("materiallibrary", _sanitize(f"{node_name}_mtl"))
    comp_material = build_component_material_custom(node_name=_sanitize(f"{node_name}_material_variant"))
    comp_out = componentoutput_custom_creation(node_name=_sanitize(f"{node_name}"))

    material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")

    # Connect nodes
    comp_material.setInput(0, comp_geo)
    comp_material.setInput(1, material_lib)
    comp_out.setInput(0, comp_material)


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
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error: Error creating group parameters: {str(e)}")


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
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error: Error linking nodes to parameters: {str(e)}")


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
        switch_node = parent.createNode("switch", _sanitize(f"switch_{node_name}"))

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
                file_import = parent.createNode("file", _sanitize(f"import_{asset_name}"))
                parm_name = "file"
            elif extension == "abc":
                file_import = parent.createNode("alembic", _sanitize(f"import_{asset_name}"))
                parm_name = "fileName"
            else:
                continue

            # Set Parms for main nodes
            file_import.parm(parm_name).set(full_asset_path)
            switch_node.setInput(i, file_import)
            file_nodes.append(file_import)

        # Create transform node for external control (like in batch_import_workflow)
        transform_node = parent.createNode("xform", _sanitize(f"transform_{node_name}"))
        transform_node.setInput(0, switch_node)

        # Create the main nodes
        match_size = parent.createNode("matchsize", _sanitize(f"matchsize_{node_name}"))
        attrib_wrangler = parent.createNode("attribwrangle", "convert_mat_to_name")
        attrib_delete = parent.createNode("attribdelete", "keep_P_N_UV_NAME")
        remove_points = parent.createNode("add", _sanitize(f"remove_points"))

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
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error: An error happened in prepare imported assets: {str(e)}")

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

def _create_materials(parent, folder_textures, material_lib, expected_names=None):
    ''' Create the material using the tex_to_mtlx script
    Args:
        parent: Parent node
        folder_textures: the folder where the textures are located
        material_lib: the material library where the materials will be saved
        expected_names: List of material names to create (from geometry files)
    Return:
         True if successful, False otherwise
    '''
    try:
        # Normalize path for existence check
        folder_textures_check = os.path.normpath(folder_textures)
        if not os.path.exists(folder_textures_check):
            print(f"Warning: Texture folder does not exist: {folder_textures_check}")
            # Print warning but continue with template materials
            print(f"Warning: Texture folder not found: {folder_textures}. Creating template materials instead.")
            _create_mtlx_templates(parent, material_lib)
            return True

        material_handler = tex_to_mtlx.TxToMtlx()
        stage = parent.stage()
        prims_name = _find_prims_by_attribute(stage, UsdGeom.Mesh)
        materials_created_length = 0

        # Combined texture list from all subfolders
        combined_texture_list = {}
        valid_folders_found = False

        # Recursively search for textures in the folder and all subfolders
        for root, dirs, files in os.walk(folder_textures_check):
            # Convert Windows path to Houdini-friendly format
            current_folder = root.replace(os.sep, "/")

            # Check if this folder contains valid textures
            if material_handler.folder_with_textures(current_folder):
                valid_folders_found = True
                # Get texture details from this folder
                folder_texture_list = material_handler.get_texture_details(current_folder)
                if folder_texture_list and isinstance(folder_texture_list, dict):
                    # Merge with combined list
                    combined_texture_list.update(folder_texture_list)

        if valid_folders_found and combined_texture_list:
            # Common data
            common_data = {
                'mtlTX': False, # If you want to create TX files set to True
                'path': material_lib.path(),
                'node': material_lib,
            }

            for material_name in combined_texture_list:
                # Skip materials not in expected_names list if provided
                if expected_names and material_name not in expected_names:
                    continue

                # Fix to provide the correct path
                path = combined_texture_list[material_name]['FOLDER_PATH']
                if not path.endswith("/"):
                    combined_texture_list[material_name]['FOLDER_PATH'] = path + "/"

                materials_created_length += 1
                create_material = tex_to_mtlx.MtlxMaterial(
                    material_name,
                    **common_data,
                    folder_path=path,
                    texture_list=combined_texture_list
                )
                create_material.create_materialx()

            # Use print instead of UI message to allow non-interactive operation
            print(f"Created {materials_created_length} materials in {material_lib.path()}")
            return True
        else:
            _create_mtlx_templates(parent, material_lib)
            # Use print instead of UI message to allow non-interactive operation
            print("No valid textures sets found in folder or subfolders")
            return True
    except Exception as e:
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error creating materials: {str(e)}")
        return False

def _extract_material_names(asset_paths):
    """
    Extract material names from geometry files by examining shop_materialpath
    and material:binding primitive attributes.

    Args:
        asset_paths (list): List of asset file paths to examine

    Returns:
        list: Sorted list of unique material names (basenames only)
    """
    material_names = set()

    for asset_path in asset_paths:
        asset_path = asset_path.strip()
        if not asset_path:
            continue

        try:
            # Load geometry in memory
            geo = hou.Geometry()
            geo.loadFromFile(asset_path)

            # Check for shop_materialpath primitive attribute
            shop_attrib = geo.findPrimAttrib("shop_materialpath")
            if shop_attrib:
                for prim in geo.prims():
                    material_path = prim.stringAttribValue(shop_attrib)
                    if material_path:
                        # Extract basename from material path
                        material_name = slugify(os.path.basename(material_path))
                        if material_name:
                            material_names.add(material_name)

            # Check for material:binding primitive attribute
            binding_attrib = geo.findPrimAttrib("material:binding")
            if binding_attrib:
                for prim in geo.prims():
                    material_path = prim.stringAttribValue(binding_attrib)
                    if material_path:
                        # Extract basename from material path
                        material_name = os.path.basename(material_path)
                        if material_name:
                            material_names.add(material_name)

        except Exception as e:
            # Skip unreadable files silently
            continue

    return sorted(list(material_names))

def _find_prims_by_attribute(stage: Usd.Stage, prim_type: Type[Usd.Typed]) -> List[Usd.Prim]:
    prims_name = set()

    # Handle case where stage is None (timing issue during workflow)
    if stage is None:
        print("⚠️ Warning: Stage is None in _find_prims_by_attribute, returning empty list")
        return []

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

def create_tops_component_builder(directory: str, filename: str) -> Optional[hou.Node]:
    '''
    Creates a component builder for use in TOP networks without creating lights, rigs, camera, and render nodes.
    Enhanced with material discovery and targeted material creation.

    Args:
        directory (str): Directory containing the asset file
        filename (str): Name of the asset file (including extension)

    Returns:
        Optional[hou.Node]: The component output node if successful, None otherwise

    Example:
        # In a Python TOP node:
        import os
        from tools.lops_asset_builder_v2 import lops_asset_builder_v2

        # Get directory and filename from TOP work item
        directory = work_item.attribValue("directory")
        filename = work_item.attribValue("filename")

        # Create the component builder
        output_node = lops_asset_builder_v2.create_tops_component_builder(directory, filename)

        # Set work item to success or failure based on result
        if output_node:
            work_item.addStatusMessage("Component builder created successfully")
            work_item.setSuccess(True)
        else:
            work_item.addStatusMessage("Failed to create component builder")
            work_item.setFailure(True)
    '''
    try:
        # Construct the full path to the asset
        selected_directory = os.path.join(directory, filename)
        selected_directory = hou.text.expandString(selected_directory)

        if not os.path.exists(selected_directory):
            print(f"Error: File does not exist: {selected_directory}")
            return None

        # Define context
        stage_context = hou.node("/stage")

        # Get the path and filename and the folder with the textures
        path, filename = os.path.split(selected_directory)
        # Get maps folder path - keep original format for Houdini but use normalized path for existence check
        folder_textures = os.path.join(path, "maps").replace(os.sep, "/")
        folder_textures_check = os.path.normpath(os.path.join(path, "maps"))

        # Check if maps folder exists
        if not os.path.exists(folder_textures_check):
            print(f"Maps folder does not exist: {folder_textures_check}")
            # Continue execution - _create_materials will handle missing folder and create template materials

        # Get asset name and extension
        asset_name = filename.split(".")[0]
        asset_extension = filename.split(".")[-1]
        if filename.endswith("bgeo.sc"):
            asset_name = filename.split(".")[0]
            asset_extension = "bgeo.sc"

        # Extract material names from the asset
        asset_paths = [selected_directory]
        material_names = _extract_material_names(asset_paths)
        print(f"Found {len(material_names)} materials in {selected_directory}: {material_names}")

        # Create nodes for the component builder setup
        comp_geo = stage_context.createNode("componentgeometry", f"{asset_name}_geo")
        material_lib = stage_context.createNode("materiallibrary", f"{asset_name}_mtl")
        comp_material = stage_context.createNode("componentmaterial", f"{asset_name}_assign")
        comp_out = stage_context.createNode("componentoutput", asset_name)

        comp_geo.parm("geovariantname").set(asset_name)
        material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
        comp_material.parm("nummaterials").set(0)

        # Create auto assigment for materials
        comp_material_edit = comp_material.node("edit")
        output_node = comp_material_edit.node("output0")

        assign_material = comp_material_edit.createNode("assignmaterial", f"{asset_name}_assign")
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
        _prepare_imported_asset(comp_geo, selected_directory, path, comp_out, asset_name)

        # Create the materials using the text_to_mtlx script with targeted material creation
        _create_materials(comp_geo, folder_textures, material_lib, material_names)

        # Network organization is disabled for TOP functions as it can cause issues
        # Just perform a basic layout of the nodes
        stage_context.layoutChildren(nodes_to_layout)

        # Set Display Flag
        comp_out.setGenericFlag(hou.nodeFlag.Display, True)

        # Set the lopoutput parameter to use @directory\@filename\ format
        comp_out.parm("lopoutput").set(r'`@directory`/`@filename`/')

        return comp_out

    except Exception as e:
        print(f"An error happened in create_tops_component_builder: {str(e)}")
        return None


def configure_network_organization(create_boxes=None, use_categories=None, default_offset=None):
    """
    Configure the network organization settings.

    Args:
        create_boxes (bool, optional): Whether to create network boxes
        use_categories (bool, optional): Whether to use category-based colors
        default_offset (hou.Vector2, optional): Default position offset for nodes

    Returns:
        dict: The current network configuration
    """
    global NETWORK_CONFIG

    if create_boxes is not None:
        NETWORK_CONFIG["create_network_boxes"] = bool(create_boxes)

    if use_categories is not None:
        NETWORK_CONFIG["use_categories"] = bool(use_categories)

    if default_offset is not None:
        NETWORK_CONFIG["default_offset"] = default_offset

    return NETWORK_CONFIG


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

def create_organized_net_note(asset_name, nodes_to_layout, offset_vector=hou.Vector2(0, 0), create_network_boxes=True, category=None):
    '''
    Creates a network box and sticky note organized around selected nodes,
    with position offset to avoid overlapping groups.

    Args:
        asset_name (str): Label text for the sticky note and network box
        nodes_to_layout (list): List of nodes to include in the network box
        offset_vector (hou.Vector2): Position offset applied to this block
        create_network_boxes (bool): Whether to create network boxes (True) or just organize nodes (False)
        category (str): Optional category for color coding (e.g., "Asset", "Light", "Camera")
    Returns:
        tuple: (parent_box, child_box) if create_network_boxes is True, else None
    '''
    if not nodes_to_layout:
        print(f"Warning: No nodes provided to organize for {asset_name}")
        return None

    parent = nodes_to_layout[0].parent()

    # Apply horizontal offset to nodes
    for node in nodes_to_layout:
        node.setPosition(node.position() + offset_vector)

    # If network boxes are disabled, just layout the nodes and return
    if not create_network_boxes:
        parent.layoutChildren(items=nodes_to_layout)
        return None

    # Define category-based colors
    category_colors = {
        "Asset": (hou.Color(0.2, 0.4, 0.6), hou.Color(0.3, 0.5, 0.7)),
        "Light": (hou.Color(0.6, 0.5, 0.2), hou.Color(0.7, 0.6, 0.3)),
        "Camera": (hou.Color(0.5, 0.2, 0.5), hou.Color(0.6, 0.3, 0.6)),
        "Material": (hou.Color(0.2, 0.5, 0.3), hou.Color(0.3, 0.6, 0.4)),
        "Render": (hou.Color(0.6, 0.2, 0.2), hou.Color(0.7, 0.3, 0.3))
    }

    # Determine colors based on category or generate random ones
    if category and category in category_colors:
        parent_colour, child_colour = category_colors[category]
    else:
        background_colour = 0.189
        parent_colour = hou.Color(background_colour, background_colour, background_colour)
        child_colour, _ = _random_color()

    text_color = hou.Color(0.8, 0.8, 0.8)

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

    return (parent_box, child_box)
