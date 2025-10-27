"""
USD Reference Importer - Import scanned assets as USD references with spatial distribution

This module provides functionality to import multiple USD assets as references in a LOPS stage,
automatically distributing them spatially for better visualization.

Designed to work with the Asset Folder Scanner results.
"""

import hou
import os
from typing import Dict, List, Optional, Tuple
from modules.misc_utils import _sanitize


class USDReferenceImporter:
    """
    Imports USD assets as references in a LOPS stage with automatic spatial distribution.
    """

    def __init__(self, stage_context: Optional[hou.LopNode] = None):
        """
        Initialize the USD Reference Importer.

        Args:
            stage_context (hou.LopNode): Optional stage context node. If None, creates new stage.
        """
        self.stage_context = stage_context
        self.imported_refs = []

    def import_scanned_assets(
        self,
        scan_result: Dict,
        stage_name: str = "asset_references",
        spacing: float = 5.0,
        layout_type: str = "grid"
    ) -> hou.LopNode:
        """
        Import all geometry assets from scan results as USD references.

        Args:
            scan_result (dict): Result from AssetFolderScanner.scan_folder()
            stage_name (str): Name for the stage network
            spacing (float): Distance between assets in Houdini units
            layout_type (str): Layout type - "grid", "line", or "circular"

        Returns:
            hou.LopNode: The merge node containing all references
        """
        # Create stage if needed
        if self.stage_context is None:
            self.stage_context = self._create_stage_context(stage_name)

        # Get geometry files from scan result
        geo_files = scan_result.get('geometry_files', {})

        if not geo_files:
            hou.ui.displayMessage(
                "No geometry files found in scan results.",
                severity=hou.severityType.Warning
            )
            return None

        # Group files by asset folder (to handle the named USD files like KB3D_NEC_BldgMD_B.usd)
        asset_folders = self._group_by_asset_folder(geo_files)

        # Get the initial stage node to connect references to
        initial_stage = None
        for child in self.stage_context.children():
            if child.type().name() == 'configurestage':
                initial_stage = child
                break

        # Import each asset as reference
        reference_nodes = []
        positions = self._calculate_positions(len(asset_folders), spacing, layout_type)

        for idx, (folder_name, files) in enumerate(asset_folders.items()):
            # Use the named USD file (e.g., KB3D_NEC_BldgMD_B.usd) if available
            usd_file = self._select_primary_usd(files)

            if usd_file:
                ref_node = self._create_reference_node(
                    folder_name,
                    usd_file['path'],
                    positions[idx],
                    initial_stage
                )
                if ref_node:
                    reference_nodes.append(ref_node)

        # Create merge node to combine all references
        if reference_nodes:
            merge_node = self._create_merge_node(reference_nodes)

            # Layout nodes
            self.stage_context.layoutChildren()

            return merge_node

        return None

    def _group_by_asset_folder(self, geo_files: Dict) -> Dict[str, List[Dict]]:
        """
        Group geometry files by their parent asset folder.

        Args:
            geo_files (dict): Geometry files from scanner

        Returns:
            dict: Files grouped by asset folder name
        """
        grouped = {}

        for file_key, file_info in geo_files.items():
            # Extract folder name from relative_dir
            folder_name = file_info.get('relative_dir', '')

            if folder_name:
                if folder_name not in grouped:
                    grouped[folder_name] = []
                grouped[folder_name].append(file_info)

        return grouped

    def _select_primary_usd(self, files: List[Dict]) -> Optional[Dict]:
        """
        Select the primary USD file for reference.
        Prefers the named file (e.g., KB3D_NEC_BldgMD_B.usd) over payload.usd.

        Args:
            files (list): List of file info dicts in a folder

        Returns:
            dict: Selected file info or None
        """
        # Priority order:
        # 1. Named USD with variant suffix (is_variant=True)
        # 2. payload.usd
        # 3. First USD file found

        named_variant = None
        payload_usd = None
        first_usd = None

        for file_info in files:
            filename = file_info.get('filename', '')

            if file_info.get('is_variant'):
                named_variant = file_info
            elif filename == 'payload.usd':
                payload_usd = file_info
            elif first_usd is None and filename.endswith('.usd'):
                first_usd = file_info

        # Return in priority order
        return named_variant or payload_usd or first_usd

    def _create_stage_context(self, stage_name: str) -> hou.LopNode:
        """
        Create a new LOPS stage context.

        Args:
            stage_name (str): Name for the stage node

        Returns:
            hou.LopNode: The created lopnet or subnet node
        """
        # Try to find existing /stage lopnet
        obj = hou.node('/obj')
        stage = obj.node('stage')

        if stage is None:
            # Create /obj/stage lopnet if it doesn't exist
            stage = obj.createNode('lopnet', node_name='stage')

        # Create a subnet for organization
        sanitized_name = _sanitize(stage_name)
        subnet = stage.createNode('subnet', node_name=sanitized_name)

        # Create an initial configurestage node inside the subnet to define the USD stage
        initial_stage = subnet.createNode('configurestage', node_name='init')
        initial_stage.setDisplayFlag(False)

        return subnet

    def _create_reference_node(
        self,
        asset_name: str,
        usd_path: str,
        position: Tuple[float, float, float],
        input_node: Optional[hou.LopNode] = None
    ) -> Optional[hou.LopNode]:
        """
        Create a reference node for a USD asset with transform.

        Args:
            asset_name (str): Name for the asset
            usd_path (str): Path to USD file
            position (tuple): (x, y, z) position for the asset
            input_node (hou.LopNode): Optional input node to connect to

        Returns:
            hou.LopNode: The created transform node or None
        """
        if not os.path.exists(usd_path):
            print(f"Warning: USD file not found: {usd_path}")
            return None

        # Sanitize asset name for node naming
        sanitized_name = _sanitize(asset_name)

        # Create reference node
        ref_node = self.stage_context.createNode('reference', node_name=f"ref_{sanitized_name}")

        # Connect to input if provided
        if input_node:
            ref_node.setInput(0, input_node)

        # Set primitive path for this reference (where it appears in the stage)
        prim_path = f"/{sanitized_name}"
        ref_node.parm('primpath').set(prim_path)

        # Enable and set the first file reference
        ref_node.parm('enable1').set(1)
        ref_node.parm('filepath1').set(usd_path)

        # Create transform node to position the asset
        xform_node = self.stage_context.createNode('xform', node_name=f"xform_{sanitized_name}")
        xform_node.setInput(0, ref_node)

        # Set transform primitive path to match the reference
        xform_node.parm('primpattern1').set(prim_path)

        # Set position
        xform_node.parm('tx').set(position[0])
        xform_node.parm('ty').set(position[1])
        xform_node.parm('tz').set(position[2])

        # Store reference info
        self.imported_refs.append({
            'name': asset_name,
            'ref_node': ref_node,
            'xform_node': xform_node,
            'path': usd_path,
            'position': position
        })

        return xform_node

    def _calculate_positions(
        self,
        count: int,
        spacing: float,
        layout_type: str
    ) -> List[Tuple[float, float, float]]:
        """
        Calculate spatial positions for assets based on layout type.

        Args:
            count (int): Number of assets to position
            spacing (float): Distance between assets
            layout_type (str): "grid", "line", or "circular"

        Returns:
            list: List of (x, y, z) position tuples
        """
        positions = []

        if layout_type == "grid":
            # Arrange in a square grid
            import math
            grid_size = math.ceil(math.sqrt(count))

            for i in range(count):
                row = i // grid_size
                col = i % grid_size

                # Center the grid around origin
                x = (col - grid_size / 2.0 + 0.5) * spacing
                z = (row - grid_size / 2.0 + 0.5) * spacing
                y = 0.0

                positions.append((x, y, z))

        elif layout_type == "line":
            # Arrange in a straight line along X axis
            for i in range(count):
                x = (i - count / 2.0 + 0.5) * spacing
                positions.append((x, 0.0, 0.0))

        elif layout_type == "circular":
            # Arrange in a circle
            import math
            radius = (count * spacing) / (2 * math.pi)

            for i in range(count):
                angle = (2 * math.pi * i) / count
                x = radius * math.cos(angle)
                z = radius * math.sin(angle)
                positions.append((x, 0.0, z))

        else:
            # Default to grid
            return self._calculate_positions(count, spacing, "grid")

        return positions

    def _create_merge_node(self, nodes: List[hou.LopNode]) -> hou.LopNode:
        """
        Create a merge node to combine all reference nodes.

        Args:
            nodes (list): List of LOP nodes to merge

        Returns:
            hou.LopNode: The merge node
        """
        merge_node = self.stage_context.createNode('merge', node_name='merge_all_references')

        # Connect all nodes to the merge
        for idx, node in enumerate(nodes):
            merge_node.setInput(idx, node)

        # Set display flag on merge node
        merge_node.setDisplayFlag(True)
        merge_node.setRenderFlag(True)

        return merge_node


