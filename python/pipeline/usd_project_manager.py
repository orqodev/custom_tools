"""
USD Project Manager
===================

A comprehensive project setup and management tool for USD-based VFX pipelines.
Follows ASWF USD Asset Structure Guidelines and industry best practices.

Features:
- Create USD-compliant project structures
- Set Houdini environment variables ($JOB, $ASSETS, $SHOTS, etc.)
- Configure context options for asset/shot workflows
- Validate and detect existing project structures
- Support for both asset and shot workflows

Author: Custom Tools Team
Version: 1.0.0
"""

from builtins import str
import hou
import os
import json
from pathlib import Path


class USDProjectManager:
    """
    Manages USD project structure creation and configuration.

    Follows ASWF guidelines:
    - Component models with payload structure
    - Sequence/shot hierarchy with department layers
    - Work/publish separation
    - Global material libraries
    """

    # Standard asset types based on VFX pipeline conventions
    ASSET_TYPES = [
        "characters",
        "props",
        "environments",
        "vehicles",
        "fx",
        "misc"
    ]

    # Standard shot departments
    SHOT_DEPARTMENTS = [
        "layout",
        "animation",
        "fx",
        "lighting",
        "rendering",
        "compositing"
    ]

    # Asset work departments
    ASSET_DEPARTMENTS = [
        "modeling",
        "surfacing",
        "rigging",
        "lookdev",
        "groom"
    ]

    # USD file types for asset publishing
    ASSET_USD_FILES = [
        "asset.usd",      # Main lightweight interface
        "payload.usdc",   # Heavy geometry data (binary)
        "geo.usdc",       # Geometry layer
        "mtl.usdc",       # Material assignments
        "proxy.usdc",     # Low-res proxy geometry
    ]

    def __init__(self):
        """Initialize the USD Project Manager."""
        self.project_root = None
        self.project_name = None
        self.config_file = None

    def create_project_structure(self, project_root, project_name=None,
                                create_asset_types=True,
                                create_sequences=False):
        """
        Create a complete USD project structure.

        Args:
            project_root (str): Root directory for the project
            project_name (str): Name of the project (optional)
            create_asset_types (bool): Create standard asset type folders
            create_sequences (bool): Create example sequence folders

        Returns:
            dict: Created directory structure information
        """
        project_root = os.path.normpath(project_root)
        self.project_root = project_root

        if project_name is None:
            project_name = os.path.basename(project_root)
        self.project_name = project_name

        created_dirs = []

        # Main project directories
        main_dirs = [
            "assets",
            "sequences",
            "lib",
            "lib/materials",
            "lib/hdri",
            "lib/luts",
            "config",
            "scripts",
            "render",
            "export"
        ]

        for dir_path in main_dirs:
            full_path = os.path.join(project_root, dir_path)
            self._create_directory(full_path)
            created_dirs.append(full_path)

        # Create asset type folders
        if create_asset_types:
            for asset_type in self.ASSET_TYPES:
                # Create template structure
                template_path = os.path.join(
                    project_root, "assets", asset_type, "_template"
                )
                self._create_asset_template(template_path)
                created_dirs.append(template_path)

        # Create example sequence structure
        if create_sequences:
            example_seq = os.path.join(project_root, "sequences", "seq_010")
            self._create_sequence_template(example_seq)
            created_dirs.append(example_seq)

        # Create project configuration
        self._create_project_config(project_root, project_name)

        return {
            'project_root': project_root,
            'project_name': project_name,
            'created_dirs': created_dirs
        }

    def _create_directory(self, path):
        """Create directory if it doesn't exist."""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created: {path}")
        return path

    def _create_asset_template(self, template_path):
        """
        Create a template asset structure following USD best practices.

        Structure:
        asset_name/
        ├── publish/         # Published USD files
        │   ├── asset.usd
        │   ├── payload.usdc
        │   ├── geo.usdc
        │   ├── mtl.usdc
        │   ├── proxy.usdc
        │   └── textures/
        └── work/            # Work in progress
            ├── houdini/
            ├── maya/
            └── substance/
        """
        # Publish directory
        publish_dir = os.path.join(template_path, "publish")
        self._create_directory(publish_dir)
        self._create_directory(os.path.join(publish_dir, "textures"))

        # Work directories
        for dept in self.ASSET_DEPARTMENTS:
            work_dir = os.path.join(template_path, "work", dept)
            self._create_directory(work_dir)

            # DCC-specific subdirectories
            for dcc in ["houdini", "maya", "blender"]:
                self._create_directory(os.path.join(work_dir, dcc))

    def _create_sequence_template(self, sequence_path):
        """
        Create a template sequence/shot structure.

        Structure:
        seq_010/
        ├── seq_010.usd      # Sequence-level opinions
        ├── shot_0010/
        │   ├── shot_0010.usd
        │   ├── layout/
        │   │   ├── shot_0010_layout.usd
        │   │   └── work/
        │   ├── animation/
        │   ├── fx/
        │   ├── lighting/
        │   └── render/
        └── shot_0020/
        """
        self._create_directory(sequence_path)

        # Create example shots
        for shot_num in ["0010", "0020"]:
            shot_name = f"shot_{shot_num}"
            shot_path = os.path.join(sequence_path, shot_name)

            for dept in self.SHOT_DEPARTMENTS:
                dept_path = os.path.join(shot_path, dept)
                self._create_directory(dept_path)
                self._create_directory(os.path.join(dept_path, "work"))
                self._create_directory(os.path.join(dept_path, "publish"))

    def _create_project_config(self, project_root, project_name):
        """
        Create project configuration file with metadata.
        """
        config = {
            "project_name": project_name,
            "project_root": project_root,
            "usd_version": "25.08",
            "pipeline_version": "1.0.0",
            "asset_types": self.ASSET_TYPES,
            "shot_departments": self.SHOT_DEPARTMENTS,
            "asset_departments": self.ASSET_DEPARTMENTS,
            "fps": 24.0,
            "resolution": [1920, 1080],
            "up_axis": "Y"
        }

        config_path = os.path.join(project_root, "config", "project.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print(f"Created project config: {config_path}")
        self.config_file = config_path
        return config_path

    def setup_houdini_environment(self, project_root):
        """
        Set up Houdini environment variables for USD pipeline.

        Sets:
        - $JOB: Project root
        - $ASSETS: Assets directory
        - $SHOTS: Sequences directory
        - $LIB: Library directory
        - $MATERIALS: Material library
        - $HDRI: HDRI library
        """
        project_root = os.path.normpath(project_root).replace('\\', '/')

        # Set global environment variables
        env_vars = {
            'JOB': project_root,
            'ASSETS': os.path.join(project_root, 'assets').replace('\\', '/'),
            'SHOTS': os.path.join(project_root, 'sequences').replace('\\', '/'),
            'LIB': os.path.join(project_root, 'lib').replace('\\', '/'),
            'MATERIALS': os.path.join(project_root, 'lib', 'materials').replace('\\', '/'),
            'HDRI': os.path.join(project_root, 'lib', 'hdri').replace('\\', '/'),
            'RENDER': os.path.join(project_root, 'render').replace('\\', '/'),
            'EXPORT': os.path.join(project_root, 'export').replace('\\', '/')
        }

        for var_name, var_value in env_vars.items():
            hou.hscript(f"set -g {var_name} = {var_value}")
            print(f"Set ${var_name} = {var_value}")

        return env_vars

    def detect_context_from_hip_file(self):
        """
        Detect project context from current .hip file path.

        Returns:
            dict: Context information (asset/shot, department, etc.)
        """
        hip_path = hou.hipFile.path()
        hip_name = hou.hipFile.basename()

        # Get project root from environment or prompt user
        job_dir = hou.getenv('JOB', '')

        if not job_dir:
            return None

        # Remove project root from hip path
        relative_path = hip_path.replace(job_dir, '').lstrip('/\\')
        path_parts = relative_path.split(os.sep)

        context = {
            'hip_path': hip_path,
            'hip_name': hip_name,
            'project_root': job_dir,
            'relative_path': relative_path,
            'path_parts': path_parts
        }

        # Detect if asset or shot
        if len(path_parts) > 0:
            root_type = path_parts[0]

            if 'asset' in root_type.lower():
                context['work_type'] = 'asset'
                if len(path_parts) >= 3:
                    context['asset_type'] = path_parts[1]
                    context['asset_name'] = path_parts[2]
                if len(path_parts) >= 4:
                    context['department'] = path_parts[3]

            elif 'sequence' in root_type.lower() or 'shot' in root_type.lower():
                context['work_type'] = 'shot'
                if len(path_parts) >= 2:
                    context['sequence'] = path_parts[1]
                if len(path_parts) >= 3:
                    context['shot'] = path_parts[2]
                if len(path_parts) >= 4:
                    context['department'] = path_parts[3]

        return context

    def set_context_options(self, context):
        """
        Set Houdini context options based on detected context.

        Args:
            context (dict): Context information from detect_context_from_hip_file
        """
        if not context:
            return

        # Set common context options
        for key, value in context.items():
            if isinstance(value, str):
                hou.setContextOption(key, value)

        # Set work-type specific options
        if context.get('work_type') == 'asset':
            asset_path = os.path.join(
                context['project_root'],
                'assets',
                context.get('asset_type', ''),
                context.get('asset_name', '')
            )
            hou.setContextOption('asset_path', asset_path)
            hou.setContextOption('publish_path', os.path.join(asset_path, 'publish'))

        elif context.get('work_type') == 'shot':
            shot_path = os.path.join(
                context['project_root'],
                'sequences',
                context.get('sequence', ''),
                context.get('shot', '')
            )
            hou.setContextOption('shot_path', shot_path)
            dept_path = os.path.join(shot_path, context.get('department', ''))
            hou.setContextOption('dept_path', dept_path)
            hou.setContextOption('publish_path', os.path.join(dept_path, 'publish'))

        print("Context options set successfully!")
        return context


# Standalone functions for shelf tools

def create_new_project():
    """
    Interactive project creation tool (for shelf button).
    """
    manager = USDProjectManager()

    # Select project root
    project_root = hou.ui.selectFile(
        start_directory=None,
        title="Select Project Root Directory",
        file_type=hou.fileType.Directory
    )

    if not project_root:
        hou.ui.displayMessage(
            "No directory selected. Operation cancelled.",
            severity=hou.severityType.Warning
        )
        return

    # Remove trailing slash
    project_root = project_root.rstrip('/')

    # Get project name
    project_name = os.path.basename(project_root)

    # Confirm with user
    choice = hou.ui.displayMessage(
        f"Create USD project structure?\n\n"
        f"Root: {project_root}\n"
        f"Name: {project_name}\n\n"
        f"This will create:\n"
        f"- assets/ (with standard types)\n"
        f"- sequences/\n"
        f"- lib/ (materials, HDRI, etc.)\n"
        f"- config/\n"
        f"- scripts/\n",
        buttons=("Create", "Cancel"),
        severity=hou.severityType.Message,
        title="Create USD Project"
    )

    if choice == 1:  # Cancel
        return

    # Create structure
    try:
        result = manager.create_project_structure(
            project_root,
            project_name,
            create_asset_types=True,
            create_sequences=True
        )

        # Set up environment
        manager.setup_houdini_environment(project_root)

        # Success message
        hou.ui.displayMessage(
            f"USD Project Created Successfully!\n\n"
            f"Project: {project_name}\n"
            f"Root: {project_root}\n\n"
            f"Created {len(result['created_dirs'])} directories.\n"
            f"Environment variables configured.\n\n"
            f"$JOB = {project_root}",
            severity=hou.severityType.Message,
            title="Project Created"
        )

    except Exception as e:
        hou.ui.displayMessage(
            f"Error creating project:\n{str(e)}",
            severity=hou.severityType.Error
        )


def setup_existing_project():
    """
    Set up environment for existing project (for shelf button).
    """
    manager = USDProjectManager()

    # Select project root
    project_root = hou.ui.selectFile(
        start_directory=None,
        title="Select Existing Project Root Folder",
        file_type=hou.fileType.Directory
    )

    if not project_root:
        hou.ui.displayMessage(
            "No directory selected. Operation cancelled.",
            severity=hou.severityType.Warning
        )
        return

    # Remove trailing slash
    project_root = project_root.rstrip('/')

    # Verify it's a valid project
    assets_dir = os.path.join(project_root, 'assets')
    sequences_dir = os.path.join(project_root, 'sequences')

    if not (os.path.exists(assets_dir) or os.path.exists(sequences_dir)):
        hou.ui.displayMessage(
            "This doesn't appear to be a valid USD project.\n\n"
            "Expected 'assets' or 'sequences' folder not found.\n\n"
            "Please select a valid project root.",
            severity=hou.severityType.Warning
        )
        return

    # Set up environment
    env_vars = manager.setup_houdini_environment(project_root)

    # Detect context from current file
    hip_path = hou.hipFile.path()
    context = None

    if hip_path and project_root in hip_path:
        context = manager.detect_context_from_hip_file()
        if context:
            manager.set_context_options(context)

    # Build info message
    info_msg = f"Project Environment Configured!\n\n"
    info_msg += f"$JOB = {env_vars['JOB']}\n"
    info_msg += f"$ASSETS = {env_vars['ASSETS']}\n"
    info_msg += f"$SHOTS = {env_vars['SHOTS']}\n\n"

    if context:
        info_msg += f"Detected Context:\n"
        info_msg += f"Type: {context.get('work_type', 'unknown').upper()}\n"
        if context.get('work_type') == 'asset':
            info_msg += f"Asset: {context.get('asset_type')}/{context.get('asset_name')}\n"
        elif context.get('work_type') == 'shot':
            info_msg += f"Shot: {context.get('sequence')}/{context.get('shot')}\n"
        info_msg += f"Department: {context.get('department', 'N/A')}\n"

    hou.ui.displayMessage(
        info_msg,
        severity=hou.severityType.Message,
        title="Project Setup Complete"
    )


def validate_current_scene():
    """
    Validate current scene against USD project structure.
    Shows warnings if file is not in correct location.
    """
    manager = USDProjectManager()

    hip_path = hou.hipFile.path()
    job_dir = hou.getenv('JOB', '')

    if not job_dir:
        hou.ui.displayMessage(
            "No project configured.\n\n"
            "Run 'Setup Existing Project' first to configure $JOB.",
            severity=hou.severityType.Warning
        )
        return

    if not hip_path:
        hou.ui.displayMessage(
            "Current scene is not saved.\n\n"
            "Save your scene in the project structure first.",
            severity=hou.severityType.Warning
        )
        return

    # Detect context
    context = manager.detect_context_from_hip_file()

    if not context:
        hou.ui.displayMessage(
            "Could not detect project context.\n\n"
            f"Current file: {hip_path}\n"
            f"Project root: {job_dir}\n\n"
            "Make sure your file is saved in:\n"
            "- assets/TYPE/NAME/work/DEPT/\n"
            "- sequences/SEQ/SHOT/DEPT/work/",
            severity=hou.severityType.Warning
        )
        return

    # Check if in work directory
    is_valid = 'work' in hip_path.lower()

    # Build validation message
    if is_valid:
        severity = hou.severityType.Message
        msg = "Scene location is VALID!\n\n"
    else:
        severity = hou.severityType.Warning
        msg = "Warning: Scene may not be in 'work' directory!\n\n"

    msg += f"Project: {context.get('project_root')}\n"
    msg += f"Type: {context.get('work_type', 'unknown').upper()}\n\n"

    if context.get('work_type') == 'asset':
        msg += f"Asset Type: {context.get('asset_type', 'N/A')}\n"
        msg += f"Asset Name: {context.get('asset_name', 'N/A')}\n"
    elif context.get('work_type') == 'shot':
        msg += f"Sequence: {context.get('sequence', 'N/A')}\n"
        msg += f"Shot: {context.get('shot', 'N/A')}\n"

    msg += f"Department: {context.get('department', 'N/A')}\n"
    msg += f"\nFile: {hip_path}"

    hou.ui.displayMessage(msg, severity=severity, title="Scene Validation")
