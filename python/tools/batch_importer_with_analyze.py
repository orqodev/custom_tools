import hou
import os
import math
import json
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


    def create_transformer_node(set_scale=False, scale_value=None, input_node=None, position_x=0, position_z=0):
        """
        Creates a transform node and optionally sets its scale and position.

        Args:
            set_scale (bool): Whether to apply scaling to the node
            scale_value (float): Scale value to apply
            input_node (hou.Node): Node to connect as input
            position_x (float): X position for the asset
            position_z (float): Z position for the asset

        Returns:
            hou.Node: The created transform node
        """
        transform_node = geo_node.createNode('xform', node_name=_sanitize(asset_name + 'x_form'))
        if set_scale:
            transform_node.parm('scale').set(scale_value)

        # Set translation to position assets with spacing
        transform_node.parm('tx').set(position_x)
        transform_node.parm('tz').set(position_z)

        transform_node.setInput(0, input_node)
        return transform_node


    def calculate_bbox(geometry_node):
        """
        Calculate the bounding box size, diagonal, volume, and size classification for a geometry node.

        Args:
            geometry_node (hou.Node): The geometry node to analyze

        Returns:
            tuple: (bbox_size, diagonal, volume, size_type)
                bbox_size (list): 3-element float list [x, y, z] representing the bounding box size
                diagonal (float): Length of the bounding box diagonal
                volume (float): Volume of the bounding box
                size_type (str): Classification based on both volume and max dimension
        """
        # Get the geometry from the node
        geo = geometry_node.geometry()

        # Get the bounding box
        bbox = geo.boundingBox()

        # Calculate the size (dimensions) of the bounding box
        min_pt = bbox.minvec()
        max_pt = bbox.maxvec()

        # Calculate the size in each dimension
        size_x = max_pt[0] - min_pt[0]
        size_y = max_pt[1] - min_pt[1]
        size_z = max_pt[2] - min_pt[2]

        # Create the bbox size list
        bbox_size = [size_x, size_y, size_z]

        # Calculate the diagonal using the Pythagorean theorem
        diagonal = math.sqrt(size_x**2 + size_y**2 + size_z**2)

        # Calculate the volume
        volume = size_x * size_y * size_z

        # Determine the size classification based on both volume and max dimension
        max_dim = max(bbox_size)

        if volume <= 2000 and max_dim <= 20:
            size_type = "small"
        elif volume <= 20000 and max_dim <= 80:
            size_type = "medium"
        else:
            size_type = "big"

        return bbox_size, diagonal, volume, size_type

    if select_directory:
        files_name = select_directory.split(';')

        # Initialize a list to collect analysis results
        analysis_results = []

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

        # Ask user for spacing preference
        button_pressed, spacing_input = hou.ui.readInput(
            "Enter the spacing between assets (recommended minimum: 10.0):",
            buttons=("OK", "Use Default (10.0)"),
            default_choice=0,
            title="Asset Spacing"
        )

        # Set spacing based on user input
        spacing = 10.0  # Default spacing
        if button_pressed == 0 and spacing_input.strip():
            try:
                spacing = float(spacing_input.strip())
                if spacing < 5.0:
                    hou.ui.displayMessage("Warning: Small spacing values may cause assets to overlap. Using minimum value of 5.0.", buttons=('OK',))
                    spacing = 5.0
            except ValueError:
                hou.ui.displayMessage("Invalid spacing value. Using default spacing of 10.0.", buttons=('OK',))
                spacing = 10.0


        for index, file_name in enumerate(files_name):
            # Update progress message for large imports
            if total_files > 5:
                progress_msg = f"Importing file {index+1} of {total_files}: {file_name.split('/')[-1]}"
                hou.ui.setStatusMessage(progress_msg, hou.severityType.ImportantMessage)

            file_name = file_name.strip()
            asset = file_name.split('/')

            # Calculate position for this asset (linear spacing)
            position_x = index * spacing
            position_z = 0

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
                transform_node = create_transformer_node(set_scale, scale_value, unpack_node, position_x, position_z)

            elif asset_type.lower() in ["fbx"]:
                # FBX files
                new_fbx_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_fbx_loader.parm('file').set(file_name)
                # Add FBX-specific parameters if needed
                transform_node = create_transformer_node(set_scale, scale_value, new_fbx_loader, position_x, position_z)

            elif asset_type.lower() in ["usd", "usda", "usdc"]:
                # USD files
                new_usd_loader = geo_node.createNode('usdimport', node_name=_sanitize(asset_name))
                new_usd_loader.parm('filepath').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_usd_loader, position_x, position_z)

            elif asset_type.lower() in ["obj"]:
                # OBJ files
                new_obj_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_obj_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_obj_loader, position_x, position_z)

            elif asset_type.lower() in ["bgeo", "bgeo.sc", "sc"]:
                # Houdini geometry files
                new_bgeo_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_bgeo_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_bgeo_loader, position_x, position_z)

            else:
                # Generic file loader for other types
                hou.ui.setStatusMessage(f"Using generic loader for file type: {asset_type}", hou.severityType.Message)
                new_file_loader = geo_node.createNode('file', node_name=_sanitize(asset_name))
                new_file_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_file_loader, position_x, position_z)

            # Add a Measure SOP to calculate bounding box
            try:
                measure_node = geo_node.createNode('measure', node_name=_sanitize(asset_name + '_measure'))
                if measure_node is not None:
                    measure_node.setInput(0, transform_node)

                    # Configure the Measure SOP
                    measure_node.parm('type').set(0)  # Bounding Box
                    measure_node.parm('boundingattrib').set('bboxsize')  # Attribute name

                    # Add an Attribute Wrangle SOP to classify size
                    attrib_wrangle = geo_node.createNode('attribwrangle', node_name=_sanitize(asset_name + '_size_classify'))
                    attrib_wrangle.setInput(0, measure_node)
                else:
                    # Fallback if measure_node is None
                    hou.ui.setStatusMessage(f"Warning: Could not create measure node for {asset_name}. Using transform node directly.", hou.severityType.Warning)
                    attrib_wrangle = geo_node.createNode('attribwrangle', node_name=_sanitize(asset_name + '_size_classify'))
                    attrib_wrangle.setInput(0, transform_node)
            except Exception as e:
                # Fallback if there's an error creating the measure node
                hou.ui.setStatusMessage(f"Error creating measure node: {str(e)}. Using transform node directly.", hou.severityType.Warning)
                attrib_wrangle = geo_node.createNode('attribwrangle', node_name=_sanitize(asset_name + '_size_classify'))
                attrib_wrangle.setInput(0, transform_node)

            # Set the VEX code for size classification
            vex_code = '''
// Check if bboxsize attribute exists (from measure node)
vector s;
if (hasprimattrib(0, "bboxsize")) {
    s = v@bboxsize;
} else {
    // Calculate bounding box manually if bboxsize attribute doesn't exist
    vector min_pt = getbbox_min(0);
    vector max_pt = getbbox_max(0);
    s = max_pt - min_pt;
}

float maxdim = max(s.x, max(s.y, s.z));
float volume = s.x * s.y * s.z;
f@volume = volume;

if (volume <= 2000 && maxdim <= 20)
    s@size_type = "Small";
else if (volume <= 20000 && maxdim <= 80)
    s@size_type = "Medium";
else
    s@size_type = "Big";
'''
            attrib_wrangle.parm('class').set(1)  # Run over primitives
            attrib_wrangle.parm('snippet').set(vex_code)

            # Create material node with proper naming
            material_node = geo_node.createNode('material', node_name=_sanitize(asset_name + '_mat'))
            material_node.setInput(0, attrib_wrangle)

            # Use material node as final node
            final_node = material_node

            # Add pack node for visualization after final node
            pack_node = geo_node.createNode('pack', node_name=_sanitize(asset_name + '_pack'))
            pack_node.setInput(0, final_node)

            # Calculate bounding box information for JSON export
            bbox_size, diagonal, volume, size_type = calculate_bbox(pack_node)

            # Add analysis result to the list
            analysis_result = {
                "name": asset_name,
                "bbox": bbox_size,
                "volume": round(volume, 3),
                "diagonal": round(diagonal, 3),
                "size_type": size_type,
                "position": [position_x, 0, position_z],
                "role": "part"  # Default role, can be customized later
            }
            analysis_results.append(analysis_result)

            # Connect to the merge node
            merge_node.setInput(add_to_merge, pack_node)
            add_to_merge += 1

        # Organize nodes in the network editor
        geo_node.layoutChildren()

        # Set display/render flags on the merge node
        merge_node.setDisplayFlag(True)
        merge_node.setRenderFlag(True)

        # Add labs::align_and_distribute node after merge
        align_and_distribute_node = geo_node.createNode('labs::align_and_distribute', 'align_and_distribute')
        align_and_distribute_node.setInput(0, merge_node)

        # Add a null node at the end for cleaner output
        output_node = geo_node.createNode('null', 'OUT')
        output_node.setInput(0, align_and_distribute_node)
        output_node.setDisplayFlag(True)
        output_node.setRenderFlag(True)
        output_node.setPosition(merge_node.position() + hou.Vector2(0, -1))

        # Save analysis results to a JSON file
        hip_dir = hou.text.expandString('$HIP')
        analysis_file_path = os.path.join(hip_dir, "batch_import_analysis.json")

        with open(analysis_file_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)

        # Format a summary of the analysis results
        analysis_summary = ""
        for result in analysis_results:
            analysis_summary += f"- {result['name']}: {result['size_type']} (volume: {result['volume']}, diagonal: {result['diagonal']})\n"

        # Show completion message with import statistics
        hou.ui.displayMessage(
            f"Import completed successfully!\n\n"
            f"Files imported: {total_files}\n"
            f"Scale applied: {scale_value if set_scale else 'No scaling'}\n"
            f"Spacing between objects: {spacing} units\n\n"
            f"Analysis Results:\n{analysis_summary}\n"
            f"Full analysis saved to: {analysis_file_path}\n\n"
            f"The imported geometry is in the node: {geo_node.path()}",
            buttons=('OK',),
            title="Batch Import Complete"
        )

    else:
        hou.ui.displayMessage("Please, check again. No valid file was selected", buttons=('OK',))
