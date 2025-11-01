"""
Texture Variant Detector - Flexible pattern matching for material variant folders

Handles various naming conventions:
- Simple: 4k/, 2k/, 1k/
- Prefixed: png4k/, jpg2k/
- Suffixed: 4k_png/, 2k_jpg/
- Complex: Cyberpunk_Trimsheets_4K_JPG_Textures/
- Mixed: 4K_JPG/, 2k_png/, 8K_EXR/
"""

import os
import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TextureVariant:
    """Represents a detected texture variant."""
    folder_name: str          # Full folder name
    folder_path: str          # Full path
    resolution: str           # Extracted resolution (4k, 2k, etc.)
    format: str              # Extracted format (png, jpg, exr, etc.)
    variant_key: str         # Normalized key for matching (4k_jpg)
    confidence: float        # Detection confidence 0-1


class TextureVariantDetector:
    """
    Intelligent texture variant folder detector.

    Supports multiple naming patterns and learns from folder structure.
    """

    # Resolution patterns
    RESOLUTION_PATTERNS = [
        r'\b(\d+)[kK]\b',                    # 4k, 2K, 8k
        r'\b(\d{4,5})(?:x\d{4,5})?\b',      # 4096, 2048x2048
        r'[_\-\s]([1248])[kK]',             # _4K, -2k, 4k
    ]

    # Format patterns
    FORMAT_PATTERNS = [
        r'\b(png|jpg|jpeg|tif|tiff|exr|tx|hdr)\b',  # Standard formats
        r'[_\-\s](PNG|JPG|JPEG|TIF|TIFF|EXR|TX|HDR)',  # Uppercase
    ]

    # Common variant folder patterns
    VARIANT_FOLDER_PATTERNS = [
        # Simple patterns
        r'^(\d+)[kK]$',                              # 4k, 2K
        r'^(png|jpg|jpeg|exr|tif)\d+[kK]$',         # png4k, jpg2k
        r'^\d+[kK]_(png|jpg|jpeg|exr|tif)$',        # 4k_png, 2k_jpg

        # Complex patterns with prefixes/suffixes
        r'.*?(\d+)[kK].*?(png|jpg|jpeg|exr|tif)',   # Any_4K_JPG_Any
        r'.*?(png|jpg|jpeg|exr|tif).*?(\d+)[kK]',   # Any_PNG_4K_Any

        # Resolution only
        r'.*?(\d+)[kK]',                             # Contains resolution

        # Format only
        r'.*?(png|jpg|jpeg|exr|tif)',               # Contains format
    ]

    def __init__(self):
        self.detected_patterns = []
        self.resolution_to_numeric = {
            '1k': 1024, '2k': 2048, '4k': 4096, '8k': 8192, '16k': 16384
        }
        # Priority config (defaults preserve previous behavior: 4k > 2k > 1k)
        self.resolution_priority: List[str] = ["4k", "2k", "1k"]
        self.format_priority: List[str] = ["jpg", "png", "exr", "tif", "tx", "hdr", "unknown"]
        self._load_priority_config()

    def _load_priority_config(self):
        """Load resolution/format priority from env or local JSON config.

        Precedence:
        1) Environment variables: LOPS_TEX_RES_PRIORITY, LOPS_TEX_FORMAT_PRIORITY
           - Comma/semicolon separated list, e.g. "8k,4k,2k,1k".
        2) JSON file next to this module: texture_variant_config.json
           {
             "resolution_priority": ["8k", "4k", "2k", "1k"],
             "format_priority": ["jpg", "png", "exr", "tif", "tx", "hdr", "unknown"]
           }
        Defaults are kept if nothing provided.
        """
        try:
            # Env vars
            res_env = os.environ.get("LOPS_TEX_RES_PRIORITY")
            fmt_env = os.environ.get("LOPS_TEX_FORMAT_PRIORITY")
            if res_env:
                parts = [p.strip().lower() for p in re.split(r"[;,]", res_env) if p.strip()]
                if parts:
                    self.resolution_priority = parts
            if fmt_env:
                parts = [p.strip().lower() for p in re.split(r"[;,]", fmt_env) if p.strip()]
                if parts:
                    self.format_priority = parts
            # JSON file
            cfg_path = os.path.join(os.path.dirname(__file__), "texture_variant_config.json")
            if os.path.exists(cfg_path):
                import json
                with open(cfg_path, "r") as f:
                    data = json.load(f) or {}
                res = data.get("resolution_priority")
                fmt = data.get("format_priority")
                if isinstance(res, list) and res:
                    self.resolution_priority = [str(x).lower() for x in res]
                if isinstance(fmt, list) and fmt:
                    self.format_priority = [str(x).lower() for x in fmt]
        except Exception:
            # Silently ignore config errors, keep defaults
            pass

    def _parse_resolution_numeric(self, res: Optional[str]) -> int:
        """Convert a resolution label like '4k' or '4096' into a comparable integer.
        Unknown returns 0.
        """
        try:
            if not res:
                return 0
            r = str(res).lower()
            # Match like '4k', '8k'
            m = re.match(r"^(\d+)[k]$", r)
            if m:
                return int(m.group(1)) * 1024
            # Match pure number like 4096
            if r.isdigit():
                return int(r)
            # Fallback via mapping
            if r in self.resolution_to_numeric:
                return int(self.resolution_to_numeric[r])
        except Exception:
            return 0
        return 0

    def resolution_rank(self, res: Optional[str]) -> Tuple[int, int]:
        """Return a tuple rank: (priority_index_desc, numeric_value) where higher is better.
        If res appears in configured priority, earlier index is higher.
        We invert index to make higher numbers better (len-index).
        """
        r = (res or "").lower()
        if r in self.resolution_priority:
            # earlier in list is better; convert to descending score
            idx = self.resolution_priority.index(r)
            return (len(self.resolution_priority) - idx, self._parse_resolution_numeric(r))
        # Not in list: rank based on numeric value only
        return (0, self._parse_resolution_numeric(r))

    def format_rank(self, fmt: Optional[str]) -> int:
        f = (fmt or "unknown").lower()
        if f in self.format_priority:
            return len(self.format_priority) - self.format_priority.index(f)
        return 0

    def choose_main_variant(self, variants: List[TextureVariant]) -> Tuple[Optional[TextureVariant], List[TextureVariant]]:
        """Choose a main variant using configured priorities.

        Returns (best_variant_or_None, others_list)
        """
        if not variants:
            return None, []
        def score(v: TextureVariant) -> Tuple[int, int, float]:
            res_primary, res_numeric = self.resolution_rank(getattr(v, 'resolution', None))
            fmt_score = self.format_rank(getattr(v, 'format', None))
            # Confidence as tie-breaker (already 0..1)
            return (res_primary, res_numeric, float(getattr(v, 'confidence', 0.0)))
        best = max(variants, key=score)
        others = [v for v in variants if v is not best]
        return best, others

    def detect_variants(self, texture_folder: str) -> List[TextureVariant]:
        """
        Detect texture variant folders in the given path.

        Args:
            texture_folder: Root texture folder path

        Returns:
            List of detected TextureVariant objects
        """
        if not os.path.exists(texture_folder):
            return []

        variants = []

        # Scan immediate subdirectories
        try:
            items = os.listdir(texture_folder)
        except PermissionError:
            return []

        for item in items:
            item_path = os.path.join(texture_folder, item)

            if not os.path.isdir(item_path):
                continue

            # Try to extract variant info
            variant = self._analyze_folder_name(item, item_path)
            if variant:
                variants.append(variant)

        # If we found variants, learn the pattern
        if variants:
            self._learn_pattern(variants)

        return sorted(variants, key=lambda v: (v.resolution, v.format))

    def _analyze_folder_name(self, folder_name: str, folder_path: str) -> Optional[TextureVariant]:
        """
        Analyze folder name to extract variant information.

        Args:
            folder_name: Name of the folder
            folder_path: Full path to folder

        Returns:
            TextureVariant if detected, None otherwise
        """
        resolution = None
        format_type = None
        confidence = 0.0

        folder_lower = folder_name.lower()

        # Extract resolution
        for pattern in self.RESOLUTION_PATTERNS:
            match = re.search(pattern, folder_lower, re.IGNORECASE)
            if match:
                res_value = match.group(1)
                # Normalize to format like "4k"
                if len(res_value) > 2:  # Like 4096
                    resolution = self._numeric_to_resolution(int(res_value))
                else:  # Like 4 (from "4k")
                    resolution = f"{res_value}k"
                confidence += 0.5
                break

        # Extract format
        for pattern in self.FORMAT_PATTERNS:
            match = re.search(pattern, folder_lower, re.IGNORECASE)
            if match:
                format_type = match.group(1).lower()
                # Normalize jpeg to jpg
                if format_type == 'jpeg':
                    format_type = 'jpg'
                elif format_type == 'tiff':
                    format_type = 'tif'
                confidence += 0.3
                break

        # Fallback: handle concatenated format+resolution like 'png4k' or 'jpg2k'
        if not resolution:
            m = re.search(r'(png|jpg|jpeg|exr|tif|tiff)(\d+)[kK]', folder_lower, re.IGNORECASE)
            if m:
                fmt = m.group(1).lower()
                if fmt == 'jpeg':
                    fmt = 'jpg'
                if fmt == 'tiff':
                    fmt = 'tif'
                format_type = format_type or fmt
                res_value = m.group(2)
                resolution = f"{res_value}k"
                confidence += 0.7  # fairly confident match
        # Also handle '4kpng' (less common)
        if not resolution:
            m = re.search(r'(\d+)[kK](png|jpg|jpeg|exr|tif|tiff)', folder_lower, re.IGNORECASE)
            if m:
                res_value = m.group(1)
                resolution = f"{res_value}k"
                fmt = m.group(2).lower()
                if fmt == 'jpeg':
                    fmt = 'jpg'
                if fmt == 'tiff':
                    fmt = 'tif'
                format_type = format_type or fmt
                confidence += 0.6

        # Must have at least resolution to be considered a variant
        if not resolution:
            return None

        # Create variant key
        if format_type:
            variant_key = f"{resolution}_{format_type}"
        else:
            variant_key = resolution
            format_type = "unknown"

        # Adjust confidence based on pattern clarity
        if self._is_simple_pattern(folder_name):
            confidence = min(1.0, confidence + 0.2)

        return TextureVariant(
            folder_name=folder_name,
            folder_path=folder_path,
            resolution=resolution,
            format=format_type,
            variant_key=variant_key,
            confidence=confidence
        )

    def _numeric_to_resolution(self, numeric_res: int) -> str:
        """Convert numeric resolution to k notation."""
        if numeric_res >= 16384:
            return "16k"
        elif numeric_res >= 8192:
            return "8k"
        elif numeric_res >= 4096:
            return "4k"
        elif numeric_res >= 2048:
            return "2k"
        elif numeric_res >= 1024:
            return "1k"
        else:
            return f"{numeric_res}px"

    def _is_simple_pattern(self, folder_name: str) -> bool:
        """Check if folder name follows simple pattern (4k, png2k, etc.)."""
        simple_patterns = [
            r'^\d+[kK]$',                           # 4k
            r'^(png|jpg|jpeg|exr|tif)\d+[kK]$',    # png4k
            r'^\d+[kK]_(png|jpg|jpeg|exr|tif)$',   # 4k_png
        ]

        for pattern in simple_patterns:
            if re.match(pattern, folder_name, re.IGNORECASE):
                return True
        return False

    def _learn_pattern(self, variants: List[TextureVariant]):
        """Learn common pattern from detected variants."""
        if not variants:
            return

        # Analyze common structure
        folder_names = [v.folder_name for v in variants]

        # Find common prefix/suffix
        common_prefix = os.path.commonprefix(folder_names)

        # Store learned pattern for future use
        self.detected_patterns.append({
            'prefix': common_prefix,
            'count': len(variants),
            'resolutions': [v.resolution for v in variants],
            'formats': [v.format for v in variants]
        })

    def get_variant_info(self, variants: List[TextureVariant]) -> Dict:
        """
        Get summary information about detected variants.

        Returns:
            Dictionary with variant statistics
        """
        if not variants:
            return {
                'count': 0,
                'resolutions': [],
                'formats': [],
                'variant_keys': []
            }

        resolutions = sorted(set(v.resolution for v in variants))
        formats = sorted(set(v.format for v in variants))
        variant_keys = sorted(set(v.variant_key for v in variants))

        return {
            'count': len(variants),
            'resolutions': resolutions,
            'formats': formats,
            'variant_keys': variant_keys,
            'folders': [v.folder_name for v in variants]
        }

    def match_variant_by_key(self, variant_key: str, variants: List[TextureVariant]) -> Optional[TextureVariant]:
        """
        Find variant by normalized key.

        Args:
            variant_key: Key like "4k_jpg" or "2k"
            variants: List of variants to search

        Returns:
            Matching TextureVariant or None
        """
        for variant in variants:
            if variant.variant_key.lower() == variant_key.lower():
                return variant
        return None


