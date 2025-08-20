#!/usr/bin/env python
"""
Node Jumper - Simple Houdini LOPS Navigation Tool

A simple utility for quickly navigating between nodes in Houdini LOPS networks.

Usage:
    import node_jumper
    node_jumper.show()
    
    # Quick jump functions
    node_jumper.quick_merge()
    node_jumper.quick_materials()
    node_jumper.quick_lights()

Author: Houdini Custom Tools
Date: 2025-07-28
"""

import hou
import re
from typing import List, Dict, Optional

try:
    from PySide2 import QtCore, QtGui, QtWidgets as QtW
    QT_AVAILABLE = True
except ImportError:
    print("Warning: PySide2 not available. Node Jumper requires Qt for the UI.")
    QT_AVAILABLE = False


class NodeInfo:
    """Simple data class to store node information."""
    
    def __init__(self, node: hou.Node, category: str = "Other"):
        self.node = node
        self.name = node.name()
        self.path = node.path()
        self.type = node.type().name()
        self.category = category
        
    def __str__(self):
        return f"{self.name} ({self.category})"


class NodeJumperCore:
    """Core functionality for node jumping and navigation."""
    
    def __init__(self, context_path: str = "/stage"):
        self.context_path = context_path
        self.context_node = None
        self.node_registry = {}
        self.refresh_context()
    
    def refresh_context(self):
        """Refresh the node context and registry."""
        try:
            self.context_node = hou.node(self.context_path)
            if self.context_node:
                self._build_node_registry()
                return True
            else:
                print(f"Warning: Context node '{self.context_path}' not found")
                return False
        except Exception as e:
            print(f"Error refreshing context: {e}")
            return False
    
    def _build_node_registry(self):
        """Build a registry of nodes categorized by their purpose."""
        if not self.context_node:
            return
        
        self.node_registry = {
            "Materials": [],
            "Lights": [],
            "Cameras": [],
            "Merge": [],
            "Transform": [],
            "Other": []
        }
        
        # Categorize nodes
        for child in self.context_node.allSubChildren():
            category = self._categorize_node(child)
            node_info = NodeInfo(child, category)
            self.node_registry[category].append(node_info)
    
    def _categorize_node(self, node: hou.Node) -> str:
        """Categorize a node based on its type and name."""
        node_type = node.type().name().lower()
        node_name = node.name().lower()
        
        # Material nodes
        if any(keyword in node_type for keyword in ['material', 'mtlx', 'shader']):
            return "Materials"
        if any(keyword in node_name for keyword in ['material', 'mtlx', 'shader']):
            return "Materials"
        
        # Light nodes
        if any(keyword in node_type for keyword in ['light', 'dome', 'distant', 'sphere']):
            return "Lights"
        if any(keyword in node_name for keyword in ['light', 'rig', 'dome']):
            return "Lights"
        
        # Camera nodes
        if any(keyword in node_type for keyword in ['camera']):
            return "Cameras"
        if any(keyword in node_name for keyword in ['camera', 'cam']):
            return "Cameras"
        
        # Merge nodes
        if any(keyword in node_type for keyword in ['merge', 'combine', 'collect']):
            return "Merge"
        
        # Transform nodes
        if any(keyword in node_type for keyword in ['transform', 'xform']):
            return "Transform"
        
        return "Other"
    
    def jump_to_node(self, node_info: NodeInfo):
        """Jump to a specific node in the network editor."""
        try:
            # Get the network editor pane
            desktop = hou.ui.curDesktop()
            pane_tabs = desktop.paneTabsOfType(hou.paneTabType.NetworkEditor)
            
            if pane_tabs:
                network_editor = pane_tabs[0]
                network_editor.setCurrentNode(node_info.node)
                network_editor.homeToSelection()
                print(f"Jumped to: {node_info.name}")
            else:
                print("No network editor found")
        except Exception as e:
            print(f"Error jumping to node: {e}")
    
    def get_nodes_by_category(self, category: str) -> List[NodeInfo]:
        """Get all nodes in a specific category."""
        return self.node_registry.get(category, [])
    
    def search_nodes(self, search_term: str) -> List[NodeInfo]:
        """Search for nodes by name or type."""
        if not search_term:
            return []
        
        results = []
        search_lower = search_term.lower()
        
        for category_nodes in self.node_registry.values():
            for node_info in category_nodes:
                if (search_lower in node_info.name.lower() or 
                    search_lower in node_info.type.lower()):
                    results.append(node_info)
        
        return results


