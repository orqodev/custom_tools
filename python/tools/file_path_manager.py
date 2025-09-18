import hou
import os
import platform
from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools

class FilePathsManagerUI(QtWidgets.QMainWindow):
    # Node types and their file path parameters to check (values as lists)
    FILE_PATH_NODES = {
        # SOP nodes
        "file": ["file"],
        "alembicarchive": ["fileName"],
        "filecache": ["file"],
        "filemerge": ["file"],
        "dopio": ["file"],
        "vellumio": ["file"],
        "rbdio": ["file"],

        # ROP nodes
        "rop_geometry": ["sopoutput"],
        "alembic": ["fileName"],
        "rop_fbx": ["sopoutput"],
        "rop_dop": ["dopoutput"],

        # Texture nodes
        "texture::2.0": ["map"],
        "redshift::TextureSampler": ["tex0"],

        # MaterialX nodes
        "mtlximage": ["file"],
        "mtlxtiledimage": ["file"],
        "usduvtexture::2.0": ["file"],

        # VEX Principled Shader (seed list; will be auto-augmented below)
        "principledshader::2.0": [
            "aniso_texture",
            "anisodir_texture",
            "baseNormal_texture",
            "basecolor_texture",
            "coatNormal_texture",
            "coat_texture",
            "coatrough_texture",
            "dispTex_texture",
            "dispersion_texture",
            "emitcolor_texture",
            "ior_texture",
            "metallic_texture",
            "occlusion_texture",
            "opaccolor_texture",
            "reflect_texture",
            "reflecttint_texture",
            "rough_texture",
            "sheen_texture",
            "sheentint_texture",
            "sss_texture",
            "ssscolor_texture",
            "sssdist_texture",
            "transcolor_texture",
            "transdist_texture",
            "transparency_texture",
        ],

        # LOP nodes
        "assetreference": ["filepath"],
        "reference::2.0": ["filepath1"],
        "layout": ["filepath1"],
        "sublayer": ["filepath1"],
        "domelight::3.0": ["inputs:texture:file"],
        "componentoutput": ["lopoutput"],
        "volume": ["filepath1"],
        "usdrender_rop": ["outputimage"],

        # Other common nodes with file paths
        "ifd": ["soho_diskfile"],
        "opengl": ["picture"],
        "comp": ["copoutput"],
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
        if column != 0:
            return
        self.paths_tree.blockSignals(True)
        check_state = item.checkState(0)
        self._update_children_check_state(item, check_state)
        self._update_parent_check_state(item.parent())
        self.paths_tree.blockSignals(False)

    def _update_children_check_state(self, parent_item, check_state):
        if not parent_item:
            return
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child.setCheckState(0, check_state)
            self._update_children_check_state(child, check_state)

    def _update_parent_check_state(self, parent_item):
        if not parent_item:
            return
        checked_count = 0
        total_count = parent_item.childCount()
        for i in range(total_count):
            if parent_item.child(i).checkState(0) == QtCore.Qt.Checked:
                checked_count += 1
        if checked_count == 0:
            parent_item.setCheckState(0, QtCore.Qt.Unchecked)
        elif checked_count == total_count:
            parent_item.setCheckState(0, QtCore.Qt.Checked)
        else:
            parent_item.setCheckState(0, QtCore.Qt.PartiallyChecked)
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

            # Copy dict so we can merge discoveries without mutating the class attr mid-iteration
            nodes_to_check = dict(self.FILE_PATH_NODES)

            # Keep track of new entries to add after iteration
            new_entries = {}

            for node_type, parm_names in nodes_to_check.items():
                # normalize to list
                if isinstance(parm_names, str):
                    parm_names = [parm_names]

                categories = [
                    hou.sopNodeTypeCategory(),
                    hou.dopNodeTypeCategory(),
                    hou.ropNodeTypeCategory(),
                    hou.vopNodeTypeCategory(),
                    hou.lopNodeTypeCategory(),
                    hou.shopNodeTypeCategory(),
                ]

                # Try to add materialx category if it exists
                try:
                    materialx_category = hou.nodeTypeCategory("materialx")
                    if materialx_category:
                        categories.append(materialx_category)
                except:
                    pass

                # Add mtlx:: namespace variant if needed
                if node_type.startswith("mtlx") and not node_type.startswith("mtlx::"):
                    new_entries[f"mtlx::{node_type}"] = parm_names

                for category in categories:
                    node_type_obj = hou.nodeType(category, node_type)
                    if not node_type_obj:
                        continue

                    nodes = node_type_obj.instances()
                    for node in nodes:
                        for parm_name in parm_names:
                            parm = node.parm(parm_name)
                            if not parm:
                                continue
                            file_path = parm.eval()
                            if not file_path:
                                continue

                            node_name, node_path, node_type_name = self._get_node_details(node)
                            all_nodes_with_paths.append({
                                "node": node,
                                "node_name": node_name,
                                "node_path": node_path,
                                "node_type": node_type_name,
                                "parameter": parm_name,
                                "file_path": file_path
                            })

            # Merge any new namespace entries (like mtlx::mtlxtiledimage)
            for k, v in new_entries.items():
                existing = self.FILE_PATH_NODES.get(k, [])
                if isinstance(existing, str):
                    existing = [existing]
                self.FILE_PATH_NODES[k] = sorted(set(existing + v))

            print(f"Found {len(all_nodes_with_paths)} nodes with file paths")

            # Phase 2: Evaluate which paths are broken and add all paths to the tree
            for node_data in all_nodes_with_paths:
                expanded_path = hou.text.expandString(node_data["file_path"])
                print(f"Checking path: {expanded_path}")

                normalized_path = os.path.normpath(expanded_path)
                path_exists = self._check_path_exists(normalized_path)
                print(f"Path exists: {path_exists}")

                node_data["expanded_path"] = expanded_path

                # Copy without the node object for UI storage
                display_data = node_data.copy()
                display_data.pop("node")
                display_data["path_exists"] = path_exists

                self._add_to_tree(display_data)
                self.all_paths_data.append(display_data)
                self.total_paths += 1

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
            if os.path.isfile(path):
                print(f"File exists (isfile): {path}")
                try:
                    with open(path, 'rb') as f:
                        f.read(1)
                    return True
                except (IOError, PermissionError) as e:
                    print(f"File exists but can't be opened: {path}, Error: {str(e)}")
                    return False

            if os.path.isdir(path):
                print(f"Directory exists: {path}")
                return True

            if os.path.exists(path):
                print(f"Path exists (generic): {path}")
                return True

            # Sequence pattern check
            import re
            sequence_match = re.search(r'\.(\d+)\.(exr|jpg|png|tif|tiff|bgeo|bgeo\.sc|abc|obj|fbx|vdb)$', path, re.IGNORECASE)
            if sequence_match:
                dir_path = os.path.dirname(path)
                if not os.path.exists(dir_path):
                    print(f"Directory does not exist: {dir_path}")
                    return False
                base_name = os.path.basename(path)
                frame_number = sequence_match.group(1)
                extension = sequence_match.group(2)
                pattern_base = base_name.replace(f".{frame_number}.{extension}", "")
                for file in os.listdir(dir_path):
                    if pattern_base in file and f".{extension}" in file.lower():
                        print(f"Found sequence file match: {file}")
                        return True
                print(f"No sequence files found matching pattern: {pattern_base}*.{extension}")
                return False

            # UNC paths on Windows
            if platform.system() == "Windows" and path.startswith("\\\\"):
                share_parts = path.split("\\")
                if len(share_parts) >= 4:
                    share_path = f"\\\\{share_parts[2]}\\{share_parts[3]}"
                    if os.path.exists(share_path):
                        print(f"Network share exists: {share_path}")
                        return False

            if "$" in path:
                expanded_path = hou.expandString(path)
                if expanded_path != path:
                    print(f"Re-expanding path with $ signs: {path} -> {expanded_path}")
                    return self._check_path_exists(expanded_path)

            print(f"Path confirmed not to exist: {path}")
            return False

        except Exception as e:
            print(f"Error checking if path exists: {str(e)}")
            return False

    def _add_to_tree(self, node_data):
        '''Add a node entry to the tree widget'''
        node_path = node_data['node_path']
        path_parts = node_path.split('/')

        if path_parts[0] == '':
            path_parts = path_parts[1:]

        parent_item = None
        current_path = ""

        if len(path_parts) > 2:
            root_name = path_parts[0]
            current_path = "/" + root_name

            root_item = None
            for i in range(self.paths_tree.topLevelItemCount()):
                top_item = self.paths_tree.topLevelItem(i)
                if top_item.data(1, QtCore.Qt.DisplayRole) == current_path:
                    root_item = top_item
                    break

            if not root_item:
                root_item = QtWidgets.QTreeWidgetItem(self.paths_tree)
                root_item.setText(0, root_name)
                root_item.setText(1, current_path)
                root_item.setFlags(root_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                root_item.setCheckState(0, QtCore.Qt.Unchecked)

            parent_item = root_item

            for i in range(1, len(path_parts) - 1):
                part = path_parts[i]
                current_path += "/" + part

                child_item = None
                for j in range(parent_item.childCount()):
                    item = parent_item.child(j)
                    if item.data(1, QtCore.Qt.DisplayRole) == current_path:
                        child_item = item
                        break

                if not child_item:
                    child_item = QtWidgets.QTreeWidgetItem(parent_item)
                    child_item.setText(0, part)
                    child_item.setText(1, current_path)
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    child_item.setCheckState(0, QtCore.Qt.Unchecked)

                parent_item = child_item

        if parent_item:
            item = QtWidgets.QTreeWidgetItem(parent_item)
        else:
            item = QtWidgets.QTreeWidgetItem(self.paths_tree)

        item.setText(0, node_data['node_name'])
        item.setText(1, node_data['node_path'])
        item.setText(2, node_data['node_type'])
        item.setText(3, node_data['parameter'])
        item.setText(4, node_data['file_path'])

        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)
        item.setData(0, QtCore.Qt.UserRole, node_data)

        if 'path_exists' in node_data:
            if not node_data['path_exists']:
                for col in range(5):
                    item.setForeground(col, QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            else:
                for col in range(5):
                    item.setForeground(col, QtGui.QBrush(QtGui.QColor(0, 128, 0)))

    def _get_node_details(self, node):
        return node.name(), node.path(), node.type().name()

    def _update_stats(self):
        self.total_nodes_label.setText(f"Total Nodes with Paths: {self.total_paths} (Broken: {self.total_broken_paths})")

    def select_node(self, item):
        try:
            node_path = item.text(1)
            path_parts = node_path.split('/')
            if len(path_parts) > 3:
                print(f"Handling nested node path: {node_path}")
                node = hou.node(node_path)
                if node:
                    node.setSelected(True)
                    network_pane = None
                    for pane in hou.ui.paneTabs():
                        if isinstance(pane, hou.NetworkEditor):
                            network_pane = pane
                            break
                    if network_pane:
                        parent_path = node.parent().path()
                        print(f"Navigating to parent: {parent_path}")
                        network_pane.cd(parent_path)
                        network_pane.frameSelection()
                else:
                    found_node = None
                    for i in range(len(path_parts) - 1, 1, -1):
                        test_path = '/'.join(path_parts[:i])
                        test_node = hou.node(test_path)
                        if test_node:
                            found_node = test_node
                            break
                    if found_node:
                        found_node.setSelected(True)
                        network_pane = None
                        for pane in hou.ui.paneTabs():
                            if isinstance(pane, hou.NetworkEditor):
                                network_pane = pane
                                break
                        if network_pane:
                            parent_path = found_node.parent().path()
                            network_pane.cd(parent_path)
                            network_pane.frameSelection()
                            hou.ui.displayMessage(
                                f"Could not find the exact node: {node_path}\nNavigated to the closest parent: {found_node.path()}",
                                severity=hou.severityType.Warning
                            )
                    else:
                        hou.ui.displayMessage(
                            f"Could not find any part of the node path: {node_path}",
                            severity=hou.severityType.Error
                        )
            else:
                node = hou.node(node_path)
                if node:
                    node.setSelected(True)
                    network_pane = None
                    for pane in hou.ui.paneTabs():
                        if isinstance(pane, hou.NetworkEditor):
                            network_pane = pane
                            break
                    if network_pane:
                        network_pane.cd(node.parent().path())
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
        selected_items = self.paths_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage("Please select a path first",
                                 severity=hou.severityType.Error)
            return
        self.reveal_in_explorer_for_item(selected_items[0])

    def fix_broken_path(self):
        selected_items = self.paths_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage("Please select a path to fix",
                                 severity=hou.severityType.Error)
            return
        self.fix_broken_path_for_item(selected_items[0])

    def _find_similar_files(self, broken_path):
        suggestions = []
        try:
            dir_path = os.path.dirname(broken_path)
            filename = os.path.basename(broken_path)
            file_base, file_ext = os.path.splitext(filename)

            if not os.path.exists(dir_path):
                parent_dir = os.path.dirname(dir_path)
                if os.path.exists(parent_dir):
                    for item in os.listdir(parent_dir):
                        potential_dir = os.path.join(parent_dir, item)
                        if os.path.isdir(potential_dir) and item.lower() in os.path.basename(dir_path).lower():
                            for file in os.listdir(potential_dir):
                                if file_ext.lower() == os.path.splitext(file)[1].lower():
                                    suggestions.append(os.path.join(potential_dir, file))
                return suggestions

            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path) and file_ext.lower() == os.path.splitext(file)[1].lower():
                    if file_base.lower() in os.path.splitext(file)[0].lower() or \
                       os.path.splitext(file)[0].lower() in file_base.lower():
                        suggestions.append(file_path)

            if not suggestions:
                parent_dir = os.path.dirname(dir_path)
                if os.path.exists(parent_dir):
                    for item in os.listdir(parent_dir):
                        potential_dir = os.path.join(parent_dir, item)
                        if os.path.isdir(potential_dir):
                            for file in os.listdir(potential_dir):
                                if file_ext.lower() == os.path.splitext(file)[1].lower():
                                    suggestions.append(os.path.join(potential_dir, file))

            suggestions.sort(key=lambda x: self._similarity_score(filename, os.path.basename(x)), reverse=True)
            return suggestions[:10]
        except Exception as e:
            print(f"Error finding similar files: {str(e)}")
            return []

    def _similarity_score(self, str1, str2):
        str1 = str1.lower()
        str2 = str2.lower()
        if str1 == str2:
            return 1.0
        if str1 in str2 or str2 in str1:
            return 0.8
        common_chars = set(str1) & set(str2)
        return len(common_chars) / max(len(str1), len(str2))

    def _get_file_type_from_path(self, path):
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
        checked_items = []
        if parent_item is None:
            for i in range(self.paths_tree.topLevelItemCount()):
                item = self.paths_tree.topLevelItem(i)
                if item.checkState(0) == QtCore.Qt.Checked and item.data(0, QtCore.Qt.UserRole) is not None:
                    checked_items.append(item)
                checked_items.extend(self._get_checked_items(item))
        else:
            for i in range(parent_item.childCount()):
                item = parent_item.child(i)
                if item.checkState(0) == QtCore.Qt.Checked and item.data(0, QtCore.Qt.UserRole) is not None:
                    checked_items.append(item)
                checked_items.extend(self._get_checked_items(item))
        return checked_items

    def batch_fix_paths(self):
        checked_items = self._get_checked_items()

        if not checked_items:
            if not self.all_paths_data:
                hou.ui.displayMessage("No paths found. Please scan the scene first.",
                                     severity=hou.severityType.Warning)
                return
            else:
                result = hou.ui.displayMessage(
                    "No paths are checked. Do you want to apply batch fix to all paths?",
                    buttons=("Yes", "No"),
                    severity=hou.severityType.Warning
                )
                if result == 1:
                    return
                use_selected_only = False
        else:
            use_selected_only = True
            selected_node_paths = [item.text(1) for item in checked_items]
            print(f"Checked node paths for batch fix: {selected_node_paths}")

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Batch Fix Paths")
        dialog.setMinimumWidth(600)

        layout = QtWidgets.QVBoxLayout(dialog)

        source_layout = QtWidgets.QHBoxLayout()
        source_label = QtWidgets.QLabel("Source Path Pattern:")
        source_layout.addWidget(source_label)
        source_edit = QtWidgets.QLineEdit()
        source_layout.addWidget(source_edit)

        if use_selected_only:
            selected_data = [data for data in self.all_paths_data if data['node_path'] in selected_node_paths]
            common_prefix = self._find_common_prefix_for_data(selected_data)
        else:
            common_prefix = self._find_common_prefix()
        if common_prefix:
            source_edit.setText(common_prefix)
        layout.addLayout(source_layout)

        target_layout = QtWidgets.QHBoxLayout()
        target_label = QtWidgets.QLabel("Target Path:")
        target_layout.addWidget(target_label)
        target_edit = QtWidgets.QLineEdit()
        target_layout.addWidget(target_edit)
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(lambda: self._browse_for_directory(target_edit))
        target_layout.addWidget(browse_button)
        layout.addLayout(target_layout)

        preview_label = QtWidgets.QLabel("Preview of changes:")
        layout.addWidget(preview_label)
        preview_text = QtWidgets.QTextEdit()
        preview_text.setReadOnly(True)
        preview_text.setMinimumHeight(200)
        layout.addWidget(preview_text)

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

        bottom_layout = QtWidgets.QHBoxLayout()
        if use_selected_only:
            info_label = QtWidgets.QLabel(f"Batch fixing {len(checked_items)} selected paths")
            info_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            info_label = QtWidgets.QLabel(f"Batch fixing all {len(self.all_paths_data)} paths")
            info_label.setStyleSheet("color: red; font-weight: bold;")
        bottom_layout.addWidget(info_label)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            source_path = source_edit.text()
            target_path = target_edit.text()
            if not source_path or not target_path:
                hou.ui.displayMessage("Source and target paths cannot be empty.",
                                     severity=hou.severityType.Error)
                return
            self._apply_batch_fix(
                source_path,
                target_path,
                use_selected_only,
                selected_node_paths if use_selected_only else None
            )

    def _find_common_prefix(self):
        if not self.all_paths_data:
            return ""
        paths = [data['file_path'] for data in self.all_paths_data]
        prefix = os.path.commonprefix(paths)
        if prefix and not prefix.endswith(os.sep):
            prefix = os.path.dirname(prefix) + os.sep
        return prefix

    def _find_common_prefix_for_data(self, data_list):
        if not data_list:
            return ""
        paths = [data['file_path'] for data in data_list]
        prefix = os.path.commonprefix(paths)
        if prefix and not prefix.endswith(os.sep):
            prefix = os.path.dirname(prefix) + os.sep
        return prefix

    def _browse_for_directory(self, line_edit):
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
        preview_text.clear()
        if not source_path:
            preview_text.setPlainText("Please enter a source path pattern.")
            return
        if not target_path:
            preview_text.setPlainText("Please enter a target path.")
            return

        if use_selected_only and selected_node_paths:
            data_to_process = [data for data in self.all_paths_data if data['node_path'] in selected_node_paths]
            if not data_to_process:
                preview_text.setPlainText("No selected paths found. Please select paths in the list.")
                return
        else:
            data_to_process = self.all_paths_data

        preview_lines = []
        for data in data_to_process:
            old_path = data['file_path']
            if source_path in old_path:
                new_path = old_path.replace(source_path, target_path)
                preview_lines.append(f"Node: {data['node_name']}")
                preview_lines.append(f"Old: {old_path}")
                preview_lines.append(f"New: {new_path}")
                preview_lines.append("-" * 50)

        if not preview_lines:
            preview_text.setPlainText("No paths match the source pattern." if not use_selected_only
                                      else "No selected paths match the source pattern.")
        else:
            preview_text.setPlainText("\n".join(preview_lines))

    def _apply_batch_fix(self, source_path, target_path, use_selected_only=False, selected_node_paths=None):
        fixed_count = 0

        if use_selected_only and selected_node_paths:
            data_to_process = [data for data in self.all_paths_data if data['node_path'] in selected_node_paths]
            if not data_to_process:
                hou.ui.displayMessage("No selected paths found. Please select paths in the list.",
                                     severity=hou.severityType.Warning)
                return
        else:
            data_to_process = self.all_paths_data

        for data in data_to_process:
            old_path = data['file_path']
            if source_path in old_path:
                new_path = old_path.replace(source_path, target_path)
                node = hou.node(data['node_path'])
                if not node:
                    continue
                parm = node.parm(data['parameter'])
                if not parm:
                    continue
                parm.set(new_path)
                fixed_count += 1

        if fixed_count > 0:
            hou.ui.displayMessage(f"Fixed {fixed_count} {'selected ' if use_selected_only else ''}paths.",
                                 severity=hou.severityType.Message)
            self.scan_all_paths()
        else:
            hou.ui.displayMessage("No paths were fixed." if not use_selected_only
                                  else "No selected paths were fixed. Make sure the source pattern matches your selected paths.",
                                  severity=hou.severityType.Warning)

    def _show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        selected_items = self.paths_tree.selectedItems()

        if selected_items:
            item = self.paths_tree.itemAt(position)
            if item:
                select_action = menu.addAction("Select Node")
                select_action.triggered.connect(lambda: self.select_node(item))

                if item.data(0, QtCore.Qt.UserRole) is not None:
                    reveal_action = menu.addAction("Reveal in Explorer")
                    reveal_action.triggered.connect(lambda: self.reveal_in_explorer_for_item(item))

                    fix_action = menu.addAction("Fix Path")
                    fix_action.triggered.connect(lambda: self.fix_broken_path_for_item(item))

                    edit_action = menu.addAction("Edit Path")
                    edit_action.triggered.connect(lambda: self._edit_path_simple_dialog(item))

                menu.addSeparator()

                check_action = menu.addAction("Check Selected")
                check_action.triggered.connect(lambda: self._check_selected_items(True))

                uncheck_action = menu.addAction("Uncheck Selected")
                uncheck_action.triggered.connect(lambda: self._check_selected_items(False))

                menu.addSeparator()
                batch_fix_action = menu.addAction("Batch Fix Checked Paths")
                batch_fix_action.triggered.connect(self.batch_fix_paths)

                if item.childCount() > 0:
                    menu.addSeparator()
                    expand_action = menu.addAction("Expand All")
                    expand_action.triggered.connect(lambda: self._expand_collapse_item(item, True))
                    collapse_action = menu.addAction("Collapse All")
                    collapse_action.triggered.connect(lambda: self._expand_collapse_item(item, False))

        menu.exec_(self.paths_tree.viewport().mapToGlobal(position))

    def _check_selected_items(self, checked):
        self.paths_tree.blockSignals(True)
        for item in self.paths_tree.selectedItems():
            check_state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
            item.setCheckState(0, check_state)
            self._update_children_check_state(item, check_state)
            self._update_parent_check_state(item.parent())
        self.paths_tree.blockSignals(False)

    def _expand_collapse_item(self, item, expand):
        if not item:
            return
        item.setExpanded(expand)
        for i in range(item.childCount()):
            self._expand_collapse_item(item.child(i), expand)

    def reveal_in_explorer_for_item(self, item):
        if not item:
            return
        file_path = item.text(4)
        expanded_path = hou.text.expandString(file_path)
        dir_path = os.path.dirname(expanded_path)

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                hou.ui.displayMessage(f"Created directory: {dir_path}",
                                     severity=hou.severityType.Message)
            except Exception as e:
                hou.ui.displayMessage(f"Failed to create directory: {str(e)}",
                                     severity=hou.severityType.Error)
                return

        if platform.system() == "Windows":
            os.startfile(dir_path)
        elif platform.system() == "Darwin":
            os.system(f"open \"{dir_path}\"")
        else:
            os.system(f"xdg-open \"{dir_path}\"")

    def _edit_path_simple_dialog(self, item):
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

        parm = node.parm(parameter)
        if not parm:
            hou.ui.displayMessage(f"Parameter not found: {parameter}",
                                 severity=hou.severityType.Error)
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Path")
        dialog.setMinimumWidth(600)

        layout = QtWidgets.QVBoxLayout(dialog)

        info_label = QtWidgets.QLabel(f"Edit path for node: <b>{node.name()}</b>")
        info_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(info_label)

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

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_path = path_edit.text()
            if new_path != current_path:
                parm.set(new_path)
                self.scan_all_paths()
                hou.ui.displayMessage(f"Updated path for {node.name()}",
                                     severity=hou.severityType.Message)

    def _browse_for_file(self, line_edit, current_path):
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

        parm = node.parm(parameter)
        if not parm:
            hou.ui.displayMessage(f"Parameter not found: {parameter}",
                                 severity=hou.severityType.Error)
            return

        suggestions = self._find_similar_files(expanded_path)

        if suggestions:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Fix Path")
            dialog.setMinimumWidth(700)

            layout = QtWidgets.QVBoxLayout(dialog)

            info_label = QtWidgets.QLabel(
                f"The file <b>{os.path.basename(expanded_path)}</b> was not found.<br>"
                f"Here are some similar files that might be what you're looking for:"
            )
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            list_widget = QtWidgets.QListWidget()
            for suggestion in suggestions:
                item2 = QtWidgets.QListWidgetItem(suggestion)
                list_widget.addItem(item2)
            layout.addWidget(list_widget)

            button_layout = QtWidgets.QHBoxLayout()
            use_selected_button = QtWidgets.QPushButton("Use Selected")
            use_selected_button.clicked.connect(dialog.accept)
            button_layout.addWidget(use_selected_button)
            browse_button = QtWidgets.QPushButton("Browse...")
            browse_button.clicked.connect(lambda: dialog.done(2))
            button_layout.addWidget(browse_button)
            cancel_button = QtWidgets.QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            result = dialog.exec_()

            if result == QtWidgets.QDialog.Accepted:
                selected_items = list_widget.selectedItems()
                if selected_items:
                    new_path = selected_items[0].text()
                    parm.set(new_path)
                    self.scan_all_paths()
                    hou.ui.displayMessage(f"Updated path for {node.name()}",
                                         severity=hou.severityType.Message)
            elif result == 2:
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

    shelf_set = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.ShelfTab)
    if not shelf_set:
        hou.ui.displayMessage("No shelf tab found.", severity=hou.severityType.Error)
        return

    tool = shelf_set.addTool("Path Manager")
    tool.setIcon("MISC_python")
    tool.setScript('''
import sys
import os
custom_tools_path = os.path.join(hou.expandString("$HOUDINI_USER_PREF_DIR"), "custom_tools", "scripts", "python")
if custom_tools_path not in sys.path:
    sys.path.append(custom_tools_path)
from tools.file_path_manager import show_file_paths_manager
win = show_file_paths_manager()
''')
    tool.setHelpText("Scan the scene for nodes with file paths and fix them")
    hou.ui.displayMessage("Path Manager shelf tool created successfully.", 
                         severity=hou.severityType.Message)

# For testing in Houdini Python Shell
if __name__ == "__main__":
    win = show_file_paths_manager()