def import_scanned_assets(
    scan_result: Dict,
    stage_name: str = "asset_references",
    spacing: float = 5.0,
    layout_type: str = "grid"
) -> Optional[hou.LopNode]:
    """
    Convenience function to import scanned assets as USD references.

    Args:
        scan_result (dict): Result from AssetFolderScanner.scan_folder()
        stage_name (str): Name for the stage network
        spacing (float): Distance between assets in Houdini units
        layout_type (str): Layout type - "grid", "line", or "circular"

    Returns:
        hou.LopNode: The merge node containing all references
    """
    importer = USDReferenceImporter()
    return importer.import_scanned_assets(scan_result, stage_name, spacing, layout_type)


# Example usage
if __name__ == "__main__":
    # This would typically be used with results from asset_folder_scanner
    from modules.asset_folder_scanner import scan_asset_folder

    # Example path
    asset_path = "/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_neocity"

    # Scan the folder
    scan_result = scan_asset_folder(asset_path, geo_subfolder="Models", tex_subfolder="Textures")

    # Import as references
    merge_node = import_scanned_assets(
        scan_result,
        stage_name="kb3d_neocity_references",
        spacing=10.0,
        layout_type="grid"
    )

    if merge_node:
        print(f"Successfully imported assets. Merge node: {merge_node.path()}")
    else:
        print("Failed to import assets.")
