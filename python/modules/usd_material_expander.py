"""
USD Material Expander - Import USD materials and expand to editable VOP networks

This module provides functionality to import materials from USD files and expand
MaterialX shaders into editable Houdini VOP networks using the 'editmaterial' LOP node.

This gives you full control to modify materials instead of working with closed USD assets.
"""

import hou
import os
from typing import Dict, List, Optional, Tuple
from modules.misc_utils import _sanitize, slugify


class USDMaterialExpander:
    """
    Imports USD materials and expands them into editable VOP networks.
    """

    def __init__(self, lop_context: Optional[hou.LopNode] = None):
        """
        Initialize the USD Material Expander.

        Args:
            lop_context (hou.LopNode): Optional LOP network to work in
        """
        self.lop_context = lop_context
        self.imported_materials = []

    def expand_materials_from_usd(
        self,
        usd_file_path: str,
        lop_network_name: str = "expanded_materials",
        expand_to_vops: bool = True
    ) -> Tuple[hou.LopNode, hou.LopNode]:
        """
        Import materials from USD file and optionally expand to editable VOPs.

        Args:
            usd_file_path (str): Path to USD file containing materials
            lop_network_name (str): Name for the LOP network
            expand_to_vops (bool): If True, expand MaterialX to VOP networks

        Returns:
            tuple: (reference_node, material_library_node or edit_material_node)
        """
        if not os.path.exists(usd_file_path):
            raise ValueError(f"USD file not found: {usd_file_path}")

        # Create or use LOP context
        if self.lop_context is None:
            self.lop_context = self._create_lop_context(lop_network_name)

        # Create reference to the USD file
        ref_node = self.lop_context.createNode('reference', node_name='usd_materials_ref')
        ref_node.parm('filepath1').set(usd_file_path)
        ref_node.parm('primpath').set('/mtl')  # Common path for materials

        if expand_to_vops:
            # Use editmaterial to expand MaterialX into editable VOPs
            edit_mat_node = self._expand_materials_to_vops(ref_node)
            return ref_node, edit_mat_node
        else:
            # Just import as-is
            return ref_node, ref_node

    def expand_materials_from_folder(
        self,
        folder_path: str,
        pattern: str = "**/mtl.usd",
        lop_network_name: str = "expanded_materials",
        merge_all: bool = True
    ) -> List[hou.LopNode]:
        """
        Import and expand materials from multiple USD files in a folder.

        Args:
            folder_path (str): Root folder to search
            pattern (str): Glob pattern for USD files (default: **/mtl.usd)
            lop_network_name (str): Name for the LOP network
            merge_all (bool): If True, merge all materials into one network

        Returns:
            list: List of created material nodes
        """
        import glob

        # Find all matching USD files
        search_path = os.path.join(folder_path, pattern)
        usd_files = glob.glob(search_path, recursive=True)

        if not usd_files:
            print(f"No USD files found matching: {search_path}")
            return []

        print(f"Found {len(usd_files)} USD material files")

        # Create or use LOP context
        if self.lop_context is None:
            self.lop_context = self._create_lop_context(lop_network_name)

        # Get the initial stage node
        initial_stage = None
        for child in self.lop_context.children():
            if child.type().name() == 'configurestage':
                initial_stage = child
                break

        # Create nodes for each USD file
        material_nodes = []
        previous_node = initial_stage

        for idx, usd_file in enumerate(usd_files):
            # Get folder name for naming
            folder_name = os.path.basename(os.path.dirname(usd_file))

            # Create reference node
            ref_node = self.lop_context.createNode(
                'reference',
                node_name=f"ref_{_sanitize(folder_name)}"
            )

            # Connect to previous node
            if previous_node:
                ref_node.setInput(0, previous_node)

            # Set the reference file path
            filepath_parm = ref_node.parm('filepath1')
            if filepath_parm:
                filepath_parm.set(usd_file)
            else:
                print(f"Warning: Could not set filepath for {folder_name}")

            # Expand to VOPs
            edit_node = self._expand_materials_to_vops(ref_node, suffix=folder_name)

            material_nodes.append(edit_node)
            previous_node = edit_node  # Chain them together

        # Merge all if requested
        if merge_all and len(material_nodes) > 1:
            merge_node = self._merge_materials(material_nodes)
            self.lop_context.layoutChildren()
            return [merge_node]

        self.lop_context.layoutChildren()
        return material_nodes

    def _create_lop_context(self, network_name: str) -> hou.LopNode:
        """
        Create a new LOP network context.

        Args:
            network_name (str): Name for the LOP network

        Returns:
            hou.LopNode: The created LOP subnet
        """
        # Find or create /obj/stage
        obj = hou.node('/obj')
        stage = obj.node('stage')

        if stage is None:
            stage = obj.createNode('lopnet', node_name='stage')

        # Create subnet
        sanitized_name = _sanitize(network_name)
        subnet = stage.createNode('subnet', node_name=sanitized_name)

        # Create initial configure stage
        init_stage = subnet.createNode('configurestage', node_name='init')
        init_stage.setDisplayFlag(False)

        return subnet

    def _expand_materials_to_vops(
        self,
        input_node: hou.LopNode,
        suffix: str = ""
    ) -> hou.LopNode:
        """
        Create a materiallibrary node that references the imported materials.
        Materials in a materiallibrary are editable as VOP networks.

        Args:
            input_node (hou.LopNode): Node with materials to expand
            suffix (str): Optional suffix for node naming

        Returns:
            hou.LopNode: The materiallibrary node
        """
        node_name = f"matlib_{suffix}" if suffix else "matlib"

        # Create materiallibrary node
        # MaterialX materials can be edited by creating a materiallibrary
        # and then diving into it to see the VOP networks
        matlib = self.lop_context.createNode(
            'materiallibrary',
            node_name=_sanitize(node_name)
        )
        matlib.setInput(0, input_node)

        # The materiallibrary will show materials from upstream
        # Users can dive in (press 'i') to edit the shader networks

        return matlib

    def _merge_materials(self, material_nodes: List[hou.LopNode]) -> hou.LopNode:
        """
        Merge multiple material nodes.

        Args:
            material_nodes (list): List of LOP nodes to merge

        Returns:
            hou.LopNode: The merge node
        """
        merge_node = self.lop_context.createNode('merge', node_name='merge_all_materials')

        for idx, node in enumerate(material_nodes):
            merge_node.setInput(idx, node)

        merge_node.setDisplayFlag(True)
        merge_node.setRenderFlag(True)

        return merge_node


