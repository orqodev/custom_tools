"""
Command-line interface for LOPS Asset Builder v3.
Allows running the asset builder in pipelines without UI interaction.

Usage:
    # From Python inside Houdini:
    from tools.lops_asset_builder_v3 import lops_asset_builder_cli

    # Build from dictionary config
    config = {
        "main_asset_file_path": "/path/to/asset.abc",
        "asset_name": "MyAsset",
        "folder_textures": "/path/to/textures",
        # ... see Config class for all options
    }
    result = lops_asset_builder_cli.build_asset(config)

    # Build from JSON config file
    result = lops_asset_builder_cli.build_asset_from_file("/path/to/config.json")

    # Batch build multiple assets
    configs = [config1, config2, config3]
    results = lops_asset_builder_cli.build_assets_batch(configs)
"""

from __future__ import annotations
import os
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

import hou

# Import core builder functions (UI-independent)
from tools.lops_asset_builder_v3.lops_asset_builder_v3 import (
    build_geo_and_mtl_variants,
    create_organized_net_note,
    create_karma_nodes,
)
from tools.lops_asset_builder_v3.subnet_lookdev_setup import create_subnet_lookdev_setup
from tools.lops_asset_builder_v3.create_transform_nodes import (
    build_transform_camera_and_scene_node,
    build_lights_spin_xform,
)
from tools import lops_light_rig
from modules.misc_utils import _sanitize


