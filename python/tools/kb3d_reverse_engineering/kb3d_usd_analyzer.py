"""
KB3D USD Analyzer

Analyzes KitBash3D USD files to extract component structure, references,
transforms, and material bindings for reverse engineering.

Usage:
    from tools.kb3d_reverse_engineering import kb3d_usd_analyzer
    analyzer = kb3d_usd_analyzer.KB3DAnalyzer("/path/to/asset.usd")
    mapping = analyzer.analyze()
    analyzer.save_mapping("/path/to/output.json")
"""

import json
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, Sdf, UsdShade
    HAS_USD = True
except ImportError:
    HAS_USD = False
    print("Warning: USD libraries not available. Install pxr package.")


@dataclass
class Transform:
    """Represents a USD transform"""
    translate: Tuple[float, float, float] = (0, 0, 0)
    rotate: Tuple[float, float, float] = (0, 0, 0)
    scale: Tuple[float, float, float] = (1, 1, 1)
    xform_op_order: List[str] = field(default_factory=list)


@dataclass
class ExternalReference:
    """Represents an external USD reference (prop asset)"""
    instance_name: str
    ref_path: str
    kind: str
    instanceable: bool
    transform: Transform
    prim_path: str


@dataclass
class InternalPrototype:
    """Represents an internal prototype definition"""
    prototype_name: str
    prim_path: str
    instances: List[Dict] = field(default_factory=list)
    geometry_source: str = ""  # Path to .bgeo.sc file


@dataclass
class AssetMapping:
    """Complete mapping of an asset's structure"""
    asset_name: str
    asset_path: str
    default_prim: str
    external_props: List[ExternalReference] = field(default_factory=list)
    internal_prototypes: List[InternalPrototype] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    texture_variants: List[str] = field(default_factory=list)


