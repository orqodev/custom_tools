import hou
import logging
import os
import sys

def get_logger(name="houdini_debug",log_file_name="houdini_debug.log",level=logging.DEBUG):
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