import hou
import os


class LopsGroupImporter:
    """
    Creates a streamlined iterative workflow for batch importing multiple asset groups in LOPS context.
    Each asset group gets its own subnetwork with unique naming and parameter prefixing
    to avoid cross-talk between groups. All subnetworks are connected to a final merge node.
    Supports material assignment and USD workflow.
    """

    def __init__(self):
        self.stage_node = None
        self.asset_groups = []  # List of asset group data
        self.group_counter = 0
        self.merge_node = None  # Merge node to connect all subnetworks
        self.material_library = None  # Global material library

    def create_workflow(self):
        """
        Creates the streamlined iterative LOPS batch import workflow:
        1. Ask for Stage node name
        2. Create the main Stage context
        3. Create global material library
        4. Iteratively import asset groups until user says "No"
        5. Create one subnetwork per asset group with unique naming
        6. Create merge node and connect all subnetworks
        7. Show final summary
        """
        # Step 1: Ask for Stage node name
        stage_node_name = self._get_stage_node_name()

        # Step 2: Create the main Stage context
        self._create_stage_context(stage_node_name)

        # Step 3: Create global material library
        self._create_material_library()

        # Step 4: Iteratively import asset groups
        self._import_asset_groups_iteratively()

        # Step 5: Create merge node and connect all subnetworks
        if self.asset_groups:
            self._create_merge_node()

        # Step 6: Layout all nodes
        self._layout_nodes()

        # Step 7: Show final summary
        self._show_final_summary()

        return self.stage_node

    def _get_stage_node_name(self):
        """Ask user for the Stage node name."""
        try:
            stage_name = hou.ui.readInput(
                "Enter name for the top-level LOPS Stage node:",
                initial_contents="lops_group_importer",
                title="LOPS Group Importer - Stage Node Name"
            )
            if stage_name[0] == 0:  # User clicked OK
                return stage_name[1].strip() or "lops_group_importer"
            else:  # User cancelled
                return "lops_group_importer"
        except:
            return "lops_group_importer"

    def _create_stage_context(self, node_name):
        """Create the main Stage context."""
        stage_context = hou.node('/stage')
        self.stage_node = stage_context.createNode('subnet', node_name=node_name)

    def _create_material_library(self):
        """Create a global material library for all asset groups."""
        self.material_library = self.stage_node.createNode(
            'materiallibrary', 
            node_name='global_materials'
        )
        self.material_library.parm('matpathprefix').set('/ASSET/mtl/')

    def _import_asset_groups_iteratively(self):
        """
        Iteratively import asset groups until user says "No".
        Each iteration creates a new asset group with its own subnetwork.
        """
        while True:
            self.group_counter += 1

            # Import assets for this group
            asset_paths = self._import_single_asset_group()

            if not asset_paths:
                # User cancelled or no files selected, break the loop
                self.group_counter -= 1
                break

            # Get or generate group name
            group_name = self._get_asset_group_name(asset_paths)

            # Create subnetwork for this group
            subnet = self._create_asset_group_subnetwork(group_name, asset_paths)

            # Store group data
            group_data = {
                'name': group_name,
                'asset_paths': asset_paths,
                'subnet': subnet,
                'group_id': self.group_counter
            }
            self.asset_groups.append(group_data)

            # Ask if user wants to add another group
            if not self._ask_for_another_group():
                break

    def _import_single_asset_group(self):
        """Import assets for a single asset group."""
        try:
            default_directory = hou.text.expandString('$HIP')
            select_directory = hou.ui.selectFile(
                start_directory=default_directory,
                title=f"Select USD/Geometry files for Asset Group {self.group_counter}",
                file_type=hou.fileType.Geometry,
                multiple_select=True
            )

            if select_directory:
                files_name = select_directory.split(';')
                asset_paths = [file_path.strip() for file_path in files_name[:10]]
                return asset_paths
            else:
                return []

        except Exception as e:
            return []

    def _get_asset_group_name(self, asset_paths):
        """Get group name - either auto-generated or user-supplied."""
        # Auto-generate name from first file's basename
        if asset_paths:
            first_file = asset_paths[0]
            auto_name = os.path.splitext(os.path.basename(first_file))[0]
        else:
            auto_name = f"group_{self.group_counter}"

        try:
            user_input = hou.ui.readInput(
                f"Enter name for Asset Group {self.group_counter}:",
                initial_contents=auto_name,
                title="Asset Group Name"
            )
            if user_input[0] == 0:  # User clicked OK
                return user_input[1].strip() or auto_name
            else:  # User cancelled
                return auto_name
        except:
            return auto_name

    def _ask_for_another_group(self):
        """Ask whether the user wants to add another group."""
        try:
            result = hou.ui.displayMessage(
                "Do you want to add another asset group?",
                buttons=("Yes", "No"),
                severity=hou.severityType.Message,
                title="Continue Import?"
            )
            return result == 0  # 0 = Yes, 1 = No
        except:
            return False

    def _create_asset_group_subnetwork(self, group_name, asset_paths):
        """
        Create a LOPS subnetwork for an asset group using componentgeometry with sopnet workflow.
        Adapted from lops_asset_builder for compatibility with all nodes.
        """
        # Create subnet with unique name
        subnet_name = f"{group_name}_group"
        subnet = self.stage_node.createNode('subnet', node_name=subnet_name)

        # Create componentgeometry nodes for each asset (adapted from lops_asset_builder)
        component_nodes = []
        num_assets = len(asset_paths)

        for i, asset_path in enumerate(asset_paths):
            # Create componentgeometry node for each asset
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]
            comp_geo = subnet.createNode("componentgeometry", f"{asset_name}_geo_{i+1}")
            comp_geo.parm("geovariantname").set(f"{asset_name}_{i+1}")

            # Prepare the imported asset using sopnet workflow
            self._prepare_imported_asset_sopnet(comp_geo, asset_path, group_name, i+1)

            # Position nodes
            spacing = max(4, 40 // num_assets) if num_assets > 0 else 4
            comp_geo.setPosition([i * spacing, 0])
            component_nodes.append(comp_geo)

        # Create switch node to select between assets
        switch_node = subnet.createNode("switch", f"{group_name}_switch")

        # Connect component nodes to switch
        for i, comp_node in enumerate(component_nodes):
            switch_node.setInput(i, comp_node)

        # Position switch node
        switch_x_pos = (num_assets - 1) * spacing + 4 if num_assets > 0 else 10
        switch_node.setPosition([switch_x_pos, -3])

        # Create transform node for positioning
        transform_node = subnet.createNode("xform", f"{group_name}_transform")
        transform_node.setInput(0, switch_node)
        transform_node.setPosition([switch_x_pos, -6])

        # Create material assignment node
        material_assign = subnet.createNode("assignmaterial", f"{group_name}_materials")
        material_assign.setInput(0, transform_node)
        material_assign.setInput(1, self.material_library)
        material_assign.setPosition([switch_x_pos, -9])

        # Create output node
        output_node = subnet.createNode("output", "OUTPUT")
        output_node.setInput(0, material_assign)
        output_node.setPosition([switch_x_pos, -12])

        # Set display and render flags
        output_node.setDisplayFlag(True)
        output_node.setRenderFlag(True)

        # Create parameters with group prefixing
        self._create_group_parameters(subnet, group_name, asset_paths, switch_node, transform_node, material_assign)

        return subnet

    def _prepare_imported_asset_sopnet(self, comp_geo, asset_path, group_name, asset_index):
        """
        Prepare imported asset using sopnet workflow adapted from lops_asset_builder.
        Creates the internal sopnet structure for asset processing.
        """
        try:
            # Get the sopnet/geo path within the componentgeometry node
            sopnet_geo = hou.node(comp_geo.path() + "/sopnet/geo")
            if not sopnet_geo:
                return

            # Get the output nodes - default, proxy and sim
            default_output = hou.node(f"{sopnet_geo.path()}/default")
            proxy_output = hou.node(f"{sopnet_geo.path()}/proxy")
            sim_output = hou.node(f"{sopnet_geo.path()}/simproxy")

            # Get asset info
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]
            asset_extension = os.path.splitext(asset_path)[1][1:]  # Remove the dot

            # Handle special case for bgeo.sc files
            if asset_path.endswith("bgeo.sc"):
                asset_name = os.path.splitext(os.path.splitext(asset_path)[0])[0]
                asset_extension = "bgeo.sc"

            # Create the file import node based on extension
            file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
            if asset_extension in file_extension:
                file_import = sopnet_geo.createNode("file", f"import_{asset_name}")
                parm_name = "file"
            elif asset_extension == "abc":
                file_import = sopnet_geo.createNode("alembic", f"import_{asset_name}")
                parm_name = "filename"
            else:
                # For unsupported extensions, create a file node anyway
                file_import = sopnet_geo.createNode("file", f"import_{asset_name}")
                parm_name = "file"

            # Set the file path
            file_import.parm(parm_name).set(asset_path)

            # Create main processing nodes (adapted from lops_asset_builder)
            match_size = sopnet_geo.createNode("matchsize", f"matchsize_{asset_name}")
            attrib_wrangler = sopnet_geo.createNode("attribwrangle", "convert_mat_to_name")
            attrib_delete = sopnet_geo.createNode("attribdelete", "keep_P_N_UV_NAME")
            remove_points = sopnet_geo.createNode("add", f"remove_points")

            # Set parameters for main nodes
            match_size.setParms({
                "justify_x": 0,
                "justify_y": 1,
                "justify_z": 0,
            })

            attrib_wrangler.setParms({
                "class": 1,
                "snippet": 's@shop_materialpath = replace(s@shop_materialpath, " ", "_");\nstring material_to_name[] = split(s@shop_materialpath,"/");\ns@name=material_to_name[-1];'

            })

            attrib_delete.setParms({
                "negate": True,
                "ptdel": "N P",
                "vtxdel": "uv",
                "primdel": "name"
            })

            remove_points.parm("remove").set(True)

            # Connect main nodes
            match_size.setInput(0, file_import)
            attrib_wrangler.setInput(0, match_size)
            attrib_delete.setInput(0, attrib_wrangler)
            remove_points.setInput(0, attrib_delete)
            default_output.setInput(0, remove_points)

            # Create proxy setup (simplified version from lops_asset_builder)
            poly_reduce = sopnet_geo.createNode("polyreduce::2.0", "reduce_to_5")
            attrib_colour = sopnet_geo.createNode("attribwrangle", "set_color")
            color_node = sopnet_geo.createNode("color", "unique_color")
            attrib_promote = sopnet_geo.createNode("attribpromote", "promote_Cd")
            attrib_delete_name = sopnet_geo.createNode("attribdelete", f"delete_asset_name")
            name_node = sopnet_geo.createNode("name", "name")

            # Set parameters for proxy setup
            poly_reduce.parm("percentage").set(5)
            attrib_colour.parm("class").set(1)

            # Create custom parameter for asset name
            ptg = attrib_colour.parmTemplateGroup()
            new_string = hou.StringParmTemplate(
                name="asset_name",
                label="Asset name",
                num_components=1,
            )
            ptg.insertAfter("class", new_string)
            attrib_colour.setParmTemplateGroup(ptg)

            # Set asset name and snippet
            attrib_colour.setParms({
                "asset_name": f"{group_name}_{asset_name}_{asset_index}",
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
            name_node.parm("name1").set(f"{group_name}_{asset_name}_{asset_index}")

            # Connect proxy nodes
            poly_reduce.setInput(0, remove_points)
            attrib_colour.setInput(0, poly_reduce)
            color_node.setInput(0, attrib_colour)
            attrib_promote.setInput(0, color_node)
            attrib_delete_name.setInput(0, attrib_promote)
            proxy_output.setInput(0, attrib_delete_name)

            # Create simple sim setup (without convex hull for simplicity)
            sim_name_node = sopnet_geo.createNode("name", "sim_name")
            sim_name_node.parm("name1").set(f"{group_name}_{asset_name}_{asset_index}")
            sim_name_node.setInput(0, remove_points)
            sim_output.setInput(0, sim_name_node)

            # Layout nodes in sopnet
            sopnet_geo.layoutChildren()

        except Exception as e:
            hou.ui.displayMessage(f"Error preparing asset {asset_path}: {str(e)}",
                                  severity=hou.severityType.Warning)

    def _create_group_parameters(self, subnet, group_name, asset_paths, switch_node, transform_node, material_assign):
        """Create parameters for an asset group with LOPS-specific controls."""
        ptg = subnet.parmTemplateGroup()

        # Add separator
        separator = hou.SeparatorParmTemplate(f"{group_name}_sep", f"{group_name} Settings")
        ptg.append(separator)

        # Add asset switch parameter
        num_assets = len(asset_paths) if asset_paths else 1
        switch_parm = hou.IntParmTemplate(
            f"{group_name}_switch",
            f"{group_name} Switch",
            1,
            default_value=(0,),
            min=0,
            max=max(0, num_assets - 1),
            help=f"Switch between {num_assets} assets in {group_name}"
        )
        ptg.append(switch_parm)

        # Add transform parameters
        transform_folder = hou.FolderParmTemplate(f"{group_name}_transform", f"{group_name} Transform", folder_type=hou.folderType.Tabs)

        translate = hou.FloatParmTemplate(f"{group_name}_t", "Translate", 3, default_value=(0, 0, 0))
        rotate = hou.FloatParmTemplate(f"{group_name}_r", "Rotate", 3, default_value=(0, 0, 0))
        scale = hou.FloatParmTemplate(f"{group_name}_s", "Scale", 3, default_value=(1, 1, 1))

        transform_folder.addParmTemplate(translate)
        transform_folder.addParmTemplate(rotate)
        transform_folder.addParmTemplate(scale)
        ptg.append(transform_folder)

        # Add material parameters
        material_folder = hou.FolderParmTemplate(f"{group_name}_materials", f"{group_name} Materials", folder_type=hou.folderType.Tabs)

        # Material assignment toggle
        use_materials = hou.ToggleParmTemplate(f"{group_name}_use_materials", "Enable Materials", default_value=True)
        material_folder.addParmTemplate(use_materials)

        # Material path
        material_path = hou.StringParmTemplate(
            f"{group_name}_material_path",
            "Material Path",
            1,
            default_value=(f"/ASSET/mtl/{group_name}_material",),
            help="USD path to material for this group"
        )
        material_folder.addParmTemplate(material_path)

        ptg.append(material_folder)

        # Add asset information folder (read-only display of imported assets)
        if asset_paths:
            info_folder = hou.FolderParmTemplate(f"{group_name}_info", f"{group_name} Assets", folder_type=hou.folderType.Tabs)

            for i, asset_path in enumerate(asset_paths):
                asset_name = os.path.splitext(os.path.basename(asset_path))[0]
                # Display asset information (read-only)
                asset_info = hou.StringParmTemplate(
                    f"{group_name}_asset_{i+1}_info",
                    f"Asset {i+1}: {asset_name}",
                    1,
                    default_value=(asset_path,),
                    string_type=hou.stringParmType.FileReference,
                    file_type=hou.fileType.Geometry,
                    help=f"Path to asset {i+1} in {group_name} (processed via sopnet)"
                )
                # Make it read-only by disabling it
                asset_info.setDisableWhen("{ 1 }")
                info_folder.addParmTemplate(asset_info)

            ptg.append(info_folder)

        # Apply parameters to subnet
        subnet.setParmTemplateGroup(ptg)

        # Link nodes to parameters
        self._link_group_nodes_to_parameters(subnet, group_name, switch_node, transform_node, material_assign)

    def _link_group_nodes_to_parameters(self, subnet, group_name, switch_node, transform_node, material_assign):
        """Link LOPS nodes to parameters with group prefixing for componentgeometry workflow."""
        # Link switch node
        if switch_node:
            switch_node.parm("input").setExpression(f'ch("../{group_name}_switch")')

        # Link transform node
        if transform_node:
            transform_node.parm("tx").setExpression(f'ch("../{group_name}_tx")')
            transform_node.parm("ty").setExpression(f'ch("../{group_name}_ty")')
            transform_node.parm("tz").setExpression(f'ch("../{group_name}_tz")')
            transform_node.parm("rx").setExpression(f'ch("../{group_name}_rx")')
            transform_node.parm("ry").setExpression(f'ch("../{group_name}_ry")')
            transform_node.parm("rz").setExpression(f'ch("../{group_name}_rz")')
            transform_node.parm("sx").setExpression(f'ch("../{group_name}_sx")')
            transform_node.parm("sy").setExpression(f'ch("../{group_name}_sy")')
            transform_node.parm("sz").setExpression(f'ch("../{group_name}_sz")')

        # Link material assignment
        if material_assign:
            material_assign.parm("enable1").setExpression(f'ch("../{group_name}_use_materials")')
            material_assign.parm("matspecpath1").setExpression(f'chs("../{group_name}_material_path")')
            material_assign.parm("primpattern1").set("*")

        # Note: File paths are now handled directly in the sopnet nodes, no parameter linking needed

    def _create_merge_node(self):
        """Create merge node and connect all asset group subnetworks."""
        self.merge_node = self.stage_node.createNode('merge', node_name='merge_all_groups')

        # Connect all asset group subnets to merge node
        for i, group_data in enumerate(self.asset_groups):
            if group_data['subnet']:
                self.merge_node.setInput(i, group_data['subnet'])

        # Set display and render flags on merge node
        self.merge_node.setDisplayFlag(True)
        self.merge_node.setRenderFlag(True)

    def _layout_nodes(self):
        """Layout all nodes in the stage context."""
        # Layout main stage nodes
        main_nodes = [self.material_library]
        main_nodes.extend([group_data['subnet'] for group_data in self.asset_groups])
        if self.merge_node:
            main_nodes.append(self.merge_node)

        self.stage_node.layoutChildren(main_nodes)

        # Layout nodes within each subnet
        for group_data in self.asset_groups:
            if group_data['subnet']:
                group_data['subnet'].layoutChildren()

    def _show_final_summary(self):
        """Show final summary of imported asset groups."""
        if not self.asset_groups:
            hou.ui.displayMessage(
                "No asset groups were imported.",
                title="LOPS Group Importer - Summary"
            )
            return

        summary_lines = [
            f"LOPS Group Importer Summary:",
            f"Total Asset Groups: {len(self.asset_groups)}",
            ""
        ]

        for group_data in self.asset_groups:
            summary_lines.append(f"Group: {group_data['name']}")
            summary_lines.append(f"  Assets: {len(group_data['asset_paths'])}")
            for i, path in enumerate(group_data['asset_paths']):
                filename = os.path.basename(path)
                summary_lines.append(f"    {i+1}. {filename}")
            summary_lines.append("")

        summary_lines.append("All groups connected to merge node with material support.")
        summary_lines.append("Use group parameters to control visibility, transforms, and materials.")

        hou.ui.displayMessage(
            "\n".join(summary_lines),
            title="LOPS Group Importer - Summary"
        )


def create_lops_group_importer():
    """
    Main function to create the LOPS group importer workflow.
    This function can be called from Houdini's Python shell or assigned to a shelf tool.
    """
    try:
        importer = LopsGroupImporter()
        stage_node = importer.create_workflow()

        if stage_node:
            # Select the created stage node
            stage_node.setSelected(True, clear_all_selected=True)

        return stage_node

    except Exception as e:
        hou.ui.displayMessage(
            f"Error creating LOPS Group Importer: {str(e)}",
            severity=hou.severityType.Error,
            title="LOPS Group Importer Error"
        )
        return None


# For backwards compatibility and easy access
if __name__ == "__main__":
    create_lops_group_importer()
