import hou
import os

def create_export_top_network():
    """
    Create a TOP network to export many split primitives from FBX or OBJ files.
    Based on split_geo functionality to get context from *_OUT nulls.
    """

    #--------------------------------------------------------------
    # 0. Parent SOP network that already holds the *_OUT nulls
    #--------------------------------------------------------------
    sel = hou.selectedNodes()
    if not sel:
        raise hou.ui.displayMessage("Select a file node inside the SOP network first.")
    sop_parent = sel[0].parent()

    #--------------------------------------------------------------
    # 1. TOP network
    #--------------------------------------------------------------
    file_path = sel[0].parm("file").eval()
    top_net_name = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)
    topnet = sop_parent.createNode("topnet", top_net_name)
    gather = topnet.createNode("pythonprocessor", "gather_parts")
    rop_geo = topnet.createNode("ropgeometry", "export_bgeo")
    rop_geo.setInput(0, gather)
    top_geo_import = hou.node(f"{topnet.path()}/geometryimport")
    if top_geo_import is not None:
        top_geo_import.destroy()

        #--------------------------------------------------------------
    # 2. Python Processor – one work item per *_OUT null
    #--------------------------------------------------------------
    generate_code = '''
import hou
import os

net = hou.node("../..")  # SOP net
nulls = []
folder_path = None

# Find folder path from file nodes - improved approach
for n in net.children():
    if n.type().name() == "file":
        file_path = n.parm('file').eval()
        if file_path:  # Check if file path is not empty
            folder_path = os.path.dirname(file_path)
            break  # Use the first valid file node found
    
# If no file node found, try to find from other import nodes
if folder_path is None:
    for n in net.children():
        if n.type().name() in ["alembic", "filmboxfbx"]:  # Common import node types
            file_parm = None
            if hasattr(n, 'parm') and n.parm('fileName'):  # Alembic
                file_parm = n.parm('fileName')
            elif hasattr(n, 'parm') and n.parm('soppath'):  # FBX
                file_parm = n.parm('soppath')
            
            if file_parm:
                file_path = file_parm.eval()
                if file_path:
                    folder_path = os.path.dirname(file_path)
                    break

# Default folder path if none found
if folder_path is None:
    folder_path = hou.expandString("$HIP")  # Use hip file directory as fallback

# Find all *_OUT null nodes
for n in net.children():
    if n.type().name() == "null" and n.name().endswith("_OUT"):
        nulls.append(n)

# Create work items for each null
for i, n in enumerate(nulls):
    wi = item_holder.addWorkItem(index=i)
    wi.setStringAttrib("soppath", n.path())          
    wi.setStringAttrib("partname", n.name()[:-4])  # Remove "_OUT" suffix   
    wi.setStringAttrib("folderpath", folder_path)
'''
    gather.parm("generate").set(generate_code)

    #--------------------------------------------------------------
    # 3. ROP Geometry TOP
    #--------------------------------------------------------------
    rop_geo.parm("usesoppath").set(1)  # Turn on SOP Path
    rop_geo.parm("soppath").set('`@soppath`')

    # Create exports directory if it doesn't exist and set output path
    rop_geo.parm("sopoutput").set("`@folderpath`/exports/`@partname`.bgeo.sc")
    rop_geo.parm("pdg_cachemode").set(3)  # 3 = Write Files

    #--------------------------------------------------------------
    # 4. Tidy layout
    #--------------------------------------------------------------
    topnet.layoutChildren()

    # Display success message
    hou.ui.displayMessage(
        f"TOP network '{topnet.name()}' created successfully!\n\n"
        f"The network will:\n"
        f"• Find all *_OUT null nodes in the SOP network\n"
        f"• Export each part as a separate .bgeo.sc file\n"
        f"• Save files to: {folder_path}/exports/\n\n"
        f"Click 'Cook Output Node' on the ROP Geometry node to start export.",
        severity=hou.severityType.Message,
        title="Export TOP Network Created"
    )

    return topnet