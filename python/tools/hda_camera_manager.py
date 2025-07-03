import hou
from hou import severityType


class MultiCameraManager:
    '''
    Helps managing multiple cameras in a Houdini scene.
    Allows to set cameras - set camera, set frame range
    Allows batch rename camera
    Merge all cameras into one single camera
    Render submission
    '''

    def __init__(self,**kwargs):
        ''' Initialize variable and context location'''
        self.cameras = {}
        self.obj = hou.node('/obj')
        self.node = kwargs.get('node',None)
        self.CAMERA_PARMS = ['tx', 'ty', 'tz', "rx", "ry", "rz", "resx", "resy",
                             "aspect", "focal", "aperture", "near","far", "focus", "fstop"]

    def scan_scene_cameras(self):
        ''' Scan the scene for camera nodes and stores that info in self.cameras'''
        try:
            # Find all the cameras
            self.cameras = {
                cam.name() : cam for cam in self.obj.recursiveGlob("*",filter=hou.nodeTypeFilter.ObjCamera)
            }
            if not self.cameras:
                hou.ui.displayMessage(f"No cameras found",severity=hou.severityType.Error)
                return
            self._update_ui_camera()
        except Exception as e:
            hou.ui.displayMessage(
                f"Error scanning the scene for cameras:{str(e)}",
                    severity=hou.severityType.Error)

    def _update_ui_camera(self):
        ''' Build the UI menu paramater for found cameras'''
        # Set node
        if not self.node:
            self.node = hou.pwd()
        cam_list = list(self.cameras.keys())
        node_ptg = self.node.parmTemplateGroup()
        camera_selection = node_ptg.find("camera_selector")
        new_menu = hou.MenuParmTemplate(
            name="camera_selector",
            label="Select Camera",
            menu_items = cam_list,
            menu_labels = cam_list,
        )
        if not camera_selection:
            node_ptg.insertAfter("scan_scene", new_menu)
        else:
            node_ptg.replace(camera_selection, new_menu)
        self.node.setParmTemplateGroup(node_ptg)
        self.node.parm("set_visible").set(1)
        self.node.parm("render_label").set("ALL")

    def set_active_camera(self):
        """Set specified camera as viewport"""

        # Get current camera
        cam_name = self.node.parm("camera_selector").rawValue()
        camera = self.cameras[cam_name]

        # Get viewport
        viewport = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if viewport:
            viewport.curViewport().setCamera(camera)
            self._get_camera_frame_range(camera)

    def _get_camera_frame_range(self,camera):
        """
        Gets the frame range of the specified camera and sets the playback range
        :param camera - camera to check
        """
        first_frame = hou.playbar.playbackRange()[0]
        last_frame = hou.playbar.playbackRange()[1]
        keyframes = []
        try:
            # Check if camera has keyframes
            if any(camera.parm(parms).isTimeDependent() for parms in self.CAMERA_PARMS):
                for parm in self.CAMERA_PARMS:
                    parm_keyframes = camera.parm(parm).keyframes()
                    if parm_keyframes:
                        keyframes.extend(value.frame() for value in parm_keyframes)
                if keyframes:
                    first_frame = min(keyframes)
                    last_frame = max(keyframes)

                hou.playbar.setPlaybackRange(first_frame, last_frame)
                set_global_frame_range = f"tset `({first_frame}-1/$FPS)` `({last_frame}/$FPS)`)"
                hou.hscript(set_global_frame_range)
                hou.setFrame(first_frame)
            return keyframes
        except  UnboundLocalError:
            return keyframes

    def merge_cameras(self):
        '''
        Merge all cameras in the scene into a single camera with sequential animations
        Camera animations are arranged sequentially with each camera's animations starting
        after previous camera's last keyframe.
        '''

        # Create the new camera node
        merged_cam = self.obj.createNode("cam","merged_camera")

        sorted_cameras = self._sorted_cameras()

        current_frame = 1000
        # Process each camera sequentially
        for cam_name, cam_data in sorted_cameras.items():
            camera = cam_data["camera"]
            original_frames = cam_data["frames"]
            if original_frames:
                #Calculate the frame offset
                frame_offset = current_frame - cam_data["start"]
                for parm_name in self.CAMERA_PARMS:
                    source_parm = camera.parm(parm_name)
                    target_parm = merged_cam.parm(parm_name)
                    if source_parm and target_parm:
                        #Get keyframes for the parm
                        keyframes = source_parm.keyframes()
                        if keyframes:
                            for key in keyframes:
                                new_key = hou.Keyframe()
                                new_key.setFrame(key.frame()+frame_offset)
                                new_key.setValue(key.value())
                                new_key.setExpression(key.expression())
                                target_parm.setKeyframe(new_key)
                        else:
                            # If the parameter is not animated but has a value
                            new_key = hou.Keyframe()
                            new_key.setFrame(current_frame)
                            new_key.setValue(source_parm.eval())
                            target_parm.setKeyframe(new_key)
                # Update current frame for the next camera
                current_frame += (cam_data["end"] - cam_data["start"] + 1)
            else:
                # for non animated cameras - create a single keyframe
                for parm_name in self.CAMERA_PARMS:
                    source_parm = camera.parm(parm_name)
                    target_parm = merged_cam.parm(parm_name)
                    if source_parm and target_parm:
                        new_key = hou.Keyframe()
                        new_key.setFrame(current_frame)
                        new_key.setValue(source_parm.eval())
                        target_parm.setKeyframe(new_key)
                current_frame += 1
        if current_frame > 1001:
            hou.playbar.setPlaybackRange(1001, current_frame -1)
            set_global_frame_range = f"tset `1001/$FPS` `{current_frame - 1}/$FPS`)"
            hou.hscript(set_global_frame_range)
            hou.setFrame(1001)

    def _sorted_cameras(self):
        ''' Sorts cameras by the lowest keyframe and gets the start, end and all keyframes
        :returns
        sorted_camera dict - dictionary containing alll the cameras sorted
        '''
        cameras_to_merge = {}
        for name, camera in self.cameras.items():
            frames = list(set(self._get_camera_frame_range(camera)))
            cameras_to_merge[name] = {
                "camera": camera,
                "frames": frames,
                "start": min(frames) if frames else float("inf"),
                "end": max(frames) if frames else float("inf"),
            }
        # Sort cameras by their start frame
        sorted_cameras = dict(sorted(cameras_to_merge.items(), key=lambda x: x[1]["start"]))
        return sorted_cameras

    def select_rendering_node(self):
        '''
        Select a karma node and setupt the rendering parameters base on a selected camera.
        :return:
        '''

        #Select karma node
        karma_node = hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.Rop)

        if not karma_node:
            hou.ui.displayMessage(f"Node valid rop node selected.",severity=hou.severityType.Error)
            return

        karma_node = hou.node(karma_node)

        # Check cameras to render
        sorted_cameras = self._sorted_cameras()
        cameras_to_render = {}
        cam_input = self.node.parm("render_label").evalAsString().split(",")

        if cam_input[0].lower() == "all":
            cameras_to_render = sorted_cameras
        else:
            camera_selection = [cam.strip() for cam in cam_input]
            cameras_to_render = {name: sorted_cameras[name] for name in camera_selection if name in sorted_cameras}

        if not cameras_to_render:
            hou.ui.displayMessage(f"No valid cameras found for rendering",severity= hou.severityType.Error)
            return

        #process each camera
        for cam_name, camera in cameras_to_render.items():
            base_output = "$HIP/render/$HIPNAME.$OS.$F4.exr"
            camera_output = base_output.replace(".$F4.exr",f".{cam_name}.$F4.exr")
            is_animated = camera["frames"]

            if is_animated:
                first_frame = min(is_animated)
                last_frame = max(is_animated)
                set_value = 1
            else:
                set_value = 0

            resx = camera["camera"].parm("resx").eval()
            resy = camera["camera"].parm("resy").eval()

            # Set karma parameters
            karma_node.parmTuple("f").deleteAllKeyframes()
            karma_node.parm('trange').set(set_value)
            if set_value:
                karma_node.parm("f1").set(first_frame)
                karma_node.parm("f2").set(last_frame)
            karma_node.parm("picture").set(camera_output)
            karma_node.parm("camera").set(camera["camera"].path())
            karma_node.parm("picture").set(camera_output)
            karma_node.parm("resolutionx").set(resx)
            karma_node.parm("resolutiony").set(resy)
            karma_node.parm("mplay").pressButton()

    def replace_cameras_name(self):
        """Replace the name of all the cameras with prefix and suffix"""
        try:
            # Find all the cameras
            prefix = self.node.parm("name_prefix").eval()
            suffix = self.node.parm("name_suffix").eval()
            cameras = self.obj.recursiveGlob("*", filter=hou.nodeTypeFilter.ObjCamera)
            if not cameras:
                hou.ui.displayMessage(f"No cameras found", severity=hou.severityType.Error)
                return
            for index,cam in enumerate(cameras):
                new_name = f"{prefix}{suffix}{index+1}"
                cam.setName(new_name)
            self._update_ui_camera()
        except Exception as e:
            hou.ui.displayMessage(
                f"Error replacing the cameras name:{str(e)}",severity=hou.severityType.Error)