def expand_usd_materials(
    usd_file_path: str,
    lop_network_name: str = "expanded_materials",
    expand_to_vops: bool = True
) -> Tuple[hou.LopNode, hou.LopNode]:
    """
    Convenience function to expand materials from a USD file.

    Args:
        usd_file_path (str): Path to USD file
        lop_network_name (str): Name for LOP network
        expand_to_vops (bool): Expand to VOP networks

    Returns:
        tuple: (reference_node, material_node)
    """
    expander = USDMaterialExpander()
    return expander.expand_materials_from_usd(
        usd_file_path,
        lop_network_name,
        expand_to_vops
    )


def expand_materials_from_folder(
    folder_path: str,
    pattern: str = "**/mtl.usd",
    lop_network_name: str = "expanded_materials",
    merge_all: bool = True
) -> List[hou.LopNode]:
    """
    Convenience function to expand materials from multiple USD files.

    Args:
        folder_path (str): Root folder to search
        pattern (str): Glob pattern for USD files
        lop_network_name (str): Name for LOP network
        merge_all (bool): Merge all materials

    Returns:
        list: List of created material nodes
    """
    expander = USDMaterialExpander()
    return expander.expand_materials_from_folder(
        folder_path,
        pattern,
        lop_network_name,
        merge_all
    )


# Example usage
if __name__ == "__main__":
    # Example: Expand materials from kb3d_neocity
    folder = "/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_neocity/Models"

    material_nodes = expand_materials_from_folder(
        folder,
        pattern="**/mtl.usd",
        lop_network_name="kb3d_neocity_materials",
        merge_all=True
    )

    print(f"Created {len(material_nodes)} material networks")
    for node in material_nodes:
        print(f"  - {node.path()}")
