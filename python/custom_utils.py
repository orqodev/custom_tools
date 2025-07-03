import logging

def reload_packages(kwargs):
    """
        This is a fucntions that reloads the rebelway packages
        Args:
            kwargs (dict): Goint to check if the alt key is pressed
            if it is , it will reload the python modules
    """
    import hou
    import importlib
    import os
    import sys


    # reload the package
    package_path = hou.text.expandString("$HOUDINI_USER_PREF_DIR/packages/") + "custom_tools.json"
    hou.ui.reloadPackage(package_path)

    # reload the python modules
    folder_path = hou.text.expandString("$RBW/scripts/python")

    # reload the python modules
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file).replace(os.sep, "/")
                module_name = os.path.relpath(module_path, folder_path).replace(os.sep, ".").replace(".py", "")

                try:
                    if module_name in sys.modules:
                        if kwargs["altclick"] == True:
                            sys.modules[module_name] = importlib.import_module(module_name)
                            importlib.reload(sys.modules[module_name])
                            print(f"Reloaded Module: {module_name}")
                    else:
                        importlib.import_module(module_name)
                        print(f"{module_name} was imported")
                except Exception as error:
                    print(f"Failed to import or reload the module {module_name}: {error}")

# reload the menus
    hou.hscript("menurefresh")
    
# reload the shelves
    shelves = hou.shelves.shelves()
    path_shelves = hou.text.expandString("$RBW/toolbar")

    for root, dir, files in os.walk(path_shelves):
        for file in files:
            if file.endswith(".shelf"):
                shelf_path = os.path.join(root, file)
                hou.shelves.loadFile(shelf_path)

def check_path_valid(path):
    '''
    This is a fuction that checks if the path is valid.
    :Args:
        path: The path to check
    :return:
        True: if the path is valid
    '''
    import hou
    import os

    ## FIX the path if is using a env variable - $HIP, $HOME, $RBW
    path = os.path.dirname(hou.text.expandString(path))

    ## Check if the path exists
    if os.path.exists(path) and os.access(path, os.R_OK):
        print(f"The path {path} is valid")
        return path
    else:
        print(f"The path {path} is not valid")
        hou.ui.displayMessage(f"The path {path} is not valid. Please try again.", title="Error")

def clean_log():
    print("\n" * 100)



# IF YOU NEED RESET THE LOGGER RUN
# logger.handlers.clear()

def get_logger(name="houdini_debug",log_file_name="houdini_debug.log",level=logging.DEBUG):
    import hou
    import logging
    import os
    import sys


    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger


    active_project = hou.getenv("PROJECT")
    project_path = hou.getenv("JOB")
    project_base_path = os.path.basename(project_path)
    print(project_path)
    if (active_project and project_base_path) and active_project.lower() == project_base_path.lower():
        folder_path = os.path.join(project_path, "logs")
    else:
        # Ask user to choose a folder if no match
        btn_pressed, values = hou.ui.readMultiInput(
            "Choose Log Folder",
            ("LOG PATH",),
            buttons=('Create', 'Cancel'),
            severity=hou.severityType.Message,
            help="Please provide a path for your logs.",
            title="Select log path",
            initial_contents=("Untitled",)
        )

        if btn_pressed != 0:  # 0 = 'Create' button
            return logger  # Return empty logger if canceled

        folder_path = os.path.join(values[0], "logs")

    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to create log folder: {e}")
            return logger

    log_file_path = os.path.join(folder_path, log_file_name)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file_path, mode='w')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        logger.addHandler(file_handler)
    except Exception as e:
        hou.ui.displayMessage(f"FileHandler error: {e}")

    # Console Stream Handler (to Python Shell)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(stream_handler)

    logger.info(f"Logging started in: {log_file_path}")
    return logger