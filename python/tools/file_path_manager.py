import hou
import os
import platform
from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools

class FilePathsManagerUI(QtWidgets.QMainWindow):
    # Node types and their file path parameters to check
    FILE_PATH_NODES = {
        # SOP nodes
        "file": "file",
        "alembicarchive": "fileName",
        "filecache": "file",
        "filemerge": "file",
        "dopio": "file",
        "vellumio": "file",
        "rbdio": "file",
        # ROP nodes
        "rop_geometry": "sopoutput",
        "alembic": "fileName",
        "rop_fbx": "sopoutput",
        "rop_dop": "dopoutput",
        # Texture nodes
        "texture::2.0": "map",
        "redshift::TextureSampler": "tex0",
        # MaterialX nodes
        "mtlximage":"file",
        "mtlxtiledimage":"file",
        "usduvtexture::2.0":"file",
        # LOP nodes
        "assetreference":"filepath",
        "reference::2.0": "filepath1",
        "layout": "filepath1",
        "sublayer": "filepath1",
        "domelight::3.0":"inputs:texture:file",
        "componentoutput":"lopoutput",
        "volume":"filepath1",
        "usdrender_rop":"outputimage",
        # Other common nodes with file paths
        "ifd": "soho_diskfile",
        "opengl": "picture",
        "comp": "copoutput",
    }

    def __init__(self):
        super().__init__()
        # Create UI from scratch since we don't have a UI file
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        self.setWindowTitle("File Paths Manager")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(600)

        # Main layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Create UI components
        self._init_ui()
        self._setup_connections()

        # Store data
        self.broken_paths_data = []
        self.total_broken_paths = 0

    def _init_ui(self):
        '''Initialize the UI components'''
        # Top buttons layout
        button_layout = QtWidgets.QHBoxLayout()

        # Scan button
        self.scan_button = QtWidgets.QPushButton("Scan for All Paths")
        button_layout.addWidget(self.scan_button)

        # Reveal in explorer button
        self.reveal_button = QtWidgets.QPushButton("Reveal in Explorer")
        button_layout.addWidget(self.reveal_button)

        # Batch fix button
        self.batch_fix_button = QtWidgets.QPushButton("Batch Fix Checked Paths")
        button_layout.addWidget(self.batch_fix_button)

        # Add button layout to main layout
        self.main_layout.addLayout(button_layout)

        # Create tree widget
        self.paths_tree = QtWidgets.QTreeWidget()
        self.paths_tree.setHeaderLabels([
            "Node Name", 
            "Node Path", 
            "Node Type", 
            "Parameter", 
            "File Path"
        ])

        # Set font size to 14px
        font = self.paths_tree.font()
        font.setPointSize(10)
        self.paths_tree.setFont(font)

        # Enable checkboxes for selection
        self.paths_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.paths_tree.setItemsExpandable(True)

        # Connect item changed signal to handle checkbox state changes
        self.paths_tree.itemChanged.connect(self._on_item_changed)

        # Set column widths
        self.paths_tree.setColumnWidth(0, 150)  # Node Name
        self.paths_tree.setColumnWidth(1, 300)  # Node Path
        self.paths_tree.setColumnWidth(2, 100)  # Node Type
        self.paths_tree.setColumnWidth(3, 100)  # Parameter
        self.paths_tree.setColumnWidth(4, 350)  # File Path

        # Enable sorting
        self.paths_tree.setSortingEnabled(True)

        # Add tree to main layout
        self.main_layout.addWidget(self.paths_tree)

        # Stats layout
        stats_layout = QtWidgets.QHBoxLayout()

        # Total nodes label
        self.total_nodes_label = QtWidgets.QLabel("Total Nodes with Paths: 0")
        stats_layout.addWidget(self.total_nodes_label)

        # Add stats layout to main layout
        self.main_layout.addLayout(stats_layout)

        # Set context menu policy
        self.paths_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def _setup_connections(self):
        '''Set up signal connections'''
        self.scan_button.clicked.connect(self.scan_all_paths)
        self.paths_tree.itemDoubleClicked.connect(self.select_node)
        self.reveal_button.clicked.connect(self.reveal_in_explorer)
        self.batch_fix_button.clicked.connect(self.batch_fix_paths)
        self.paths_tree.customContextMenuRequested.connect(self._show_context_menu)

    def _on_item_changed(self, item, column):
        '''Handle checkbox state changes'''
        # Only process changes to the checkbox column (0)
        if column != 0:
            return

        # Prevent recursive signal handling
        self.paths_tree.blockSignals(True)

        # Get the current check state
        check_state = item.checkState(0)

        # Update all children to match parent's state
        self._update_children_check_state(item, check_state)

        # Update parent's state based on children
        self._update_parent_check_state(item.parent())

        # Re-enable signals
        self.paths_tree.blockSignals(False)

    def _update_children_check_state(self, parent_item, check_state):
        '''Update all children to match parent's check state'''
        if not parent_item:
            return

        # Update all children
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child.setCheckState(0, check_state)
            # Recursively update grandchildren
            self._update_children_check_state(child, check_state)

    def _update_parent_check_state(self, parent_item):
        '''Update parent's check state based on children'''
        if not parent_item:
            return

        # Count checked and unchecked children
        checked_count = 0
        total_count = parent_item.childCount()

        for i in range(total_count):
            if parent_item.child(i).checkState(0) == QtCore.Qt.Checked:
                checked_count += 1

        # Set parent state based on children
        if checked_count == 0:
            parent_item.setCheckState(0, QtCore.Qt.Unchecked)
        elif checked_count == total_count:
            parent_item.setCheckState(0, QtCore.Qt.Checked)
        else:
            parent_item.setCheckState(0, QtCore.Qt.PartiallyChecked)

        # Recursively update grandparent
        self._update_parent_check_state(parent_item.parent())

    def scan_all_paths(self):
        '''Scan scene for all nodes with file paths and update UI'''
        try:
            self.paths_tree.clear()
            self.broken_paths_data = []
            self.all_paths_data = []
            self.total_broken_paths = 0
            self.total_paths = 0

            # Phase 1: Collect all nodes with file paths
            all_nodes_with_paths = []

            # Create a copy of the dictionary to avoid modifying it during iteration
            nodes_to_check = dict(self.FILE_PATH_NODES)

            # Keep track of new entries to add after iteration
            new_entries = {}

            # Get all nodes in the scene
            for node_type, parm_name in nodes_to_check.items():
                # Find all nodes of this type in all categories
                categories = [hou.sopNodeTypeCategory(), hou.dopNodeTypeCategory(), 
                             hou.ropNodeTypeCategory(), hou.vopNodeTypeCategory(),
                             hou.lopNodeTypeCategory(), hou.shopNodeTypeCategory()]

                # Try to add materialx category if it exists
                try:
                    materialx_category = hou.nodeTypeCategory("materialx")
                    if materialx_category:
                        categories.append(materialx_category)
                except:
                    pass

                # Special handling for MaterialX nodes which might be in different namespaces
                if node_type.startswith("mtlx") and not node_type.startswith("mtlx::"):
                    # Also try with the mtlx:: namespace prefix
                    new_entries[f"mtlx::{node_type}"] = parm_name

                # Debug print for mtlxtiledimage
                if node_type == "mtlxtiledimage" or node_type == "mtlx::mtlxtiledimage":
                    print(f"Searching for node type: {node_type}")

                found_in_category = False
                for category in categories:
                    # Debug print for mtlxtiledimage
                    if node_type == "mtlxtiledimage" or node_type == "mtlx::mtlxtiledimage":
                        print(f"  Checking category: {category.name()}")

                    node_type_obj = hou.nodeType(category, node_type)
                    if node_type_obj:
                        found_in_category = True
                        # Debug print for mtlxtiledimage
                        if node_type == "mtlxtiledimage" or node_type == "mtlx::mtlxtiledimage":
                            print(f"  Found node type in category: {category.name()}")

                        nodes = node_type_obj.instances()
                        for node in nodes:
                            # Check if the node has the parameter
                            if node.parm(parm_name):
                                file_path = node.parm(parm_name).eval()

                                # Skip empty paths
                                if not file_path:
                                    continue

                                # Store node information for later evaluation
                                node_name, node_path, node_type_name = self._get_node_details(node)
                                all_nodes_with_paths.append({
                                    "node": node,
                                    "node_name": node_name,
                                    "node_path": node_path,
                                    "node_type": node_type_name,
                                    "parameter": parm_name,
                                    "file_path": file_path
                                })

                # Debug print for mtlxtiledimage if not found
                if (node_type == "mtlxtiledimage" or node_type == "mtlx::mtlxtiledimage") and not found_in_category:
                    print(f"  Node type {node_type} not found in any category")

            # Add any new entries to the original dictionary after iteration is complete
            self.FILE_PATH_NODES.update(new_entries)

            # Special handling for mtlxtiledimage nodes - search all nodes in the scene
            if "mtlxtiledimage" in self.FILE_PATH_NODES or "mtlx::mtlxtiledimage" in self.FILE_PATH_NODES:
                print("Performing special search for mtlxtiledimage nodes...")
                # Get all nodes in the scene
                all_nodes = hou.node("/").allSubChildren()

                # Check each node's type
                for node in all_nodes:
                    node_type_name = node.type().name()

                    # Check if this is a mtlxtiledimage node
                    if "mtlxtiledimage" in node_type_name.lower():
                        print(f"Found mtlxtiledimage node: {node.path()}, type: {node_type_name}")

                        # Check if it has the file parameter
                        if node.parm("file"):
                            file_path = node.parm("file").eval()

                            # Skip empty paths
                            if not file_path:
                                continue

                            # Check if this node is already in our list
                            node_path = node.path()
                            already_added = any(nd.get("node_path") == node_path for nd in all_nodes_with_paths)

                            if not already_added:
                                print(f"  Adding mtlxtiledimage node to search list: {node.path()}")
                                node_name, node_path, node_type_name = self._get_node_details(node)
                                all_nodes_with_paths.append({
                                    "node": node,
                                    "node_name": node_name,
                                    "node_path": node_path,
                                    "node_type": node_type_name,
                                    "parameter": "file",
                                    "file_path": file_path
                                })

            print(f"Found {len(all_nodes_with_paths)} nodes with file paths")

            # Phase 2: Evaluate which paths are broken and add all paths to the tree
            for node_data in all_nodes_with_paths:
                # Expand environment variables
                expanded_path = hou.text.expandString(node_data["file_path"])

                # Debug print to see what paths are being checked
                print(f"Checking path: {expanded_path}")

                # Normalize path for OS (important for Windows)
                normalized_path = os.path.normpath(expanded_path)

                # Check if the path exists using our enhanced method
                path_exists = self._check_path_exists(normalized_path)

                # Debug print to see the result
                print(f"Path exists: {path_exists}")

                # Add expanded path to node data
                node_data["expanded_path"] = expanded_path

                # Make a copy of the node data without the node object
                display_data = node_data.copy()
                display_data.pop("node")

                # Add path status to the data
                display_data["path_exists"] = path_exists

                # Add to the tree widget
                self._add_to_tree(display_data)

                # Add to all paths list
                self.all_paths_data.append(display_data)
                self.total_paths += 1

                # If path doesn't exist, add to broken paths list
                if not path_exists:
                    self.broken_paths_data.append(display_data)
                    self.total_broken_paths += 1

            self._update_stats()

            if self.total_paths == 0:
                hou.ui.displayMessage("No paths found in the scene.", 
                                     severity=hou.severityType.Message)
            else:
                print(f"Found {self.total_paths} paths, {self.total_broken_paths} broken")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error scanning scene: {str(e)}\n{error_details}")
            hou.ui.displayMessage(f"Error scanning scene: {str(e)}", 
                                 severity=hou.severityType.Error)

    def _check_path_exists(self, path):
        '''Enhanced method to check if a path exists, handling special cases'''
        try:
            # Basic check - first try os.path.isfile for files
            if os.path.isfile(path):
                print(f"File exists (isfile): {path}")
                # Try to open the file to verify it's accessible
                try:
                    with open(path, 'rb') as f:
                        # Just read a byte to verify it's accessible
                        f.read(1)
                    return True
                except (IOError, PermissionError) as e:
                    print(f"File exists but can't be opened: {path}, Error: {str(e)}")
                    # File exists but can't be opened, consider it broken
                    return False

            # Check if it's a directory
            if os.path.isdir(path):
                print(f"Directory exists: {path}")
                return True

            # Secondary check with exists (might catch some edge cases)
            if os.path.exists(path):
                print(f"Path exists (generic): {path}")
                return True

            # Check for sequence files (e.g., file.0001.exr)
            # If the path contains frame numbers like .0001.exr, .0002.exr, etc.
            import re
            sequence_match = re.search(r'\.(\d+)\.(exr|jpg|png|tif|tiff|bgeo|bgeo\.sc|abc|obj|fbx|vdb)$', path, re.IGNORECASE)
            if sequence_match:
                # Try to check if the directory exists
                dir_path = os.path.dirname(path)
                if not os.path.exists(dir_path):
                    print(f"Directory does not exist: {dir_path}")
                    return False

                # Check if any files with similar pattern exist in the directory
                base_name = os.path.basename(path)
                frame_number = sequence_match.group(1)
                extension = sequence_match.group(2)
                pattern_base = base_name.replace(f".{frame_number}.{extension}", "")

                # Look for any file that matches the pattern
                for file in os.listdir(dir_path):
                    if pattern_base in file and f".{extension}" in file.lower():
                        print(f"Found sequence file match: {file}")
                        return True

                print(f"No sequence files found matching pattern: {pattern_base}*.{extension}")
                return False

            # Handle UNC paths (network paths) on Windows
            if platform.system() == "Windows" and path.startswith("\\\\"):
                # For UNC paths, just check if the share exists
                share_parts = path.split("\\")
                if len(share_parts) >= 4:
                    share_path = f"\\\\{share_parts[2]}\\{share_parts[3]}"
                    if os.path.exists(share_path):
                        print(f"Network share exists: {share_path}")
                        # The share exists, but the specific file might not
                        return False

            # For Houdini-specific paths, try to use hou.expandString again
            if "$" in path:
                expanded_path = hou.expandString(path)
                if expanded_path != path:
                    print(f"Re-expanding path with $ signs: {path} -> {expanded_path}")
                    return self._check_path_exists(expanded_path)

            # Path doesn't exist
            print(f"Path confirmed not to exist: {path}")
            return False

        except Exception as e:
            print(f"Error checking if path exists: {str(e)}")
            # If there's an error checking the path, assume it's broken
            return False

    def _add_to_tree(self, node_data):
        '''Add a node entry to the tree widget'''
        # Parse the node path to create a hierarchical structure
        node_path = node_data['node_path']
        path_parts = node_path.split('/')

        # Skip the first empty part (paths start with /)
        if path_parts[0] == '':
            path_parts = path_parts[1:]

        # Find or create parent items for the hierarchy
        parent_item = None
        current_path = ""

        # For deep paths, create the hierarchy
        if len(path_parts) > 2:  # More than /obj/node
            # Start from the root (e.g., 'obj', 'stage')
            root_name = path_parts[0]
            current_path = "/" + root_name

            # Find if the root already exists
            root_item = None
            for i in range(self.paths_tree.topLevelItemCount()):
                top_item = self.paths_tree.topLevelItem(i)
                if top_item.data(1, QtCore.Qt.DisplayRole) == current_path:
                    root_item = top_item
                    break

            # Create the root item if it doesn't exist
            if not root_item:
                root_item = QtWidgets.QTreeWidgetItem(self.paths_tree)
                root_item.setText(0, root_name)
                root_item.setText(1, current_path)
                root_item.setFlags(root_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                root_item.setCheckState(0, QtCore.Qt.Unchecked)

            parent_item = root_item

            # Create the rest of the hierarchy
            for i in range(1, len(path_parts) - 1):
                part = path_parts[i]
                current_path += "/" + part

                # Check if this part already exists as a child
                child_item = None
                for j in range(parent_item.childCount()):
                    item = parent_item.child(j)
                    if item.data(1, QtCore.Qt.DisplayRole) == current_path:
                        child_item = item
                        break

                # Create the child item if it doesn't exist
                if not child_item:
                    child_item = QtWidgets.QTreeWidgetItem(parent_item)
                    child_item.setText(0, part)
                    child_item.setText(1, current_path)
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    child_item.setCheckState(0, QtCore.Qt.Unchecked)

                parent_item = child_item

        # Create the actual node item
        if parent_item:
            item = QtWidgets.QTreeWidgetItem(parent_item)
        else:
            item = QtWidgets.QTreeWidgetItem(self.paths_tree)

        # Set the item data
        item.setText(0, node_data['node_name'])
        item.setText(1, node_data['node_path'])
        item.setText(2, node_data['node_type'])
        item.setText(3, node_data['parameter'])
        item.setText(4, node_data['file_path'])

        # Add checkbox for selection
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)

        # Store the node data in the item for later use
        item.setData(0, QtCore.Qt.UserRole, node_data)

        # Color code based on path existence
        if 'path_exists' in node_data:
            if not node_data['path_exists']:
                # Red text for broken paths
                for col in range(5):
                    item.setForeground(col, QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            else:
                # Green text for valid paths
                for col in range(5):
                    item.setForeground(col, QtGui.QBrush(QtGui.QColor(0, 128, 0)))

    def _get_node_details(self, node):
        '''Get the correct node details - name, path, type'''
        node_name = node.name()
        node_path = node.path()
        node_type = node.type().name()

        return node_name, node_path, node_type

    def _update_stats(self):
        '''Update the stats labels'''
        self.total_nodes_label.setText(f"Total Nodes with Paths: {self.total_paths} (Broken: {self.total_broken_paths})")

    def select_node(self, item):
        '''Select and jump to the node when double-clicked'''
        try:
            node_path = item.text(1)

            # Check if this is a nested node path (e.g., /stage/componentoutput1/fromdisk)
            path_parts = node_path.split('/')
            if len(path_parts) > 3:  # More than just /obj/node
                # This is a nested node, handle it specially
                print(f"Handling nested node path: {node_path}")

                # Find the node
                node = hou.node(node_path)
                if node:
                    # Select the node
                    node.setSelected(True)

                    # Find the closest network editor
                    network_pane = None
                    for pane in hou.ui.paneTabs():
                        if isinstance(pane, hou.NetworkEditor):
                            network_pane = pane
                            break

                    if network_pane:
                        # For nested nodes, we want to navigate to the immediate parent
                        # and then frame the selected node
                        parent_path = node.parent().path()
                        print(f"Navigating to parent: {parent_path}")

                        # Navigate to the parent network
                        network_pane.cd(parent_path)

                        # Frame the selected node
                        network_pane.frameSelection()
                else:
                    # Try to find the closest parent that exists
                    found_node = None
                    for i in range(len(path_parts) - 1, 1, -1):
                        # Try progressively shorter paths
                        test_path = '/'.join(path_parts[:i])
                        test_node = hou.node(test_path)
                        if test_node:
                            found_node = test_node
                            break

                    if found_node:
                        # We found a parent node, select it
                        found_node.setSelected(True)

                        # Find the closest network editor
                        network_pane = None
                        for pane in hou.ui.paneTabs():
                            if isinstance(pane, hou.NetworkEditor):
                                network_pane = pane
                                break

                        if network_pane:
                            # Navigate to the parent of the found node
                            parent_path = found_node.parent().path()
                            network_pane.cd(parent_path)
                            network_pane.frameSelection()

                            # Show a message about the partial navigation
                            hou.ui.displayMessage(
                                f"Could not find the exact node: {node_path}\nNavigated to the closest parent: {found_node.path()}",
                                severity=hou.severityType.Warning
                            )
                    else:
                        # Could not find any parent node
                        hou.ui.displayMessage(
                            f"Could not find any part of the node path: {node_path}",
                            severity=hou.severityType.Error
                        )
            else:
                # Regular node path handling (existing code)
                node = hou.node(node_path)
                if node:
                    # Select the node
                    node.setSelected(True)

                    # Find the closest network editor
                    network_pane = None
                    for pane in hou.ui.paneTabs():
                        if isinstance(pane, hou.NetworkEditor):
                            network_pane = pane
                            break

                    if network_pane:
                        # Move to the parent network
                        network_pane.cd(node.parent().path())
                        # Frame the node
                        network_pane.frameSelection()
                else:
                    raise Exception(f"Node not found: {node_path}")
        except Exception as e:
            node_name = item.text(0)
            hou.ui.displayMessage(
                f"The node selected: {node_name} isn't in the scene. Please refresh the path manager.",
                severity=hou.severityType.Error
            )

    def reveal_in_explorer(self):
        '''Open the folder where the file should be located'''
        selected_items = self.paths_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage("Please select a path first", 
                                 severity=hou.severityType.Error)
            return

        # Use the first selected item
        self.reveal_in_explorer_for_item(selected_items[0])

    def fix_broken_path(self):
        '''Fix the path by allowing the user to select a new file'''
        selected_items = self.paths_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage("Please select a path to fix", 
                                 severity=hou.severityType.Error)
            return

        # Use the first selected item
        self.fix_broken_path_for_item(selected_items[0])

    def _find_similar_files(self, broken_path):
        '''Find similar files to suggest as replacements for a path'''
        suggestions = []

        try:
            # Get the directory and filename
            dir_path = os.path.dirname(broken_path)
            filename = os.path.basename(broken_path)
            file_base, file_ext = os.path.splitext(filename)

            # Check if the directory exists
            if not os.path.exists(dir_path):
                # Try to find a similar directory
                parent_dir = os.path.dirname(dir_path)
                if os.path.exists(parent_dir):
                    # Look for similar directories
                    for item in os.listdir(parent_dir):
                        potential_dir = os.path.join(parent_dir, item)
                        if os.path.isdir(potential_dir) and item.lower() in os.path.basename(dir_path).lower():
                            # Found a similar directory, check for similar files
                            for file in os.listdir(potential_dir):
                                if file_ext.lower() == os.path.splitext(file)[1].lower():
                                    suggestions.append(os.path.join(potential_dir, file))
                return suggestions

            # Directory exists, look for similar files
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path) and file_ext.lower() == os.path.splitext(file)[1].lower():
                    # Check if the filename is similar
                    if file_base.lower() in os.path.splitext(file)[0].lower() or \
                       os.path.splitext(file)[0].lower() in file_base.lower():
                        suggestions.append(file_path)

            # If we didn't find any suggestions, look in parent directory
            if not suggestions:
                parent_dir = os.path.dirname(dir_path)
                if os.path.exists(parent_dir):
                    for item in os.listdir(parent_dir):
                        potential_dir = os.path.join(parent_dir, item)
                        if os.path.isdir(potential_dir):
                            for file in os.listdir(potential_dir):
                                if file_ext.lower() == os.path.splitext(file)[1].lower():
                                    suggestions.append(os.path.join(potential_dir, file))

            # Sort suggestions by similarity to the original filename
            suggestions.sort(key=lambda x: self._similarity_score(filename, os.path.basename(x)), reverse=True)

            # Limit to top 10 suggestions
            return suggestions[:10]

        except Exception as e:
            print(f"Error finding similar files: {str(e)}")
            return []

    def _similarity_score(self, str1, str2):
        '''Calculate a simple similarity score between two strings'''
        # Convert to lowercase for case-insensitive comparison
        str1 = str1.lower()
        str2 = str2.lower()

        # Check for exact match
        if str1 == str2:
            return 1.0

        # Check for substring
        if str1 in str2 or str2 in str1:
            return 0.8

        # Count common characters
        common_chars = set(str1) & set(str2)
        return len(common_chars) / max(len(str1), len(str2))

    def _get_file_type_from_path(self, path):
        '''Get the file type from the path extension'''
        ext = os.path.splitext(path)[1].lower()

        if ext in ['.bgeo', '.geo', '.bgeo.sc']:
            return hou.fileType.Geometry
        elif ext in ['.abc']:
            return hou.fileType.Alembic
        elif ext in ['.fbx']:
            return hou.fileType.FBX
        elif ext in ['.obj']:
            return hou.fileType.OBJ
        elif ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.exr']:
            return hou.fileType.Image
        elif ext in ['.vdb']:
            return hou.fileType.VDB
        else:
            return hou.fileType.Any

    def _get_checked_items(self, parent_item=None):
        '''Recursively get all checked items in the tree'''
        checked_items = []

        # Start from the root if no parent is provided
        if parent_item is None:
            # Iterate through all top-level items
            for i in range(self.paths_tree.topLevelItemCount()):
                item = self.paths_tree.topLevelItem(i)
                # Check if this item is checked
                if item.checkState(0) == QtCore.Qt.Checked:
                    # Only add leaf nodes (actual file nodes, not hierarchy nodes)
                    if item.data(0, QtCore.Qt.UserRole) is not None:
                        checked_items.append(item)
                # Recursively check children
                checked_items.extend(self._get_checked_items(item))
        else:
            # Iterate through all children of the parent
            for i in range(parent_item.childCount()):
                item = parent_item.child(i)
                # Check if this item is checked
                if item.checkState(0) == QtCore.Qt.Checked:
                    # Only add leaf nodes (actual file nodes, not hierarchy nodes)
                    if item.data(0, QtCore.Qt.UserRole) is not None:
                        checked_items.append(item)
                # Recursively check children
                checked_items.extend(self._get_checked_items(item))

        return checked_items

    def batch_fix_paths(self):
        '''Batch fix multiple paths by replacing a common path prefix'''
        # Get all checked items
        checked_items = self._get_checked_items()

        # If no items are checked, check if there are any paths at all
        if not checked_items:
            if not self.all_paths_data:
                hou.ui.displayMessage("No paths found. Please scan the scene first.", 
                                     severity=hou.severityType.Warning)
                return
            else:
                # Ask if user wants to apply to all paths
                result = hou.ui.displayMessage(
                    "No paths are checked. Do you want to apply batch fix to all paths?",
                    buttons=("Yes", "No"),
                    severity=hou.severityType.Warning
                )
                if result == 1:  # "No" was clicked
                    return
                # If "Yes" was clicked, continue with all paths
                use_selected_only = False
        else:
            use_selected_only = True
            # Get the selected node paths
            selected_node_paths = [item.text(1) for item in checked_items]
            print(f"Checked node paths for batch fix: {selected_node_paths}")

        # Create a dialog to get source and target paths
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Batch Fix Paths")
        dialog.setMinimumWidth(600)

        layout = QtWidgets.QVBoxLayout(dialog)


        # Source path
        source_layout = QtWidgets.QHBoxLayout()
        source_label = QtWidgets.QLabel("Source Path Pattern:")
        source_layout.addWidget(source_label)

        source_edit = QtWidgets.QLineEdit()
        source_layout.addWidget(source_edit)

        # Try to find a common prefix among broken paths
        if use_selected_only:
            # Find common prefix among selected paths
            selected_data = []
            for data in self.all_paths_data:
                if data['node_path'] in selected_node_paths:
                    selected_data.append(data)
            common_prefix = self._find_common_prefix_for_data(selected_data)
        else:
            common_prefix = self._find_common_prefix()

        if common_prefix:
            source_edit.setText(common_prefix)

        layout.addLayout(source_layout)

        # Target path
        target_layout = QtWidgets.QHBoxLayout()
        target_label = QtWidgets.QLabel("Target Path:")
        target_layout.addWidget(target_label)

        target_edit = QtWidgets.QLineEdit()
        target_layout.addWidget(target_edit)

        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(lambda: self._browse_for_directory(target_edit))
        target_layout.addWidget(browse_button)

        layout.addLayout(target_layout)

        # Preview section
        preview_label = QtWidgets.QLabel("Preview of changes:")
        layout.addWidget(preview_label)

        preview_text = QtWidgets.QTextEdit()
        preview_text.setReadOnly(True)
        preview_text.setMinimumHeight(200)
        layout.addWidget(preview_text)

        # Update preview button
        update_preview_button = QtWidgets.QPushButton("Update Preview")
        update_preview_button.clicked.connect(
            lambda: self._update_batch_preview(
                source_edit.text(), 
                target_edit.text(), 
                preview_text,
                use_selected_only,
                selected_node_paths if use_selected_only else None
            )
        )
        layout.addWidget(update_preview_button)

        # Info label at the bottom left
        bottom_layout = QtWidgets.QHBoxLayout()

        # Add info label about selection
        if use_selected_only:
            info_label = QtWidgets.QLabel(f"Batch fixing {len(checked_items)} selected paths")
            info_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            info_label = QtWidgets.QLabel(f"Batch fixing all {len(self.all_paths_data)} paths")
            info_label.setStyleSheet("color: red; font-weight: bold;")
        bottom_layout.addWidget(info_label)

        # Add spacer to push the info label to the left
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            source_path = source_edit.text()
            target_path = target_edit.text()

            if not source_path or not target_path:
                hou.ui.displayMessage("Source and target paths cannot be empty.", 
                                     severity=hou.severityType.Error)
                return

            # Apply the changes
            self._apply_batch_fix(
                source_path, 
                target_path, 
                use_selected_only,
                selected_node_paths if use_selected_only else None
            )

    def _find_common_prefix(self):
        '''Find a common prefix among all paths'''
        if not self.all_paths_data:
            return ""

        paths = [data['file_path'] for data in self.all_paths_data]

        # Find the common prefix
        prefix = os.path.commonprefix(paths)

        # Make sure the prefix ends at a directory boundary
        if prefix and not prefix.endswith(os.sep):
            prefix = os.path.dirname(prefix) + os.sep

        return prefix

    def _find_common_prefix_for_data(self, data_list):
        '''Find a common prefix among a specific list of path data'''
        if not data_list:
            return ""

        paths = [data['file_path'] for data in data_list]

        # Find the common prefix
        prefix = os.path.commonprefix(paths)

        # Make sure the prefix ends at a directory boundary
        if prefix and not prefix.endswith(os.sep):
            prefix = os.path.dirname(prefix) + os.sep

        return prefix

    def _browse_for_directory(self, line_edit):
        """Open a directory browser and set the selected path to the line edit (Qt dialog, proper z-order)."""
        self.raise_()
        self.activateWindow()

        dlg = QtWidgets.QFileDialog(self, "Select Target Directory")
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        dlg.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)

        start_dir = line_edit.text().strip() or hou.expandString("$HIP")
        if os.path.isdir(hou.text.expandString(start_dir)):
            dlg.setDirectory(hou.text.expandString(start_dir))

        if dlg.exec() == QtWidgets.QDialog.Accepted:
            selection = dlg.selectedFiles()
            if selection:
                line_edit.setText(selection[0])


    def _update_batch_preview(self, source_path, target_path, preview_text, use_selected_only=False, selected_node_paths=None):
        '''Update the preview of batch path changes'''
        preview_text.clear()

        if not source_path:
            preview_text.setPlainText("Please enter a source path pattern.")
            return

        if not target_path:
            preview_text.setPlainText("Please enter a target path.")
            return

        preview_lines = []

        # Determine which data to process
        if use_selected_only and selected_node_paths:
            # Only process selected nodes
            data_to_process = [data for data in self.all_paths_data if data['node_path'] in selected_node_paths]
            if not data_to_process:
                preview_text.setPlainText("No selected paths found. Please select paths in the list.")
                return
        else:
            # Process all paths, not just broken ones
            data_to_process = self.all_paths_data

        # Generate preview for each path
        for data in data_to_process:
            old_path = data['file_path']
            if source_path in old_path:
                new_path = old_path.replace(source_path, target_path)
                preview_lines.append(f"Node: {data['node_name']}")
                preview_lines.append(f"Old: {old_path}")
                preview_lines.append(f"New: {new_path}")
                preview_lines.append("-" * 50)

        if not preview_lines:
            if use_selected_only:
                preview_text.setPlainText("No selected paths match the source pattern.")
            else:
                preview_text.setPlainText("No paths match the source pattern.")
        else:
            preview_text.setPlainText("\n".join(preview_lines))

    def _apply_batch_fix(self, source_path, target_path, use_selected_only=False, selected_node_paths=None):
        '''Apply batch fix to matching paths'''
        fixed_count = 0

        # Determine which data to process
        if use_selected_only and selected_node_paths:
            # Only process selected nodes
            data_to_process = [data for data in self.all_paths_data if data['node_path'] in selected_node_paths]
            if not data_to_process:
                hou.ui.displayMessage("No selected paths found. Please select paths in the list.", 
                                     severity=hou.severityType.Warning)
                return
        else:
            # Process all paths, not just broken ones
            data_to_process = self.all_paths_data

        for data in data_to_process:
            old_path = data['file_path']
            if source_path in old_path:
                new_path = old_path.replace(source_path, target_path)

                # Get the node and parameter
                node = hou.node(data['node_path'])
                if not node:
                    continue

                parm = node.parm(data['parameter'])
                if not parm:
                    continue

                # Update the parameter
                parm.set(new_path)
                fixed_count += 1

        if fixed_count > 0:
            if use_selected_only:
                hou.ui.displayMessage(f"Fixed {fixed_count} selected paths.", 
                                     severity=hou.severityType.Message)
            else:
                hou.ui.displayMessage(f"Fixed {fixed_count} paths.", 
                                     severity=hou.severityType.Message)
            # Refresh the list
            self.scan_all_paths()
        else:
            if use_selected_only:
                hou.ui.displayMessage("No selected paths were fixed. Make sure the source pattern matches your selected paths.", 
                                     severity=hou.severityType.Warning)
            else:
                hou.ui.displayMessage("No paths were fixed.", 
                                     severity=hou.severityType.Warning)

    def _show_context_menu(self, position):
        '''Show the context menu for right-click'''
        menu = QtWidgets.QMenu()
        selected_items = self.paths_tree.selectedItems()

        if selected_items:
            # Get the item under the cursor
            item = self.paths_tree.itemAt(position)
            if item:
                # Node navigation actions
                select_action = menu.addAction("Select Node")
                select_action.triggered.connect(lambda: self.select_node(item))

                # Only show these options for leaf nodes (actual file nodes)
                if item.data(0, QtCore.Qt.UserRole) is not None:
                    reveal_action = menu.addAction("Reveal in Explorer")
                    reveal_action.triggered.connect(lambda: self.reveal_in_explorer_for_item(item))

                    fix_action = menu.addAction("Fix Path")
                    fix_action.triggered.connect(lambda: self.fix_broken_path_for_item(item))

                    edit_action = menu.addAction("Edit Path")
                    edit_action.triggered.connect(lambda: self._edit_path_simple_dialog(item))

                # Add separator
                menu.addSeparator()

                # Checkbox actions
                check_action = menu.addAction("Check Selected")
                check_action.triggered.connect(lambda: self._check_selected_items(True))

                uncheck_action = menu.addAction("Uncheck Selected")
                uncheck_action.triggered.connect(lambda: self._check_selected_items(False))

                # Add separator
                menu.addSeparator()

                # Add batch fix option
                batch_fix_action = menu.addAction("Batch Fix Checked Paths")
                batch_fix_action.triggered.connect(self.batch_fix_paths)

                # Add expand/collapse options for items with children
                if item.childCount() > 0:
                    menu.addSeparator()
                    expand_action = menu.addAction("Expand All")
                    expand_action.triggered.connect(lambda: self._expand_collapse_item(item, True))

                    collapse_action = menu.addAction("Collapse All")
                    collapse_action.triggered.connect(lambda: self._expand_collapse_item(item, False))

        menu.exec_(self.paths_tree.viewport().mapToGlobal(position))

    def _check_selected_items(self, checked):
        '''Check or uncheck all selected items'''
        # Block signals to prevent recursive updates
        self.paths_tree.blockSignals(True)

        # Set check state for all selected items
        for item in self.paths_tree.selectedItems():
            check_state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
            item.setCheckState(0, check_state)
            # Update children
            self._update_children_check_state(item, check_state)
            # Update parent
            self._update_parent_check_state(item.parent())

        # Re-enable signals
        self.paths_tree.blockSignals(False)

    def _expand_collapse_item(self, item, expand):
        '''Expand or collapse an item and all its children'''
        if not item:
            return

        # Set the expanded state of this item
        item.setExpanded(expand)

        # Recursively set the expanded state of all children
        for i in range(item.childCount()):
            self._expand_collapse_item(item.child(i), expand)

    def reveal_in_explorer_for_item(self, item):
        '''Open the folder where the file should be located for a specific item'''
        if not item:
            return

        file_path = item.text(4)
        expanded_path = hou.text.expandString(file_path)
        dir_path = os.path.dirname(expanded_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                hou.ui.displayMessage(f"Created directory: {dir_path}", 
                                     severity=hou.severityType.Message)
            except Exception as e:
                hou.ui.displayMessage(f"Failed to create directory: {str(e)}", 
                                     severity=hou.severityType.Error)
                return

        # Open the directory
        if platform.system() == "Windows":
            os.startfile(dir_path)
        elif platform.system() == "Darwin":
            os.system(f"open \"{dir_path}\"")
        else:
            os.system(f"xdg-open \"{dir_path}\"")

    def _edit_path_simple_dialog(self, item):
        '''Edit the path directly using a simple dialog'''
        if not item:
            return

        node_path = item.text(1)
        parameter = item.text(3)
        current_path = item.text(4)
        expanded_path = hou.text.expandString(current_path)

        node = hou.node(node_path)
        if not node:
            hou.ui.displayMessage(f"Node not found: {node_path}", 
                                 severity=hou.severityType.Error)
            return

        # Get the parameter
        parm = node.parm(parameter)
        if not parm:
            hou.ui.displayMessage(f"Parameter not found: {parameter}", 
                                 severity=hou.severityType.Error)
            return

        # Create a dialog for editing the path
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Path")
        dialog.setMinimumWidth(600)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Add info label
        info_label = QtWidgets.QLabel(f"Edit path for node: <b>{node.name()}</b>")
        info_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(info_label)

        # Path edit field
        path_layout = QtWidgets.QHBoxLayout()
        path_label = QtWidgets.QLabel("Path:")
        path_label.setStyleSheet("font-size: 14px;")
        path_layout.addWidget(path_label)

        path_edit = QtWidgets.QLineEdit(current_path)
        path_edit.setStyleSheet("font-size: 14px;")
        path_edit.setMinimumWidth(400)
        path_layout.addWidget(path_edit)

        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(lambda: self._browse_for_file(path_edit, current_path))
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_path = path_edit.text()
            if new_path != current_path:
                parm.set(new_path)
                self.scan_all_paths()
                hou.ui.displayMessage(f"Updated path for {node.name()}", 
                                     severity=hou.severityType.Message)

    def _browse_for_file(self, line_edit, current_path):
        '''Browse for a file and update the line edit'''
        file_type = self._get_file_type_from_path(current_path)
        expanded_path = hou.text.expandString(current_path)

        new_path = hou.ui.selectFile(
            title="Select File Path",
            file_type=file_type,
            start_directory=os.path.dirname(expanded_path),
            chooser_mode=hou.fileChooserMode.Read
        )

        if new_path:
            line_edit.setText(new_path)

    def fix_broken_path_for_item(self, item):
        '''Fix the path for a specific item'''
        if not item:
            return

        node_path = item.text(1)
        parameter = item.text(3)
        current_path = item.text(4)
        expanded_path = hou.text.expandString(current_path)

        node = hou.node(node_path)
        if not node:
            hou.ui.displayMessage(f"Node not found: {node_path}", 
                                 severity=hou.severityType.Error)
            return

        # Get the parameter
        parm = node.parm(parameter)
        if not parm:
            hou.ui.displayMessage(f"Parameter not found: {parameter}", 
                                 severity=hou.severityType.Error)
            return

        # Check if we can find similar files to suggest
        suggestions = self._find_similar_files(expanded_path)

        if suggestions:
            # Create a dialog to show suggestions
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Fix Path")
            dialog.setMinimumWidth(700)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Add info label
            info_label = QtWidgets.QLabel(
                f"The file <b>{os.path.basename(expanded_path)}</b> was not found.<br>"
                f"Here are some similar files that might be what you're looking for:"
            )
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            # Add list widget for suggestions
            list_widget = QtWidgets.QListWidget()
            for suggestion in suggestions:
                item = QtWidgets.QListWidgetItem(suggestion)
                list_widget.addItem(item)

            layout.addWidget(list_widget)

            # Add buttons
            button_layout = QtWidgets.QHBoxLayout()

            use_selected_button = QtWidgets.QPushButton("Use Selected")
            use_selected_button.clicked.connect(dialog.accept)
            button_layout.addWidget(use_selected_button)

            browse_button = QtWidgets.QPushButton("Browse...")
            browse_button.clicked.connect(lambda: dialog.done(2))  # Custom return code
            button_layout.addWidget(browse_button)

            cancel_button = QtWidgets.QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

            # Show dialog
            result = dialog.exec_()

            if result == QtWidgets.QDialog.Accepted:
                # Use selected suggestion
                selected_items = list_widget.selectedItems()
                if selected_items:
                    new_path = selected_items[0].text()
                    parm.set(new_path)
                    self.scan_all_paths()
                    hou.ui.displayMessage(f"Updated path for {node.name()}", 
                                         severity=hou.severityType.Message)
            elif result == 2:  # Browse
                # Let the user select a new file
                file_type = self._get_file_type_from_path(current_path)
                new_path = hou.ui.selectFile(
                    title="Select New File Path",
                    file_type=file_type,
                    start_directory=os.path.dirname(expanded_path),
                    chooser_mode=hou.fileChooserMode.Read
                )

                if new_path:
                    parm.set(new_path)
                    self.scan_all_paths()
                    hou.ui.displayMessage(f"Updated path for {node.name()}", 
                                         severity=hou.severityType.Message)
        else:
            # No suggestions found, just show the file browser
            file_type = self._get_file_type_from_path(current_path)
            new_path = hou.ui.selectFile(
                title="Select New File Path",
                file_type=file_type,
                start_directory=os.path.dirname(expanded_path),
                chooser_mode=hou.fileChooserMode.Read
            )

            if new_path:
                parm.set(new_path)
                self.scan_all_paths()
                hou.ui.displayMessage(f"Updated path for {node.name()}", 
                                     severity=hou.severityType.Message)

def show_file_paths_manager():
    '''Show the path manager window'''
    win = FilePathsManagerUI()
    win.show()
    return win

# Create a shelf tool function
def create_shelf_tool():
    '''Create a shelf tool for the Path Manager'''
    import hou

    # Get the current shelf set
    shelf_set = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.ShelfTab)
    if not shelf_set:
        hou.ui.displayMessage("No shelf tab found.", severity=hou.severityType.Error)
        return

    # Create the tool
    tool = shelf_set.addTool("Path Manager")

    # Set the icon - using a default icon
    tool.setIcon("MISC_python")

    # Set the script
    tool.setScript('''
import sys
import os

# Add the custom_tools path to sys.path if it's not already there
custom_tools_path = os.path.join(hou.expandString("$HOUDINI_USER_PREF_DIR"), "custom_tools", "scripts", "python")
if custom_tools_path not in sys.path:
    sys.path.append(custom_tools_path)

# Import and show the path manager
from tools.file_path_manager import show_file_paths_manager
win = show_file_paths_manager()
''')

    # Set the help text
    tool.setHelpText("Scan the scene for nodes with file paths and fix them")

    hou.ui.displayMessage("Path Manager shelf tool created successfully.", 
                         severity=hou.severityType.Message)

# For testing in Houdini Python Shell
if __name__ == "__main__":
    win = show_file_paths_manager()