@dataclass
class AssetBuilderConfig:
    """Configuration for LOPS Asset Builder command-line execution.

    Required fields:
        main_asset_file_path: Path to main geometry file
        folder_textures: Path to texture folder

    Optional fields with defaults:
        asset_name: Asset name (auto-derived from file if not provided)
        asset_variants: List of additional geometry variant file paths
        asset_vset_name: Geometry variant set name
        mtl_variants: List of material variant folder paths
        mtl_vset_name: Material variant set name
        create_lookdev: Enable lookdev setup
        create_light_rig: Enable light rig creation
        enable_env_lights: Enable environment lights
        env_light_paths: List of HDRI paths for environment lights
        create_network_boxes: Create network boxes around node groups (default: False)
        skip_matchsize: Skip matchsize node creation in component geometry (default: False)
        stage_context_path: Path to stage node (default: /stage)
        verbose: Print detailed progress logs
    """
    # Required
    main_asset_file_path: str
    folder_textures: str

    # Optional with defaults (all bool options default to False)
    asset_name: str = ""
    asset_variants: List[str] = field(default_factory=list)
    create_geo_variants: bool = True
    asset_vset_name: str = "geo_variant"
    mtl_variants: List[str] = field(default_factory=list)
    mtl_vset_name: str = "mtl_variant"
    create_lookdev: bool = False
    create_light_rig: bool = False
    enable_env_lights: bool = False
    env_light_paths: List[str] = field(default_factory=list)
    create_network_boxes: bool = False
    skip_matchsize: bool = False
    stage_context_path: str = "/stage"
    verbose: bool = True
    lowercase_material_names: bool = False  # Default to False to preserve FBX naming
    use_custom_component_output: bool = True

    def __post_init__(self):
        """Auto-derive asset name if not provided and validate paths."""
        if not self.asset_name:
            self.asset_name = self._derive_asset_name(self.main_asset_file_path)

        # Validate required paths
        if not os.path.isfile(self.main_asset_file_path):
            raise ValueError(f"Main asset file does not exist: {self.main_asset_file_path}")
        if not os.path.isdir(self.folder_textures):
            raise ValueError(f"Texture folder does not exist: {self.folder_textures}")

    @staticmethod
    def _derive_asset_name(path: str) -> str:
        """Derive asset name from file path."""
        base = os.path.basename(path) if path else ""
        if not base:
            return "ASSET"
        # Strip .bgeo.sc specially, otherwise strip last extension
        if base.endswith(".bgeo.sc"):
            base = base[:-len(".bgeo.sc")]
        else:
            if "." in base:
                base = base.split(".")[0]
        return base or "ASSET"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetBuilderConfig":
        """Create config from dictionary."""
        # Filter only known fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @classmethod
    def from_json_file(cls, filepath: str) -> "AssetBuilderConfig":
        """Load config from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    def to_json_file(self, filepath: str):
        """Save config to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class ConsoleProgressReporter:
    """Simple console-based progress reporter for non-UI execution."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._cancelled = False
        self._step = 0
        self._total = 100
        self._start_time = time.time()

    def set_total(self, total: int):
        self._total = max(1, int(total))

    def step(self, message: str = None):
        self._step += 1
        if self._cancelled:
            raise KeyboardInterrupt("Cancelled by user")
        if message and self.verbose:
            elapsed = time.time() - self._start_time
            print(f"[{self._step}/{self._total}] ({elapsed:.1f}s) {message}")

    def log(self, message: str):
        if self.verbose:
            print(f"  → {message}")

    def is_cancelled(self) -> bool:
        return self._cancelled

    def request_cancel(self):
        self._cancelled = True

    def mark_finished(self, message: str = None):
        elapsed = time.time() - self._start_time
        if message and self.verbose:
            print(f"[FINISHED] ({elapsed:.1f}s) {message}")


class BuildResult:
    """Result of an asset builder execution."""

    def __init__(self, success: bool, message: str, output_node: Optional[hou.Node] = None,
                 error: Optional[Exception] = None, duration: float = 0.0):
        self.success = success
        self.message = message
        self.output_node = output_node
        self.error = error
        self.duration = duration

    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"BuildResult({status}: {self.message}, duration={self.duration:.2f}s)"


def build_asset(config: Dict[str, Any] | AssetBuilderConfig,
                progress: Optional[ConsoleProgressReporter] = None) -> BuildResult:
    """
    Build a LOPS asset from configuration.

    Args:
        config: Configuration dictionary or AssetBuilderConfig instance
        progress: Optional progress reporter (auto-created if None)

    Returns:
        BuildResult with success status, message, and output node

    Example:
        config = {
            "main_asset_file_path": "/path/to/model.abc",
            "folder_textures": "/path/to/textures",
            "asset_name": "MyAsset",
            "create_lookdev": True,
        }
        result = build_asset(config)
        if result.success:
            print(f"Built asset: {result.output_node.path()}")
    """
    start_time = time.time()

    try:
        # Convert dict to config object if needed
        if isinstance(config, dict):
            cfg = AssetBuilderConfig.from_dict(config)
        else:
            cfg = config

        # Create progress reporter if not provided
        if progress is None:
            progress = ConsoleProgressReporter(verbose=cfg.verbose)

        # Use a large internal total to allow fine-grained updates during long operations (e.g., material creation)
        progress.set_total(1000)

        # Validate stage context
        progress.step("Validating stage context")
        stage_context = hou.node(cfg.stage_context_path)
        if stage_context is None:
            raise ValueError(f"Stage context not found: {cfg.stage_context_path}")

        if progress.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")

        # Build geometry and material variants
        progress.step("Building geometry and material variants")
        geometry_variants_node, comp_out, nodes_to_layout, comp_material_last = build_geo_and_mtl_variants(
            stage_context=stage_context,
            node_name=cfg.asset_name,
            main_asset_file_path=cfg.main_asset_file_path,
            asset_variants=cfg.asset_variants,
            create_geo_variants=cfg.create_geo_variants,
            asset_vset_name=cfg.asset_vset_name,
            mtl_variants=cfg.mtl_variants,
            folder_textures=cfg.folder_textures,
            mtl_vset_name=cfg.mtl_vset_name,
            skip_matchsize=cfg.skip_matchsize,
            progress=progress,
            lowercase_material_names=cfg.lowercase_material_names,
            use_custom_component_output=cfg.use_custom_component_output,
        )

        if progress.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")

        # Layout nodes
        progress.step("Organizing network layout")
        stage_context.layoutChildren(nodes_to_layout)

        if progress.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")

        # Create sticky note
        create_organized_net_note(f"Asset {cfg.asset_name.upper()}", nodes_to_layout, hou.Vector2(-4, 18), create_network_boxes=cfg.create_network_boxes)

        # Select the Component Output
        comp_out.setSelected(True, clear_all_selected=True)

        # If lookdev is disabled, stop here
        if not cfg.create_lookdev:
            progress.log("Lookdev setup disabled; finished base setup.")
            progress.mark_finished("Done")
            duration = time.time() - start_time
            return BuildResult(
                success=True,
                message=f"Asset built successfully (no lookdev): {comp_out.path()}",
                output_node=comp_out,
                duration=duration
            )

        # Lookdev setup
        progress.step("Creating lookdev scope and graft stages")
        lookdev_setup_layout = []

        # Create primitive scope node
        primitive_node = stage_context.createNode("primitive", _sanitize(f"{cfg.asset_name}_geo"))
        primitive_node.parm("primpath").set("/turntable/asset/\n/turntable/lookdev/\n/turntable/lights/")
        primitive_node.parm("parentprimtype").set("UsdGeomScope")

        # Create graftstage for asset
        graftstage_asset_node = stage_context.createNode("graftstages", "graftstage_asset")
        graftstage_asset_node.parm("primpath").set("/turntable/asset")
        graftstage_asset_node.parm("destpath").set("/")
        graftstage_asset_node.setInput(0, primitive_node)
        graftstage_asset_node.setInput(1, comp_out)

        current_stream = graftstage_asset_node

        # Light rig
        if cfg.create_light_rig:
            progress.step("Building light rig")
            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")

            graftstage_lights_node = stage_context.createNode("graftstages", "graftstage_lights_rig")
            graftstage_lights_node.parm("primpath").set("/turntable/")
            graftstage_lights_node.parm("destpath").set("/")
            graftstage_lights_node.setInput(0, current_stream)

            light_rig_nodes_to_layout, light_mixer = lops_light_rig.create_three_point_light(selected_node=comp_out)

            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")

            create_organized_net_note("Light Rig", light_rig_nodes_to_layout, hou.Vector2(5, 10), create_network_boxes=cfg.create_network_boxes)

            graftstage_lights_node.setInput(1, light_mixer)

            switch_lights_rig_node = stage_context.createNode("switch", "switch_lights_rig")
            switch_lights_rig_node.setInput(0, current_stream)
            switch_lights_rig_node.setInput(1, graftstage_lights_node)
            switch_lights_rig_node.parm("input").set(1)
            lookdev_setup_layout.extend([switch_lights_rig_node, graftstage_lights_node])

            current_stream = switch_lights_rig_node

        # Environment lights
        if cfg.enable_env_lights:
            progress.step("Creating environment lights")
            graftstage_envlights_node = stage_context.createNode("graftstages", "graftstage_envlights")
            graftstage_envlights_node.parm("primpath").set("/turntable/lights")
            graftstage_envlights_node.parm("destpath").set("/")
            graftstage_envlights_node.setInput(0, current_stream)

            domes = []
            if cfg.env_light_paths:
                for idx, path in enumerate(cfg.env_light_paths):
                    base = os.path.splitext(os.path.basename(path))[0]
                    dome = stage_context.createNode("domelight::3.0", _sanitize(f"{base or 'env_light'}_{idx+1}"))
                    dome.parm("primpath").set("/$OS")
                    dome.parm("xn__inputstexturefile_r3ah").set(path)
                    domes.append(dome)
            else:
                dome = stage_context.createNode("domelight::3.0", "env_light")
                dome.parm("primpath").set("/$OS")
                domes.append(dome)

            switch_envlights_selection_node = stage_context.createNode("switch", "switch_envlights_selection")
            for i, dome in enumerate(domes):
                switch_envlights_selection_node.setInput(i, dome)
            envlights_nodes_to_layout = domes + [switch_envlights_selection_node]

            stage_context.layoutChildren(items=envlights_nodes_to_layout)

            if progress.is_cancelled():
                raise KeyboardInterrupt("Cancelled by user")

            create_organized_net_note("Env Light", envlights_nodes_to_layout, hou.Vector2(5, 6), create_network_boxes=cfg.create_network_boxes)

            graftstage_envlights_node.setInput(1, switch_envlights_selection_node)
            switch_env_lights = stage_context.createNode("switch", "switch_env_lights")
            switch_env_lights.setInput(0, current_stream)
            switch_env_lights.setInput(1, graftstage_envlights_node)
            switch_env_lights.parm("input").set(1)
            current_stream = switch_env_lights
            lookdev_setup_layout.extend([switch_env_lights, graftstage_envlights_node])

        # Lookdev subnet
        progress.step("Creating lookdev subnetwork")
        subnetwork_lookdevsetup_node = create_subnet_lookdev_setup(node_name="lookdev_setup")
        subnetwork_lookdevsetup_node.setInput(0, current_stream)

        switch_lookdev_setup_node = stage_context.createNode("switch", "switch_lookdev_setup")
        switch_lookdev_setup_node.setInput(0, current_stream)
        switch_lookdev_setup_node.setInput(1, subnetwork_lookdevsetup_node)
        switch_lookdev_setup_node.parm("input").set(1)
        lookdev_setup_layout = lookdev_setup_layout + [
            switch_lookdev_setup_node, subnetwork_lookdevsetup_node,
            graftstage_asset_node, primitive_node
        ]
        stage_context.layoutChildren(items=lookdev_setup_layout, horizontal_spacing=0.3, vertical_spacing=1.5)
        create_organized_net_note("LookDev Setup", lookdev_setup_layout, hou.Vector2(15, -5), create_network_boxes=cfg.create_network_boxes)

        # Camera, animations, and render nodes
        progress.step("Creating camera, animations, and render nodes")
        transform_camera_and_scene_node = build_transform_camera_and_scene_node()
        transform_camera_and_scene_node.setInput(0, switch_lookdev_setup_node)
        switch_transform_camera_and_scene_node = stage_context.createNode("switch", "switch_transform_camera_and_scene_node")
        switch_transform_camera_and_scene_node.setInput(0, switch_lookdev_setup_node)
        switch_transform_camera_and_scene_node.setInput(1, transform_camera_and_scene_node)
        transform_envlights_node = build_lights_spin_xform()
        transform_envlights_node.setInput(0, switch_transform_camera_and_scene_node)
        switch_animate_lights = stage_context.createNode("switch", "switch_animate_lights")
        switch_animate_lights.setInput(0, switch_transform_camera_and_scene_node)
        switch_animate_lights.setInput(1, transform_envlights_node)

        # Create Karma nodes
        karma_settings, usdrender_rop = create_karma_nodes(stage_context)
        karma_settings.setInput(0, switch_animate_lights)
        usdrender_rop.setInput(0, karma_settings)

        # Layout karma nodes
        karma_nodes = [
            switch_transform_camera_and_scene_node, transform_camera_and_scene_node,
            switch_animate_lights, transform_envlights_node, karma_settings, usdrender_rop
        ]
        stage_context.layoutChildren(items=karma_nodes, horizontal_spacing=0.25, vertical_spacing=1)

        if progress.is_cancelled():
            raise KeyboardInterrupt("Cancelled by user")

        create_organized_net_note("Camera Render", karma_nodes, hou.Vector2(0, -5), create_network_boxes=cfg.create_network_boxes)
        comp_out.setSelected(True, clear_all_selected=True)

        progress.mark_finished("Done")
        duration = time.time() - start_time

        return BuildResult(
            success=True,
            message=f"Asset built successfully: {comp_out.path()}",
            output_node=comp_out,
            duration=duration
        )

    except KeyboardInterrupt as e:
        duration = time.time() - start_time
        return BuildResult(
            success=False,
            message=f"Build cancelled: {str(e)}",
            error=e,
            duration=duration
        )
    except Exception as e:
        duration = time.time() - start_time
        return BuildResult(
            success=False,
            message=f"Build failed: {str(e)}",
            error=e,
            duration=duration
        )


def build_asset_from_file(config_filepath: str, verbose: bool = True) -> BuildResult:
    """
    Build a LOPS asset from a JSON configuration file.

    Args:
        config_filepath: Path to JSON config file
        verbose: Enable verbose logging

    Returns:
        BuildResult with success status and details

    Example:
        result = build_asset_from_file("/path/to/config.json")
        print(result)
    """
    try:
        config = AssetBuilderConfig.from_json_file(config_filepath)
        config.verbose = verbose
        return build_asset(config)
    except Exception as e:
        return BuildResult(
            success=False,
            message=f"Failed to load config file: {str(e)}",
            error=e
        )


def build_assets_batch(configs: List[Dict[str, Any] | AssetBuilderConfig],
                      verbose: bool = True) -> List[BuildResult]:
    """
    Build multiple LOPS assets in batch mode.

    Args:
        configs: List of configuration dictionaries or AssetBuilderConfig instances
        verbose: Enable verbose logging

    Returns:
        List of BuildResult objects, one per asset

    Example:
        configs = [
            {"main_asset_file_path": "/assets/asset1.abc", "folder_textures": "/tex/asset1"},
            {"main_asset_file_path": "/assets/asset2.abc", "folder_textures": "/tex/asset2"},
        ]
        results = build_assets_batch(configs)
        for i, result in enumerate(results):
            print(f"Asset {i+1}: {result}")
    """
    results = []
    total = len(configs)

    print(f"\n{'='*60}")
    print(f"BATCH BUILD: Processing {total} assets")
    print(f"{'='*60}\n")

    for i, config in enumerate(configs, 1):
        print(f"\n[BATCH {i}/{total}] Starting build...")
        result = build_asset(config, progress=ConsoleProgressReporter(verbose=verbose))
        results.append(result)

        status = "✓ SUCCESS" if result.success else "✗ FAILED"
        print(f"[BATCH {i}/{total}] {status} - {result.message}")

    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH BUILD SUMMARY")
    print(f"{'='*60}")
    success_count = sum(1 for r in results if r.success)
    failed_count = total - success_count
    total_duration = sum(r.duration for r in results)
    print(f"Total: {total} | Success: {success_count} | Failed: {failed_count}")
    print(f"Total duration: {total_duration:.2f}s")
    print(f"{'='*60}\n")

    return results


def create_example_config(output_path: str = None) -> str:
    """
    Create an example JSON configuration file.

    Args:
        output_path: Where to save the example (defaults to current dir)

    Returns:
        Path to created example file
    """
    example_config = {
        "main_asset_file_path": "/path/to/your/model.abc",
        "folder_textures": "/path/to/your/textures",
        "asset_name": "MyAsset",
        "asset_variants": [
            "/path/to/variant1.abc",
            "/path/to/variant2.abc"
        ],
        "asset_vset_name": "geo_variant",
        "mtl_variants": [
            "/path/to/material_variant1",
            "/path/to/material_variant2"
        ],
        "mtl_vset_name": "mtl_variant",
        "create_lookdev": True,
        "create_light_rig": True,
        "enable_env_lights": True,
        "env_light_paths": [
            "/path/to/hdri1.exr",
            "/path/to/hdri2.exr"
        ],
        "stage_context_path": "/stage",
        "verbose": True
    }

    if output_path is None:
        output_path = "asset_builder_config_example.json"

    with open(output_path, 'w') as f:
        json.dump(example_config, f, indent=2)

    print(f"Example config created: {output_path}")
    return output_path


# Convenience function for quick testing
def quick_build(asset_path: str, textures_path: str, **kwargs) -> BuildResult:
    """
    Quick build with minimal configuration.

    Args:
        asset_path: Path to main geometry file
        textures_path: Path to texture folder
        **kwargs: Additional config options (asset_name, create_lookdev, etc.)

    Returns:
        BuildResult

    Example:
        result = quick_build("/assets/model.abc", "/textures", asset_name="MyAsset")
    """
    config = {
        "main_asset_file_path": asset_path,
        "folder_textures": textures_path,
        **kwargs
    }
    return build_asset(config)