class KB3DAnalyzer:
    """Analyzes KB3D USD files to extract component structure"""

    def __init__(self, usd_file_path: str):
        """
        Initialize analyzer with USD file path.

        Args:
            usd_file_path: Path to main USD file (e.g., KB3D_MTM_BldgLgCommsArray_A.usd)
        """
        if not HAS_USD:
            raise ImportError("USD libraries (pxr) not available")

        self.usd_file_path = os.path.abspath(usd_file_path)
        if not os.path.exists(self.usd_file_path):
            raise FileNotFoundError(f"USD file not found: {self.usd_file_path}")

        self.asset_dir = os.path.dirname(self.usd_file_path)
        self.asset_name = os.path.splitext(os.path.basename(self.usd_file_path))[0]

        self.stage = None
        self.mapping = None

    def analyze(self) -> AssetMapping:
        """
        Analyze the USD file and extract component structure.

        Returns:
            AssetMapping object containing all extracted data
        """
        print(f"Analyzing USD file: {self.usd_file_path}")

        # Open USD stage
        self.stage = Usd.Stage.Open(self.usd_file_path)
        if not self.stage:
            raise RuntimeError(f"Failed to open USD stage: {self.usd_file_path}")

        # Initialize mapping
        default_prim = self.stage.GetDefaultPrim()
        self.mapping = AssetMapping(
            asset_name=self.asset_name,
            asset_path=self.usd_file_path,
            default_prim=default_prim.GetPath().pathString if default_prim else ""
        )

        # Extract data
        self._extract_texture_variants()
        self._extract_materials()
        self._extract_external_references()
        self._extract_internal_prototypes()

        print(f"Analysis complete:")
        print(f"  - External props: {len(self.mapping.external_props)}")
        print(f"  - Internal prototypes: {len(self.mapping.internal_prototypes)}")
        print(f"  - Materials: {len(self.mapping.materials)}")
        print(f"  - Texture variants: {len(self.mapping.texture_variants)}")

        return self.mapping

    def _extract_texture_variants(self):
        """Extract texture variant names from variant sets"""
        default_prim = self.stage.GetDefaultPrim()
        if not default_prim:
            return

        variant_sets = default_prim.GetVariantSets()
        if variant_sets.HasVariantSet("texture_variant"):
            vset = variant_sets.GetVariantSet("texture_variant")
            self.mapping.texture_variants = vset.GetVariantNames()
            print(f"  Found texture variants: {', '.join(self.mapping.texture_variants)}")

    def _extract_materials(self):
        """Extract material names from the USD"""
        # Look for material scope/definitions
        for prim in self.stage.Traverse():
            if prim.IsA(UsdShade.Material):
                mat_name = prim.GetName()
                if mat_name not in self.mapping.materials:
                    self.mapping.materials.append(mat_name)

        print(f"  Found {len(self.mapping.materials)} materials")

    def _extract_external_references(self):
        """Extract external prop references"""
        for prim in self.stage.Traverse():
            # Skip prototypes scope
            if "__prototypes__" in prim.GetPath().pathString:
                continue

            # Check if prim has external references
            prim_spec = self.stage.GetRootLayer().GetPrimAtPath(prim.GetPath())
            if not prim_spec:
                continue

            references = prim_spec.referenceList.prependedItems
            for ref in references:
                ref_path = ref.assetPath
                # External reference has "../" or absolute path
                if ref_path and ("../" in ref_path or ref_path.startswith("/")):
                    # This is an external prop reference
                    ext_ref = ExternalReference(
                        instance_name=prim.GetName(),
                        ref_path=ref_path,
                        kind=prim.GetMetadata("kind") or "",
                        instanceable=prim.IsInstanceable(),
                        transform=self._extract_transform(prim),
                        prim_path=prim.GetPath().pathString
                    )
                    self.mapping.external_props.append(ext_ref)

        print(f"  Found {len(self.mapping.external_props)} external prop references")

    def _extract_internal_prototypes(self):
        """Extract internal prototype definitions and their instances"""
        # Find prototypes scope
        prototypes_path = None
        for prim in self.stage.Traverse():
            if prim.GetName() == "__prototypes__":
                prototypes_path = prim.GetPath()
                break

        if not prototypes_path:
            print("  No __prototypes__ scope found, checking for class definitions...")
            # Some USD files may use class definitions instead
            return

        # Extract prototype definitions
        prototypes_prim = self.stage.GetPrimAtPath(prototypes_path)
        prototype_map = {}

        for child in prototypes_prim.GetChildren():
            proto_name = child.GetName()
            proto_path = child.GetPath().pathString
            prototype = InternalPrototype(
                prototype_name=proto_name,
                prim_path=proto_path,
                instances=[]
            )
            prototype_map[proto_path] = prototype
            self.mapping.internal_prototypes.append(prototype)

        print(f"  Found {len(prototype_map)} internal prototype definitions")

        # Find all instances of each prototype
        for prim in self.stage.Traverse():
            # Skip prototypes themselves
            if prototypes_path and prototypes_path.IsPrefixOf(prim.GetPath()):
                continue

            # Check if this prim references a prototype
            prim_spec = self.stage.GetRootLayer().GetPrimAtPath(prim.GetPath())
            if not prim_spec:
                continue

            references = prim_spec.referenceList.prependedItems
            for ref in references:
                # Internal reference points to prototype path
                if ref.primPath and str(ref.primPath) in prototype_map:
                    proto_ref = str(ref.primPath)
                    instance_data = {
                        "instance_name": prim.GetName(),
                        "prim_path": prim.GetPath().pathString,
                        "transform": asdict(self._extract_transform(prim)),
                        "instanceable": prim.IsInstanceable()
                    }
                    prototype_map[proto_ref].instances.append(instance_data)

        # Report instance counts
        for proto in self.mapping.internal_prototypes:
            print(f"    - {proto.prototype_name}: {len(proto.instances)} instances")

    def _extract_transform(self, prim) -> Transform:
        """Extract transform data from a prim"""
        if not prim.IsA(UsdGeom.Xformable):
            return Transform()

        xformable = UsdGeom.Xformable(prim)
        xform_ops = xformable.GetOrderedXformOps()

        translate = (0, 0, 0)
        rotate = (0, 0, 0)
        scale = (1, 1, 1)
        xform_op_order = []

        for op in xform_ops:
            op_type = op.GetOpType()
            op_name = op.GetOpName()
            xform_op_order.append(op_name)

            if op_type == UsdGeom.XformOp.TypeTranslate:
                translate = tuple(op.Get())
            elif op_type == UsdGeom.XformOp.TypeRotateXYZ:
                rotate = tuple(op.Get())
            elif op_type == UsdGeom.XformOp.TypeScale:
                scale = tuple(op.Get())

        return Transform(
            translate=translate,
            rotate=rotate,
            scale=scale,
            xform_op_order=xform_op_order
        )

    def map_to_extracted_geometry(self, extracted_geo_dir: str):
        """
        Map prototype names to extracted geometry folders.

        Args:
            extracted_geo_dir: Path to kb3d_clone/geo/{asset_name}/ directory
        """
        if not self.mapping:
            raise RuntimeError("Must run analyze() first")

        if not os.path.isdir(extracted_geo_dir):
            print(f"Warning: Extracted geometry directory not found: {extracted_geo_dir}")
            return

        # List available geometry folders
        geo_folders = [f for f in os.listdir(extracted_geo_dir)
                       if os.path.isdir(os.path.join(extracted_geo_dir, f))]

        print(f"\nMapping prototypes to extracted geometry...")
        print(f"  Available geometry folders: {len(geo_folders)}")

        # Map each prototype to a geometry folder
        for proto in self.mapping.internal_prototypes:
            # Try to match prototype name to folder name
            # Prototype names often have prefixes like "KB3D_MTM_BldgLgCommsArray_A_"
            proto_basename = proto.prototype_name

            # Remove asset prefix
            if proto_basename.startswith(self.asset_name + "_"):
                proto_basename = proto_basename[len(self.asset_name) + 1:]

            # Try exact match first
            if proto_basename in geo_folders:
                bgeo_path = os.path.join(extracted_geo_dir, proto_basename, f"{proto_basename}.bgeo.sc")
                if os.path.exists(bgeo_path):
                    proto.geometry_source = bgeo_path
                    print(f"    ✓ Mapped {proto.prototype_name} → {proto_basename}")
                    continue

            # Try fuzzy matching
            best_match = None
            best_score = 0
            for folder in geo_folders:
                # Simple similarity: count matching characters
                similarity = sum(1 for a, b in zip(proto_basename.lower(), folder.lower()) if a == b)
                if similarity > best_score:
                    best_score = similarity
                    best_match = folder

            if best_match and best_score > len(proto_basename) * 0.5:
                bgeo_path = os.path.join(extracted_geo_dir, best_match, f"{best_match}.bgeo.sc")
                if os.path.exists(bgeo_path):
                    proto.geometry_source = bgeo_path
                    print(f"    ~ Fuzzy matched {proto.prototype_name} → {best_match} (score: {best_score})")
                else:
                    print(f"    ✗ No match for {proto.prototype_name}")
            else:
                print(f"    ✗ No match for {proto.prototype_name}")

    def save_mapping(self, output_path: str):
        """
        Save mapping to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        if not self.mapping:
            raise RuntimeError("Must run analyze() first")

        # Convert dataclass to dict
        mapping_dict = asdict(self.mapping)

        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(mapping_dict, f, indent=2)

        print(f"\nMapping saved to: {output_path}")

    def load_mapping(self, json_path: str) -> AssetMapping:
        """Load mapping from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Reconstruct dataclass (simplified, may need refinement)
        self.mapping = AssetMapping(**data)
        return self.mapping


def analyze_asset(usd_path: str, extracted_geo_dir: str = None, output_json: str = None):
    """
    Convenience function to analyze a single asset.

    Args:
        usd_path: Path to main USD file
        extracted_geo_dir: Optional path to extracted geometry directory
        output_json: Optional path to save JSON mapping

    Returns:
        AssetMapping object
    """
    analyzer = KB3DAnalyzer(usd_path)
    mapping = analyzer.analyze()

    if extracted_geo_dir:
        analyzer.map_to_extracted_geometry(extracted_geo_dir)

    if output_json:
        analyzer.save_mapping(output_json)

    return mapping


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python kb3d_usd_analyzer.py <usd_file> [extracted_geo_dir] [output_json]")
        sys.exit(1)

    usd_file = sys.argv[1]
    geo_dir = sys.argv[2] if len(sys.argv) > 2 else None
    output = sys.argv[3] if len(sys.argv) > 3 else None

    analyze_asset(usd_file, geo_dir, output)
