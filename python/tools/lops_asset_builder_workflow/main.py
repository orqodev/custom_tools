"""Main entry point for LOPS Asset Builder Workflow."""

import os
import hou
import voptoolutils
import shiboken2
import time
from typing import List, Type
from pxr import Usd, UsdGeom
from PySide2 import QtCore, QtGui, QtWidgets as QtW
import sys
import io
import json
from contextlib import redirect_stdout, redirect_stderr

from tools import tex_to_mtlx, lops_light_rig, lops_lookdev_camera
from tools.lops_asset_builder_v2.lops_asset_builder_v2 import create_camera_lookdev, create_karma_nodes
from tools.lops_light_rig_pipeline import setup_light_rig_pipeline
from modules.misc_utils import _sanitize, slugify

# Handle both relative and absolute imports for flexibility
try:
    # Try relative imports first (when imported as part of package)
    from .config.constants import DEFAULT_NODE_SPACING, CONVEX_HULL_TOLERANCE, MATERIAL_LIB_NAME, MTLX_TEMPLATE_PREFIX
    from .models.data_model import WorkflowData, AssetGroup
    from .models.settings_model import SettingsManager
    from .utils.validation import ValidationUtils
    # Note: AssetGroupsDialog import moved to _create_ui_form method to avoid Qt initialization issues
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config.constants import DEFAULT_NODE_SPACING, CONVEX_HULL_TOLERANCE, MATERIAL_LIB_NAME, MTLX_TEMPLATE_PREFIX
    from models.data_model import WorkflowData, AssetGroup
    from models.settings_model import SettingsManager
    from utils.validation import ValidationUtils
    # Note: AssetGroupsDialog import moved to _create_ui_form method to avoid Qt initialization issues


