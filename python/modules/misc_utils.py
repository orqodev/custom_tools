import hou
import loputils
import re
import unicodedata
from typing import Optional, Set, Iterable
from dataclasses import dataclass, field


@dataclass
class MaterialNamingConfig:
    """
    Unified configuration for material name processing across the entire pipeline.

    This ensures consistent material naming between:
    - Geometry material extraction
    - Texture scanning
    - Material validation
    - Material creation

    Attributes:
        lowercase: If True, convert material names to lowercase (default: False)
        drop_tokens: Set of tokens to remove from material names (default: {"base", "bake", "baked", "bake1", "pbr"})
        enabled: If True, apply sanitization; if False, use raw material names (default: True)
    """
    lowercase: bool = False
    drop_tokens: Optional[Set[str]] = None
    enabled: bool = True

    def __post_init__(self):
        """Set default drop_tokens if not provided."""
        if self.drop_tokens is None:
            self.drop_tokens = {"base", "bake", "baked", "bake1", "pbr"}

    def to_sanitize_options(self) -> dict:
        """
        Convert to legacy sanitize_options dict format for backward compatibility.

        Returns:
            dict: Legacy format {'enabled': bool, 'lowercase': bool, 'drop_tokens': set}
        """
        return {
            'enabled': self.enabled,
            'lowercase': self.lowercase,
            'drop_tokens': self.drop_tokens
        }

    @classmethod
    def from_sanitize_options(cls, sanitize_options: dict) -> 'MaterialNamingConfig':
        """
        Create MaterialNamingConfig from legacy sanitize_options dict.

        Args:
            sanitize_options: Legacy dict format

        Returns:
            MaterialNamingConfig instance
        """
        return cls(
            enabled=sanitize_options.get('enabled', True),
            lowercase=sanitize_options.get('lowercase', False),
            drop_tokens=sanitize_options.get('drop_tokens', None)
        )

    @classmethod
    def from_ui(cls, lowercase: bool = False) -> 'MaterialNamingConfig':
        """
        Create MaterialNamingConfig from UI checkbox state.

        Args:
            lowercase: Checkbox state for lowercase material names

        Returns:
            MaterialNamingConfig instance with UI settings
        """
        return cls(
            enabled=True,
            lowercase=lowercase,
            drop_tokens=None  # Will use defaults from __post_init__
        )


def _is_in_solaris():
    ''' Checks if the current context is Stage'''
    # Get the current network editor pane
    network_editor = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)

    if network_editor.pwd().childTypeCategory().name() == "Lop":
        return True
    return False

def calculate_prim_bounds(target_node):
    '''Calculate the bounding box for a prim in solaris
    Args:
        target_node = The LOP node
    Return:
        dict : Contains the bounding box information - min, max, center, size and original bounding box
    '''

    # Get the stage
    stage = target_node.stage()

    if not stage:
        print("No USD stage found")
        return None

    # Get the target prim
    prim = stage.GetDefaultPrim()

    if not prim or not prim.IsValid():
        print(f"Invalid prim {prim}")
        return None

    # Calculate the bounding box
    bounds = loputils.computePrimWorldBounds(target_node,[prim])
    print(type(bounds))

    # Extract the bounding box information
    range3d = bounds.GetRange()
    min_point = hou.Vector3(range3d.GetMin())
    max_point = hou.Vector3(range3d.GetMax())

    center = (min_point + max_point) * 0.5
    size = max_point - min_point

    return {"min":min_point, "max":max_point, "center":center, "size":size, "bbox":bounds}

def safe_node_name(raw: str) -> str:
    """
    Replace illegal chars with underscores and make sure
    the name doesn't start with a digit.
    """
    # Keep only [A‑Z a‑z 0‑9 _]
    name = re.sub(r'[^A-Za-z0-9_]+', '_', str(raw))

    # Prepend underscore if the first char is a digit
    if name and name[0].isdigit():
        name = f"_{name}"

    return name


def _sanitize(text: str) -> str:
    """
    Replace every whitespace character (space, tab, newline, etc.)
    with a single underscore.  Collapses multiple spaces to one _.
    """
    # \W+ matches one or more non-word characters (opposite of [a-zA-Z0-9_])
    # Should use \s+ to match one or more whitespace characters instead
    return re.sub('\\s+', '_', text)


def sanitize_all_prim_string_attribs(geo: hou.Geometry):
    """
    Walk every primitive attribute that is of String type and sanitise values.
    """
    # Get all primitive attribs that store STRING data
    prim_str_attribs = [
        a for a in geo.primAttribs()
        if a.dataType() == hou.attribData.String
    ]

    if not prim_str_attribs:
        return  # nothing to do

    for prim in geo.prims():
        for attrib in prim_str_attribs:
            raw_val = prim.stringAttribValue(attrib.name())
            cleaned = _sanitize(raw_val)
            if cleaned != raw_val:
                prim.setAttribValue(attrib, cleaned)


def slugify(text: str, drop_tokens: Optional[Set[str]] = None, lowercase: bool = False) -> str:
    """
    Normalize material names so that Geometry prims and MaterialX subnets align automatically.

    Args:
        text: The input text to slugify
        drop_tokens: Set of tokens to drop. If None, uses default set.
        lowercase: If True, convert to lowercase. If False, preserve original case (default: False).

    Returns:
        Normalized string with tokens joined by underscores
    """
    if drop_tokens is None:
        drop_tokens = {"base", "bake", "baked", "bake1", "pbr"}

    # Optionally convert to lowercase
    if lowercase:
        text = text.lower()
        drop_tokens_normalized = drop_tokens
    else:
        # Case-insensitive drop_tokens matching when preserving case
        drop_tokens_normalized = {token.lower() for token in drop_tokens}

    # Unicode-normalize
    text = unicodedata.normalize('NFKD', text)
    # Remove diacritical marks after normalization
    text = ''.join(c for c in text if not unicodedata.combining(c))

    # Replace any non-alphanumeric run with "_" (underscore)
    # Preserve uppercase letters if lowercase=False
    if lowercase:
        text = re.sub(r'[^a-z0-9]+', '_', text)
    else:
        text = re.sub(r'[^a-zA-Z0-9]+', '_', text)

    # Split into tokens and drop unwanted ones (case-insensitive matching)
    if lowercase:
        tokens = [token for token in text.split('_') if token and token not in drop_tokens_normalized]
    else:
        tokens = [token for token in text.split('_') if token and token.lower() not in drop_tokens_normalized]

    # Join the remaining tokens with "_"
    return '_'.join(tokens)


def slugify_name_material(value: str, drop_tokens: Optional[Iterable[str]] = None, lowercase: bool = False) -> str:
    v = (value or "").strip()

    # Optionally convert to lowercase
    if lowercase:
        v = v.lower()

    # Drop tokens literally, anywhere they appear
    if drop_tokens:
        for tok in sorted({t for t in drop_tokens if t}, key=len, reverse=True):
            v = re.sub(re.escape(tok.lower()), "", v, flags=re.IGNORECASE)

    # Replace non-alnum with underscore
    # Preserve uppercase if lowercase=False
    if lowercase:
        v = re.sub(r"[^a-z0-9]+", "_", v)
    else:
        v = re.sub(r"[^a-zA-Z0-9]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")

    if not v:
        return "material"
    # Check if starts with letter (case-insensitive if preserving case)
    if lowercase:
        if not re.match(r"^[a-z]", v):
            v = f"m_{v}"
    else:
        if not re.match(r"^[a-zA-Z]", v):
            v = f"m_{v}"
    return v