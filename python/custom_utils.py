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
    import json


    # reload the package
    package_path = hou.text.expandString("$HOUDINI_USER_PREF_DIR/packages/") + "custom_tools.json"
    hou.ui.reloadPackage(package_path)

    # reload the python modules
    folder_path = hou.text.expandString("$CUSTOM_TOOLS/scripts/python")

    # Load optional settings to exclude folders during reload
    settings = {}
    settings_file_used = None
    candidate_paths = [
        os.path.join(folder_path, "reload_settings.json"),
        hou.text.expandString("$HOUDINI_USER_PREF_DIR/custom_tools_reload.json"),
        os.environ.get("CUSTOM_TOOLS_RELOAD_SETTINGS") or os.environ.get("RBW_RELOAD_SETTINGS") or ""
    ]
    for p in candidate_paths:
        if not p:
            continue
        try:
            if os.path.isfile(p):
                with open(p, "r") as f:
                    settings = json.load(f) or {}
                settings_file_used = p
                print(f"reload_packages: using settings from {p}")
                break
        except Exception as e:
            print(f"reload_packages: failed to read settings file {p}: {e}")

    exclude_list = settings.get("reload_exclude_dirs", settings.get("exclude_folders", []))
    # Normalize exclusion criteria
    exclude_names = set()
    exclude_paths = []
    if isinstance(exclude_list, list):
        for item in exclude_list:
            if not isinstance(item, str):
                continue
            item = item.strip()
            if not item:
                continue
            # If looks like a name (no slash), treat as folder name
            if ("/" not in item) and ("\\" not in item):
                exclude_names.add(item)
            # Otherwise treat as path (relative to folder_path if not abs)
            else:
                p = item
                if not os.path.isabs(p):
                    p = os.path.normpath(os.path.join(folder_path, p))
                else:
                    p = os.path.normpath(p)
                exclude_paths.append(p)

    # Always exclude common virtualenv and package cache folders by default
    default_exclude_names = {".venv", "venv", "env", "site-packages", "dist-packages", "__pycache__"}
    exclude_names |= default_exclude_names

    if exclude_names or exclude_paths:
        print(f"reload_packages: excluding folders by name {sorted(list(exclude_names))} and paths {exclude_paths}")

    # Prepare quick path segment checks (using forward slashes later)
    excluded_segments = {"/site-packages/", "/dist-packages/", "/.venv/", "/venv/", "/env/"}

    altclick = bool(kwargs.get("altclick"))

    # reload the python modules
    for root, dirs, files in os.walk(folder_path):
        # prune excluded directories
        pruned = []
        for d in list(dirs):
            full_d = os.path.normpath(os.path.join(root, d))
            rel_d = os.path.relpath(full_d, folder_path)
            if d in exclude_names:
                continue
            if any(full_d.startswith(p) for p in exclude_paths):
                continue
            pruned.append(d)
        dirs[:] = pruned

        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file).replace(os.sep, "/")
                # Quick path-based skip for virtualenv and package directories
                if any(seg in module_path for seg in excluded_segments):
                    continue
                module_name = os.path.relpath(module_path, folder_path).replace(os.sep, ".").replace(".py", "")
                # Skip invalid module names that start with a leading dot (e.g., from .venv)
                if module_name.startswith('.'):
                    continue
                try:
                    if module_name in sys.modules:
                        if altclick:
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
    path_shelves = hou.text.expandString("$CUSTOM_TOOLS/toolbar")

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

    ## FIX the path if is using a env variable - $HIP, $HOME, $CUSTOM_TOOLS
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