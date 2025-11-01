import os
import time

import hou
import voptoolutils

from tools import tex_to_mtlx, lops_light_rig
import colorsys
import random
from typing import List, Type
from pxr import Usd,UsdGeom
from modules.misc_utils import _sanitize, slugify, MaterialNamingConfig
from tools.lops_asset_builder_v3.component_material_custom import build_component_material_custom
from tools.lops_asset_builder_v3.componentoutput_custom import componentoutput_custom_creation
from tools.lops_asset_builder_v3.create_transform_nodes import build_transform_camera_and_scene_node, \
    build_lights_spin_xform
from tools.lops_asset_builder_v3.subnet_lookdev_setup import create_subnet_lookdev_setup
from tools.lops_asset_builder_v3.asset_builder_ui import AssetMaterialVariantsDialog, ProgressReporter
from tools.lops_asset_builder_v3.material_validator import validate_and_warn_user
from PySide6 import QtWidgets, QtCore


# UI components moved to asset_builder_ui.py: SimpleProgressDialog




def create_component_builder(selected_directory=None):
    '''
    Main function to create the component builder based on a provided asset
    '''

    # 1) Show the selection dialog first; do not start progress/logging yet
    dialog = AssetMaterialVariantsDialog(
        default_asset="",
        default_maps=""
    )
    if dialog.exec_() != QtWidgets.QDialog.Accepted:
        # User cancelled before starting the process — nothing to log
        return

    # 2) Collect UI data after confirmation
    ui = dialog.data()
    main_asset_file_path = ui.get("main_asset_file_path") or ""
    asset_name_input = (ui.get("asset_name_input") or "").strip() or "ASSET"
    asset_variants = ui.get("asset_variants") or []
    create_geo_variants = bool(ui.get("create_geo_variants", True))
    lowercase_material_names = bool(ui.get("lowercase_material_names", False))
    asset_vset_name = ui.get("asset_variant_set") or "geo_variant"
    mtl_vset_name = ui.get("material_variant_set") or "mtl_variant"
    folder_textures = ui.get("main_textures") or ""
    mtl_variants = ui.get("material_variants") or []
    create_lookdev = bool(ui.get("create_lookdev_setup", True))
    create_light_rig = bool(ui.get("create_light_rig", True))
    enable_env_lights = bool(ui.get("enable_env_lights", False))
    env_light_paths = ui.get("env_light_paths") or []

    # 3) Now start progress and logging UI, after OK
    progress = ProgressReporter("LOPs Asset Builder v3")
    progress.set_total(12)
    try:
            progress.step("Validating inputs")
            # Inputs were already validated by the dialog's accept(); these are just safety checks with logging
            if not (main_asset_file_path and os.path.isfile(main_asset_file_path)):
                progress.log("Error: invalid main asset file.")
                progress.mark_finished("Error: invalid main asset file.")
                return
            if not (folder_textures and os.path.isdir(folder_textures)):
                progress.log("Error: invalid texture folder.")
                progress.mark_finished("Error: invalid texture folder.")
                return

            # Validate materials before building
            progress.step("Validating materials")
            # Create unified naming config for validation
            naming_config = MaterialNamingConfig.from_ui(lowercase=lowercase_material_names)
            all_asset_paths = [main_asset_file_path] + asset_variants
            validation_result, user_continues = validate_and_warn_user(
                asset_paths=all_asset_paths,
                texture_folder=folder_textures,
                texture_variants=[os.path.basename(v) for v in mtl_variants] if mtl_variants else None,
                show_dialog=True,
                naming_config=naming_config
            )

            # Log validation results
            if validation_result.materials_missing:
                progress.log(f"⚠️ Warning: {len(validation_result.materials_missing)} material(s) have no matching textures")
                for mat in sorted(validation_result.materials_missing):
                    progress.log(f"  Missing: {mat}")
                progress.log("Missing materials will use fallback template shaders")
            else:
                progress.log(f"✓ All {len(validation_result.materials_expected)} material(s) validated successfully")

            if not user_continues:
                progress.log("Build cancelled by user")
                progress.mark_finished("Cancelled by user")
                return

            # Define context
            stage_context = hou.node("/stage")
            # Yield to UI and allow cancel after obtaining stage context
            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")
            # Determine stage node name from UI or fallback logic
            node_name = asset_name_input

            progress.step("Building geometry and material variants")
            # Reuse the same naming_config from validation for consistency
            geometry_variants_node, comp_out, nodes_to_layout, comp_material_last = build_geo_and_mtl_variants(
                stage_context=stage_context,
                node_name=node_name,
                main_asset_file_path=main_asset_file_path,
                asset_variants=asset_variants,
                create_geo_variants=create_geo_variants,
                asset_vset_name=asset_vset_name,
                mtl_variants=mtl_variants,
                folder_textures=folder_textures,
                mtl_vset_name=mtl_vset_name,
                progress=progress,
                lowercase_material_names=lowercase_material_names,
            )

            # Yield to UI between heavy build phases
            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")
            
            progress.step("Organizing network layout")
            #Nodes to layout
            stage_context.layoutChildren(nodes_to_layout)
            # Allow user interaction after layout
            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")

            #Sticky note creation
            create_organized_net_note(f"Asset {node_name.upper()}", nodes_to_layout,hou.Vector2(-4, 18))

            # Select the Component Output
            comp_out.setSelected(True, clear_all_selected=True)

            # If lookdev is disabled, stop here as requested
            if not create_lookdev:
                progress.log("Lookdev setup disabled; finished base setup.")
                progress.mark_finished("Done")
                return

            progress.step("Creating lookdev scope and graft stages")
            lookdev_setup_layout = []
            # Create primitive scope node
            primitive_node = stage_context.createNode("primitive", _sanitize(f"{node_name}_geo"))
            primitive_node.parm("primpath").set("/turntable/asset/\n/turntable/lookdev/\n/turntable/lights/")
            primitive_node.parm("parentprimtype").set("UsdGeomScope")

            # Create graftstage for asset
            graftstage_asset_node = stage_context.createNode("graftstages", "graftstage_asset")
            graftstage_asset_node.parm("primpath").set("/turntable/asset")
            graftstage_asset_node.parm("destpath").set("/")
            graftstage_asset_node.setInput(0,primitive_node)
            graftstage_asset_node.setInput(1,comp_out)

            current_stream = graftstage_asset_node
            if create_light_rig:
                progress.step("Building light rig")
                # Give UI a chance before heavy light rig creation
                if progress.is_cancelled():
                    raise KeyboardInterrupt("Cancelled by user")
                # Create grafstages node lights
                graftstage_lights_node = stage_context.createNode("graftstages", "graftstage_lights_rig")
                graftstage_lights_node.parm("primpath").set("/turntable/")
                graftstage_lights_node.parm("destpath").set("/")
                graftstage_lights_node.setInput(0,current_stream)

                # Create light rig
                light_rig_nodes_to_layout,light_mixer = lops_light_rig.create_three_point_light(selected_node=comp_out)
                # Allow user interaction after light rig creation
                if progress.is_cancelled():
                    raise KeyboardInterrupt("Cancelled by user")

                # Light Rig Nodes to layout
                create_organized_net_note("Light Rig", light_rig_nodes_to_layout, hou.Vector2(5, 10))

                # Hook grafstages light to lightmixer
                graftstage_lights_node.setInput(1,light_mixer)

                # Create switch to activate and deactivate lights
                switch_lights_rig_node = stage_context.createNode("switch", "switch_lights_rig")
                switch_lights_rig_node.setInput(0,current_stream)
                switch_lights_rig_node.setInput(1,graftstage_lights_node)
                switch_lights_rig_node.parm("input").set(1)
                lookdev_setup_layout.extend([switch_lights_rig_node,graftstage_lights_node])

                current_stream = switch_lights_rig_node


            # Environment lights branch (optional)
            if enable_env_lights:
                progress.step("Creating environment lights")
                graftstage_envlights_node = stage_context.createNode("graftstages", "graftstage_envlights")
                graftstage_envlights_node.parm("primpath").set("/turntable/lights")
                graftstage_envlights_node.parm("destpath").set("/")
                graftstage_envlights_node.setInput(0, current_stream)

                # Create Env Lights (dynamic count based on env_light_paths)
                domes = []
                if env_light_paths:
                    for idx, path in enumerate(env_light_paths):
                        base = os.path.splitext(os.path.basename(path))[0]
                        dome = stage_context.createNode("domelight::3.0", _sanitize(f"{base or 'env_light'}_{idx+1}"))
                        dome.parm("primpath").set("/$OS")
                        dome.parm("xn__inputstexturefile_r3ah").set(path)
                        domes.append(dome)
                else:
                    dome = stage_context.createNode("domelight::3.0", "env_light")
                    dome.parm("primpath").set("/$OS")
                    domes.append(dome)

                switch_envlights_selection_node = stage_context.createNode("switch", "switch_envlights_selection")
                for i, dome in enumerate(domes):
                    switch_envlights_selection_node.setInput(i, dome)
                envlights_nodes_to_layout = domes + [switch_envlights_selection_node]

                stage_context.layoutChildren(items=envlights_nodes_to_layout)
                # Yield after laying out env lights
                if progress.is_cancelled():
                    raise KeyboardInterrupt("Cancelled by user")
                create_organized_net_note("Env Light", envlights_nodes_to_layout, hou.Vector2(5, 6))

                graftstage_envlights_node.setInput(1, switch_envlights_selection_node)
                switch_env_lights = stage_context.createNode("switch", "switch_env_lights")
                switch_env_lights.setInput(0, current_stream)
                switch_env_lights.setInput(1, graftstage_envlights_node)

                # Enable the Env Lights branch by default when Lookdev is active
                switch_env_lights.parm("input").set(1)
                current_stream = switch_env_lights
                lookdev_setup_layout.extend([switch_env_lights,graftstage_envlights_node])


            progress.step("Creating lookdev subnetwork")
            # Create Subnetwork lookdev setup
            subnetwork_lookdevsetup_node = create_subnet_lookdev_setup(node_name="lookdev_setup")
            subnetwork_lookdevsetup_node.setInput(0, current_stream)

            # Create switch to activate lookdev
            switch_lookdev_setup_node = stage_context.createNode("switch", "switch_lookdev_setup")
            switch_lookdev_setup_node.setInput(0, current_stream)
            switch_lookdev_setup_node.setInput(1, subnetwork_lookdevsetup_node)
            switch_lookdev_setup_node.parm("input").set(1)
            lookdev_setup_layout = lookdev_setup_layout + [ switch_lookdev_setup_node,subnetwork_lookdevsetup_node,graftstage_asset_node,primitive_node]
            stage_context.layoutChildren(items=lookdev_setup_layout, horizontal_spacing=0.3, vertical_spacing=1.5)
            create_organized_net_note("LookDev Setup", lookdev_setup_layout, hou.Vector2(15, -5))

            progress.step("Creating camera, animations, and render nodes")
            # Camera and Animations
            transform_camera_and_scene_node = build_transform_camera_and_scene_node()
            transform_camera_and_scene_node.setInput(0, switch_lookdev_setup_node)
            switch_transform_camera_and_scene_node = stage_context.createNode("switch", "switch_transform_camera_and_scene_node")
            switch_transform_camera_and_scene_node.setInput(0, switch_lookdev_setup_node)
            switch_transform_camera_and_scene_node.setInput(1, transform_camera_and_scene_node)
            transform_envlights_node = build_lights_spin_xform()
            transform_envlights_node.setInput(0, switch_transform_camera_and_scene_node)
            switch_animate_lights = stage_context.createNode("switch", "switch_animate_lights")
            switch_animate_lights.setInput(0, switch_transform_camera_and_scene_node)
            switch_animate_lights.setInput(1, transform_envlights_node)

            # Create Karma nodes
            karma_settings, usdrender_rop = create_karma_nodes(stage_context)
            karma_settings.setInput(0, switch_animate_lights)
            usdrender_rop.setInput(0, karma_settings)

            # Karma Nodes to layout
            karma_nodes = [switch_transform_camera_and_scene_node, transform_camera_and_scene_node, switch_animate_lights, transform_envlights_node, karma_settings, usdrender_rop]
            stage_context.layoutChildren(items=karma_nodes, horizontal_spacing=0.25, vertical_spacing=1)
            # Yield after laying out camera/render nodes
            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")
            create_organized_net_note("Camera Render", karma_nodes, hou.Vector2(0, -5))
            comp_out.setSelected(True, clear_all_selected=True)
            # Log completion only once via mark_finished
            progress.mark_finished("Done")

    except KeyboardInterrupt as e:
        progress.log(str(e))
        progress.mark_finished("Cancelled.")
    except Exception as e:
        # Use print instead of UI message to allow non-interactive operation
        print(f"Error: An error happened in create component builder: {str(e)}")
        progress.log(f"Error: {str(e)}")
        progress.mark_finished("Error.")

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

