import hou
import os


class BatchImportWorkflow:
    """
    Creates a workflow with a Geo node containing a subnetwork for batch importing assets.
    The subnetwork includes UI controls for asset paths, file nodes, switch node, and transform node.
    """

    def __init__(self):
        self.geo_node = None
        self.subnet = None
        self.file_nodes = []
        self.switch_node = None
        self.transform_node = None
        self.output_node = None

    def create_workflow(self):
        """
        Creates the complete batch import workflow with the new refactored approach:
        1. First import assets and get their paths
        2. Generate the subnetwork structure based on actual assets
        3. Then populate parent parameters based on the generated subnetwork
        """
        # Create the main Geo node
        self._create_geo_node()

        # Step 1: First import assets and get their paths
        asset_paths = self._import_assets()

        # Step 2: Generate the subnetwork structure based on actual assets
        self._generate_subnetwork_from_assets(asset_paths)

        # Step 3: Populate parent parameters based on the generated subnetwork
        self._populate_parent_parameters(asset_paths)

        # Layout nodes
        self.geo_node.layoutChildren()
        self.subnet.layoutChildren()

        return self.geo_node

    def _create_geo_node(self):
        """Create the main Geo node."""
        obj = hou.node('/obj')
        self.geo_node = obj.createNode('geo', node_name='batch_import_workflow')

        # Remove default file node
        for child in self.geo_node.children():
            child.destroy()

    def _import_assets(self):
        """
        Step 1: Import assets and get their paths from user selection.
        This is the first step in the refactored workflow.

        Returns:
            list: List of selected asset file paths from batch importer
        """
        try:
            # Get file selection from user using the same logic as batch_importer
            default_directory = hou.text.expandString('$HIP')
            select_directory = hou.ui.selectFile(
                start_directory=default_directory,
                title="Select the files you want to import for the workflow",
                file_type=hou.fileType.Geometry,
                multiple_select=True
            )

            if select_directory:
                # Split the selected files and return as list
                files_name = select_directory.split(';')
                # Strip whitespace and return up to 10 files (max supported)
                asset_paths = [file_path.strip() for file_path in files_name[:10]]

                hou.ui.displayMessage(
                    f"Selected {len(asset_paths)} asset files for the workflow",
                    title="Batch Import Workflow - Step 1: Assets Imported"
                )

                return asset_paths
            else:
                # User cancelled selection - provide default empty workflow
                hou.ui.displayMessage(
                    "No files selected. Creating empty workflow template.",
                    severity=hou.severityType.Message,
                    title="Batch Import Workflow"
                )
                return []

        except Exception as e:
            hou.ui.displayMessage(
                f"Error during file selection: {str(e)}",
                severity=hou.severityType.Error,
                title="Batch Import Workflow"
            )
            return []

    def _generate_subnetwork_from_assets(self, asset_paths):
        """
        Step 2: Generate the subnetwork structure based on actual assets.
        This creates the subnetwork and builds the internal network directly with asset paths.

        Args:
            asset_paths (list): List of asset file paths from step 1
        """
        # Create the subnetwork
        self.subnet = self.geo_node.createNode('subnet', node_name='asset_importer')

        # If no assets were selected, create a minimal template
        if not asset_paths:
            hou.ui.displayMessage(
                "No assets selected. Creating minimal template structure.",
                title="Batch Import Workflow - Step 2: Subnetwork Generated"
            )
            self._create_minimal_template()
            return

        # Create file nodes directly with asset paths (no parameter expressions)
        self.file_nodes = []
        num_assets = len(asset_paths)

        for i, asset_path in enumerate(asset_paths):
            file_node = self.subnet.createNode("file", f"file_{i+1}")

            # Set the file path directly - no expressions, no parameter references
            file_node.parm("file").set(asset_path)

            # Position nodes with proper spacing
            spacing = max(2, 20 // num_assets) if num_assets > 0 else 2
            file_node.setPosition([i * spacing, 0])
            self.file_nodes.append(file_node)

        # Create switch node
        self.switch_node = self.subnet.createNode("switch", "asset_switch_node")

        # Connect all file nodes to switch node
        for i, file_node in enumerate(self.file_nodes):
            self.switch_node.setInput(i, file_node)

        # Position switch node
        switch_x_pos = (num_assets - 1) * spacing + 4 if num_assets > 0 else 10
        self.switch_node.setPosition([switch_x_pos, -2])

        # Create transform node
        self.transform_node = self.subnet.createNode("xform", "transform_node")
        self.transform_node.setInput(0, self.switch_node)
        self.transform_node.setPosition([switch_x_pos, -4])

        # Create output node
        self.output_node = self.subnet.createNode("output", "OUTPUT")
        self.output_node.setInput(0, self.transform_node)
        self.output_node.setPosition([switch_x_pos, -6])

        # Set display and render flags on output
        self.output_node.setDisplayFlag(True)
        self.output_node.setRenderFlag(True)

        hou.ui.displayMessage(
            f"Generated subnetwork with {num_assets} file nodes, switch, transform, and output.",
            title="Batch Import Workflow - Step 2: Subnetwork Generated"
        )

    def _create_minimal_template(self):
        """Create a minimal template structure when no assets are selected."""
        # Create a single file node as template
        file_node = self.subnet.createNode("file", "file_template")
        file_node.setPosition([0, 0])
        self.file_nodes = [file_node]

        # Create switch node
        self.switch_node = self.subnet.createNode("switch", "asset_switch_node")
        self.switch_node.setInput(0, file_node)
        self.switch_node.setPosition([4, -2])

        # Create transform node
        self.transform_node = self.subnet.createNode("xform", "transform_node")
        self.transform_node.setInput(0, self.switch_node)
        self.transform_node.setPosition([4, -4])

        # Create output node
        self.output_node = self.subnet.createNode("output", "OUTPUT")
        self.output_node.setInput(0, self.transform_node)
        self.output_node.setPosition([4, -6])

        # Set display and render flags on output
        self.output_node.setDisplayFlag(True)
        self.output_node.setRenderFlag(True)

    def _populate_parent_parameters(self, asset_paths):
        """
        Step 3: Populate parent parameters based on the generated subnetwork.
        This creates parameters on both the subnet and parent geo node to control the workflow.

        Args:
            asset_paths (list): List of asset file paths from step 1
        """
        # First, create subnet parameters based on what was actually generated
        self._create_subnet_parameters(asset_paths)

        # Then, create parent geo node parameters and link them to subnet
        self._create_parent_parameters(asset_paths)

        # Finally, link the subnet nodes to the parameters
        self._link_nodes_to_parameters(asset_paths)

        hou.ui.displayMessage(
            f"Populated parameters for {len(asset_paths)} assets with proper channel linking.",
            title="Batch Import Workflow - Step 3: Parameters Populated"
        )

    def _create_subnet_parameters(self, asset_paths):
        """Create parameters on the subnet based on actual generated content."""
        ptg = self.subnet.parmTemplateGroup()

        # Add separator
        separator = hou.SeparatorParmTemplate("sep1", "Asset Import Settings")
        ptg.append(separator)

        # Add asset switch parameter based on actual number of assets
        num_assets = len(asset_paths) if asset_paths else 1
        switch_parm = hou.IntParmTemplate(
            "asset_switch",
            "Asset Switch",
            1,
            default_value=(0,),
            min=0,
            max=max(0, num_assets - 1),
            help=f"Switch between {num_assets} imported assets"
        )
        ptg.append(switch_parm)

        # Add transform parameters
        transform_folder = hou.FolderParmTemplate("transform", "Transform", folder_type=hou.folderType.Tabs)

        # Translation parameters
        tx = hou.FloatParmTemplate("tx", "Translate X", 1, default_value=(0,))
        ty = hou.FloatParmTemplate("ty", "Translate Y", 1, default_value=(0,))
        tz = hou.FloatParmTemplate("tz", "Translate Z", 1, default_value=(0,))

        # Rotation parameters
        rx = hou.FloatParmTemplate("rx", "Rotate X", 1, default_value=(0,))
        ry = hou.FloatParmTemplate("ry", "Rotate Y", 1, default_value=(0,))
        rz = hou.FloatParmTemplate("rz", "Rotate Z", 1, default_value=(0,))

        # Scale parameters
        sx = hou.FloatParmTemplate("sx", "Scale X", 1, default_value=(1,))
        sy = hou.FloatParmTemplate("sy", "Scale Y", 1, default_value=(1,))
        sz = hou.FloatParmTemplate("sz", "Scale Z", 1, default_value=(1,))

        transform_folder.addParmTemplate(tx)
        transform_folder.addParmTemplate(ty)
        transform_folder.addParmTemplate(tz)
        transform_folder.addParmTemplate(rx)
        transform_folder.addParmTemplate(ry)
        transform_folder.addParmTemplate(rz)
        transform_folder.addParmTemplate(sx)
        transform_folder.addParmTemplate(sy)
        transform_folder.addParmTemplate(sz)

        ptg.append(transform_folder)

        # Add asset information folder (read-only info about imported assets)
        if asset_paths:
            info_folder = hou.FolderParmTemplate("asset_info", "Asset Information", folder_type=hou.folderType.Tabs)

            for i, asset_path in enumerate(asset_paths):
                asset_info = hou.StringParmTemplate(
                    f"asset_info_{i+1}",
                    f"Asset {i+1} Path",
                    1,
                    default_value=(asset_path,),
                    string_type=hou.stringParmType.Regular,
                    help=f"Path to imported asset {i+1}"
                )
                asset_info.setDisableWhen("{ 1 == 1 }")  # Always disabled (read-only)
                info_folder.addParmTemplate(asset_info)

            ptg.append(info_folder)

        self.subnet.setParmTemplateGroup(ptg)

    def _create_parent_parameters(self, asset_paths):
        """Create parameters on the parent geo node and link them to subnet."""
        parent_ptg = self.geo_node.parmTemplateGroup()

        # Add separator for exported parameters
        separator = hou.SeparatorParmTemplate("exported_controls", "Asset Controls")
        parent_ptg.append(separator)

        # Export asset switch parameter
        num_assets = len(asset_paths) if asset_paths else 1
        switch_parm = hou.IntParmTemplate(
            "asset_switch_control",
            "Asset Switch",
            1,
            default_value=(0,),
            min=0,
            max=max(0, num_assets - 1),
            help=f"Switch between {num_assets} imported assets"
        )
        parent_ptg.append(switch_parm)

        # Export transform parameters in a folder
        transform_folder = hou.FolderParmTemplate("asset_transform", "Asset Transform", folder_type=hou.folderType.Tabs)

        # Translation parameters
        tx = hou.FloatParmTemplate("asset_tx", "Translate X", 1, default_value=(0,))
        ty = hou.FloatParmTemplate("asset_ty", "Translate Y", 1, default_value=(0,))
        tz = hou.FloatParmTemplate("asset_tz", "Translate Z", 1, default_value=(0,))

        # Rotation parameters
        rx = hou.FloatParmTemplate("asset_rx", "Rotate X", 1, default_value=(0,))
        ry = hou.FloatParmTemplate("asset_ry", "Rotate Y", 1, default_value=(0,))
        rz = hou.FloatParmTemplate("asset_rz", "Rotate Z", 1, default_value=(0,))

        # Scale parameters
        sx = hou.FloatParmTemplate("asset_sx", "Scale X", 1, default_value=(1,))
        sy = hou.FloatParmTemplate("asset_sy", "Scale Y", 1, default_value=(1,))
        sz = hou.FloatParmTemplate("asset_sz", "Scale Z", 1, default_value=(1,))

        transform_folder.addParmTemplate(tx)
        transform_folder.addParmTemplate(ty)
        transform_folder.addParmTemplate(tz)
        transform_folder.addParmTemplate(rx)
        transform_folder.addParmTemplate(ry)
        transform_folder.addParmTemplate(rz)
        transform_folder.addParmTemplate(sx)
        transform_folder.addParmTemplate(sy)
        transform_folder.addParmTemplate(sz)

        parent_ptg.append(transform_folder)

        # Apply the parameter template group to the parent geo node
        self.geo_node.setParmTemplateGroup(parent_ptg)

    def _link_nodes_to_parameters(self, asset_paths):
        """Link the generated nodes to the parameters for proper control."""
        # Link subnet parameters to parent parameters
        self.subnet.parm("asset_switch").setExpression('ch("../asset_switch_control")')

        # Link transform parameters
        transform_params = [
            ("tx", "asset_tx"),
            ("ty", "asset_ty"), 
            ("tz", "asset_tz"),
            ("rx", "asset_rx"),
            ("ry", "asset_ry"),
            ("rz", "asset_rz"),
            ("sx", "asset_sx"),
            ("sy", "asset_sy"),
            ("sz", "asset_sz")
        ]

        for subnet_param, parent_param in transform_params:
            self.subnet.parm(subnet_param).setExpression(f'ch("../{parent_param}")')

        # Link switch node to subnet parameter
        if self.switch_node:
            self.switch_node.parm("input").setExpression('ch("../asset_switch")')

        # Link transform node to subnet parameters
        if self.transform_node:
            for param_name, subnet_param in transform_params:
                self.transform_node.parm(param_name).setExpression(f'ch("../{param_name}")')

    # OLD METHODS - No longer used in refactored workflow
    # These methods have been replaced by the new 3-step approach:
    # 1. _import_assets() 
    # 2. _generate_subnetwork_from_assets()
    # 3. _populate_parent_parameters()

    # These old methods are replaced by the new _populate_parent_parameters() approach
    # which creates parameters based on actual generated content rather than templates


def create_batch_import_workflow():
    """
    Main function to create the batch import workflow.
    This is the function that should be called to create the complete workflow.
    """
    workflow = BatchImportWorkflow()
    geo_node = workflow.create_workflow()

    hou.ui.displayMessage(
        f"Batch Import Workflow created successfully!\n\n"
        f"Geo Node: {geo_node.path()}\n"
        f"Subnetwork: {workflow.subnet.path()}\n\n"
        f"Instructions:\n"
        f"1. Click 'Run Batch Importer' to select files\n"
        f"2. Adjust 'Number of Asset Paths' if needed\n"
        f"3. Use 'Asset Switch' to change between assets\n"
        f"4. Use Transform parameters to position/scale\n"
        f"5. The output is connected to the OUTPUT node",
        title="Workflow Created"
    )

    return geo_node


if __name__ == "__main__":
    create_batch_import_workflow()
