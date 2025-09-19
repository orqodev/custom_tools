"""
TexToMtlX Configuration Constants
Centralized configuration for texture processing and MaterialX creation
"""
import re

# Supported texture file extensions
TEXTURE_EXT = {
    ".jpg", ".jpeg", ".png", ".tga", ".bmp", ".tiff", ".tif", 
    ".exr", ".hdr", ".hdri", ".dpx", ".pic", ".rat", ".tx"
}

# Texture type mappings with priorities and detection patterns
TEXTURE_TYPE = {
    "color": {
        "tokens": ["_BaseColor", "_Diffuse", "_Albedo", "_Color", "_Col", "_Diff", "_basecolor", "_diffuse", "_albedo", "_color", "_col", "_diff"],
        "priority": 1,
        "description": "Base Color / Diffuse maps"
    },
    "metal": {
        "tokens": ["_Metallic", "_Metal", "_Met", "_metallic", "_metal", "_met"],
        "priority": 2,
        "description": "Metallic maps"
    },
    "rough": {
        "tokens": ["_Roughness", "_Rough", "_roughness", "_rough", "_R"],
        "priority": 3,
        "description": "Roughness maps"
    },
    "specular": {
        "tokens": ["_Specular", "_Spec", "_specular", "_spec"],
        "priority": 4,
        "description": "Specular maps"
    },
    "gloss": {
        "tokens": ["_Glossiness", "_Gloss", "_glossiness", "_gloss"],
        "priority": 5,
        "description": "Glossiness maps"
    },
    "normal": {
        "tokens": ["_Normal", "_Norm", "_NRM", "_normal", "_norm", "_nrm"],
        "priority": 6,
        "description": "Normal maps"
    },
    "bump": {
        "tokens": ["_Bump", "_bump"],
        "priority": 7,
        "description": "Bump maps"
    },
    "displacement": {
        "tokens": ["_Displacement", "_Height", "_Disp", "_displacement", "_height", "_disp"],
        "priority": 8,
        "description": "Displacement / Height maps"
    },
    "emission": {
        "tokens": ["_Emission", "_Emissive", "_Emm", "_Emit", "_emission", "_emissive", "_emm", "_emit"],
        "priority": 9,
        "description": "Emission maps"
    },
    "alpha": {
        "tokens": ["_Opacity", "_Alpha", "_opacity", "_alpha"],
        "priority": 10,
        "description": "Opacity / Alpha maps"
    },
    "transmission": {
        "tokens": ["_Transmission", "_Trans", "_Refraction", "_transmission", "_trans", "_refraction"],
        "priority": 11,
        "description": "Transmission maps"
    },
    "sss": {
        "tokens": ["_SubsurfaceColor", "_SSS", "_Subsurface", "_subsurfacecolor", "_sss", "_subsurface"],
        "priority": 12,
        "description": "Subsurface Scattering maps"
    },
    "ao": {
        "tokens": ["_AO", "_AmbientOcclusion", "_ambient_occlusion", "_ao", "_Occlusion", "_occlusion", "_Cavity", "_cavity"],
        "priority": 13,
        "description": "Ambient Occlusion maps"
    },
    "mask": {
        "tokens": ["_Mask", "_mask", "_ID", "_id", "_MatID", "_matid"],
        "priority": 14,
        "description": "Mask/ID maps"
    }
}

# Sorted texture types by priority for consistent processing order
TEXTURE_TYPE_SORTED = sorted(TEXTURE_TYPE.items(), key=lambda x: x[1]["priority"])

# Size detection pattern for resolution parsing
# Match only 1–2 digit K sizes (e.g., 1k, 2K, 8k, 16k). Avoid plain numbers and UDIMs.
SIZE_PATTERN = re.compile(r'(?i)(?:^|[_-])(\d{1,2}k)\b')

# Default drop tokens for material name sanitization
DEFAULT_DROP_TOKENS = [
    # Resolution indicators
    "1K", "2K", "4K", "8K", "16K", "1k", "2k", "4k", "8k", "16k",
    "512", "1024", "2048", "4096", "8192", "16384",
    
    # Common suffixes
    "_Mat", "_Material", "_mat", "_material", "_Mtl", "_mtl",
    
    # Version indicators  
    "_v1", "_v2", "_v3", "_v01", "_v02", "_v03", "_V1", "_V2", "_V3",
    "_001", "_002", "_003", "_final", "_Final", "_FINAL",
    
    # Quality indicators
    "_High", "_Med", "_Low", "_high", "_med", "_low", "_HD", "_SD",
    
    # Source indicators
    "_Substance", "_substance", "_SP", "_Designer", "_Painter",
    "_Quixel", "_Megascans", "_MS", "_Bridge",
    
    # Common separators that should be cleaned
    "__", "---", "___"
]

# Worker thread configuration
WORKER_FRACTION = 0.5  # Use 50% of available CPU cores for TX conversion

# Default imaketx path (can be overridden by user)
DEFAULT_IMAKETX_PATH = "imaketx"

# Material library settings
DEFAULT_MATLIB_PREFIX = "/ASSET/mtl/"
MATLIB_NAME_PREFIX = "MaterialLibrary"