class NodeJumperDialog(QtW.QDialog):
    """Simple dialog for node navigation."""
    
    def __init__(self, parent=None, context_path="/stage"):
        super().__init__(parent)
        self.jumper_core = NodeJumperCore(context_path)
        self.current_nodes = []
        self.setup_ui()
        self.refresh_nodes()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Node Jumper")
        self.setMinimumSize(400, 500)
        self.resize(500, 600)
        
        layout = QtW.QVBoxLayout(self)
        
        # Header
        header = QtW.QLabel("Node Jumper - LOPS Navigation")
        header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QtW.QLabel("Use [ and ] keys to navigate • Double-click to jump")
        instructions.setStyleSheet("color: gray; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Search
        search_layout = QtW.QHBoxLayout()
        search_label = QtW.QLabel("Search:")
        self.search_input = QtW.QLineEdit()
        self.search_input.setPlaceholderText("Search nodes...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Category filter
        filter_layout = QtW.QHBoxLayout()
        filter_label = QtW.QLabel("Category:")
        self.category_combo = QtW.QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.addItems(["Materials", "Lights", "Cameras", "Merge", "Transform", "Other"])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Node list
        self.node_list = QtW.QListWidget()
        self.node_list.itemDoubleClicked.connect(self.on_node_double_clicked)
        layout.addWidget(self.node_list)
        
        # Jump button
        self.jump_button = QtW.QPushButton("Jump to Selected Node")
        self.jump_button.clicked.connect(self.jump_to_selected_node)
        layout.addWidget(self.jump_button)
    
    def refresh_nodes(self):
        """Refresh the node list."""
        self.jumper_core.refresh_context()
        self.populate_node_list()
    
    def populate_node_list(self):
        """Populate the node list based on current filters."""
        self.node_list.clear()
        self.current_nodes = []
        
        # Get search term
        search_term = self.search_input.text().strip()
        
        # Get category filter
        category_filter = self.category_combo.currentText()
        
        # Collect nodes
        if search_term:
            # Search mode
            nodes = self.jumper_core.search_nodes(search_term)
            if category_filter != "All":
                nodes = [n for n in nodes if n.category == category_filter]
        else:
            # Category mode
            if category_filter == "All":
                nodes = []
                for category_nodes in self.jumper_core.node_registry.values():
                    nodes.extend(category_nodes)
            else:
                nodes = self.jumper_core.get_nodes_by_category(category_filter)
        
        # Sort nodes by name
        nodes.sort(key=lambda n: n.name)
        self.current_nodes = nodes
        
        # Populate list
        for node_info in nodes:
            item = QtW.QListWidgetItem(f"{node_info.name} ({node_info.category})")
            item.setData(QtCore.Qt.UserRole, node_info)
            self.node_list.addItem(item)
    
    def on_search_changed(self):
        """Handle search text changes."""
        self.populate_node_list()
    
    def on_category_changed(self):
        """Handle category filter changes."""
        self.populate_node_list()
    
    def on_node_double_clicked(self, item):
        """Handle double-click on node item."""
        node_info = item.data(QtCore.Qt.UserRole)
        if node_info:
            self.jumper_core.jump_to_node(node_info)
    
    def jump_to_selected_node(self):
        """Jump to the currently selected node."""
        current_item = self.node_list.currentItem()
        if current_item:
            node_info = current_item.data(QtCore.Qt.UserRole)
            if node_info:
                self.jumper_core.jump_to_node(node_info)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == QtCore.Qt.Key_BracketLeft:  # [ key
            self.navigate_to_previous_node()
        elif event.key() == QtCore.Qt.Key_BracketRight:  # ] key
            self.navigate_to_next_node()
        elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.jump_to_selected_node()
        else:
            super().keyPressEvent(event)
    
    def navigate_to_previous_node(self):
        """Navigate to the previous node in the list."""
        if self.node_list.count() == 0:
            return
        
        current_row = self.node_list.currentRow()
        if current_row <= 0:
            new_row = self.node_list.count() - 1
        else:
            new_row = current_row - 1
        
        self.node_list.setCurrentRow(new_row)
        self.jump_to_selected_node()
    
    def navigate_to_next_node(self):
        """Navigate to the next node in the list."""
        if self.node_list.count() == 0:
            return
        
        current_row = self.node_list.currentRow()
        if current_row >= self.node_list.count() - 1:
            new_row = 0
        else:
            new_row = current_row + 1
        
        self.node_list.setCurrentRow(new_row)
        self.jump_to_selected_node()


# Main functions
def show(context_path="/stage"):
    """Show the node jumper dialog."""
    if not QT_AVAILABLE:
        print("Error: PySide2 not available. Cannot show Node Jumper dialog.")
        return None
    
    try:
        # Ensure QApplication exists
        app = QtW.QApplication.instance()
        if app is None:
            app = QtW.QApplication([])
        
        dialog = NodeJumperDialog(context_path=context_path)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        return dialog
    except Exception as e:
        print(f"Error showing node jumper dialog: {e}")
        return None


def launch():
    """Launch the Node Jumper dialog with status messages."""
    print("🚀 Node Jumper")
    
    # Check Houdini environment
    try:
        import hou
        print("✅ Houdini environment detected")
    except ImportError:
        print("❌ Not running in Houdini")
        return None
    
    print("🎯 Launching dialog...")
    dialog = show()
    
    if dialog:
        print("✅ Node Jumper dialog opened")
        print("💡 Use [ and ] keys to navigate between nodes")
        return dialog
    else:
        print("❌ Failed to open dialog")
        return None


def quick_merge(context_path="/stage"):
    """Quick jump to the first merge node."""
    try:
        core = NodeJumperCore(context_path)
        merge_nodes = core.get_nodes_by_category("Merge")
        if merge_nodes:
            core.jump_to_node(merge_nodes[0])
            print(f"Jumped to merge node: {merge_nodes[0].name}")
        else:
            print("No merge nodes found")
    except Exception as e:
        print(f"Error jumping to merge node: {e}")


def quick_materials(context_path="/stage"):
    """Quick jump to the first material node."""
    try:
        core = NodeJumperCore(context_path)
        material_nodes = core.get_nodes_by_category("Materials")
        if material_nodes:
            core.jump_to_node(material_nodes[0])
            print(f"Jumped to material node: {material_nodes[0].name}")
        else:
            print("No material nodes found")
    except Exception as e:
        print(f"Error jumping to material node: {e}")


def quick_lights(context_path="/stage"):
    """Quick jump to the first light node."""
    try:
        core = NodeJumperCore(context_path)
        light_nodes = core.get_nodes_by_category("Lights")
        if light_nodes:
            core.jump_to_node(light_nodes[0])
            print(f"Jumped to light node: {light_nodes[0].name}")
        else:
            print("No light nodes found")
    except Exception as e:
        print(f"Error jumping to light node: {e}")


# Convenience aliases
show_dialog = show
quick_jump_to_merge = quick_merge
quick_jump_to_materials = quick_materials
quick_jump_to_lights = quick_lights


if __name__ == "__main__":
    print("Node Jumper - Simple LOPS Navigation Tool")
    print("=" * 40)
    print("Usage:")
    print("  import node_jumper")
    print("  node_jumper.show()  # Show the main dialog")
    print("  node_jumper.launch()  # Launch with status messages")
    print("")
    print("Quick functions:")
    print("  node_jumper.quick_merge()")
    print("  node_jumper.quick_materials()")
    print("  node_jumper.quick_lights()")
    
    # Auto-launch if in Houdini
    try:
        import hou
        print("\n🚀 Auto-launching Node Jumper...")
        launch()
    except ImportError:
        print("\nNot running in Houdini - dialog not shown")