import hou
import os


class BatchImportWorkflow:
    """
    Creates a streamlined iterative workflow for batch importing multiple asset groups.
    Each asset group gets its own subnetwork with unique naming and parameter prefixing
    to avoid cross-talk between groups. All subnetworks are connected to a final merge node.
    """

    def __init__(self):
        self.geo_node = None
        self.asset_groups = []  # List of asset group data
        self.group_counter = 0
        self.merge_node = None  # Merge node to connect all subnetworks

    def create_workflow(self):
        """
        Creates the streamlined iterative batch import workflow:
        1. Ask for GEO node name
        2. Create the main GEO node
        3. Iteratively import asset groups until user says "No"
        4. Create one subnetwork per asset group with unique naming
        5. Create merge node and connect all subnetworks
        6. Show final summary only
        """
        # Step 1: Ask for GEO node name
        geo_node_name = self._get_geo_node_name()

        # Step 2: Create the main Geo node with user-specified name
        self._create_geo_node(geo_node_name)

        # Step 3: Iteratively import asset groups
        self._import_asset_groups_iteratively()

        # Step 4: Create merge node and connect all subnetworks
        if self.asset_groups:
            self._create_merge_node()

        # Step 5: Layout all nodes
        self.geo_node.layoutChildren()
        for group_data in self.asset_groups:
            if group_data['subnet']:
                group_data['subnet'].layoutChildren()

        # Step 6: Show final summary (optional)
        self._show_final_summary()

        return self.geo_node

    def _get_geo_node_name(self):
        """Ask user for the GEO node name."""
        try:
            geo_name = hou.ui.readInput(
                "Enter name for the top-level GEO node:",
                initial_contents="batch_import_workflow",
                title="Batch Import Workflow - GEO Node Name"
            )
            if geo_name[0] == 0:  # User clicked OK
                return geo_name[1].strip() or "batch_import_workflow"
            else:  # User cancelled
                return "batch_import_workflow"
        except:
            return "batch_import_workflow"

    def _create_geo_node(self, node_name):
        """Create the main Geo node with specified name."""
        obj = hou.node('/obj')
        self.geo_node = obj.createNode('geo', node_name=node_name)

        # Remove default file node
        for child in self.geo_node.children():
            child.destroy()

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

            # Ask if user wants to add another group (no extra pop-ups otherwise)
            if not self._ask_for_another_group():
                break

    def _import_single_asset_group(self):
        """Import assets for a single asset group."""
        try:
            default_directory = hou.text.expandString('$HIP')
            select_directory = hou.ui.selectFile(
                start_directory=default_directory,
                title=f"Select files for Asset Group {self.group_counter}",
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
            # Suppress error dialogs, just return empty list
            return []

    def _get_asset_group_name(self, asset_paths):
        """
        Get group name - either auto-generated from first file's basename
        or user-supplied name.
        """
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
        """Ask once whether the user wants to add another group."""
        try:
            result = hou.ui.displayMessage(
                "Do you want to add another asset group?",
                buttons=("Yes", "No"),
                severity=hou.severityType.Message,
                title="Continue Import?"
            )
            return result == 0  # 0 = Yes, 1 = No
        except:
            return False  # Default to No if there's an error

    def _create_asset_group_subnetwork(self, group_name, asset_paths):
        """
        Create a subnetwork for an asset group with unique naming and parameter prefixing.

        Args:
            group_name (str): Name for the asset group
            asset_paths (list): List of asset file paths

        Returns:
            hou.Node: The created subnet node
        """
        # Create subnet with unique name
        subnet_name = f"{group_name}_group"
        subnet = self.geo_node.createNode('subnet', node_name=subnet_name)

        # Create internal network structure
        file_nodes = []
        num_assets = len(asset_paths)

        # Create file nodes
        for i, asset_path in enumerate(asset_paths):
            file_node = subnet.createNode("file", f"file_{i+1}")

            # Link to parameter with group prefix to avoid cross-talk
            param_name = f"{group_name}_asset_{i+1}"
            file_node.parm("file").setExpression(f'chs("../{param_name}")')

            # Position nodes
            spacing = max(2, 20 // num_assets) if num_assets > 0 else 2
            file_node.setPosition([i * spacing, 0])
            file_nodes.append(file_node)

        # Create switch node
        switch_node = subnet.createNode("switch", f"{group_name}_switch")

        # Connect file nodes to switch
        for i, file_node in enumerate(file_nodes):
            switch_node.setInput(i, file_node)

        # Position switch node
        switch_x_pos = (num_assets - 1) * spacing + 4 if num_assets > 0 else 10
        switch_node.setPosition([switch_x_pos, -2])

        # Create transform node
        transform_node = subnet.createNode("xform", f"{group_name}_transform")
        transform_node.setInput(0, switch_node)
        transform_node.setPosition([switch_x_pos, -4])

        # Create output node
        output_node = subnet.createNode("output", "OUTPUT")
        output_node.setInput(0, transform_node)
        output_node.setPosition([switch_x_pos, -6])

        # Set display and render flags
        output_node.setDisplayFlag(True)
        output_node.setRenderFlag(True)

        # Create parameters with group prefixing
        self._create_group_parameters(subnet, group_name, asset_paths, switch_node, transform_node)

        return subnet

    def _create_group_parameters(self, subnet, group_name, asset_paths, switch_node, transform_node):
        """
        Create parameters for an asset group with proper prefixing to avoid cross-talk.

        Args:
            subnet (hou.Node): The subnet node
            group_name (str): Name of the asset group
            asset_paths (list): List of asset file paths
            switch_node (hou.Node): The switch node
            transform_node (hou.Node): The transform node
        """
        ptg = subnet.parmTemplateGroup()

        # Add separator
        separator = hou.SeparatorParmTemplate(f"{group_name}_sep", f"{group_name} Settings")
        ptg.append(separator)

        # Add asset switch parameter with group prefix
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

        # Add transform parameters with group prefix
        transform_folder = hou.FolderParmTemplate(f"{group_name}_transform", f"{group_name} Transform", folder_type=hou.folderType.Tabs)

        # Translation vector parameter
        translate = hou.FloatParmTemplate(f"{group_name}_t", "Translate", 3, default_value=(0, 0, 0))

        # Rotation vector parameter  
        rotate = hou.FloatParmTemplate(f"{group_name}_r", "Rotate", 3, default_value=(0, 0, 0))

        # Scale vector parameter
        scale = hou.FloatParmTemplate(f"{group_name}_s", "Scale", 3, default_value=(1, 1, 1))

        transform_folder.addParmTemplate(translate)
        transform_folder.addParmTemplate(rotate)
        transform_folder.addParmTemplate(scale)

        ptg.append(transform_folder)

        # Add asset information folder with group prefix
        if asset_paths:
            info_folder = hou.FolderParmTemplate(f"{group_name}_info", f"{group_name} Assets", folder_type=hou.folderType.Tabs)

            for i, asset_path in enumerate(asset_paths):
                asset_info = hou.StringParmTemplate(
                    f"{group_name}_asset_{i+1}",
                    f"Asset {i+1}",
                    1,
                    default_value=(asset_path,),
                    string_type=hou.stringParmType.FileReference,
                    file_type=hou.fileType.Geometry,
                    help=f"Path to asset {i+1} in {group_name}"
                )
                info_folder.addParmTemplate(asset_info)

            ptg.append(info_folder)

        # Apply parameters to subnet
        subnet.setParmTemplateGroup(ptg)

        # Link nodes to parameters with group prefixing
        self._link_group_nodes_to_parameters(subnet, group_name, switch_node, transform_node)

    def _link_group_nodes_to_parameters(self, subnet, group_name, switch_node, transform_node):
        """Link nodes to parameters with group prefixing."""
        # Link switch node
        if switch_node:
            switch_node.parm("input").setExpression(f'ch("../{group_name}_switch")')

        # Link transform node using vector parameters with group prefix
        if transform_node:
            transform_mappings = [
                ("t", f"{group_name}_t"),
                ("r", f"{group_name}_r"),
                ("s", f"{group_name}_s")
            ]

            for xform_base, subnet_param in transform_mappings:
                subnet_tuple = subnet.parmTuple(subnet_param)

                # Link each component
                xform_components = ["x", "y", "z"]
                for i, component in enumerate(xform_components):
                    xform_param = f"{xform_base}{component}"
                    subnet_param_name = f"{subnet_param}{component}"
                    transform_node.parm(xform_param).setExpression(f'ch("../{subnet_param_name}")')

    def _create_merge_node(self):
        """
        Create a merge node and connect all asset group subnetworks to it.
        This allows all subnetworks to be combined into a single output.
        """
        if not self.asset_groups:
            return

        # Create merge node
        self.merge_node = self.geo_node.createNode('merge', 'asset_groups_merge')

        # Connect each subnetwork to the merge node
        for i, group_data in enumerate(self.asset_groups):
            subnet = group_data['subnet']
            if subnet:
                self.merge_node.setInput(i, subnet)

        # Position merge node below all subnetworks
        # Calculate position based on number of groups
        num_groups = len(self.asset_groups)
        merge_x_pos = (num_groups - 1) * 4  # Spread based on number of groups
        merge_y_pos = -2  # Position below subnetworks
        self.merge_node.setPosition([merge_x_pos, merge_y_pos])

        # Set display and render flags on merge node
        self.merge_node.setDisplayFlag(True)
        self.merge_node.setRenderFlag(True)

    def _show_final_summary(self):
        """Show a single final success summary (optional)."""
        if not self.asset_groups:
            return

        summary_lines = [
            f"Batch Import Workflow completed successfully!",
            f"",
            f"GEO Node: {self.geo_node.path()}",
            f"Total Asset Groups: {len(self.asset_groups)}",
            f"Merge Node: {self.merge_node.path() if self.merge_node else 'None'}",
            f""
        ]

        for i, group_data in enumerate(self.asset_groups, 1):
            summary_lines.extend([
                f"Group {i}: {group_data['name']}",
                f"  Subnet: {group_data['subnet'].path()}",
                f"  Assets: {len(group_data['asset_paths'])} files",
                f""
            ])

        summary_lines.extend([
            f"Instructions:",
            f"• Each asset group has its own subnetwork with unique parameters",
            f"• Use the switch parameter to change between assets within each group",
            f"• Use transform parameters to position/scale each group independently",
            f"• Parameters are prefixed by group name to avoid conflicts",
            f"• All asset groups are merged together in the final merge node"
        ])

        hou.ui.displayMessage(
            "\n".join(summary_lines),
            title="Batch Import Workflow - Complete"
        )






def create_batch_import_workflow():
    """
    Main function to create the streamlined iterative batch import workflow.
    This creates a tool that lets the artist:
    - Name the top-level GEO node when the tool starts
    - Iteratively import any number of "asset groups"
    - Ask once whether to add another group after each batch
    - Stop when they answer "No"
    - Create one subnetwork per asset group with unique naming
    - Use parameter prefixing to avoid cross-talk between groups
    - Suppress intermediate dialogs, show only final summary
    """
    workflow = BatchImportWorkflow()
    geo_node = workflow.create_workflow()
    return geo_node


if __name__ == "__main__":
    create_batch_import_workflow()