def _prepare_imported_asset(parent, name, extension, path, out_node, skip_matchsize=False, lowercase_material_names: bool = True):
    '''

    Creates the network layout for the default, proxy and sim outputs
    Args:
        parent = node where the file needs to be imported and prepared
        name = asset's name
        extension = if we are working with FBX, ABC, OBJ, etc
        path = path where the asset is located
        out_node = component output node for reference expressions
        skip_matchsize = if True, skips matchsize node creation
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
            parm_name = "fileName"
        else:
            return

        # Create the main nodes
        attrib_wrangler = parent.createNode("attribwrangle", "convert_mat_to_name")
        attrib_delete = parent.createNode("attribdelete", "keep_P_N_UV_NAME")
        remove_points = parent.createNode("add", _sanitize(f"remove_points"))

        # Conditionally create matchsize node
        if not skip_matchsize:
            match_size = parent.createNode("matchsize", _sanitize(f"matchsize_{name}"))
            match_size.setParms({
                "justify_x": 0,
                "justify_y": 1,
                "justify_z": 0,
            })

        # Set Parms for main nodes
        file_import.parm(parm_name).set(f"{path}/{name}.{extension}")

        # Build VEX snippet for material-to-name conversion with optional lowercasing
        vex_lines = []
        if lowercase_material_names:
            vex_lines.append('s@shop_materialpath = tolower(replace(s@shop_materialpath, " ", "_"));')
        else:
            vex_lines.append('s@shop_materialpath = replace(s@shop_materialpath, " ", "_");')
        vex_lines.append('string material_to_name[] = split(s@shop_materialpath, "/");')
        vex_lines.append('s@name = material_to_name[-1];')
        vex_lines.append('// Remove trailing underscores')
        vex_lines.append('s@name = rstrip(s@name, "_");')
        attrib_wrangler.setParms({
            "class": 1,
            "snippet": "\n".join(vex_lines)
        })

        attrib_delete.setParms({
            "negate": True,
            "ptdel": "N P",
            "vtxdel": "uv",
            "primdel": "name"
        })

        remove_points.parm("remove").set(True)

        # Connect Main nodes (conditional connection based on skip_matchsize)
        if skip_matchsize:
            # Skip matchsize, connect directly to file import
            attrib_wrangler.setInput(0, file_import)
        else:
            # Use matchsize in the chain
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
        hou.ui.displayMessage(f"An error happened in prepare imported assets: {str(e)}", severity=hou.severityType.Error)

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
    # Ensure the Karma Render Settings use the Lookdev camera
    _ldev_cam_path = '/turntable/lookdev/ldevCam0'
    cam_parm = karma_settings.parm('camera') or karma_settings.parm('camerapath')
    if cam_parm is not None:
        cam_parm.set(_ldev_cam_path)
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

def _create_materials(parent, folder_textures, material_lib, expected_names=None, progress: ProgressReporter | None = None, naming_config: MaterialNamingConfig = None):
    ''' Create the material using the tex_to_mtlx script
    Args:
        parent: Parent node
        folder_textures: the folder where the textures are located
        material_lib: the material library where the materials will be saved
        expected_names: List of material names to create (from geometry files)
        progress: Progress reporter instance
        naming_config: Material naming configuration (if None, uses default)
    Return:
         True if successful, False otherwise
    '''
    # Use provided config or create default
    if naming_config is None:
        naming_config = MaterialNamingConfig()
    try:
        # Normalize path for existence check
        folder_textures_check = os.path.normpath(folder_textures)
        if progress:
            progress.log(f"Scanning texture folder: {folder_textures_check}")
            # Nudge progress so the bar reflects scanning work
            try:
                progress.step("Scanning texture folders…")
            except Exception:
                pass
        if not os.path.exists(folder_textures_check):
            warn1 = f"Warning: Texture folder does not exist: {folder_textures_check}"
            warn2 = f"Warning: Texture folder not found: {folder_textures}. Creating template materials instead."
            if progress:
                progress.log(warn1)
                progress.log(warn2)
                # Step a bit so the user sees movement even when falling back
                try:
                    for _ in range(3):
                        progress.step("Texture folder missing; creating template materials…")
                except Exception:
                    pass
            else:
                print(warn1)
                print(warn2)
            _create_mtlx_templates(parent, material_lib)
            return True

        material_handler = tex_to_mtlx.TxToMtlx(naming_config=naming_config)
        materials_created_length = 0

        # Combined texture list from all subfolders
        combined_texture_list = {}
        valid_folders_found = False

        # Recursively search for textures in the folder and all subfolders
        for root, dirs, files in os.walk(folder_textures_check):
            if progress and progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")
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
                # Minor progress tick per valid subfolder discovered
                if progress:
                    try:
                        progress.step(f"Found textures in: {os.path.basename(current_folder)}")
                    except Exception:
                        pass

        if valid_folders_found and combined_texture_list:
            start_time = time.perf_counter()
            # Common data
            common_data = {
                'mtlTX': False, # If you want to create TX files set to True
                'path': material_lib.path(),
                'node': material_lib,
            }

            total_to_create = sum(1 for material_name in combined_texture_list if not expected_names or material_name in expected_names)
            created_so_far = 0
            if progress:
                progress.log(f"Creating up to {total_to_create} materials in {material_lib.path()}")
                # Pre-creation bump so users see movement before the first material completes
                try:
                    for _ in range(min(5, max(1, total_to_create // 10))):
                        progress.step("Preparing material creation…")
                except Exception:
                    pass

            # Determine how many progress steps to allocate per material so the bar moves continuously.
            # Aim to spend ~800 steps (out of the 1000 total set by the caller) within this phase.
            target_phase_steps = 800
            per_mat_steps = 1
            if total_to_create > 0:
                per_mat_steps = max(1, target_phase_steps // total_to_create)

            for material_name in combined_texture_list:
                if progress and progress.is_cancelled():
                    raise KeyboardInterrupt("Cancelled by user")
                # Skip materials not in expected_names list if provided
                if expected_names and material_name not in expected_names:
                    continue

                # Fix to provide the correct path
                path = combined_texture_list[material_name]['FOLDER_PATH']
                if not path.endswith("/"):
                    combined_texture_list[material_name]['FOLDER_PATH'] = path + "/"

                create_material = tex_to_mtlx.MtlxMaterial(
                    material_name,
                    **common_data,
                    folder_path=path,
                    texture_list=combined_texture_list,
                    naming_config=naming_config
                )
                create_material.create_materialx()

                materials_created_length += 1
                created_so_far += 1
                # Advance progress multiple ticks per material to convey ongoing work
                if progress:
                    try:
                        # First tick with a message, the rest silent to avoid log spam
                        progress.step(f"Created material {created_so_far}/{total_to_create}: {material_name}")
                        for _ in range(per_mat_steps - 1):
                            progress.step()
                    except Exception:
                        pass

                if progress and (created_so_far % 5 == 0 or created_so_far == total_to_create):
                    progress.log(f"Created {created_so_far}/{total_to_create} materials…")

            elapsed = time.perf_counter() - start_time
            msg = f"Created {materials_created_length} materials in {material_lib.path()} in {elapsed:.2f}s"
            if progress:
                progress.log(msg)
                # Small tail steps to reach the phase target smoothly
                try:
                    for _ in range(5):
                        progress.step()
                except Exception:
                    pass
            else:
                print(msg)
            return True
        else:
            _create_mtlx_templates(parent, material_lib)
            msg = "No valid textures sets found in folder or subfolders"
            if progress:
                progress.log(msg)
                try:
                    for _ in range(5):
                        progress.step("No textures found; using template materials…")
                except Exception:
                    pass
            else:
                print(msg)
            return True
    except Exception as e:
        # Use print instead of UI message to allow non-interactive operation
        err = f"Error creating materials: {str(e)}"
        if progress:
            progress.log(err)
        else:
            print(err)
        return False

def _extract_material_names(asset_paths, lowercase: bool = False):
    """
    Extract material names from geometry files by examining shop_materialpath
    and material:binding primitive attributes.

    Args:
        asset_paths (list): List of asset file paths to examine
        lowercase (bool): If True, convert material names to lowercase

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
                        material_name = slugify(os.path.basename(material_path), lowercase=lowercase)
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


def extract_material_names_from_assets(asset_paths, lowercase: bool = False):
    """Public helper to expose expected material names extracted from geometry files.

    This wraps the internal _extract_material_names so UI/CLI code can
    use the exact same logic as the builder when estimating materials.

    Args:
        asset_paths (list): List of asset file paths to examine
        lowercase (bool): If True, convert material names to lowercase
    """
    return _extract_material_names(asset_paths, lowercase=lowercase)


def estimate_materials_in_folder(folder_textures: str, expected_names=None) -> int:
    """Estimate how many materials would be created for a given textures folder.

    Mirrors the counting logic inside _create_materials: walks subfolders,
    collects a combined texture list via TxToMtlx, and returns the number of
    materials filtered by expected_names (if provided).
    """
    try:
        folder_textures_check = os.path.normpath(folder_textures or "")
        if not folder_textures_check or not os.path.exists(folder_textures_check):
            return 0
        material_handler = tex_to_mtlx.TxToMtlx()
        combined_texture_list = {}
        # Recursively search for textures in the folder and all subfolders
        for root, dirs, files in os.walk(folder_textures_check):
            current_folder = root.replace(os.sep, "/")
            if material_handler.folder_with_textures(current_folder):
                folder_texture_list = material_handler.get_texture_details(current_folder)
                if folder_texture_list and isinstance(folder_texture_list, dict):
                    combined_texture_list.update(folder_texture_list)
        if not combined_texture_list:
            return 0
        if expected_names:
            expected_set = set(expected_names)
            total = sum(1 for n in combined_texture_list if n in expected_set)
        else:
            total = len(combined_texture_list)
        return int(total)
    except Exception:
        return 0


def build_geo_and_mtl_variants(stage_context, node_name: str, main_asset_file_path: str,
                               asset_variants: list, asset_vset_name: str,
                               mtl_variants: list, folder_textures: str,
                               mtl_vset_name: str, skip_matchsize: bool = False,
                               progress: ProgressReporter | None = None,
                               lowercase_material_names: bool = False,
                               use_custom_component_output: bool = True,
                               create_geo_variants: bool = True):
    """
    Build the geometry variants, material variants, and materials, returning
    key nodes for further wiring.

    Returns:
        tuple: (geometry_variants_node or comp_geo, comp_out, nodes_to_layout, comp_material_last)
    """
    # Create unified material naming configuration
    naming_config = MaterialNamingConfig.from_ui(lowercase=lowercase_material_names)

    # Assemble assets list - only include variants if create_geo_variants is True
    if create_geo_variants:
        assets = [main_asset_file_path] + (asset_variants or [])
    else:
        assets = [main_asset_file_path]

    has_geo_variants = len(assets) > 1  # More than just the main asset

    # Create Component Output (custom or normal) based on flag
    if use_custom_component_output:
        comp_out = componentoutput_custom_creation(node_name=_sanitize(f"{node_name}"))
    else:
        comp_out = stage_context.createNode("componentoutput", _sanitize(f"{node_name}"))
        comp_out.parm("rootprim").set("/ASSET")

    # Only create componentgeometryvariants if we have actual variants
    if has_geo_variants:
        geometry_variants_node = stage_context.createNode("componentgeometryvariants", "geometry_variants")
        if asset_vset_name:
            geometry_variants_node.parm("variantset").set(asset_vset_name)
        nodes_to_layout = [geometry_variants_node, comp_out]

        # Geometry variants population
        for index, asset in enumerate(assets):
            if progress and progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")
            path, filename = os.path.split(asset.split(";")[0])
            # Get asset name and extension
            asset_name = filename.split(".")[0]
            asset_extension = filename.split(".")[-1]
            if filename.endswith("bgeo.sc"):
                asset_name = filename.split(".")[0]
                asset_extension = "bgeo.sc"
            if progress:
                progress.log(f"Creating geometry variant {index+1}/{len(assets)}: {asset_name}")
            comp_geo = stage_context.createNode("componentgeometry", _sanitize(f"{asset_name}_geo"))
            geometry_variants_node.setInput(index, comp_geo)
            _prepare_imported_asset(comp_geo, _sanitize(f"{asset_name}"), asset_extension, path, comp_out, skip_matchsize=skip_matchsize, lowercase_material_names=lowercase_material_names)
            nodes_to_layout.append(comp_geo)

        first_geo_node = geometry_variants_node
    else:
        # No variants - just create a single componentgeometry node
        if progress:
            progress.log(f"No geometry variants - creating single geometry node")
        path, filename = os.path.split(main_asset_file_path.split(";")[0])
        asset_name = filename.split(".")[0]
        asset_extension = filename.split(".")[-1]
        if filename.endswith("bgeo.sc"):
            asset_name = filename.split(".")[0]
            asset_extension = "bgeo.sc"

        comp_geo = stage_context.createNode("componentgeometry", _sanitize(f"{asset_name}_geo"))
        _prepare_imported_asset(comp_geo, _sanitize(f"{asset_name}"), asset_extension, path, comp_out, skip_matchsize=skip_matchsize, lowercase_material_names=lowercase_material_names)
        nodes_to_layout = [comp_geo, comp_out]
        first_geo_node = comp_geo
        geometry_variants_node = comp_geo  # Return comp_geo as the "geometry node" for consistency

    # Material variants list (mtl_variants + main textures at end)
    mtl_folders = list(mtl_variants or [])
    if folder_textures:
        mtl_folders.append(folder_textures)

    comp_material_last = None
    for index, mtl_folder in enumerate(mtl_folders):
        if progress and progress.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")
        mtl_folder_name = os.path.basename(mtl_folder)
        if progress:
            progress.log(f"Creating material variant {index+1}/{len(mtl_folders)} from folder: {mtl_folder_name}")
        material_lib = stage_context.createNode("materiallibrary", _sanitize(f"{node_name}_mtl_{mtl_folder_name}"))
        comp_material = build_component_material_custom(node_name=_sanitize(f"{node_name}_material_variant_{mtl_folder_name}"))
        if mtl_vset_name:
            comp_material.parm("variantset").set(mtl_vset_name)
        material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
        if index == 0:
            comp_material.setInput(0, first_geo_node)  # Use first_geo_node instead of geometry_variants_node
        else:
            comp_material.setInput(0, comp_material_last)
        comp_material.setInput(1, material_lib)
        comp_material_last = comp_material
        # Extract material names from ALL geometry variant assets (main + variants)
        # Ensure asset paths are unique (order-preserving) to avoid repeated processing
        all_asset_paths = []
        for a in assets:
            all_asset_paths.append(a)
        material_names = _extract_material_names(all_asset_paths, lowercase=naming_config.lowercase)
        readable_list = "\n".join(f"- {m}" for m in material_names)
        progress.log(f"Found {len(material_names)} Materials across all geometry{'variants' if has_geo_variants else ''} (from {len(all_asset_paths)} unique asset{'s' if len(all_asset_paths) > 1 else ''}):\n{readable_list}")
        # Create the materials using the text_to_mtlx script with targeted material creation
        _create_materials(first_geo_node, mtl_folder, material_lib, material_names, progress=progress, naming_config=naming_config)  # Use first_geo_node
        nodes_to_layout.append(material_lib)
        nodes_to_layout.append(comp_material)

    # Wire final material output to component output
    if comp_material_last is not None:
        comp_out.setInput(0, comp_material_last)

    return geometry_variants_node, comp_out, nodes_to_layout, comp_material_last

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