def example_usage():
    """Example usage with various folder structures."""

    detector = TextureVariantDetector()

    # Example 1: Simple naming
    print("Example 1: Simple KB3D-style")
    print("-" * 50)
    test_folders_1 = ["png4k", "png2k", "png1k", "jpg4k", "jpg2k"]
    for folder in test_folders_1:
        variant = detector._analyze_folder_name(folder, f"/test/{folder}")
        if variant:
            print(f"  {folder:20s} → res:{variant.resolution:5s} fmt:{variant.format:6s} key:{variant.variant_key:10s} ({variant.confidence:.0%})")

    # Example 2: Complex BigMediumSmall naming
    print("\nExample 2: BigMediumSmall SciFi-style")
    print("-" * 50)
    test_folders_2 = [
        "Cyberpunk_Trimsheets_4K_JPG_Textures",
        "Cyberpunk_Trimsheets_2K_JPG_Textures",
        "Cyberpunk_Trimsheets_4K_PNG_Textures",
    ]
    for folder in test_folders_2:
        variant = detector._analyze_folder_name(folder, f"/test/{folder}")
        if variant:
            print(f"  {folder:40s} → res:{variant.resolution:5s} fmt:{variant.format:6s} key:{variant.variant_key:10s} ({variant.confidence:.0%})")

    # Example 3: Mixed patterns
    print("\nExample 3: Mixed patterns")
    print("-" * 50)
    test_folders_3 = ["4k", "2K", "8K_EXR", "2048x2048", "textures_4k_png"]
    for folder in test_folders_3:
        variant = detector._analyze_folder_name(folder, f"/test/{folder}")
        if variant:
            print(f"  {folder:20s} → res:{variant.resolution:5s} fmt:{variant.format:6s} key:{variant.variant_key:10s} ({variant.confidence:.0%})")


if __name__ == "__main__":
    example_usage()