# UI Configuration
UI_CONFIG = {
    "window_title": "TexToMtlX v2.0",
    "window_size": (600, 800),
    "default_spacing": 10,
    "button_height": 30,
    "group_margin": 5
}

# Renderer configurations
RENDERER_CONFIG = {
    "karma": {
        "name": "Karma",
        "enabled_by_default": True,
        "material_builder_type": "subnet",
        "surface_shader": "mtlxstandard_surface",
        "render_context": "mtlx"
    },
    "arnold": {
        "name": "Arnold",
        "enabled_by_default": False,  # Only if detected
        "material_builder_type": "arnold_materialbuilder", 
        "surface_shader": "standard_surface",
        "render_context": "arnold",
        "detection_paths": ["htoa"]  # Look for these in hou.houdiniPath()
    }
}

# Colorspace mappings for different renderers
COLORSPACE_CONFIG = {
    "karma": {
        "color": {"signature": "color3", "colorspace": "srgb_texture"},
        "color_hdr": {"signature": "color3", "colorspace": "scene_linear"},
        "data": {"signature": "default", "colorspace": "raw"},
        "normal": {"signature": "vector3", "colorspace": "raw"}
    },
    "arnold": {
        "color": {"color_family": "Utility", "color_space": "sRGB - Texture"},
        "color_hdr": {"color_family": "ACES", "color_space": "ACEScg"},
        "data": {"color_family": "ACES", "color_space": "ACEScg"},
        "normal": {"color_family": "Utility", "color_space": "Raw"}
    }
}

# Displacement configuration
DISPLACEMENT_CONFIG = {
    "default_scale": 0.1,
    "default_remap_low": -0.5,
    "default_remap_high": 0.5,
    "enable_remap_by_default": False
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "tx_conversion_logger": "TX_CONVERSION"
}

# Error handling
ERROR_CONFIG = {
    "max_retry_attempts": 3,
    "retry_delay": 1.0,  # seconds
    "show_detailed_errors": True
}

# File validation
VALIDATION_CONFIG = {
    "min_file_size": 1024,  # bytes
    "max_file_size": 1024 * 1024 * 1024,  # 1GB
    "check_file_permissions": True,
    "verify_image_headers": False  # Can be slow for large directories
}

def get_texture_tokens():
    """Get flattened list of all texture detection tokens"""
    tokens = []
    for texture_type, config in TEXTURE_TYPE.items():
        tokens.extend(config["tokens"])
    return tokens

def get_renderer_names():
    """Get list of available renderer names"""
    return list(RENDERER_CONFIG.keys())

def is_hdr_extension(extension):
    """Check if file extension indicates HDR format"""
    hdr_extensions = {".exr", ".hdr", ".hdri", ".tif", ".tiff"}
    return extension.lower() in hdr_extensions

def is_ldr_extension(extension):
    """Check if file extension indicates LDR format"""
    ldr_extensions = {".jpg", ".jpeg", ".png", ".tga", ".bmp"}
    return extension.lower() in ldr_extensions

# --- Extend token lists with additional aliases from tool instructions ---
# Supports textures named like MATERIAL_TEXTURE_UDIM or MATERIAL_TEXTURE (with/without UDIMs)
# The following aliases are appended to cover more naming conventions in the wild.
try:
    # Color
    TEXTURE_TYPE['color']['tokens'].extend([
        '_base', '_col', '_color', '_basecolor', '_diffuse', '_diff', '_albedo', '_alb'
    ])
    # Metal
    TEXTURE_TYPE['metal']['tokens'].extend([
        '_metalness', '_mlt', '_met'
    ])
    # Specular
    TEXTURE_TYPE['specular']['tokens'].extend([
        '_specularity', '_spc', '_spec'
    ])
    # Roughness
    TEXTURE_TYPE['rough']['tokens'].extend([
        '_roughness', '_rough', '_rgh'
    ])
    # Transmission
    TEXTURE_TYPE['transmission']['tokens'].extend([
        '_transmission', '_transparency', '_trans'
    ])
    # SSS
    TEXTURE_TYPE['sss']['tokens'].extend([
        '_transluncecy', '_translucency', '_sss'
    ])
    # Emission
    TEXTURE_TYPE['emission']['tokens'].extend([
        '_emission', '_emissive', '_emit', '_emm'
    ])
    # Opacity
    TEXTURE_TYPE['alpha']['tokens'].extend([
        '_opacity', '_opac', '_alpha'
    ])
    # Ambient/AO
    TEXTURE_TYPE['ao']['tokens'].extend([
        '_ambient_occlusion', '_ao', '_occlusion', '_cavity'
    ])
    # Mask/ID
    TEXTURE_TYPE['mask']['tokens'].extend([
        '_mask', '_id', '_matid'
    ])
    # Bump
    TEXTURE_TYPE['bump']['tokens'].extend([
        '_bump', '_bmp'
    ])
    # Displacement / Height
    TEXTURE_TYPE['displacement']['tokens'].extend([
        '_displacement', '_displace', '_disp', '_dsp', '_heightmap', '_height'
    ])
    # Normal
    TEXTURE_TYPE['normal']['tokens'].extend([
        '_normal', '_nor', '_nrm', '_nrml', '_norm'
    ])
except Exception:
    # If structure changed, ignore silently to avoid breaking runtime
    pass