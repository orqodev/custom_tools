import hou
import os
import platform
import shutil
from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools

class SceneCacheManagerUI(QtWidgets.QMainWindow):
    # CONST
    CACHE_NODES = {
        "filecache":"file",
        "rop_geometry":"sopoutput",
        "rop_alembic":"filename",
        "rop_fbx":"sopoutput",
        "rop_dop":"dopoutput",
        "vellumio":"sopoutput",
        "rbdio":"sopoutput",
        "kinefx::characteriom":"sopoutput",
    }


    def __init__(self):
        super().__init__()
        script_path = hou.text.expandString("$CUSTOM_TOOLS/ui/scene_cache_manager.ui")
        self.ui = QtUiTools.QUiLoader().load(script_path, parentWidget=self)
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Scene Cache Manager")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(400)
        self._init_ui()
        self._setup_connections()
        self.total_cache_size = 0
        #STORE DATA
        self.cache_data = []

    def _init_ui(self):
        ''' INITIALIZE THE UI COMPONENTS'''
        self.cache_tree = self.ui.findChild(QtWidgets.QTreeWidget, 'cache_tree')
        self.total_nodes = self.ui.findChild(QtWidgets.QLabel, 'lb_total_nodes')
        self.total_cache  = self.ui.findChild(QtWidgets.QLabel, 'lb_total_size')
        self.unused_version = self.ui.findChild(QtWidgets.QLabel, 'lb_unused_versions')
        self.scan_scene = self.ui.findChild(QtWidgets.QPushButton, 'bt_scan')
        self.show_explorer = self.ui.findChild(QtWidgets.QPushButton,'bt_reveal')
        self.clean_old = self.ui.findChild(QtWidgets.QPushButton, 'bt_cleanup')

        #Enable Alphabetic Order
        self.cache_tree.setSortingEnabled(True)

        # Add right-click context menu
        self.cache_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cache_tree.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_connections(self):
        ''' Set up Signal Connections'''
        self.scan_scene.clicked.connect(self.scan_scene_caches)
        self.cache_tree.itemDoubleClicked.connect(self.select_node)
        self.show_explorer.clicked.connect(self.reveal_in_explorer)
        self.clean_old.clicked.connect(self.cleanup_old_versions)

    def scan_scene_caches(self):
        ''' Scan scene for all cache nodes and updates UI'''
        try:
            self.cache_tree.clear()
            self.cache_data = []
            self.total_cache_size = 0
            # Get all nodes in the scene
            for node_type,parm_name in self.CACHE_NODES.items():
                # Find all nodes based on the category
                for category in [hou.sopNodeTypeCategory(), hou.dopNodeTypeCategory(), hou.ropNodeTypeCategory()]:
                    node_type_sop = hou.nodeType(category,node_type)
                    if node_type_sop:
                        cache_nodes = node_type_sop.instances()
                        for node in cache_nodes:
                            cache_path = node.parm(parm_name).eval()
                            env_var = hou.text.expandString("$CUSTOM_TOOLS")
                            if cache_path.startswith(env_var):
                                cache_path = cache_path.replace(env_var,"$CUSTOM_TOOLS")

                            #Check if the path is valid
                            if not cache_path:
                                continue
                            node_name, node_path, node_type_name =  self._get_node_details(node)
                            current_version = self._get_current_version(node_path)
                            node_data = {
                                "node_name": node_name,
                                "node_path": node_path,
                                "node_type": node_type_name,
                                "cache_path": cache_path,
                                "current_version":current_version,
                                "other_versions":self._get_other_versions(current_version,cache_path),
                                "last_modified":self._get_last_modified(cache_path),
                                "total_size": self._get_total_size(node,cache_path,node_type_name),
                            }
                            self._add_to_tree(node_data)
                            self.cache_data.append(node_data)
            self._update_stats()
        except Exception as e:
            hou.ui.displayMessage(f"Error scanning scene: {str(e)}",severity=hou.severityType.Error)

    def _add_to_tree(self,node_data):
        ''' Add a note entry to the tree widget'''
        item = QtWidgets.QTreeWidgetItem(self.cache_tree)
        item.setText(0,node_data['node_name'])
        item.setText(1,node_data['node_path'])
        item.setText(2,node_data['node_type'])
        item.setText(3,node_data['cache_path'])
        item.setText(4,str(node_data['current_version']))
        item.setText(5,str(node_data['other_versions']))
        item.setText(6,node_data['last_modified'])
        item.setText(7,node_data['total_size'])

    def _get_node_details(self, node):
        ''' Get the correct node details - name, path, type
        Args
            node - the node we want to check
        Return
            tuple - with 3 values
        '''
        node_name = node.name()
        node_path = node.path()
        node_type = node.type().name()
        check_parent = node.parent()

        if node_name == "render" and check_parent.name() == "filecache":
            node_name = node.parent().parent().name()
            node_path = node.parent().parent().path()
            node_type = node.parent().parent().type().name()
        elif node_name == "render":
            node_name = node.parent().name()
            node_path = node.parent().path()
            node_type = node.parent().type().name()

        return node_name, node_path, node_type

    def _get_current_version(self,node_path):
        ''' Get the current version for filecache , ignores ROP nodes'''
        node = hou.node(node_path)
        try:
            version = node.parm("version").eval()
            return version if version else "N/A"
        except AttributeError:
            return "--"

    def _get_other_versions(self,current_version,cache_path):
        ''' Get a lis of versions folders in the cache directory'''
        try:
            if current_version != "N/A":
                # Get the directory that contains the cache - root folder
                cache_dir = os.path.dirname(os.path.split(cache_path)[0])
                # Find all the version fodlers starting "v"
                version = []
                for item in os.listdir(cache_dir):
                    path = os.path.join(cache_dir,item)
                    if os.path.isdir(path) and item.startswith("v"):
                        try:
                            version_num = int(item[1:])
                            version.append(version_num)
                        except ValueError:
                            continue
                if len(version) == 0:
                    other_version = 0
                else:
                    other_version = len(version) - 1
                return other_version
            else:
                return"--"
        except OSError:
            return "--"

    def _get_last_modified(self,cache_path):
        ''' Get the last modified date of a cache file '''
        try:
            timestamp = os.path.getmtime(cache_path)
            return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
        except (OSError,ValueError):
            return "--"

    def _get_total_size(self,node,cache_path,node_type_name):
        ''' Get the total size of a cache file '''
        try:
            total_size = 0
            dir_path = os.path.dirname(cache_path)
            if node_type_name == "rop_geometry":
                node_ouput = node.parm('sopoutput').eval()
                node_trange = node.parm('trange').eval()
                node_frame_start = int(node.parm('f1').eval())
                node_frame_end = int(node.parm('f2').eval())
                if node_trange == 0:
                    total_size = os.path.getsize(node_ouput)
                elif node_trange == 1:
                    if os.path.exists(dir_path):
                        # NOT SURE ABOUT THIS
                        # LOOKS UNSTABLE
                        for file in os.listdir(dir_path)[node_frame_start:node_frame_end]:
                            file_size = os.path.getsize(os.path.join(dir_path, file))
                            total_size += file_size
            elif node_type_name == "rop_fbx":
                node_ouput = node.parm('sopoutput').eval()
                total_size = os.path.getsize(node_ouput)
            elif node_type_name == "rop_alembic":
                node_ouput = node.parm('filename').eval()
                total_size = os.path.getsize(node_ouput)
            else:
                if os.path.exists(dir_path):
                    list_dir = os.listdir(dir_path)
                    for file in list_dir:
                        file_size = os.path.getsize(os.path.join(dir_path,file))
                        total_size += file_size
                else:
                    total_size = 0
            self.total_cache_size += total_size
            return self._get_readadble_size(total_size)
        except Exception as e:
            print(str(e))
            return "--"

    def _get_readadble_size(self,size):
        ''' Get the readable size of a cache file '''
        for unit in ("", "K", "M", "G", "T"):
            if abs(size) < 1024.0:
                return f"{size:3.1f}{unit}B"
            size /= 1024.0
        return f"{size:.1f}YiB"

    def _show_context_menu(self,position):
        """ Show the context menu for right click"""

        menu = QtWidgets.QMenu()
        selected_items = self.cache_tree.selectedItems()
        if selected_items:
            reveal_action = menu.addAction("Show Folder")
            reveal_action.triggered.connect(self.reveal_in_explorer)

            cleanup_action = menu.addAction("Clean old versions")
            cleanup_action.triggered.connect(self.cleanup_old_versions)

        menu.exec_(self.cache_tree.viewport().mapToGlobal(position))

    def _update_stats(self):
        ''' Update the stats labs'''
        total_nodes = len(self.cache_data)
        self.total_nodes.setText(f"Total Cache Nodes {str(total_nodes)}")

        unused_versions = sum(data['other_versions'] for data in self.cache_data
                              if isinstance(data['other_versions'], int))
        self.unused_version.setText(f"Unused Versions: {unused_versions}")

        self.total_cache.setText(f"Total Cache Size: {self._get_readadble_size(self.total_cache_size)}")

    def select_node(self,item):
        ''' Select an jum, to the node when double clicked'''
        try:
            node_path = item.text(1)
            node = hou.node(node_path)
            if node:
                # Select the node
                node.setSelected(True)
                # Finding the closest network editor name
                for pane in hou.ui.paneTabs():
                    if isinstance(pane,hou.NetworkEditor):
                        network_pane = pane
                if network_pane:
                    # Move to the parent network
                    network_pane.cd(node.parent().path())
                    # Frame the node
                    network_pane.frameSelection()
        except:
            node_delete = item.text(0)
            hou.ui.displayMessage(f"The node selected: {node_delete} isn't in the scene. Please refresh the scene cache manager",
                                  severity=hou.severityType.Error)

    def reveal_in_explorer(self):
        """ Open the folder where the current cache is saved"""

        selected_items = self.cache_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage(f"Please select a cache first",severity=hou.severityType.Error)
        cache_path = selected_items[0].text(3)
        dir_path = os.path.dirname(cache_path)

        if os.path.exists(dir_path):
            if platform.system() == "Windows":
                os.startfile(dir_path)
            elif platform.system() == "Darwin":
                os.system("open " + dir_path)
            else:
                os.system("xdg-open " + dir_path)

        else:
            hou.ui.displayMessage(f"The cache path doesn't exist:{dir_path}",severity=hou.severityType.Error)

    def cleanup_old_versions(self):
        """
        Clean up old version of the selected caches
        """
        selected_items = self.cache_tree.selectedItems()
        if not selected_items:
            hou.ui.displayMessage(f"Please select a cache first",severity=hou.severityType.Error)
            return
        cache_path = selected_items[0].text(3)
        current_version = selected_items[0].text(4)
        other_version = selected_items[0].text(5)
        cache_dir = os.path.dirname(os.path.split(cache_path)[0])
        if current_version == "--":
            hou.ui.displayMessage(f"The selected node doesn't have current version",severity=hou.severityType.Warning)
            return
        if other_version == "--" or int(other_version) == 0:
            hou.ui.displayMessage(f"The selected node doesn't have other versions",severity=hou.severityType.Error)
            return
        try:
            is_only_new_version = True
            for folder in os.listdir(cache_dir):
                folder_path = os.path.join(cache_dir,folder)
                if os.path.isdir(folder_path) and folder.startswith("v") and int(folder[1:]) < int(current_version):
                    is_only_new_version = False
                    shutil.rmtree(folder_path)
            if is_only_new_version:
                hou.ui.displayMessage(f"There were no old versions to clean", severity=hou.severityType.Message)
            else:
                hou.ui.displayMessage(f"Successfully Cleaned Old Versions",severity=hou.severityType.Message)
            self.scan_scene_caches()
        except Exception as e:
            hou.ui.displayMessage(f"Something went wrong while cleaning old versions: {e}",severity=hou.severityType.Error)



