import os
import hou
import random
import colorsys
from typing import List


def create_component_builder(selected_directory=None):
    '''
    Main function to create the component builder for Houdini FX
    This version works with geometry nodes instead of USD/Solaris
    '''
    
    # Get File
    if selected_directory is None:
        selected_directory = hou.ui.selectFile(title="Select the file you want to import",
                                               file_type=hou.fileType.Geometry,
                                               multiple_select=False)
    selected_directory = hou.text.expandString(selected_directory)

    try:
        if os.path.exists(selected_directory):
            # Define context - using /obj instead of /stage
            obj_context = hou.node("/obj")

            # Get the path and filename and the folder with the textures
            path, filename = os.path.split(selected_directory)
            folder_textures = os.path.join(path, "maps").replace(os.sep, "/")

            # Get asset name and extension
            asset_name = filename.split(".")[0]
            asset_extension = filename.split(".")[-1]
            if filename.endswith("bgeo.sc"):
                asset_name = filename.split(".")[0]
                asset_extension = "bgeo.sc"

            # Create main geometry container
            geo_container = obj_context.createNode("geo", f"{asset_name}_geo")
            
            # Create material network
            material_net = obj_context.createNode("matnet", f"{asset_name}_materials")
            
            # Create camera for lookdev
            camera_node = obj_context.createNode("cam", f"{asset_name}_camera")
            
            # Create lights setup
            light_nodes = _create_lighting_setup(obj_context, asset_name)
            
            # Prepare the imported asset in the geometry container
            _prepare_imported_asset(geo_container, asset_name, asset_extension, path, selected_directory)
            
            # Create materials for geometry context
            _create_materials(material_net, folder_textures, asset_name)
            
            # Setup camera for asset viewing
            _setup_camera(camera_node, geo_container)
            
            # Create render setup
            render_node = _create_render_setup(obj_context, asset_name, camera_node)
            
            # Layout all nodes
            all_nodes = [geo_container, material_net, camera_node] + light_nodes + [render_node]
            obj_context.layoutChildren(all_nodes)
            
            # Create organized network notes
            create_organized_net_note(f"Asset {asset_name.upper()}", 
                                        [geo_container, material_net], 
                                        hou.Vector2(0, 0))
            create_organized_net_note("Lighting Setup", 
                                        light_nodes, 
                                        hou.Vector2(-3, 0))
            create_organized_net_note("Camera & Render", 
                                        [camera_node, render_node], 
                                        hou.Vector2(3, 0))
            
            # Select the main geometry node
            geo_container.setSelected(True, clear_all_selected=True)
            
            # Set display flags
            geo_container.setGenericFlag(hou.nodeFlag.Display, True)
            camera_node.setGenericFlag(hou.nodeFlag.Display, True)

    except Exception as e:
        hou.ui.displayMessage(f"An error happened in create component builder: {str(e)}",
                              severity=hou.severityType.Error)


def _prepare_imported_asset(parent, name, extension, path, full_path):
    '''
    Creates the network layout for importing and preparing geometry assets
    Args:
        parent: geometry node where the file needs to be imported
        name: asset's name
        extension: file extension (FBX, ABC, OBJ, etc)
        path: path where the asset is located
        full_path: complete path to the asset file
    '''
    
    try:
        # Create the file import node based on extension
        file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
        if extension in file_extension:
            file_import = parent.createNode("file", f"import_{name}")
            file_import.parm("file").set(full_path)
        elif extension == "abc":
            file_import = parent.createNode("alembic", f"import_{name}")
            file_import.parm("fileName").set(full_path)
        else:
            hou.ui.displayMessage(f"Unsupported file format: {extension}", 
                                severity=hou.severityType.Warning)
            return

        # Create processing nodes
        transform_node = parent.createNode("xform", f"transform_{name}")
        normal_node = parent.createNode("normal", f"normals_{name}")
        material_node = parent.createNode("material", f"assign_material_{name}")
        
        # Create proxy version
        proxy_reduce = parent.createNode("polyreduce::2.0", f"proxy_{name}")
        proxy_color = parent.createNode("color", f"proxy_color_{name}")
        
        # Create collision/sim version
        convex_hull = parent.createNode("shrinkwrap::2.0", f"collision_{name}")
        
        # Create output nulls for different versions
        render_output = parent.createNode("null", "RENDER_OUTPUT")
        proxy_output = parent.createNode("null", "PROXY_OUTPUT")
        sim_output = parent.createNode("null", "SIM_OUTPUT")
        
        # Set parameters
        transform_node.setParms({
            "px": 0, "py": 0, "pz": 0,
            "rx": 0, "ry": 0, "rz": 0,
            "sx": 1, "sy": 1, "sz": 1
        })
        
        normal_node.setParms({
            "type": 0,  # Point normals
            "cuspangle": 60
        })
        
        proxy_reduce.parm("percentage").set(10)  # 10% of original geometry
        
        proxy_color.setParms({
            "colorr": 0.8,
            "colorg": 0.4,
            "colorb": 0.2
        })
        
        # Connect render chain
        normal_node.setInput(0, file_import)
        transform_node.setInput(0, normal_node)
        material_node.setInput(0, transform_node)
        render_output.setInput(0, material_node)
        
        # Connect proxy chain
        proxy_reduce.setInput(0, transform_node)
        proxy_color.setInput(0, proxy_reduce)
        proxy_output.setInput(0, proxy_color)
        
        # Connect sim chain
        convex_hull.setInput(0, transform_node)
        sim_output.setInput(0, convex_hull)
        
        # Layout nodes
        parent.layoutChildren()
        
        # Set display flag on render output
        render_output.setGenericFlag(hou.nodeFlag.Display, True)
        render_output.setGenericFlag(hou.nodeFlag.Render, True)

    except Exception as e:
        hou.ui.displayMessage(f"An error happened in prepare imported assets: {str(e)}",
                              severity=hou.severityType.Error)