class LopsAssetBuilderWorkflow:
    """
    LOPS Asset Builder Workflow - Step-by-step UI for multiple asset importing

    This class combines the functionality of lops_asset_builder_v2 with the
    step-by-step UI workflow pattern from batch_import_workflow.

    Features:
    - Interactive step-by-step asset group importing
    - Multiple asset groups with individual component builders
    - Material creation and assignment
    - Automatic network layout
    """

    def __init__(self):
        self.stage_context = None
        self.asset_groups = []  # List of asset group data
        self.merge_node = None  # Final merge node to connect all component outputs

        # UI Data storage as instance variables
        self.asset_scope = "ASSET"  # Default asset scope
        self.groups_data = []  # Raw groups data from UI
        self.ui_result = None  # Complete UI result data
        self.main_dialog = None  # Reference to the main dialog for logging

    def _is_dialog_valid(self):
        """
        Check if the main dialog is valid and accessible.
        
        Returns:
            bool: True if dialog is valid and can be used, False otherwise
        """
        if not self.main_dialog:
            return False
            
        try:
            # Check if the dialog has the required methods
            if not hasattr(self.main_dialog, 'isVisible') or not callable(getattr(self.main_dialog, 'isVisible', None)):
                return False
                
            # Try to access a Qt property to ensure C++ object is not deleted
            _ = self.main_dialog.isVisible()
            return True
            
        except RuntimeError as e:
            if "Internal C++ object" in str(e) and "already deleted" in str(e):
                return False
            else:
                # Re-raise other RuntimeErrors
                raise
        except Exception:
            return False

    def _log_message(self, message, severity=None):
        """
        Log a message to the unified dialog if available, otherwise print to console.

        Args:
            message (str): The message to log
            severity (hou.severityType): The severity type (Error, Warning, Message)
        """
        # Format message based on severity
        if severity == hou.severityType.Error:
            formatted_message = f"❌ ERROR: {message}"
        elif severity == hou.severityType.Warning:
            formatted_message = f"⚠️ WARNING: {message}"
        else:
            formatted_message = f"ℹ️ INFO: {message}"

        # Log to dialog if available and Qt objects are still valid
        if self._is_dialog_valid() and hasattr(self.main_dialog, 'add_log'):
            try:
                self.main_dialog.add_log(formatted_message)
            except RuntimeError as e:
                if "Internal C++ object" in str(e) and "already deleted" in str(e):
                    # Qt object is deleted, fall back to console logging
                    print(f"[Dialog Closed] {formatted_message}")
                else:
                    # Re-raise other RuntimeErrors
                    raise
            except Exception as e:
                # If any error occurs, fall back to console logging
                print(f"[Logging Error] {formatted_message}")
                print(f"[Debug] Logging error: {str(e)}")
        else:
            print(formatted_message)

    def _create_ui_form(self):
        """Create and show the UI form for asset group configuration."""
        try:
            # Ensure QApplication exists before creating widgets
            app = QtW.QApplication.instance()
            if app is None:
                app = QtW.QApplication([])

            # Import AssetGroupsDialog after QApplication is initialized to avoid Qt initialization issues
            try:
                from .ui.main_dialog import AssetGroupsDialog
            except ImportError:
                from ui.main_dialog import AssetGroupsDialog

            # Create the main dialog
            self.main_dialog = AssetGroupsDialog()

            # Show the dialog and get result
            if self.main_dialog.exec_() == QtW.QDialog.Accepted:
                # Get the result data
                self.ui_result = self.main_dialog.get_result_data()
                self.asset_scope = self.main_dialog.get_workflow_data().asset_scope

                if self.ui_result:
                    self._log_message(f"Collected {len(self.ui_result)} asset groups for processing")
                    # Keep dialog open for progress updates - show it again after exec_() closed it
                    self.main_dialog.show()
                    return True
                else:
                    self._log_message("No asset groups were configured", hou.severityType.Warning)
                    return False
            else:
                self._log_message("User cancelled the workflow")
                return False

        except Exception as e:
            self._log_message(f"Failed to create UI form: {str(e)}", hou.severityType.Error)
            return False

    def create_workflow(self):
        """Main workflow creation method."""
        start_time = time.time()

        try:
            print("=" * 80)
            print("🚀 STARTING LOPS ASSET BUILDER WORKFLOW")
            print("=" * 80)

            # Step 1: Show UI form to collect asset groups
            print("\n📋 STEP 1: Creating UI Form")
            print("-" * 40)
            self._log_message("Starting LOPS Asset Builder Workflow...")
            step1_start = time.time()

            print("🔍 Attempting to create UI form...")
            if not self._create_ui_form():
                print("❌ UI form creation failed - workflow aborted")
                return False

            step1_time = time.time() - step1_start
            print(f"✅ UI form created successfully in {step1_time:.2f}s")
            print(f"📊 Collected {len(self.ui_result) if self.ui_result else 0} asset groups from UI")

            # Validate UI result data
            if not self.ui_result:
                print("❌ No asset groups collected from UI")
                return False

            for i, group in enumerate(self.ui_result):
                print(f"   Group {i+1}: {group.get('group_name', 'Unnamed')} - {len(group.get('asset_paths', []))} assets")

            # Step 2: Initialize stage context
            print("\n🎭 STEP 2: Initializing Stage Context")
            print("-" * 40)
            step2_start = time.time()

            print("🔍 Checking stage context...")
            self._initialize_stage_context()

            step2_time = time.time() - step2_start
            print(f"✅ Stage context initialized in {step2_time:.2f}s")
            print(f"📍 Stage context: {self.stage_context.path() if self.stage_context else 'None'}")

            # Step 3: Create node scope
            print("\n🏷️ STEP 3: Creating Node Scope")
            print("-" * 40)
            step3_start = time.time()

            print(f"🔍 Creating scope from asset scope: '{self.asset_scope}'")
            scope_name = self._create_node_scope()

            step3_time = time.time() - step3_start
            print(f"✅ Node scope created in {step3_time:.2f}s")
            print(f"🏷️ Scope name: '{scope_name}'")

            # Step 4: Process each asset group
            print(f"\n⚙️ STEP 4: Processing Asset Groups ({len(self.ui_result)} groups)")
            print("-" * 40)
            step4_start = time.time()

            # Switch dialog to processing mode (old style)
            if self._is_dialog_valid():
                try:
                    self.main_dialog.start_processing_mode(len(self.ui_result))
                except RuntimeError as e:
                    if "Internal C++ object" in str(e) and "already deleted" in str(e):
                        print("[Dialog Closed] Cannot start processing mode - dialog object deleted")
                    else:
                        raise

            self._log_message(f"Processing {len(self.ui_result)} asset groups...")
            component_outputs = []

            for group_index, asset_data in enumerate(self.ui_result):
                group_start_time = time.time()
                group_name = asset_data.get('group_name', f'Group_{group_index + 1}')
                asset_paths = asset_data.get('asset_paths', [])

                print(f"\n   🔧 Processing Group {group_index + 1}/{len(self.ui_result)}: {group_name}")
                print(f"      📁 Asset paths: {len(asset_paths)}")
                print(f"      🎨 Texture folder: {asset_data.get('texture_folder', 'None')}")

                try:
                    # Update progress in dialog
                    if self._is_dialog_valid():
                        try:
                            self.main_dialog.update_progress(
                                group_index, 
                                group_name,
                                f"Processing group: {group_name}"
                            )
                        except RuntimeError as e:
                            if "Internal C++ object" in str(e) and "already deleted" in str(e):
                                print("[Dialog Closed] Cannot update progress - dialog object deleted")
                            else:
                                raise

                    # Extract material names for this group
                    print(f"      🎨 Extracting material names from {len(asset_paths)} assets...")
                    material_extract_start = time.time()
                    material_names = self._extract_material_names(asset_paths)
                    material_extract_time = time.time() - material_extract_start
                    asset_data['material_names'] = material_names
                    print(f"      ✅ Found {len(material_names)} materials in {material_extract_time:.2f}s: {material_names}")

                    # Create component builder for this group
                    print(f"      🏗️ Creating component builder...")
                    component_start = time.time()
                    component_output = self._create_component_builder_for_group(asset_data)
                    component_time = time.time() - component_start

                    if component_output:
                        component_outputs.append(component_output)
                        group_time = time.time() - group_start_time
                        print(f"      ✅ Component created in {component_time:.2f}s (total: {group_time:.2f}s)")
                        print(f"      📍 Output node: {component_output.path()}")
                        self._log_message(f"✓ Successfully processed group: {group_name}")
                    else:
                        print(f"      ❌ Component creation failed")
                        self._log_message(f"Failed to process group: {group_name}", hou.severityType.Warning)

                except Exception as e:
                    group_time = time.time() - group_start_time
                    print(f"      ❌ Error in group processing after {group_time:.2f}s: {str(e)}")
                    import traceback
                    print(f"      📋 Traceback: {traceback.format_exc()}")
                    self._log_message(f"Error processing group {group_name}: {str(e)}", hou.severityType.Error)
                    continue

            step4_time = time.time() - step4_start
            print(f"\n✅ Asset group processing completed in {step4_time:.2f}s")
            print(f"📊 Successfully created {len(component_outputs)} component outputs")

            # Step 5: Create final merge node if we have multiple components
            print(f"\n🔗 STEP 5: Creating Final Merge Node")
            print("-" * 40)
            step5_start = time.time()

            if len(component_outputs) > 1:
                print(f"🔍 Multiple components ({len(component_outputs)}) - creating merge node...")
                self._log_message("Creating final merge node...")
                self.merge_node = self._create_final_merge_node()

                if self.merge_node:
                    print(f"✅ Merge node created: {self.merge_node.path()}")

                    # Connect all component outputs to the merge node
                    print(f"🔌 Connecting {len(component_outputs)} components to merge node...")
                    for i, output_node in enumerate(component_outputs):
                        if output_node:
                            print(f"   Connecting input {i}: {output_node.path()}")
                            self.merge_node.setInput(i, output_node)
                        else:
                            print(f"   ⚠️ Skipping null output at index {i}")
                    print(f"✅ All connections completed")
                else:
                    print(f"❌ Failed to create merge node")

            elif len(component_outputs) == 1:
                self.merge_node = component_outputs[0]
                print(f"📍 Single component - using as final output: {self.merge_node.path()}")
            else:
                print(f"❌ No component outputs available for merge")

            step5_time = time.time() - step5_start
            print(f"✅ Merge step completed in {step5_time:.2f}s")

            # Step 6: Layout all nodes
            print(f"\n📐 STEP 6: Layout All Nodes")
            print("-" * 40)
            step6_start = time.time()

            print(f"🔍 Laying out nodes in network...")
            self._layout_all_nodes()

            step6_time = time.time() - step6_start
            print(f"✅ Node layout completed in {step6_time:.2f}s")

            # Step 7: Setup light rig pipeline
            print(f"\n💡 STEP 7: Setup Light Rig Pipeline")
            print("-" * 40)
            step7_start = time.time()

            print(f"🔍 Setting up light rig pipeline with scope: '{scope_name}'")
            self._setup_light_rig_pipeline(scope_name)

            step7_time = time.time() - step7_start
            print(f"✅ Light rig pipeline setup completed in {step7_time:.2f}s")

            # Step 8: Show final summary
            print(f"\n📋 STEP 8: Final Summary")
            print("-" * 40)
            step8_start = time.time()

            print(f"🔍 Generating workflow summary...")
            self._show_final_summary()

            step8_time = time.time() - step8_start
            print(f"✅ Summary generated in {step8_time:.2f}s")

            # Update final progress
            if self._is_dialog_valid():
                try:
                    self.main_dialog.update_progress(
                        len(self.ui_result),
                        "Complete",
                        "✓ Workflow completed successfully!"
                    )
                except RuntimeError as e:
                    if "Internal C++ object" in str(e) and "already deleted" in str(e):
                        print("[Dialog Closed] Cannot update final progress - dialog object deleted")
                    else:
                        raise

            total_time = time.time() - start_time
            print("\n" + "=" * 80)
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"⏱️ Total execution time: {total_time:.2f}s")
            print(f"📊 Final merge node: {self.merge_node.path() if self.merge_node else 'None'}")
            print(f"🎯 Asset scope: {self.asset_scope}")
            print(f"📁 Groups processed: {len(self.ui_result)}")
            print("=" * 80)

            return True

        except Exception as e:
            total_time = time.time() - start_time
            print("\n" + "=" * 80)
            print("❌ WORKFLOW FAILED!")
            print("=" * 80)
            print(f"💥 Error: {str(e)}")
            print(f"⏱️ Failed after: {total_time:.2f}s")

            # Print detailed traceback
            import traceback
            print(f"📋 Full traceback:")
            print(traceback.format_exc())
            print("=" * 80)

            self._log_message(f"Workflow creation failed: {str(e)}", hou.severityType.Error)
            return False

    def _extract_material_names(self, asset_paths):
        """Extract material names from asset file paths."""
        print(f"         🎨 Starting material extraction from {len(asset_paths)} assets...")
        material_names = []

        try:
            for i, asset_path in enumerate(asset_paths):
                print(f"         📁 Processing asset {i+1}/{len(asset_paths)}: {os.path.basename(asset_path)}")

                if not os.path.exists(asset_path):
                    print(f"         ⚠️ Asset file does not exist: {asset_path}")
                    continue

                # Try to read the geometry file and extract material information
                try:
                    print(f"         🔍 Loading geometry to extract materials...")
                    # Create a temporary SOP network to load the geometry
                    temp_geo = hou.node("/obj").createNode("geo", "temp_material_extract")
                    file_node = temp_geo.createNode("file")
                    file_node.parm("file").set(asset_path)

                    # Get the geometry
                    geo = file_node.geometry()

                    if geo:
                        print(f"         ✅ Geometry loaded - {geo.intrinsicValue('primitivecount')} primitives")

                        # Look for material attributes
                        material_attrib = geo.findPrimAttrib("name")
                        if not material_attrib:
                            material_attrib = geo.findPrimAttrib("material")

                        if material_attrib:
                            print(f"         🎯 Found material attribute: {material_attrib.name()}")
                            # Get unique material names
                            for prim in geo.prims():
                                material_name = slugify(prim.attribValue(material_attrib))
                                if material_name and material_name not in material_names:
                                    # Clean up the material name
                                    clean_name = os.path.basename(material_name)
                                    if clean_name and clean_name not in material_names:
                                        material_names.append(clean_name)
                                        print(f"         ➕ Added material: {clean_name}")
                        else:
                            print(f"         ⚠️ No material attributes found in geometry")
                    else:
                        print(f"         ❌ Failed to load geometry from file")

                    # Clean up temporary node
                    temp_geo.destroy()
                    print(f"         🧹 Cleaned up temporary geometry node")

                except Exception as e:
                    print(f"         ❌ Material extraction failed for {asset_path}: {str(e)}")
                    self._log_message(f"Could not extract materials from {asset_path}: {str(e)}", hou.severityType.Warning)
                    continue

        except Exception as e:
            print(f"         💥 Critical error in material extraction: {str(e)}")
            self._log_message(f"Error extracting material names: {str(e)}", hou.severityType.Warning)

        # If no materials found, create a default one based on the group name
        if not material_names and asset_paths:
            group_name = os.path.basename(asset_paths[0]).split('.')[0]
            default_material = f"material_{_sanitize(group_name)}"
            material_names.append(default_material)
            print(f"         🔧 No materials found - created default: {default_material}")

        print(f"         ✅ Material extraction complete - found {len(material_names)} materials")
        return material_names

    def _create_component_builder_for_group(self, asset_data):
        """Create a component builder for a single asset group."""
        try:
            group_name = asset_data.get('group_name', 'Unnamed_Group')
            asset_paths = asset_data.get('asset_paths', [])
            base_path = asset_data.get('base_path', '')
            texture_folder = asset_data.get('texture_folder', '')
            material_names = asset_data.get('material_names', [])

            print(f"      🏗️ Starting component builder creation for: {group_name}")
            print(f"      📊 Asset paths: {len(asset_paths)}")
            print(f"      📁 Base path: {base_path}")
            print(f"      🎨 Texture folder: {texture_folder}")
            print(f"      🧩 Materials: {len(material_names)} - {material_names}")

            if not asset_paths:
                print(f"      ❌ No asset paths found for group: {group_name}")
                self._log_message(f"No asset paths found for group: {group_name}", hou.severityType.Warning)
                return None

            # Sanitize the node name
            node_name = _sanitize(group_name)
            print(f"      🏷️ Sanitized node name: {node_name}")

            self._log_message(f"Creating component builder for group: {group_name}")

            # Create initial nodes
            print(f"      🔧 Creating initial nodes...")
            initial_start = time.time()
            comp_geo, material_lib, comp_material, comp_out = self._create_initial_nodes(node_name)
            initial_time = time.time() - initial_start

            if not comp_geo or not comp_out:
                print(f"      ❌ Failed to create initial nodes")
                self._log_message(f"Failed to create initial nodes for group: {group_name}", hou.severityType.Error)
                return None

            # Map to expected variable names for compatibility
            parent = comp_geo  # Component geometry node acts as parent for SOP operations
            out_node = comp_out  # Component output node is the final output

            print(f"      ✅ Initial nodes created in {initial_time:.2f}s")
            print(f"         Component Geometry: {comp_geo.path() if comp_geo else 'None'}")
            print(f"         Material Library: {material_lib.path() if material_lib else 'None'}")
            print(f"         Component Material: {comp_material.path() if comp_material else 'None'}")
            print(f"         Component Output: {comp_out.path() if comp_out else 'None'}")

            # Prepare imported assets
            print(f"      📦 Preparing imported assets...")
            asset_start = time.time()
            switch_node, transform_node = self._prepare_imported_asset(
                parent, asset_paths, base_path, out_node, node_name
            )
            asset_time = time.time() - asset_start

            if not switch_node or not transform_node:
                print(f"      ❌ Failed to prepare assets")
                self._log_message(f"Failed to prepare assets for group: {group_name}", hou.severityType.Error)
                return None

            print(f"      ✅ Assets prepared in {asset_time:.2f}s")
            print(f"         Switch: {switch_node.path() if switch_node else 'None'}")
            print(f"         Transform: {transform_node.path() if transform_node else 'None'}")

            # Create group parameters
            print(f"      ⚙️ Creating group parameters...")
            param_start = time.time()
            self._create_group_parameters(parent, node_name, asset_paths, switch_node, transform_node)
            param_time = time.time() - param_start
            print(f"      ✅ Parameters created in {param_time:.2f}s")

            # Link group nodes to parameters
            print(f"      🔗 Linking nodes to parameters...")
            link_start = time.time()
            self._link_group_nodes_to_parameters(parent, node_name, switch_node, transform_node)
            link_time = time.time() - link_start
            print(f"      ✅ Nodes linked in {link_time:.2f}s")

            # Create materials if texture folder is provided
            if texture_folder and os.path.exists(texture_folder):
                print(f"      🎨 Creating materials from texture folder...")
                material_start = time.time()
                material_result = self._create_materials(parent, texture_folder, material_lib, material_names)
                material_time = time.time() - material_start

                if material_result:
                    print(f"      ✅ Materials created in {material_time:.2f}s: {material_lib.path()}")

                    print(f"      🔧 Creating MaterialX templates...")
                    mtlx_start = time.time()
                    self._create_mtlx_templates(parent, material_lib)
                    mtlx_time = time.time() - mtlx_start
                    print(f"      ✅ MaterialX templates created in {mtlx_time:.2f}s")
                else:
                    print(f"      ⚠️ Material creation failed after {material_time:.2f}s")
            else:
                if not texture_folder:
                    print(f"      ⚠️ No texture folder provided - skipping materials")
                else:
                    print(f"      ⚠️ Texture folder does not exist: {texture_folder}")

            # Create convex hull
            print(f"      🔺 Creating convex hull...")
            convex_start = time.time()
            # Get the SOP context from the LOPS componentgeometry node (like backup file)
            parent_sop = hou.node(parent.path() + "/sopnet/geo")
            if parent_sop:
                self._create_convex(parent_sop)
                convex_time = time.time() - convex_start
                print(f"      ✅ Convex hull created in {convex_time:.2f}s")
            else:
                convex_time = time.time() - convex_start
                print(f"      ⚠️ Could not find SOP context for convex hull creation")

            print(f"      🎉 Component builder completed successfully!")
            return out_node

        except Exception as e:
            print(f"      💥 Critical error in component builder creation: {str(e)}")
            import traceback
            print(f"      📋 Traceback: {traceback.format_exc()}")
            self._log_message(f"Error creating component builder for group {asset_data.get('group_name', 'Unknown')}: {str(e)}", hou.severityType.Error)
            return None

    def _create_initial_nodes(self, node_name):
        """Create initial nodes for the component builder setup."""
        try:
            print(f"         🎭 Getting LOPS context...")
            # Get the current LOPS network
            lops_context = hou.node("/stage")
            if not lops_context:
                print(f"         ❌ No /stage context found")
                self._log_message("No /stage context found", hou.severityType.Error)
                return None, None, None, None

            print(f"         ✅ LOPS context found: {lops_context.path()}")

            print(f"         🏗️ Creating component nodes...")
            # Create nodes for the component builder setup
            comp_geo = lops_context.createNode("componentgeometry", _sanitize(f"{node_name}_geo"))
            material_lib = lops_context.createNode("materiallibrary", _sanitize(f"{node_name}_mtl"))
            comp_material = lops_context.createNode("componentmaterial", _sanitize(f"{node_name}_assign"))
            comp_out = lops_context.createNode("componentoutput", _sanitize(node_name))

            print(f"         ✅ Component geometry created: {comp_geo.path()}")
            print(f"         ✅ Material library created: {material_lib.path()}")
            print(f"         ✅ Component material created: {comp_material.path()}")
            print(f"         ✅ Component output created: {comp_out.path()}")

            # Set up parameters
            comp_geo.parm("geovariantname").set(node_name)
            material_lib.parm("matpathprefix").set(f"/ASSET/mtl/")
            comp_material.parm("nummaterials").set(0)

            # Create auto assignment for materials
            comp_material_edit = comp_material.node("edit")
            output_node = comp_material_edit.node("output0")

            assign_material = comp_material_edit.createNode("assignmaterial", _sanitize(f"{node_name}_assign"))
            # SET PARMS
            assign_material.setParms({
                "primpattern1": "%type:Mesh",
                "matspecmethod1": 2,
                "matspecvexpr1": '"/ASSET/mtl/"+@primname;',
                "bindpurpose1": "full",
            })

            # Connect nodes
            comp_material.setInput(0, comp_geo)
            comp_material.setInput(1, material_lib)
            comp_out.setInput(0, comp_material)

            # Connect the input of assign material node to the first subnet indirect input
            assign_material.setInput(0, comp_material_edit.indirectInputs()[0])
            output_node.setInput(0, assign_material)

            print(f"         ✅ All component nodes created and connected successfully")
            return comp_geo, material_lib, comp_material, comp_out

        except Exception as e:
            print(f"         💥 Error creating initial nodes: {str(e)}")
            self._log_message(f"Error creating initial nodes: {str(e)}", hou.severityType.Error)
            return None, None, None, None

    def _prepare_imported_asset(self, parent, asset_paths, base_path, out_node, node_name):
        """
        Prepare imported assets with switch node and transform controls.
        Assets are processed through a matchsize node for consistent positioning.
        Based on _prepare_imported_asset from lops_asset_builder_v2.
        Returns switch_node and transform_node for parameter linking.
        """
        try:
            # Set the parent node where the nodes are going to be created
            parent_sop = hou.node(parent.path() + "/sopnet/geo")
            # Get the output nodes - default, proxy and sim
            default_output = hou.node(f"{parent_sop.path()}/default")
            proxy_output = hou.node(f"{parent_sop.path()}/proxy")
            sim_output = hou.node(f"{parent_sop.path()}/simproxy")

            # Create the file nodes that import the assets
            file_nodes = []
            processed_paths = []
            switch_node = parent_sop.createNode("switch", _sanitize(f"switch_{node_name}"))

            for i, asset_path in enumerate(asset_paths):
                asset_path = asset_path.strip()
                if not asset_path:
                    continue

                # Get asset name and extension
                file_path, filename = os.path.split(asset_path)
                asset_name = filename.split(".")[0]
                extension = filename.split(".")[-1]
                if ".bgeo.sc" in filename:
                    asset_name = filename.split(".")[0]
                    extension = "bgeo.sc"

                # Store full path for parameters
                full_asset_path = asset_path
                processed_paths.append(full_asset_path)

                file_extension = ["fbx", "obj", "bgeo", "bgeo.sc"]
                if extension in file_extension:
                    file_import = parent_sop.createNode("file", _sanitize(f"import_{asset_name}"))
                    parm_name = "file"
                elif extension == "abc":
                    file_import = parent_sop.createNode("alembic", _sanitize(f"import_{asset_name}"))
                    parm_name = "filename"
                else:
                    continue

                # Set parameters for main nodes
                file_import.parm(parm_name).set(asset_path)
                switch_node.setInput(i, file_import)
                file_nodes.append(file_import)

            # Create the main processing nodes
            match_size = parent_sop.createNode("matchsize", _sanitize(f"matchsize_{node_name}"))
            attrib_wrangler = parent_sop.createNode("attribwrangle", "convert_mat_to_name")
            attrib_delete = parent_sop.createNode("attribdelete", "keep_P_N_UV_NAME")
            remove_points = parent_sop.createNode("add", f"remove_points")

            # Create transform node for external control (after remove_points)
            transform_node = parent_sop.createNode("xform", _sanitize(f"transform_{node_name}"))

            match_size.setParms({
                "justify_x": 2,
                "justify_y": 1,
                "justify_z": 2,
            })

            attrib_wrangler.setParms({
                "class": 1,
                "snippet": 's@shop_materialpath = tolower(replace(s@shop_materialpath, " ", "_"));\nstring material_to_name[] = split(s@shop_materialpath,"/");\ns@name=material_to_name[-1];'
            })

            attrib_delete.setParms({
                "negate": True,
                "ptdel": "N P",
                "vtxdel": "uv",
                "primdel": "name"
            })

            remove_points.parm("remove").set(True)

            # Connect main nodes - transform node now comes after remove_points
            match_size.setInput(0, switch_node)
            attrib_wrangler.setInput(0, match_size)
            attrib_delete.setInput(0, attrib_wrangler)
            remove_points.setInput(0, attrib_delete)
            transform_node.setInput(0, remove_points)
            default_output.setInput(0, transform_node)

            return switch_node, transform_node

        except Exception as e:
            self._log_message(f"Error preparing imported asset: {str(e)}", hou.severityType.Error)
            return None, None

    def _create_group_parameters(self, parent_node, node_name, asset_paths, switch_node, transform_node):
        """Create group parameters for asset selection and transformation."""
        try:
            # Create parameter template group
            ptg = hou.ParmTemplateGroup()

            # Asset selection parameter
            if len(asset_paths) > 1:
                asset_names = [os.path.basename(path) for path in asset_paths]
                menu_items = []
                for i, name in enumerate(asset_names):
                    menu_items.extend([str(i), name])

                asset_menu = hou.MenuParmTemplate(
                    f"{node_name}_asset",
                    f"{node_name} Asset",
                    menu_items,
                    default_value=0
                )
                ptg.append(asset_menu)

            # Transform parameters
            translate_parm = hou.FloatParmTemplate(
                f"{node_name}_translate",
                f"{node_name} Translate",
                3,
                default_value=(0, 0, 0)
            )
            ptg.append(translate_parm)

            rotate_parm = hou.FloatParmTemplate(
                f"{node_name}_rotate",
                f"{node_name} Rotate",
                3,
                default_value=(0, 0, 0)
            )
            ptg.append(rotate_parm)

            scale_parm = hou.FloatParmTemplate(
                f"{node_name}_scale",
                f"{node_name} Scale",
                3,
                default_value=(1, 1, 1)
            )
            ptg.append(scale_parm)

            # Add parameters to parent node
            parent_node.setParmTemplateGroup(ptg)

        except Exception as e:
            self._log_message(f"Error creating group parameters: {str(e)}", hou.severityType.Error)

    def _link_group_nodes_to_parameters(self, parent_node, node_name, switch_node, transform_node):
        """Link group nodes to the created parameters."""
        try:
            # Link switch node to asset selection parameter
            if parent_node.parm(f"{node_name}_asset"):
                switch_node.parm("input").setExpression(f'ch("../{node_name}_asset")')

            # Link transform node to transform parameters
            if parent_node.parm(f"{node_name}_translate1"):
                transform_node.parm("tx").setExpression(f'ch("../{node_name}_translate1")')
                transform_node.parm("ty").setExpression(f'ch("../{node_name}_translate2")')
                transform_node.parm("tz").setExpression(f'ch("../{node_name}_translate3")')

            if parent_node.parm(f"{node_name}_rotate1"):
                transform_node.parm("rx").setExpression(f'ch("../{node_name}_rotate1")')
                transform_node.parm("ry").setExpression(f'ch("../{node_name}_rotate2")')
                transform_node.parm("rz").setExpression(f'ch("../{node_name}_rotate3")')

            if parent_node.parm(f"{node_name}_scale1"):
                transform_node.parm("sx").setExpression(f'ch("../{node_name}_scale1")')
                transform_node.parm("sy").setExpression(f'ch("../{node_name}_scale2")')
                transform_node.parm("sz").setExpression(f'ch("../{node_name}_scale3")')

        except Exception as e:
            self._log_message(f"Error linking group nodes to parameters: {str(e)}", hou.severityType.Error)

    def _create_materials(self, parent, folder_textures, material_lib, expected_names):
        """
        Create materials using the tex_to_mtlx script.
        Only creates materials for names found in expected_names list.
        Based on backup file approach that worked without locking issues.

        Args:
            parent: Parent node
            folder_textures: Path to texture folder
            material_lib: Material library node
            expected_names: List of material names to create (from geometry files)
        """
        try:
            if not os.path.exists(folder_textures):
                self._log_message(f"Texture folder does not exist: {folder_textures}", hou.severityType.Warning)
                self._create_mtlx_templates(parent, material_lib)
                return False

            material_handler = tex_to_mtlx.TxToMtlx()
            stage = parent.stage()
            prims_name = self._find_prims_by_attribute(stage, UsdGeom.Mesh)
            materials_created_length = 0

            if material_handler.folder_with_textures(folder_textures):
                # Get the texture detail
                texture_list = material_handler.get_texture_details(folder_textures)
                print(texture_list)
                if texture_list and isinstance(texture_list, dict):
                    # Common data
                    common_data = {
                        'mtlTX': False,  # If you want to create TX files set to True
                        'path': material_lib.path(),
                        'node': material_lib,
                    }
                    for material_name in texture_list:
                        # Skip materials not in expected_names list
                        print(material_name)
                        print(expected_names)
                        if material_name not in expected_names:
                            continue

                        # Fix to provide the correct path
                        path = texture_list[material_name]['FOLDER_PATH']
                        if not path.endswith("/"):
                            texture_list[material_name]['FOLDER_PATH'] = path + "/"

                        materials_created_length += 1
                        create_material = tex_to_mtlx.MtlxMaterial(
                            material_name,
                            **common_data,
                            folder_path=path,
                            texture_list=texture_list
                        )
                        create_material.create_materialx()
                    self._log_message(f"Created {materials_created_length} materials in {material_lib.path()}")
                    return True
                else:
                    self._create_mtlx_templates(parent, material_lib)
                    self._log_message("No valid texture sets found..")
                    return True
            else:
                self._create_mtlx_templates(parent, material_lib)
                self._log_message("No valid texture sets found in folder")
                return True
        except Exception as e:
            self._log_message(f"Error creating materials: {str(e)}", hou.severityType.Error)
            return False

    def _create_mtlx_templates(self, parent, material_lib):
        """Create MaterialX templates using backup file approach."""
        name = "mtlxstandard_surface"
        voptoolutils._setupMtlXBuilderSubnet(
            subnet_node=None,
            destination_node=material_lib,
            name=name,
            mask=voptoolutils.MTLX_TAB_MASK,
            folder_label="MaterialX Builder",
            render_context="mtlx"
        )
        material_lib.layoutChildren()

    def _find_prims_by_attribute(self, stage: Usd.Stage, prim_type: Type[Usd.Typed]):
        """Find primitives by attribute type using backup file approach."""
        prims_name = set()
        for prim in stage.Traverse():
            if prim.IsA(prim_type) and "render" in str(prim.GetPath()):
                prims_name.add(prim.GetName())
        return list(prims_name)

    def _create_convex(self, parent):
        """
        Creates the Python sop node that is used to create a convex hull using Scipy
        Based on backup file approach that worked without locking issues.
        Args:
            parent = the component geometry node where the file is imported
        Return:
            python_sop = python_sop node created
        """
        # Create the extra parms to use
        python_sop = parent.createNode("python", "convex_hull_setup")

        # Create the extra parms to use
        ptg = python_sop.parmTemplateGroup()

        # Normalize normals toggle
        normalize_toggle = hou.ToggleParmTemplate(
            name="normalize",
            label="Normalize",
            default_value=True
        )

        # Invert Normals Toggle
        flip_normals = hou.ToggleParmTemplate(
            name="flip_normals",
            label="Flip Normals",
            default_value=True
        )

        # Simplify Toggle
        simplify_toggle = hou.ToggleParmTemplate(
            name="simplify",
            label="Simplify",
            default_value=True
        )

        # Level of Detail Float
        level_detail = hou.FloatParmTemplate(
            name="level_detail",
            label="Level Detail",
            num_components=1,
            disable_when="{simplify == 0}",
            max=1
        )

        # Append to node
        ptg.append(normalize_toggle)
        ptg.append(flip_normals)
        ptg.append(simplify_toggle)
        ptg.append(level_detail)

        python_sop.setParmTemplateGroup(ptg)

        code = '''
from modules import convex_hull_utils

node = hou.pwd()
geo = node.geometry()

# Get user parms
normalize_parm = node.parm("normalize")
flip_normals_parm = node.parm("flip_normals")
simplify_parm = node.parm("simplify")
level_detail = node.parm("level_detail").eval()

# Get the points
points = [point.position() for point in geo.points()]

convex_hull_utils.create_convex_hull(geo, points, normalize_parm,flip_normals_parm, simplify_parm, level_detail)
'''
        # Prepare the Sim setup
        python_sop.parm("python").set(code)

        return python_sop

    def _create_final_merge_node(self):
        """Create final merge node to combine all components."""
        try:
            lops_context = hou.node("/stage")
            merge_node = lops_context.createNode("merge", f"merge_{self.asset_scope}")
            merge_node.moveToGoodPosition()

            self._log_message("Created final merge node")
            return merge_node

        except Exception as e:
            self._log_message(f"Error creating final merge node: {str(e)}", hou.severityType.Error)
            return None

    def _layout_all_nodes(self):
        """Layout all created nodes in the network."""
        try:
            lops_context = hou.node("/stage")
            if lops_context:
                lops_context.layoutChildren()
                self._log_message("Laid out all nodes in the network")
        except Exception as e:
            self._log_message(f"Error laying out nodes: {str(e)}", hou.severityType.Warning)

    def _initialize_stage_context(self):
        """Initialize the USD stage context."""
        try:
            print(f"         🎭 Attempting to get /stage context...")
            self.stage_context = hou.node("/stage")
            if not self.stage_context:
                print(f"         ⚠️ No /stage context found - this might need manual creation")
                self._log_message("No /stage context found, creating one...", hou.severityType.Warning)
                # Could create stage context here if needed
                print(f"         💡 Consider creating a LOPS network manually if needed")
            else:
                print(f"         ✅ Successfully found /stage context: {self.stage_context.path()}")
                print(f"         📊 Stage context type: {self.stage_context.type().name()}")
                print(f"         🔢 Number of child nodes: {len(self.stage_context.children())}")
                self._log_message("Initialized USD stage context")
        except Exception as e:
            print(f"         💥 Critical error initializing stage context: {str(e)}")
            import traceback
            print(f"         📋 Traceback: {traceback.format_exc()}")
            self._log_message(f"Error initializing stage context: {str(e)}", hou.severityType.Error)

    def _create_node_scope(self):
        """Create node scope for the workflow."""
        try:
            scope_name = _sanitize(self.asset_scope)
            self._log_message(f"Created node scope: {scope_name}")
            return scope_name
        except Exception as e:
            self._log_message(f"Error creating node scope: {str(e)}", hou.severityType.Warning)
            return "default_scope"

    def _setup_light_rig_pipeline(self, scope_name):
        """Setup light rig pipeline for the workflow."""
        try:
            # Use the light rig pipeline setup
            setup_light_rig_pipeline(scope_name)
            self._log_message("Setup light rig pipeline")
        except Exception as e:
            self._log_message(f"Error setting up light rig pipeline: {str(e)}", hou.severityType.Warning)

    def _show_final_summary(self):
        """Show final summary of the workflow."""
        try:
            total_groups = len(self.ui_result) if self.ui_result else 0
            total_assets = sum(len(group.get('asset_paths', [])) for group in self.ui_result) if self.ui_result else 0

            summary_message = f"""
✓ LOPS Asset Builder Workflow Completed Successfully!

Summary:
- Asset Scope: {self.asset_scope}
- Total Groups: {total_groups}
- Total Assets: {total_assets}
- Final Output: {self.merge_node.path() if self.merge_node else 'No output node'}

The workflow has been set up in your LOPS network.
You can now adjust parameters and render your scene.
"""

            self._log_message(summary_message)

        except Exception as e:
            self._log_message(f"Error showing final summary: {str(e)}", hou.severityType.Warning)


def toggle_lops_asset_builder_workflow():
    """Toggle function for shelf tool - shows or hides the workflow dialog."""
    try:
        # Check if dialog already exists by window title
        app = QtW.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if (hasattr(widget, 'windowTitle') and 
                    widget.windowTitle() == "LOPS Asset Builder - Asset Groups" and 
                    widget.isVisible()):
                    widget.close()
                    return

        # Create new workflow instance
        workflow = LopsAssetBuilderWorkflow()
        success = workflow.create_workflow()

        if success:
            print("LOPS Asset Builder Workflow completed successfully!")
        else:
            print("LOPS Asset Builder Workflow was cancelled or failed.")

    except Exception as e:
        print(f"Error in LOPS Asset Builder Workflow: {str(e)}")
        hou.ui.displayMessage(f"Error: {str(e)}", severity=hou.severityType.Error)


def create_lops_asset_builder_workflow():
    """Create LOPS Asset Builder Workflow - main entry point."""
    workflow = LopsAssetBuilderWorkflow()
    return workflow.create_workflow()


def main():
    """Main function for direct execution."""
    return create_lops_asset_builder_workflow()


# Entry point for shelf tools
if __name__ == "__main__":
    main()
