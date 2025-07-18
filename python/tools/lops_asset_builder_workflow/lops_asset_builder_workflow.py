import os
import hou
import voptoolutils
from typing import List, Type
from pxr import Usd, UsdGeom

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
from tools.lops_asset_builder_v2.lops_asset_builder_v2 import create_camera_lookdev, create_karma_nodes


class LopsAssetBuilderWorkflow:
    """
    LOPS Asset Builder Workflow - Step-by-step UI for multiple asset importing

    This class combines the functionality of lops_asset_builder_v2 with the 
    step-by-step UI workflow pattern from batch_import_workflow.

    Features:
    - Interactive step-by-step asset group importing
    - Multiple asset groups with individual component builders
    - Material creation and assignment
    - Automatic network layout
    """

    def __init__(self):
        self.stage_context = None
        self.asset_groups = []  # List of asset group data
        self.group_counter = 0
        self.merge_node = None  # Final merge node to connect all component outputs

    def create_workflow(self):
        """
        Creates the LOPS Asset Builder workflow:
        1. Initialize stage context
        2. Iteratively import asset groups until user says "No"
        3. Create component builder for each asset group
        4. Create merge node and connect all component outputs
        5. Show final summary
        """
        # Step 1: Initialize stage context
        self.stage_context = hou.node("/stage")

        # Step 2: Iteratively import asset groups
        self._import_asset_groups_iteratively()

        # Step 3: Create merge node and connect all component outputs
        if self.asset_groups:
            self._create_final_merge_node()

        # Step 4: Layout all nodes
        self._layout_all_nodes()



        self._show_final_summary()

        # Select the Component Output
        self.merge_node.setSelected(True, clear_all_selected=True)
        # Ask the user for an assembly name
        default_name = "ASSET"
        rv = hou.ui.readInput(
            f"Enter a name for the top-level **Scope** prim (default: {default_name})",
            buttons=("OK", "Cancel"),
            title="LOPS Asset Builder – Scope Name",
            initial_contents=default_name)
        if rv[0] != 0:   # Cancel
            assembly_name = default_name
        else:
            assembly_name = rv[1].strip() or default_name

        # Insert a Scope prim (not Xform)
        assembly = self.stage_context.createNode("scope", f"{assembly_name}_scope")
        assembly.parm("primpath").set(f"/{assembly_name}")
        assembly.setInput(0, self.merge_node)          # merge → scope
        assembly.setGenericFlag(hou.nodeFlag.Display, True)
        self.merge_node.setGenericFlag(hou.nodeFlag.Display, False)
        # Create light rig
        light_rig_nodes_to_layout, graft_branch = lops_light_rig.create_three_point_light()
        # Light Rig Nodes to layout
        # Set Display Flag
        graft_branch.setGenericFlag(hou.nodeFlag.Display, True)
        # Create Camera Node
        camera_render = self.stage_context.createNode('camera','camera_render')
        camera_render.setInput(0,graft_branch)
        # Create Python Script

        camera_python_script = create_camera_lookdev(self.stage_context, assembly_name)
        # Connect script
        camera_python_script.setInput(0, camera_render)

        # Create Karma nodes
        karma_settings,usdrender_rop = create_karma_nodes(self.stage_context)
        karma_settings.setInput(0, camera_python_script)
        usdrender_rop.setInput(0, karma_settings)
        # Karma Nodes to layout
        karma_nodes = [camera_render,camera_python_script,karma_settings,usdrender_rop]
        self.stage_context.layoutChildren(items=karma_nodes)

        return self.stage_context

    def _import_asset_groups_iteratively(self):
        """
        Iteratively import asset groups until user says "No".
        Each iteration creates a new asset group with its own component builder.
        """
        while True:
            self.group_counter += 1

            # Import assets for this group
            asset_data = self._import_single_asset_group()

            if not asset_data:
                # User cancelled or no files selected, break the loop
                self.group_counter -= 1
                break

            # Create component builder for this group
            component_nodes = self._create_component_builder_for_group(asset_data)

            if component_nodes:
                # Store group data
                group_data = {
                    'name': asset_data['group_name'],
                    'asset_paths': asset_data['asset_paths'],
                    'texture_folder': asset_data['texture_folder'],
                    'component_nodes': component_nodes,
                    'group_id': self.group_counter
                }
                self.asset_groups.append(group_data)

            # Ask if user wants to add another group
            if not self._ask_for_another_group():
                break

    def _extract_material_names(self, asset_paths):
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
                            material_name = os.path.basename(material_path)
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
                # Skip unreadable files silently as per requirements
                continue

        return sorted(list(material_names))

    def _import_single_asset_group(self):
        """Import assets for a single asset group."""
        try:
            # Select asset files
            default_directory = hou.text.expandString('$HIP')
            selected_directory = hou.ui.selectFile(
                start_directory=default_directory,
                title=f"Select asset files for Group {self.group_counter}",
                file_type=hou.fileType.Geometry,
                multiple_select=True
            )

            if not selected_directory:
                return None

            selected_directory = hou.text.expandString(selected_directory)
            asset_paths = selected_directory.split(";")

            # Get the base path for textures
            path, filename = os.path.split(asset_paths[0].strip())

            # Get group name from user
            group_name = self._get_asset_group_name(asset_paths)

            # Check for texture folder
            texture_folder = os.path.join(path, "maps").replace(os.sep, "/")

            # Extract material names from geometry files
            material_names = self._extract_material_names(asset_paths)

            return {
                'group_name': group_name,
                'asset_paths': asset_paths,
                'base_path': path,
                'texture_folder': texture_folder,
                'material_names': material_names
            }

        except Exception as e:
            hou.ui.displayMessage(f"Error importing asset group: {str(e)}",
                                  severity=hou.severityType.Error)
            return None

    def _get_asset_group_name(self, asset_paths):
        """Get or generate group name from user input."""
        # Generate default name from first asset
        first_asset = os.path.basename(asset_paths[0].strip())
        default_name = first_asset.split(".")[0]
        if ".bgeo.sc" in first_asset:
            default_name = first_asset.split(".")[0]

        try:
            group_name = hou.ui.readInput(
                f"Enter name for Asset Group {self.group_counter}:",
                initial_contents=f"{default_name}_group_{self.group_counter}",
                title="LOPS Asset Builder Workflow - Group Name"
            )
            if group_name[0] == 0:  # User clicked OK
                return group_name[1].strip() or f"{default_name}_group_{self.group_counter}"
            else:  # User cancelled
                return f"{default_name}_group_{self.group_counter}"
        except:
            return f"{default_name}_group_{self.group_counter}"

    def _ask_for_another_group(self):
        """Ask user if they want to add another asset group."""
        try:
            choice = hou.ui.displayMessage(
                f"Asset Group {self.group_counter} created successfully!\n\n"
                f"Do you want to add another asset group?",
                buttons=("Yes", "No"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="LOPS Asset Builder Workflow"
            )
            return choice == 0  # 0 = Yes, 1 = No
        except:
            return False

    def _create_component_builder_for_group(self, asset_data):
        """
        Create a component builder for a single asset group.
        Based on the create_component_builder function from lops_asset_builder_v2.
        """
        try:
            group_name = asset_data['group_name']
            asset_paths = asset_data['asset_paths']
            texture_folder = asset_data['texture_folder']

            # Create initial nodes
            comp_geo, material_lib, comp_material, comp_out = self._create_initial_nodes(group_name)

            # Prepare imported assets
            self._prepare_imported_asset(comp_geo, asset_paths, asset_data['base_path'], comp_out, group_name)

            # Create materials if texture folder exists
            if os.path.exists(texture_folder):
                self._create_materials(
                    comp_geo,
                    texture_folder,
                    material_lib,
                    asset_data["material_names"]
                )
            else:
                # Create default MaterialX templates
                self._create_mtlx_templates(comp_geo, material_lib)

            # Layout nodes
            nodes_to_layout = [comp_geo, material_lib, comp_material, comp_out]
            self.stage_context.layoutChildren(nodes_to_layout)

            return {
                'comp_geo': comp_geo,
                'material_lib': material_lib,
                'comp_material': comp_material,
                'comp_out': comp_out,
                'nodes_to_layout': nodes_to_layout
            }

        except Exception as e:
            hou.ui.displayMessage(f"Error creating component builder for group {asset_data['group_name']}: {str(e)}",
                                  severity=hou.severityType.Error)
            return None

    def _create_initial_nodes(self, node_name):
        """Create initial nodes for the component builder setup."""
        # Create nodes for the component builder setup
        comp_geo = self.stage_context.createNode("componentgeometry", f"{node_name}_geo")
        material_lib = self.stage_context.createNode("materiallibrary", f"{node_name}_mtl")
        comp_material = self.stage_context.createNode("componentmaterial", f"{node_name}_assign")
        comp_out = self.stage_context.createNode("componentoutput", node_name)

        comp_geo.parm("geovariantname").set(node_name)
        material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
        comp_material.parm("nummaterials").set(0)

        # Create auto assignment for materials
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

        return comp_geo, material_lib, comp_material, comp_out

    def _prepare_imported_asset(self, parent, asset_paths, base_path, out_node, node_name):
        """
        Prepare imported assets with switch node and transform controls.
        Based on _prepare_imported_asset from lops_asset_builder_v2.
        Returns switch_node and transform_node for parameter linking.
        """
        try:
            # Set the parent node where the nodes are going to be created
            parent_sop = hou.node(parent.path() + "/sopnet/geo")
            # Get the output nodes - default, proxy and sim
            default_output = hou.node(f"{parent_sop.path()}/default")
            proxy_output = hou.node(f"{parent_sop.path()}/proxy")
            sim_output = hou.node(f"{parent_sop.path()}/simproxy")

            # Create the file nodes that import the assets
            file_nodes = []
            processed_paths = []
            switch_node = parent_sop.createNode("switch", f"switch_{node_name}")

            for i, asset_path in enumerate(asset_paths):
                asset_path = asset_path.strip()
                if not asset_path:
                    continue

                # Get asset name and extension
                file_path, filename = os.path.split(asset_path)
                asset_name = filename.split(".")[0]
                extension = filename.split(".")[-1]
                if ".bgeo.sc" in filename:
                    asset_name = filename.split(".")[0]
                    extension = "bgeo.sc"

                # Store full path for parameters
                full_asset_path = asset_path
                processed_paths.append(full_asset_path)

                file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
                if extension in file_extension:
                    file_import = parent_sop.createNode("file", f"import_{asset_name}")
                    parm_name = "file"
                elif extension == "abc":
                    file_import = parent_sop.createNode("alembic", f"import_{asset_name}")
                    parm_name = "filename"
                else:
                    continue

                # Set parameters for main nodes
                file_import.parm(parm_name).set(asset_path)
                switch_node.setInput(i, file_import)
                file_nodes.append(file_import)

            # Create the main processing nodes
            match_size = parent_sop.createNode("matchsize", f"matchsize_{node_name}")
            attrib_wrangler = parent_sop.createNode("attribwrangle", "convert_mat_to_name")
            attrib_delete = parent_sop.createNode("attribdelete", "keep_P_N_UV_NAME")
            remove_points = parent_sop.createNode("add", f"remove_points")

            # Create transform node for external control (after remove_points)
            transform_node = parent_sop.createNode("xform", f"transform_{node_name}")

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

            # Connect main nodes - transform node now comes after remove_points
            match_size.setInput(0, switch_node)
            attrib_wrangler.setInput(0, match_size)
            attrib_delete.setInput(0, attrib_wrangler)
            remove_points.setInput(0, attrib_delete)
            transform_node.setInput(0, remove_points)
            default_output.setInput(0, transform_node)

            # Prepare Proxy Setup
            poly_reduce = parent_sop.createNode("polyreduce::2.0", "reduce_to_5")
            attrib_colour = parent_sop.createNode("attribwrangle", "set_color")
            color_node = parent_sop.createNode("color", "unique_color")
            attrib_promote = parent_sop.createNode("attribpromote", "promote_Cd")
            attrib_delete_name = parent_sop.createNode("attribdelete", f"delete_asset_name")
            name_node = parent_sop.createNode("name", "name")
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

            # Need to grab the rootprim from the component output and paste relative reference
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
            # Connect proxy nodes
            poly_reduce.setInput(0, transform_node)
            attrib_colour.setInput(0, poly_reduce)
            color_node.setInput(0, attrib_colour)
            attrib_promote.setInput(0, color_node)
            attrib_delete_name.setInput(0, attrib_promote)
            proxy_output.setInput(0, attrib_delete_name)

            # Prepare the sim Setup
            python_sop = self._create_convex(parent_sop)
            # Connect sim nodes
            python_sop.setInput(0, transform_node)
            name_node.setInput(0, python_sop)
            sim_output.setInput(0, name_node)

            # Layout nodes
            parent_sop.layoutChildren()

            # Create UI parameters for multi-asset switch workflow
            # This adds controls to the componentgeometry node
            if len(processed_paths) > 1:
                # Only create multi-asset parameters if we have multiple assets
                self._create_group_parameters(parent, node_name, processed_paths, switch_node, transform_node)

            return switch_node, transform_node

        except Exception as e:
            hou.ui.displayMessage(f"Error preparing imported asset: {str(e)}",
                                  severity=hou.severityType.Error)
            return None, None

    def _create_group_parameters(self, parent_node, node_name, asset_paths, switch_node, transform_node):
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
            self._link_group_nodes_to_parameters(parent_node, node_name, switch_node, transform_node)

        except Exception as e:
            hou.ui.displayMessage(f"Error creating group parameters: {str(e)}",
                                  severity=hou.severityType.Error)

    def _link_group_nodes_to_parameters(self, parent_node, node_name, switch_node, transform_node):
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

    def _create_materials(self, parent, folder_textures, material_lib, expected_names):
        """
        Create materials using the tex_to_mtlx script.
        Only creates materials for names found in expected_names list.

        Args:
            parent: Parent node
            folder_textures: Path to texture folder
            material_lib: Material library node
            expected_names: List of material names to create (from geometry files)
        """
        try:
            if not os.path.exists(folder_textures):
                hou.ui.displayMessage(f"Texture folder does not exist: {folder_textures}",
                                      severity=hou.severityType.Warning)
                self._create_mtlx_templates(parent, material_lib)
                return False

            material_handler = tex_to_mtlx.TxToMtlx()
            stage = parent.stage()
            prims_name = self._find_prims_by_attribute(stage, UsdGeom.Mesh)
            materials_created_length = 0

            if material_handler.folder_with_textures(folder_textures):
                # Get the texture detail
                texture_list = material_handler.get_texture_details(folder_textures)
                if texture_list and isinstance(texture_list, dict):
                    # Common data
                    common_data = {
                        'mtlTX': False,  # If you want to create TX files set to True
                        'path': material_lib.path(),
                        'node': material_lib,
                    }
                    for material_name in texture_list:
                        # Skip materials not in expected_names list
                        if material_name not in expected_names:
                            continue

                        # Fix to provide the correct path
                        path = texture_list[material_name]['FOLDER_PATH']
                        if not path.endswith("/"):
                            texture_list[material_name]['FOLDER_PATH'] = path + "/"

                        materials_created_length += 1
                        create_material = tex_to_mtlx.MtlxMaterial(
                            material_name,
                            **common_data,
                            folder_path=path,
                            texture_list=texture_list
                        )
                        create_material.create_materialx()
                    hou.ui.displayMessage(f"Created {materials_created_length} materials in {material_lib.path()}",
                                          severity=hou.severityType.Message)
                    return True
                else:
                    self._create_mtlx_templates(parent, material_lib)
                    hou.ui.displayMessage("No valid texture sets found..", severity=hou.severityType.Message)
                    return True
            else:
                self._create_mtlx_templates(parent, material_lib)
                hou.ui.displayMessage("No valid texture sets found in folder", severity=hou.severityType.Message)
                return True
        except Exception as e:
            hou.ui.displayMessage(f"Error creating materials: {str(e)}", severity=hou.severityType.Error)
            return False

    def _create_mtlx_templates(self, parent, material_lib):
        """Create MaterialX templates."""
        name = "mtlxstandard_surface"
        voptoolutils._setupMtlXBuilderSubnet(
            subnet_node=None,
            destination_node=material_lib,
            name=name,
            mask=voptoolutils.MTLX_TAB_MASK,
            folder_label="MaterialX Builder",
            render_context="mtlx"
        )
        material_lib.layoutChildren()

    def _find_prims_by_attribute(self, stage: Usd.Stage, prim_type: Type[Usd.Typed]) -> List[str]:
        """Find primitives by attribute type."""
        prims_name = set()
        for prim in stage.Traverse():
            if prim.IsA(prim_type) and "render" in str(prim.GetPath()):
                prims_name.add(prim.GetName())
        return list(prims_name)

    def _create_convex(self, parent):
        """
        Creates the Python sop node that is used to create a convex hull using Scipy
        Args:
            parent = the component geometry node where the file is imported
        Return:
            python_sop = python_sop node created
        """
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

        # Simplify Toggle
        simplify_toggle = hou.ToggleParmTemplate(
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
        ptg.append(simplify_toggle)
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

    def _create_final_merge_node(self):
        """Create a final merge node to connect all component outputs."""
        try:
            self.merge_node = self.stage_context.createNode("merge", "final_merge")

            for i, group_data in enumerate(self.asset_groups):
                comp_out = group_data['component_nodes']['comp_out']
                self.merge_node.setInput(i, comp_out)

            # Set display flag on merge node
            self.merge_node.setGenericFlag(hou.nodeFlag.Display, True)

        except Exception as e:
            hou.ui.displayMessage(f"Error creating final merge node: {str(e)}",
                                  severity=hou.severityType.Error)

    def _layout_all_nodes(self):
        """
        Layout all nodes in the stage context with proper spacing and organization.
        This function ensures nodes are properly positioned for optimal workflow organization.
        """
        try:
            # First, layout nodes within each component builder group
            # This ensures proper spacing within each group
            for group_data in self.asset_groups:
                nodes_to_layout = group_data['component_nodes']['nodes_to_layout']
                if nodes_to_layout:
                    # Layout the specific nodes for this group
                    self.stage_context.layoutChildren(nodes_to_layout)

            # Then layout all main stage nodes for overall organization
            # This provides the final positioning for all nodes
            self.stage_context.layoutChildren()

        except Exception as e:
            hou.ui.displayMessage(f"Error laying out nodes: {str(e)}",
                                  severity=hou.severityType.Error)


    def _show_final_summary(self):
        """Show final summary of the workflow."""
        try:
            if not self.asset_groups:
                hou.ui.displayMessage("No asset groups were created.",
                                      severity=hou.severityType.Warning)
                return

            summary_text = f"LOPS Asset Builder Workflow Complete!\n\n"
            summary_text += f"Created {len(self.asset_groups)} asset groups:\n\n"

            for group_data in self.asset_groups:
                summary_text += f"• {group_data['name']}: {len(group_data['asset_paths'])} assets\n"

            if self.merge_node:
                summary_text += f"\nAll groups connected to final merge node: {self.merge_node.name()}"

            hou.ui.displayMessage(summary_text,
                                  severity=hou.severityType.Message,
                                  title="LOPS Asset Builder Workflow - Complete")

        except Exception as e:
            hou.ui.displayMessage(f"Error showing summary: {str(e)}",
                                  severity=hou.severityType.Error)


def create_lops_asset_builder_workflow():
    """
    Main entry point for the LOPS Asset Builder Workflow.
    Creates and runs the step-by-step workflow for multiple asset importing.
    """
    try:
        workflow = LopsAssetBuilderWorkflow()
        return workflow.create_workflow()
    except Exception as e:
        hou.ui.displayMessage(f"Error in LOPS Asset Builder Workflow: {str(e)}",
                              severity=hou.severityType.Error)
        return None


# For backwards compatibility and easy access
def main():
    """Alternative entry point."""
    return create_lops_asset_builder_workflow()


if __name__ == "__main__":
    create_lops_asset_builder_workflow()