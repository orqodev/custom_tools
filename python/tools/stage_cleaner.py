#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stage Cleaner

A utility script to delete all nodes in the /stage context in Houdini.
The script asks for user confirmation before proceeding with deletion.
"""

import hou


def delete_all_stage_nodes():
    """
    Delete all nodes in the /stage context after asking for user confirmation.
    
    Returns:
        bool: True if nodes were deleted, False if operation was cancelled
    """
    # Get the stage context
    stage = hou.node("/stage")
    
    if not stage:
        hou.ui.displayMessage(
            "Stage context not found.",
            severity=hou.severityType.Error
        )
        return False
    
    # Count the number of nodes to delete
    nodes = stage.children()
    node_count = len(nodes)
    
    if node_count == 0:
        hou.ui.displayMessage(
            "No nodes found in /stage context.",
            severity=hou.severityType.Message
        )
        return False
    
    # Ask for confirmation
    message = f"Are you sure you want to delete all {node_count} nodes in /stage?"
    confirmation = hou.ui.displayConfirmation(
        message,
        title="Stage Cleaner",
        suppress=False
    )
    
    if not confirmation:
        print("Operation cancelled by user.")
        return False
    
    # Delete all nodes
    try:
        for node in nodes:
            node.destroy()
        
        hou.ui.displayMessage(
            f"Successfully deleted {node_count} nodes from /stage.",
            severity=hou.severityType.Message
        )
        return True
    
    except Exception as e:
        hou.ui.displayMessage(
            f"Error deleting nodes: {str(e)}",
            severity=hou.severityType.Error
        )
        return False


def main():
    """
    Main function to run the stage cleaner.
    """
    delete_all_stage_nodes()


if __name__ == "__main__":
    main()