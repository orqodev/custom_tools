import hou
from tools import lops_light_rig
from tools.lops_asset_builder_v2.lops_asset_builder_v2 import create_camera_lookdev, create_karma_nodes


def setup_light_rig_pipeline(stage_context=None, target_node=None, scope_name=None, auto_prompt=True):
    """
    Setup light rig pipeline with camera and Karma render setup.
    
    This function can be used in two ways:
    1. Workflow usage: Pass stage_context and scope_name
    2. External usage: Pass target_node (selected node with primpath)
    
    Args:
        stage_context (hou.Node, optional): Stage context node (for workflow usage)
        target_node (hou.Node, optional): Target node with primpath (for external usage)
        scope_name (str, optional): Scope name for camera lookdev (for workflow usage)
        auto_prompt (bool): Whether to prompt user for confirmation (default: True)
    
    Returns:
        dict: Dictionary with created nodes or None if cancelled/failed
    """
    try:
        # Determine usage mode and validate inputs
        if target_node is not None:
            # External usage mode
            if not target_node or not hasattr(target_node, 'parm'):
                raise ValueError("target_node must be a valid Houdini node")
            
            # Check if target node has primpath parameter
            primpath_parm = target_node.parm('primpath')
            if not primpath_parm:
                raise ValueError("Selected node must have a 'primpath' parameter (e.g., scope, xform)")
            
            # Get the primpath value
            primpath_value = primpath_parm.eval()
            if not primpath_value or not primpath_value.startswith('/'):
                raise ValueError(f"Selected node has invalid primpath: '{primpath_value}'. Must start with '/'")
            
            # Use the target node's parent as stage context
            stage_context = target_node.parent()
            # Extract scope name from primpath (remove leading slash)
            scope_name = primpath_value.lstrip('/')
            
        elif stage_context is not None and scope_name is not None:
            # Workflow usage mode
            if not stage_context or not hasattr(stage_context, 'createNode'):
                raise ValueError("stage_context must be a valid Houdini node")
            if not scope_name or not isinstance(scope_name, str):
                raise ValueError("scope_name must be a non-empty string")
        else:
            raise ValueError("Must provide either target_node OR (stage_context and scope_name)")
        
        # Ask user if they want to add light rig and camera (if auto_prompt is True)
        if auto_prompt:
            add_light_rig = hou.ui.displayMessage(
                "Do you want to add a light rig and camera setup?",
                buttons=("Yes", "No"),
                severity=hou.severityType.Message,
                default_choice=0,
                close_choice=1,
                title="LOPS Light Rig Pipeline Setup"
            )
            
            if add_light_rig != 0:  # User chose "No" or cancelled
                return None
        
        # Create light rig
        light_rig_nodes_to_layout, graft_branch = lops_light_rig.create_three_point_light()
        
        # Set Display Flag
        graft_branch.setGenericFlag(hou.nodeFlag.Display, True)
        
        # Create Camera Node
        camera_render = stage_context.createNode('camera', 'camera_render')
        camera_render.setInput(0, graft_branch)
        
        # Create Python Script for camera lookdev
        camera_python_script = create_camera_lookdev(stage_context, scope_name)
        camera_python_script.setInput(0, camera_render)
        
        # Create Karma nodes
        karma_settings, usdrender_rop = create_karma_nodes(stage_context)
        karma_settings.setInput(0, camera_python_script)
        usdrender_rop.setInput(0, karma_settings)
        
        # Layout Karma nodes
        karma_nodes = [camera_render, camera_python_script, karma_settings, usdrender_rop]
        stage_context.layoutChildren(items=karma_nodes)
        
        # Return created nodes
        return {
            'light_rig_nodes': light_rig_nodes_to_layout,
            'light_merge': graft_branch,
            'camera': camera_render,
            'camera_script': camera_python_script,
            'karma_settings': karma_settings,
            'usd_rop': usdrender_rop,
            'all_nodes': karma_nodes + light_rig_nodes_to_layout
        }
        
    except Exception as e:
        hou.ui.displayMessage(f"Error setting up light rig pipeline: {str(e)}",
                              severity=hou.severityType.Error)
        return None


def setup_light_rig_pipeline_from_selection():
    """
    Setup light rig pipeline using the currently selected node.
    
    This is a convenience function for external usage that automatically
    uses the first selected node as the target.
    
    Returns:
        dict: Dictionary with created nodes or None if failed
    """
    try:
        # Get selected nodes
        selected_nodes = hou.selectedNodes()
        
        if not selected_nodes:
            hou.ui.displayMessage(
                "No node selected. Please select a node with a primpath parameter (e.g., scope, xform).",
                severity=hou.severityType.Warning,
                title="LOPS Light Rig Pipeline"
            )
            return None
        
        # Use the first selected node
        target_node = selected_nodes[0]
        
        # Check if we're in a LOPS context
        if target_node.parent().childTypeCategory().name() != 'Lop':
            hou.ui.displayMessage(
                "Selected node is not in a LOPS context. Please select a node in /stage.",
                severity=hou.severityType.Warning,
                title="LOPS Light Rig Pipeline"
            )
            return None
        
        return setup_light_rig_pipeline(target_node=target_node)
        
    except Exception as e:
        hou.ui.displayMessage(f"Error setting up light rig pipeline from selection: {str(e)}",
                              severity=hou.severityType.Error)
        return None


# Main entry point for external usage
def main():
    """Main entry point for external script usage."""
    return setup_light_rig_pipeline_from_selection()


if __name__ == "__main__":
    main()