def _create_lighting_setup(parent, asset_name):
    '''
    Create a three-point lighting setup for geometry viewing
    Args:
        parent: parent context to create lights in
        asset_name: name of the asset for naming lights
    Returns:
        list of created light nodes
    '''
    
    try:
        # Key light (main light)
        key_light = parent.createNode("hlight", f"{asset_name}_key_light")
        key_light.setParms({
            "light_type": "distant",
            "light_intensity": 1.0,
            "light_color": (1.0, 0.95, 0.9),
            "tx": 2, "ty": 3, "tz": 2,
            "rx": -30, "ry": 45, "rz": 0
        })
        
        # Fill light (softer secondary light)
        fill_light = parent.createNode("hlight", f"{asset_name}_fill_light")
        fill_light.setParms({
            "light_type": "distant",
            "light_intensity": 0.4,
            "light_color": (0.9, 0.95, 1.0),
            "tx": -2, "ty": 2, "tz": 1,
            "rx": -20, "ry": -30, "rz": 0
        })
        
        # Rim light (back light for edge definition)
        rim_light = parent.createNode("hlight", f"{asset_name}_rim_light")
        rim_light.setParms({
            "light_type": "distant",
            "light_intensity": 0.6,
            "light_color": (1.0, 1.0, 0.95),
            "tx": -1, "ty": 1, "tz": -3,
            "rx": 10, "ry": 180, "rz": 0
        })
        
        return [key_light, fill_light, rim_light]
        
    except Exception as e:
        hou.ui.displayMessage(f"Error creating lighting setup: {str(e)}", 
                              severity=hou.severityType.Error)
        return []


def _create_materials(material_net, folder_textures, asset_name):
    '''
    Create materials for geometry context
    Args:
        material_net: material network node
        folder_textures: path to texture folder
        asset_name: name of the asset
    '''
    
    try:
        # Create a basic principled shader
        principled_shader = material_net.createNode("principledshader::2.0", f"{asset_name}_material")
        material_output = material_net.createNode("output", f"{asset_name}_output")
        
        # Connect shader to output
        material_output.setInput(0, principled_shader)
        
        # If textures folder exists, try to load basic textures
        if os.path.exists(folder_textures):
            texture_files = os.listdir(folder_textures)
            
            # Look for common texture types
            diffuse_tex = None
            normal_tex = None
            rough_tex = None
            
            for tex_file in texture_files:
                tex_lower = tex_file.lower()
                if any(keyword in tex_lower for keyword in ['diffuse', 'albedo', 'color', 'base']):
                    diffuse_tex = os.path.join(folder_textures, tex_file)
                elif any(keyword in tex_lower for keyword in ['normal', 'norm']):
                    normal_tex = os.path.join(folder_textures, tex_file)
                elif any(keyword in tex_lower for keyword in ['rough', 'roughness']):
                    rough_tex = os.path.join(folder_textures, tex_file)
            
            # Create texture nodes if textures found
            if diffuse_tex:
                tex_node = material_net.createNode("texture::2.0", f"{asset_name}_diffuse")
                tex_node.parm("map").set(diffuse_tex)
                principled_shader.setInput(0, tex_node)  # Connect to basecolor
            
            if normal_tex:
                normal_node = material_net.createNode("texture::2.0", f"{asset_name}_normal")
                normal_node.parm("map").set(normal_tex)
                normal_node.parm("signature").set("normal")
                principled_shader.setInput(39, normal_node)  # Connect to normal
            
            if rough_tex:
                rough_node = material_net.createNode("texture::2.0", f"{asset_name}_roughness")
                rough_node.parm("map").set(rough_tex)
                rough_node.parm("signature").set("float")
                principled_shader.setInput(6, rough_node)  # Connect to roughness
        
        # Layout material network
        material_net.layoutChildren()
        
    except Exception as e:
        hou.ui.displayMessage(f"Error creating materials: {str(e)}", 
                              severity=hou.severityType.Error)


