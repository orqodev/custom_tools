import hou
import os
import math
from modules.misc_utils import _sanitize




def batch_importer():
    """
    Batch imports multiple geometry files into Houdini.

    This function allows users to select multiple geometry files and import them
    into a single Houdini geometry node. It provides options for scaling all imported
    objects uniformly.

    Supported file types:
    - .abc (Alembic)
    - .bgeo, .bgeo.sc (Houdini geometry)
    - .obj (Wavefront OBJ)
    - .fbx (FBX)
    - .usd, .usda, .usdc (USD)
    """
    # Declaring Variables
    default_directory = f"{hou.text.expandString('$HIP')}"
    select_directory = hou.ui.selectFile(start_directory=default_directory,
                                         title="Select the files you want to import",
                                         file_type=hou.fileType.Geometry,
                                         multiple_select=True)


    def create_transformer_node(set_scale=False, scale_value=None, input_node=None):
        """
        Creates a transform node and optionally sets its scale.

        Args:
            set_scale (bool): Whether to apply scaling to the node
            scale_value (float): Scale value to apply
            input_node (hou.Node): Node to connect as input

        Returns:
            hou.Node: The created transform node
        """
        transform_node = geo_node.createNode('xform', node_name=_sanitize(asset_name + 'x_form'))
        if set_scale:
            transform_node.parm('scale').set(scale_value)

        transform_node.setInput(0, input_node)
        return transform_node


    if select_directory:
        files_name = select_directory.split(';')

        # Ask for scale preference once at the beginning
        set_scale = False
        scale_value = "1.0"  # Default scale value

        # Ask user if they want to apply scaling to all imported objects
        button_pressed, user_input = hou.ui.readInput(
            "Do you want to apply scaling to all imported objects? If yes, enter the scale value:",
            buttons=("Yes", "No"),
            default_choice=1,  # Default to "No"
            title="Batch Import Scale Option"
        )

        if button_pressed == 0:  # User clicked "Yes"
            set_scale = True
            # Use the user input as scale value if provided, otherwise use default
            if user_input.strip():
                scale_value = user_input.strip()

        obj = hou.node('/obj')
        geo_node = obj.createNode('geo', node_name='batch_import')

        merge_node = geo_node.createNode('merge', node_name='mergeAll')
        add_to_merge = 0

        # Display progress for large imports
        total_files = len(files_name)

        # No grid layout or spacing options needed

        for index, file_name in enumerate(files_name):
            # Update progress message for large imports
            if total_files > 5:
                progress_msg = f"Importing file {index+1} of {total_files}: {file_name.split('/')[-1]}"
                hou.ui.setStatusMessage(progress_msg, hou.severityType.ImportantMessage)

            file_name = file_name.strip()
            asset = file_name.split('/')

            # No grid position calculation needed

            try:
                # Get file extension and handle multi-part extensions like .bgeo.sc
                filename = asset[-1]
                asset_name = os.path.splitext(filename)[0]
                # Get the full extension including compound extensions like .bgeo.sc
                _, extension = os.path.splitext(filename)
                if extension and asset_name.endswith('.bgeo'):
                    asset_type = 'bgeo.sc'
                    asset_name = asset_name[:-5]  # Remove .bgeo from asset_name
                else:
                    asset_type = extension[1:] if extension else ""  # Remove the dot from extension

                if not asset_type:
                    raise ValueError("File has no extension")

                new_file_loader = None
                transform_node = None
            except (IndexError, ValueError) as e:
                hou.ui.displayMessage(f"Error parsing file: {file_name}. {str(e)}. Skipping.", buttons=('OK',))
                continue

            # Handle different file types
            if asset_type.lower() in ["abc", "abcs"]:
                # Alembic files
                new_alembic_loader = geo_node.createNode('alembic', node_name=_sanitize(asset_name))
                new_alembic_loader.parm('fileName').set(file_name)
                unpack_node = geo_node.createNode('unpack', node_name=_sanitize(asset_name + '_unpack'))
                unpack_node.setInput(0, new_alembic_loader)
                transform_node = create_transformer_node(set_scale, scale_value, unpack_node)

            elif asset_type.lower() in ["fbx"]:
                # FBX files
                new_fbx_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_fbx_loader.parm('file').set(file_name)
                # Add FBX-specific parameters if needed
                transform_node = create_transformer_node(set_scale, scale_value, new_fbx_loader)

            elif asset_type.lower() in ["usd", "usda", "usdc"]:
                # USD files
                new_usd_loader = geo_node.createNode('usdimport', node_name=_sanitize(asset_name))
                new_usd_loader.parm('filepath').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_usd_loader)

            elif asset_type.lower() in ["obj"]:
                # OBJ files
                new_obj_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_obj_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_obj_loader)

            elif asset_type.lower() in ["bgeo", "bgeo.sc", "sc"]:
                # Houdini geometry files
                new_bgeo_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_bgeo_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_bgeo_loader)

            else:
                # Generic file loader for other types
                hou.ui.setStatusMessage(f"Using generic loader for file type: {asset_type}", hou.severityType.Message)
                new_file_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_file_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_file_loader)

            # Create material node with proper naming
            material_node = geo_node.createNode('material', node_name=_sanitize(asset_name + '_mat'))
            material_node.setInput(0, transform_node)

            # Add pack node for visualization after material node
            pack_node = geo_node.createNode('pack', node_name=_sanitize(asset_name + '_pack'))
            pack_node.setInput(0, material_node)

            merge_node.setInput(add_to_merge, pack_node)
            add_to_merge += 1

        # Set display/render flags on the merge node
        merge_node.setDisplayFlag(True)
        merge_node.setRenderFlag(True)

        # Add labs::align_and_distribute node after merge
        align_and_distribute_node = geo_node.createNode('labs::align_and_distribute', 'align_and_distribute')
        align_and_distribute_node.parm('sort_by').set(1)
        align_and_distribute_node.setInput(0, merge_node)

        # Add OUT_RENDER null node
        out_render_node = geo_node.createNode('null', 'OUT_RENDER')
        out_render_node.setInput(0, align_and_distribute_node)
        out_render_node.setDisplayFlag(True)
        out_render_node.setRenderFlag(True)
        out_render_node.setColor(hou.Color(0, 0, 0))  # Set black color
        
        # Add polyreduce node with percentage parameter set to 10
        poly_reduce_node = geo_node.createNode('polyreduce::2.0', 'polyreduce_proxy')
        poly_reduce_node.parm('percentage').set(10)
        poly_reduce_node.setInput(0, align_and_distribute_node)
        
        # Add OUT_PROXY null node
        out_proxy_node = geo_node.createNode('null', 'OUT_PROXY')
        out_proxy_node.setInput(0, poly_reduce_node)
        out_proxy_node.setColor(hou.Color(0, 0, 0))  # Set black color

        # Organize nodes in the network editor
        geo_node.layoutChildren()

        # Show completion message with import statistics
        hou.ui.displayMessage(
            f"Import completed successfully!\n\n"
            f"Files imported: {total_files}\n"
            f"Scale applied: {scale_value if set_scale else 'No scaling'}\n\n"
            f"The imported geometry is in the node: {geo_node.path()}",
            buttons=('OK',),
            title="Batch Import Complete"
        )

    else:
        hou.ui.displayMessage("Please, check again. No valid file was selected", buttons=('OK',))
