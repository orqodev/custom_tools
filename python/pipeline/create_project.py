import hou
import os
import json
import custom_utils

from PySide6 import QtCore, QtUiTools, QtWidgets, QtGui


class CreateProject(QtWidgets.QMainWindow):
    # CLASS CONSTANTS
    UI_FILE = "$CUSTOM_TOOLS/ui/project_creator.ui"
    CONFIG_DIR = "$CUSTOM_TOOLS/config"
    CONFIG_FILE = "projects_config.json"
    
    # Default folders that should be created for every project
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

    def __init__(self):
        super().__init__()
        # INITIALIZE UI
        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        '''
        Initialize the UI components
        :return:
        '''
        script_path = hou.text.expandString(self.UI_FILE)
        self.ui = QtUiTools.QUiLoader().load(script_path, parentWidget=self)
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        self.setWindowTitle('Project Creator')
        self.setMaximumSize(400, 500)
        
        # FIND UI COMPONENTS
        self.sel_directory = self.ui.findChild(QtWidgets.QPushButton, 'bt_directory')
        self.project_name = self.ui.findChild(QtWidgets.QLineEdit, 'le_proj_name')
        self.project_code = self.ui.findChild(QtWidgets.QLineEdit, 'le_proj')
        self.project_fps = self.ui.findChild(QtWidgets.QLineEdit, 'le_fps')
        self.project_folders = self.ui.findChild(QtWidgets.QPlainTextEdit, 'qpt_folders')
        self.create_project = self.ui.findChild(QtWidgets.QPushButton, 'bt_create_project')
        
        # SET UP VALIDATORS
        self.ui.int_validator = QtGui.QIntValidator()
        self.project_fps.setValidator(self.ui.int_validator)
        
        # SET INITIAL STATES
        self.project_name.setEnabled(False)
        self.project_code.setEnabled(False)
        self.project_fps.setEnabled(False)
        self.create_project.setEnabled(False)
        self.project_folders.setEnabled(False)

    def _setup_connections(self):
        '''
        Setup signal connections
        :return:
        '''
        self.sel_directory.clicked.connect(self.select_directory)
        self.create_project.clicked.connect(self.create_set_project)

    def select_directory(self):
        '''
        Grabs the folderss where to setup the new project
        '''
        start_directory = hou.text.expandString('$HOME')
        global directory
        directory = hou.ui.selectFile(start_directory=start_directory,
                                      title="Select a folders where the project is going to be created",
                                      file_type=hou.fileType.Directory)
        custom_utils.check_path_valid(directory)
        print(directory)
        if directory:
            self.project_name.setEnabled(True)
            self.project_name.textChanged.connect(self.check_button_state)
            self.project_code.setEnabled(True)
            self.project_code.textChanged.connect(self.check_button_state)
            self.project_fps.setEnabled(True)
            self.project_fps.textChanged.connect(self.check_button_state)
            self.project_folders.setEnabled(True)
            self.project_folders.textChanged.connect(self.check_button_state)
            self.raise_()

    def check_button_state(self):
        '''
        This enable the create project button only if the project code, project name and project fps hast text on it
        '''

        if (
                self.project_name.text().strip() and self.project_code.text().strip() and self.project_fps.text().strip() and self.project_folders.toPlainText().strip()):
            self.create_project.setEnabled(True)
        else:
            self.create_project.setEnabled(False)

    def create_set_project(self):
        '''
        Create the json file with the information provided by the user,
        grabs the path, name, code, fps and folders for a project.
        Saves it as JSON file
        '''
        project_name = self.project_name.text().strip()
        project_code = self.project_code.text().strip()
        project_fps = self.project_fps.text().strip()
        project_folders = [item_list.strip() for item_list in self.project_folders.toPlainText().split(',')]

        # Fix path concatenation bug - use os.path.join instead of string concatenation
        project_path = os.path.join(directory, project_name)

        project_dict = {
            project_name: {
                "PROJECT_CODE": project_code,
                "PROJECT_PATH": project_path,
                "PROJECT_FPS": project_fps,
                "PROJECT_FOLDERS": project_folders,
                "PROJECT_ACTIVE": False
            }
        }

        config_path = hou.text.expandString(self.CONFIG_DIR)
        json_file_path = os.path.join(config_path, self.CONFIG_FILE)
        data = []
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []

        if len(data) > 0:
            for existing_project in data:
                project_name_check = list(existing_project.keys())[0]
                project_data = existing_project[project_name_check]
                project_code_check = project_data["PROJECT_CODE"]
                if (project_name_check == project_name or project_code_check == project_code):
                    hou.ui.displayMessage(
                        f"A project with the same name or code already exists:\n\n"
                        f"Name:{project_name_check}\n"
                        f"Code: {project_code_check}\n"
                        f"Please choose a different name or code",
                        severity=hou.severityType.Error
                    )
                    return


        data.append(project_dict)

        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)

        print(f"Project data saved to {json_file_path}")

        project_root = os.path.join(directory, project_name)
        os.makedirs(project_root, exist_ok=True)

        # Create DEFAULT_FOLDERS first
        all_folders = set(self.DEFAULT_FOLDERS)  # Use set to avoid duplicates
        
        # Add user-specified folders (filter out empty strings)
        user_folders = [folder.strip() for folder in project_folders if folder.strip()]
        all_folders.update(user_folders)
        
        # Create all folders
        for folder in sorted(all_folders):  # Sort for consistent order
            folder_path = os.path.join(project_root, folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder}")

        print(f"Project folder structure created at {project_root}")
        print(f"Created {len(all_folders)} folders: {sorted(all_folders)}")
        hou.ui.displayMessage(f"Project {project_name} created at {project_root}\nCreated {len(all_folders)} folders including default pipeline structure.")


