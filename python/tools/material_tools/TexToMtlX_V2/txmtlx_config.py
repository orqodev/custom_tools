"""
TexToMtlX Configuration Constants
Centralized configuration for texture processing and MaterialX creation
"""
import re
import os

# Text to display in the help menu

TEXT_TO_DISPLAY =  """
                        Instructions\n\n\nSupports textures with  and without UDIMs.
                        \nMATERIAL_TEXTURE_UDIM or MATERIAL_TEXTURE 
                        \nFor Example: tires_Alb_997.tif or tires_Alb_tif
                        \nNaming Convention for the textures:
                        \nColor: diffuse, diff, albedo, alb, base, col, color, basecolor,
                        \nMetal: diffuse, metalness, metal, mlt, met,
                        \nSpecular: specular, specularity, spec, spc,
                        \nRoughness: roughness, rough, rgh,
                        \nTransmission: transmission, transparency, trans,
                        \nSSS: transluncecy, sss,
                        \nEmission: emission, emissive, emit, emm,
                        \nOpacity: opacity, opac, alpha,
                        \nAmbient: ambient_occlusion, ao, occlusion, cavity,
                        \nBump: bump, bmp,
                        \nHeight: Displacement,displace, disp, dsp, heightmap, height,
                        \nExtra: user, mask,
                        \nNormal: normal, nor, nrm, nrml, norm,
                        """

# Supported texture file extensions
TEXTURE_EXT = {
    ".jpg", ".jpeg", ".png", ".tga", ".bmp", ".tiff", ".tif", 
    ".exr", ".hdr", ".hdri", ".dpx", ".pic", ".rat", ".tx"
}
SKIP_KEYS = {'UDIM', 'Size', 'FOLDER_PATH', 'normal', 'bump'}

NAMING_MAP = {
    'color': {'input': 'base_color', 'label': 'basecolor_tex'},
    'metal': {'input': 'metalness', 'label': 'metalness_tex'},
    'rough': {'input': 'specular_roughness', 'label': 'roughness_tex'},
    'specular': {'input': 'specular', 'label': 'specular_tex'},
    'gloss': {'input': 'specular_roughness', 'label': 'gloss_tex'},
    'emission': {'input': 'emission', 'label': 'emission_tex'},
    'alpha': {'input': 'opacity', 'label': 'opacity_tex'},
    'transmission': {'input': 'transmission', 'label': 'transmission_tex'},
    'sss': {'input': 'subsurface_color', 'label': 'sss_tex'},
    'displacement': {'input': None, 'label': 'displacement_tex'},
    'normal': {'input': None, 'label': 'normal_tex'},
    'bump': {'input': None, 'label': 'bump_tex'},
    'ao': {'input': None, 'label': 'ao_tex'},
    'mask': {'input': None, 'label': 'mask_tex'},
}

# Texture type mappings with priorities and detection patterns
TEXTURE_TYPE =  [
    "diffuse", "diff", "albedo", "alb", "base", "col", "color", "basecolor",
    "metalness", "metal", "mlt", "met","metallic",
    "specular", "specularity", "spec", "spc",
    "roughness", "rough", "rgh",
    "transmission", "transparency", "trans",
    "translucency", "sss",
    "emission", "emissive", "emit", "emm",
    "opacity", "opac", "alpha",
    "ambient_occlusion", "ao", "occlusion", "cavity",
    "bump", "bmp",
    "displacement", "height", "displace", "disp", "dsp", "heightmap",
    "user", "mask",
    "normal", "nor", "nrm", "nrml", "norm"
]

# Sorted texture types by priority for consistent processing order
TEXTURE_TYPE_SORTED = {
'texturesColor': ["diffuse", "diff", "albedo", "alb", "base", "col", "color", "basecolor"],
"texturesMetal": ["metalness", "metal", "mlt", "met", "metallic"],
"texturesSpecular": ["specular", "specularity", "spec", "spc"],
"texturesRough": ["roughness", "rough", "rgh"],
"texturesTrans": ["transmission", "transparency", "trans"],
"texturesGloss": ["gloss", "glossy", "glossiness"],
"texturesEmm": ["emission", "emissive", "emit", "emm"],
"texturesAlpha": ["opacity", "opac", "alpha"],
"texturesAO": ["ambient_occlusion", "ao", "occlusion", "cavity"],
"texturesBump": ["bump", "bmp", "height"],
"texturesDisp": ["displacement", "displace", "disp", "dsp", "heightmap"],
"texturesExtra": ["user", "mask"],
"texturesNormal": ["normal", "nor", "nrm", "nrml", "norm"],
"texturesSSS": ["translucency"]
}

# Size detection pattern for resolution parsing
# Match only 1–2 digit K sizes (e.g., 1k, 2K, 8k, 16k). Avoid plain numbers and UDIMs.
SIZE_PATTERN = re.compile(r'(?i)(?:^|[_-])(\d{1,2}k)\b')
UDIM_PATTERN = re.compile(r'(?:_)?(\d{4}())')


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
MAX_WORKERS = os.cpu_count()

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
