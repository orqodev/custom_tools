import hou
import json
import os
import shutil

from PySide6 import QtCore, QtUiTools, QtWidgets, QtGui
from PySide6.QtCore import Qt
from pipeline.save_tool import SaveToolWindow


class ProjectManager(QtWidgets.QMainWindow):
    # CLASS CONSTANST
    CONFIG_DIR = "$CUSTOM_TOOLS/config"
    CONFIG_FILE = "projects_config.json"
    UI_FILE = "$CUSTOM_TOOLS/ui/project_manager.ui"
    DEFAULT_FOLDERS = [
        "geo",
        "hda",
        "sim",
        "abc",
        "tex",
        "render",
        "flip",
        "scripts",
        "comp",
        "audio",
        "video",
        "desk",
        "cache",
        "seq",
        "assets"
    ]
    FILE_EXTENSIONS = [".hip", ".hiplc", ".hipnc", ".hipl" ]

    def __init__(self):
        super().__init__()
        # INITIALIE UI
        self._init_ui()
        self._setup_connections()
        # STORE PROJECT DATA
        self.projects_data = []
        self.sequences_data = []
        self.files_data = []
        self.json_path = os.path.join(hou.text.expandString(self.CONFIG_DIR), self.CONFIG_FILE)
        # LOAD PROJECTS WHEN INITIALIZZING
        self.load_projects()
        self.save_tool_window = None

    def _init_ui(self):
        '''
        Initialise the UI components
        :return:
        '''
        script_path = hou.text.expandString(self.UI_FILE)
        self.ui = QtUiTools.QUiLoader().load(script_path, parentWidget=self)
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Project Manager")
        self.setMaximumSize(1280, 640)
        # PROJECTS
        self.project_list = self.ui.findChild(QtWidgets.QListWidget, "lw_projects")
        self.btn_delete = self.ui.findChild(QtWidgets.QPushButton, "bt_proj_delete")
        self.btn_project_details = self.ui.findChild(QtWidgets.QPushButton, "bt_proj_details")
        self.btn_project_disable = self.ui.findChild(QtWidgets.QPushButton, "bt_proj_disable")
        self.btn_project_enable = self.ui.findChild(QtWidgets.QPushButton, "bt_proj_enable")
        # SEQ/SCENES
        self.sequence_list = self.ui.findChild(QtWidgets.QListWidget, "lw_seq")
        self.btn_create_scene = self.ui.findChild(QtWidgets.QPushButton, "create_scene")
        self.btn_delete_scene = self.ui.findChild(QtWidgets.QPushButton, "delete_scene")
        # FILES
        self.file_list = self.ui.findChild(QtWidgets.QListWidget, "lw_files")
        self.btn_open_file = self.ui.findChild(QtWidgets.QPushButton, "bt_open")
        self.btn_save_file = self.ui.findChild(QtWidgets.QPushButton, "bt_save")
        # STATUS
        self.status_line = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit")

    def _setup_connections(self):
        '''
        Setup connections
        :return:
        '''
        self.btn_project_details.clicked.connect(self.show_project_details)
        self.btn_project_enable.clicked.connect(lambda: self.toggle_project(True))
        self.btn_project_disable.clicked.connect(lambda: self.toggle_project(False))
        self.btn_delete.clicked.connect(self.remove_projects)
        self.project_list.currentItemChanged.connect(self.handle_item_change)
        self.btn_create_scene.clicked.connect(self.create_scene)
        self.btn_delete_scene.clicked.connect(self.delete_scene)
        self.sequence_list.currentItemChanged.connect(self.handle_scene_change)
        self.btn_open_file.clicked.connect(self.open_file)
        self.btn_save_file.clicked.connect(self.show_save_tool)

    def handle_item_change(self, current, previous):
        """
        Only call load_scenes when there is a valid current item
        Args:
            current: The current QListWidgetItem
            previous: The previous QListWidgetItem
        """
        if current is not None:
            self.load_scenes()

    def handle_scene_change(self, current, previous):
        """
        Only call load_scenes when there is a valid current item
        Args:
            current: The current QListWidgetItem
            previous: The previous QListWidgetItem
        """
        if current is not None:
            self.load_files()

    def update_status(self, message, severity=None):
        '''
        Update status line and optionally display message
        :param message (str): Message to display
        :param severity (hou.SeverityType,optional): Severity for UI display
        '''
        self.status_line.setText(message)
        if severity is not None:
            hou.ui.displayMessage(message, severity=severity)

    def get_selected_project(self):
        """
        Get currently selected project or display error
        Returns:
            tuple: (project_name, project_data) or (None, None) if no selection
        """
        if not self.project_list.selectedItems():
            self.update_status("Please select a project", hou.severityType.Error)
            return None, None

        project_name = self.project_list.currentItem().text()
        project_data = None

        for project in self.projects_data:
            if project_name in project:
                project_data = project[project_name]
                break

        return project_name, project_data

    def get_selected_scene(self):
        """
        Get currently selected scene_error or display error
        Returns:
           scene_name
        """
        if  self.sequence_list.count() == 0:
            return None

        if self.sequence_list.count() > 0 and not self.sequence_list.selectedItems():
            self.update_status("Please select a scene", hou.severityType.Error)
            return None

        scene_name = self.sequence_list.currentItem().text()
        return scene_name

    def get_selected_file(self,save=False):
        """
        Get currently selected scene_error or display error
        Returns:
           file_name
        """
        if  self.file_list.count() == 0:
            if save == True:
                btn_pressed, file_name = hou.ui.readMultiInput("Create New File",
                                                                 ("File Name",),
                                                                 buttons=('Create', 'Cancel'),
                                                                 severity=hou.severityType.Message,
                                                                 help="It was not file selected. You can create a new file.",
                                                                 title="Create File",
                                                                 initial_contents=("Untitled",))
                if btn_pressed == 1:
                    return
                return file_name[0]
            else:
                return None
        if self.file_list.count() > 0 and not self.file_list.selectedItems():
            message = "Please select a file"
            self.update_status(message, hou.severityType.Error)
            return None

        file_name = self.file_list.currentItem().text()
        return file_name

    def load_projects(self):
        '''
        Load projects from the json file and populate the project list
        '''

        try:
            with open(self.json_path, 'r') as file:
                self.projects_data = json.load(file)
            projects_names = []
            active_project_index = 0
            for index,project in enumerate(self.projects_data):
                project_name = list(project.keys())[0]
                projects_names.append(project_name)

                if project[project_name].get("PROJECT_ACTIVE",False):
                    hou.putenv("JOB", project[project_name]["PROJECT_PATH"])
                    active_project_index = index

            self.project_list.clear()
            projects_names.sort()
            # ADD SORTED PROJECTS NAMES TO THE LIST WIDGETS
            for name in projects_names:
                self.project_list.addItem(name)
            self.update_status(f"{self.json_path} was loaded")

            # Select first item
            if self.project_list.count() > 0:
                sorted_active_index = projects_names.index(list(self.projects_data[active_project_index].keys())[0])
                self.project_list.setCurrentRow(sorted_active_index)

        except Exception as e:
            self.update_status(f"No project was found: {e}")

    def show_project_details(self):
        '''
        Diplay project details in the message box
        '''
        project_name, project_data = self.get_selected_project()
        if project_data:
            hou.ui.displayMessage(f"Project details for {project_name}:\n"
                                  f"Project CODE : {project_data['PROJECT_CODE']}\n"
                                  f"Project PATH : {project_data['PROJECT_PATH']}\n"
                                  f"Project FPS: {project_data['PROJECT_FPS']}\n",
                                  title=f"Details for {project_name}")
        else:
            self.update_status(f"Project {project_name} not found", hou.severityType.Error)

    def toggle_project(self, status=True):
        '''
        Toggle the project env variables
        Args:
            status (bool): True to enable, False to disable

        '''
        project_name, project_data = self.get_selected_project()

        env_vars = {"JOB": "", "CODE": "", "FPS": "", "PROJECT": ""}

        # FIND THE PROJECT DATA
        if status:
            if project_data:
                for project in self.projects_data:
                    project_current_name = list(project.keys())[0]
                    project[project_current_name]["PROJECT_ACTIVE"] = project_name == project_current_name
                env_vars.update({
                    "JOB": project_data['PROJECT_PATH'],
                    "CODE": project_data['PROJECT_CODE'],
                    "FPS": project_data['PROJECT_FPS'],
                    "PROJECT": project_name
                })
            else:
                self.update_status(f"Could not find data for project {project_name}", hou.severityType.Error)
                return
            status_msg = f"Current Active Project is:{project_name}"
        else:
            for project in self.projects_data:
                project_current_name = list(project.keys())[0]
                if project_name == project_current_name:
                    project[project_name]["PROJECT_ACTIVE"] = status
            status_msg = f"Project: {project_name} is disabled"

        with open(self.json_path, 'w') as file:
            json.dump(self.projects_data, file, indent=4, sort_keys=True)
        print(env_vars)
        for var, value in env_vars.items():
            print(f"{var}: {value}")
            hou.putenv(var, value)

        self.update_status(status_msg)

    def remove_projects(self):
        '''
        Remove the selected project from the JSON file, the list widget and deletes the folder
        :return:
        '''
        project_name, project_data = self.get_selected_project()
        if not project_name:
            return

        confirm_delete = hou.ui.displayMessage(f"Are you sure you want to delete this project: {project_name}???\n"
                                               f"ATTENTION!!! - This action will delete all the folders and files for this project!",
                                               buttons=("Yes", "No"),
                                               severity=hou.severityType.Warning)

        if confirm_delete == 1:
            return

        try:
            with open(self.json_path, 'r') as file:
                self.projects_data = json.load(file)

            project_path_delete = None

            for project in self.projects_data:
                if project_name in project:
                    project_data = project[project_name]
                    project_path_delete = project_data["PROJECT_PATH"]
                    self.projects_data.remove(project)
                    break
            if project_path_delete:
                if os.path.exists(project_path_delete):
                    try:
                        shutil.rmtree(project_path_delete)
                    except Exception as e:
                        error_msg = f"Error deleting project directory: {str(e)}"
                        self.update_status(error_msg, severity=hou.severityType.Error)
            with open(self.json_path, 'w') as file:
                json.dump(self.projects_data, file, indent=4, sort_keys=True)

            self.load_projects()
            success_message = f"Project {project_name} has been deleted"
            self.update_status(success_message)

        except Exception as e:
            error_msg = f"Error during project deletion: {str(e)}"
            self.update_status(error_msg, severity=hou.severityType.Error)

    def load_scenes(self):
        '''
        This loads the folders inside the SEQ folder for each project
        '''
        project_name, project_data = self.get_selected_project()
        if not project_name or not project_data:
            return

        try:
            self.sequence_list.clear()
            self.file_list.clear()
            sequences = []



            for project in self.projects_data:
                if project_name in project:
                    projec_data = project[project_name]
                    seq_path = os.path.join(projec_data["PROJECT_PATH"], "seq").replace(os.sep, "/")

                    if os.path.exists(seq_path):

                        sequences = []

                        for dir in os.listdir(seq_path):
                            if os.path.isdir(os.path.join(seq_path, dir)):
                                sequences.append(dir)
                        sequences.sort()

                        for scene in sequences:
                            self.sequence_list.addItem(scene)
                    else:
                        error_msg = f"No sequence folder found for the project {project_name}"
                        self.status_line.setText(error_msg)
                    break
            if self.sequence_list.count() > 0:
                self.sequence_list.setCurrentRow(0)
            self.sequences_data = sequences
        except Exception as e:
            error_msg = f"Error loading sequences: {str(e)}"
            self.update_status(error_msg, hou.severityType.Error)

    def create_scene(self):
        project_name, project_data = self.get_selected_project()
        if not project_name or not project_data:
            return
        default_folders = (",").join(self.DEFAULT_FOLDERS)
        btn_pressed, (scene_name, extra_folders) = hou.ui.readMultiInput("Create New Scene",
                                                                         ("Scene Name", "Extra Folders"),
                                                                         buttons=('Create', 'Cancel'),
                                                                         severity=hou.severityType.Message,
                                                                         help=None,
                                                                         title="Create Scene",
                                                                         initial_contents=("", default_folders))



        # Ensure the seq directory exists before creating scene folders
        seq_dir = os.path.join(project_data["PROJECT_PATH"], "seq")
        os.makedirs(seq_dir, exist_ok=True)
        
        scene_path = os.path.join(project_data["PROJECT_PATH"], "seq", scene_name).replace(os.sep, "/")
        if btn_pressed == 1:
            return
        scene_exists = False

        if scene_name in self.sequences_data:
            scene_exists = True

        try:
            if scene_exists:
                btn_pressed = hou.ui.displayMessage(f"Project {scene_name} already exists.\n"
                                                    f"Do you want to overwrite it???\n"
                                                    f"All the folders inside the scene folder will be deleted.",
                                                    buttons=("Yes", "No"))
                if btn_pressed == 1:
                    return
                for folder in os.listdir(scene_path):
                    folder_path = os.path.join(scene_path, folder)
                    shutil.rmtree(folder_path, ignore_errors=True)

                for folder in extra_folders.split(","):
                    folder_path = os.path.join(scene_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
            else:
                try:
                    self.sequence_list.addItem(scene_name)
                    self.sequence_list.sortItems(Qt.AscendingOrder)
                    os.makedirs(scene_path, exist_ok=True)
                    for folder in extra_folders.split(","):
                        folder_path = os.path.join(scene_path, folder)
                        os.makedirs(folder_path, exist_ok=True)
                    self.update_status(f"Scene {scene_name} has been created.\n")
                except Exception as e:
                    error_msg = f"Error creating folder: {str(e)}"
                    self.update_status(error_msg, severity=hou.severityType.Error)
        except Exception as e:
            error_message = f"Error during scene creation: {str(e)}"
            self.update_status(error_message,severity=hou.severityType.Error)

    def delete_scene(self):
        scene_name = self.get_selected_scene()
        project_name, project_data = self.get_selected_project()
        if not scene_name:
            return

        confirm_delete = hou.ui.displayMessage(f"Are you sure you want to delete this scene: {scene_name}???\n"
                                               f"ATTENTION!!! - This action will delete all the folders and files for this scene!",
                                               buttons=("Yes", "No"),
                                               severity=hou.severityType.Warning)
        if confirm_delete == 1:
            return
        self.sequence_list.clear()
        self.file_list.clear()
        try:
            for scene in self.sequences_data:
                if scene_name in scene:
                    self.sequences_data.remove(scene)
            for seq in self.sequences_data:
                self.sequence_list.addItem(seq)
            scene_path = os.path.join(project_data["PROJECT_PATH"], "seq", scene_name).replace(os.sep, "/")
            if scene_path:
                if os.path.exists(scene_path):
                    try:
                        shutil.rmtree(scene_path)
                    except Exception as e:
                        error_msg = f"Error deleting scene scene and directories: {str(e)}"
                        self.update_status(error_msg, severity=hou.severityType.Error)
            if self.sequence_list.count() > 0:
                self.sequence_list.setCurrentRow(0)
        except Exception as e:
            error_msg = f"Error during scene deletion: {str(e)}"
            self.update_status(error_msg, severity=hou.severityType.Error)

    def load_files(self):
        scene_name = self.get_selected_scene()
        if not scene_name:
            return
        project_name, project_data = self.get_selected_project()
        scene_path = os.path.join(project_data["PROJECT_PATH"], "seq", scene_name).replace(os.sep, "/")
        if scene_path:
            self.files_data = []
            self.file_list.clear()
            if os.path.exists(scene_path):
                for root, dir, files in os.walk(scene_path):
                    for file in files:
                        ext = os.path.splitext(file)[1]
                        if ext in self.FILE_EXTENSIONS:
                            file_path = os.path.normpath(os.path.join(root, file))
                            self.files_data.append(file_path)
                            self.file_list.addItem(file)

    def open_file(self):
        file_name = self.get_selected_file()
        if not file_name:
            return
        for file in self.files_data:
            current_file = os.path.basename(file)
            if current_file == file_name:
                hou.hipFile.load(file)

    def show_save_tool(self):
        scene_name = self.get_selected_scene()
        project_name, project_data = self.get_selected_project()
        file_name = self.get_selected_file(save=True)
        if not project_name:
            return
        if not scene_name:
            return
        if not file_name:
            return
        file_name = file_name.split(".")[0]
        if not self.save_tool_window:
            self.save_tool_window = SaveToolWindow(project_data,scene_name,project_name,file_name)
            # Connect the file saved signal to load the method load_hip_files
            self.save_tool_window.file_saved.connect(self.load_files)
        else:
            self.save_tool_window.project_data = project_data
            self.save_tool_window.scene_name = scene_name
            self.save_tool_window.project_name = project_name
            self.save_tool_window.file_name = file_name
            self.save_tool_window.update_project_info()
            self.save_tool_window.update_preview_path()
        self.save_tool_window.show()
        self.save_tool_window.raise_()