def _setup_camera(camera_node, geo_container):
    '''
    Setup camera to frame the imported geometry
    Args:
        camera_node: camera node to setup
        geo_container: geometry container to frame
    '''
    
    try:
        # Set camera parameters for good framing
        camera_node.setParms({
            "resx": 1920,
            "resy": 1080,
            "focal": 50,
            "tx": 3, "ty": 2, "tz": 3,
            "rx": -15, "ry": 45, "rz": 0
        })
        
        # Create a python script to auto-frame the geometry
        python_script = f'''
import hou

# Get the geometry bounds
geo_node = hou.node("{geo_container.path()}")
if geo_node:
    try:
        geo = geo_node.geometry()
        if geo:
            bbox = geo.boundingBox()
            center = bbox.center()
            size = bbox.size()
            max_size = max(size)
            
            # Position camera to frame the object
            distance = max_size * 2.5
            cam_node = hou.node("{camera_node.path()}")
            if cam_node:
                cam_node.setParms({{
                    "tx": center[0] + distance * 0.7,
                    "ty": center[1] + distance * 0.5,
                    "tz": center[2] + distance * 0.7
                }})
                
                # Look at the center
                import math
                dx = center[0] - cam_node.parm("tx").eval()
                dy = center[1] - cam_node.parm("ty").eval()
                dz = center[2] - cam_node.parm("tz").eval()
                
                ry = math.degrees(math.atan2(dx, dz))
                rx = math.degrees(math.atan2(-dy, math.sqrt(dx*dx + dz*dz)))
                
                cam_node.setParms({{"rx": rx, "ry": ry}})
    except:
        pass
'''
        
        # Add the script as a callback or execute it
        try:
            exec(python_script)
        except:
            pass  # Fallback to default camera position
            
    except Exception as e:
        hou.ui.displayMessage(f"Error setting up camera: {str(e)}", 
                              severity=hou.severityType.Error)


def _create_render_setup(parent, asset_name, camera_node):
    '''
    Create render setup for geometry (Mantra or other renderers)
    Args:
        parent: parent context
        asset_name: name of the asset
        camera_node: camera to render from
    Returns:
        render node
    '''
    
    try:
        # Create Mantra render node
        render_node = parent.createNode("ifd", f"{asset_name}_render")
        
        # Set basic render parameters
        render_node.setParms({
            "camera": camera_node.path(),
            "vm_picture": f"$JOB/render/{asset_name}.$F4.exr",
            "trange": 0,  # Render current frame
            "vm_renderengine": "pbrraytrace",
            "vm_samplesx": 3,
            "vm_samplesy": 3,
            "vm_maxraysamples": 9
        })
        
        return render_node
        
    except Exception as e:
        hou.ui.displayMessage(f"Error creating render setup: {str(e)}", 
                              severity=hou.severityType.Error)
        return None


def create_organized_net_note(asset_name, nodes_to_layout, offset_vector=hou.Vector2(0, 0)):
    '''
    Creates a network box and organizes nodes for geometry context
    Args:
        asset_name: Label text for the network box
        nodes_to_layout: List of nodes to include in the network box
        offset_vector: Position offset for the network box
    '''
    
    if not nodes_to_layout:
        return
        
    try:
        parent = nodes_to_layout[0].parent()
        
        # Generate colors
        main_color, secondary_color = _random_color()
        
        # Apply offset to nodes
        for node in nodes_to_layout:
            node.setPosition(node.position() + offset_vector)
        
        # Create network box
        network_box = parent.createNetworkBox()
        
        # Add nodes to network box
        for node in nodes_to_layout:
            network_box.addItem(node)
        
        # Set network box properties
        network_box.setComment(asset_name)
        network_box.setColor(main_color)
        network_box.fitAroundContents()
        
    except Exception as e:
        hou.ui.displayMessage(f"Error creating network organization: {str(e)}", 
                              severity=hou.severityType.Error)


def _random_color():
    '''Generate random colors for network organization'''
    red_color = random.random()
    green_color = random.random()
    blue_color = random.random()
    
    # Get main color
    main_color = hou.Color(red_color, green_color, blue_color)
    
    # Convert RGB to HSV for secondary color
    hue, saturation, value = colorsys.rgb_to_hsv(red_color, green_color, blue_color)
    new_saturation = saturation * 0.5
    
    # Get secondary color
    sec_red, sec_green, sec_blue = colorsys.hsv_to_rgb(hue, new_saturation, value)
    secondary_color = hou.Color(sec_red, sec_green, sec_blue)
    
    return main_color, secondary_color


# Utility function to create a simple UI for the asset builder
def show_asset_builder_ui():
    '''
    Simple UI to launch the asset builder
    '''
    try:
        result = hou.ui.displayMessage(
            "Asset Builder\n\nThis tool creates a geometry-based asset builder setup in Houdini FX.\n\nClick OK to select an asset file to import.",
            buttons=("OK", "Cancel"),
            severity=hou.severityType.Message,
            title="Asset Builder"
        )
        
        if result == 0:  # OK clicked
            create_component_builder()
    except Exception as e:
        hou.ui.displayMessage(f"Error in UI: {str(e)}", severity=hou.severityType.Error)


if __name__ == "__main__":
    # If run directly, show the UI
    show_asset_builder_ui()