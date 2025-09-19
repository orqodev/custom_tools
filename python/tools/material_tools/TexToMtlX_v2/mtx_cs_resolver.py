"""
MaterialX Colorspace Resolver and Utilities
Provides colorspace detection, UDIM handling, and texture semantic analysis
"""
import re
import os
from pathlib import Path

# UDIM pattern for detecting UDIM sequences (1001-2999)
UDIM_PATTERN = re.compile(r'\b(10[0-9][0-9]|1[1-9][0-9][0-9]|2[0-9][0-9][0-9])\b')

# Texture type detection patterns
COLOR_TOKENS = {
    'basecolor', 'base_color', 'diffuse', 'albedo', 'color', 'col', 'diff', 
    'basecolour', 'base_colour', 'subsurface', 'sss', 'emission', 'emissive', 
    'emm', 'emit'
}

DATA_TOKENS = {
    'metallic', 'metal', 'met', 'roughness', 'rough', 'r', 'specular', 'spec',
    'glossiness', 'gloss', 'transmission', 'trans', 'opacity', 'alpha', 'ao',
    'ambient_occlusion', 'occlusion', 'height', 'displacement', 'disp', 'mask', 'matid', 'id'
}

NORMAL_TOKENS = {
    'normal', 'norm', 'nrm', 'bump'
}

# Colorspace override patterns (filename-based)
COLORSPACE_OVERRIDES = {
    'srgb': 'srgb_texture',
    'linear': 'scene_linear',
    'lin': 'scene_linear',
    'acescg': 'acescg',
    'raw': 'raw',
    'data': 'raw'
}

def guess_semantics_and_colorspace(tex_name, file_path):
    """
    Analyze texture filename and path to determine semantics and colorspace
    
    Args:
        tex_name (str): Texture type identifier (e.g., 'color', 'metal')
        file_path (str): Full path to the texture file
        
    Returns:
        tuple: (signature, filecolorspace, is_data, is_normal)
            signature: MaterialX node signature ('color3', 'default', 'vector3', 'float')
            filecolorspace: Colorspace string ('srgb_texture', 'scene_linear', 'raw')
            is_data: Boolean indicating if this is data/non-color texture
            is_normal: Boolean indicating if this is a normal map
    """
    
    # Extract filename and extension
    filename = os.path.basename(file_path).lower()
    name_without_ext, ext = os.path.splitext(filename)
    
    # Check for filename-based colorspace overrides
    for override_key, colorspace in COLORSPACE_OVERRIDES.items():
        if override_key in name_without_ext:
            if override_key in ['raw', 'data']:
                return 'default', colorspace, True, False
            elif override_key in ['srgb']:
                return 'color3', colorspace, False, False
            else:  # linear, acescg
                return 'color3', colorspace, False, False
    
    # Determine if this is a normal map
    is_normal = any(token in name_without_ext for token in NORMAL_TOKENS)
    if is_normal:
        return 'vector3', 'raw', True, True
    
    # Determine if this is data (non-color) texture
    is_data = any(token in name_without_ext for token in DATA_TOKENS)
    
    # Check texture type from MaterialX naming convention
    if tex_name in ['color', 'sss', 'emission']:
        is_data = False
    elif tex_name in ['metal', 'rough', 'specular', 'gloss', 'transmission', 'alpha', 'displacement']:
        is_data = True
    elif tex_name in ['normal', 'bump']:
        is_normal = True
        is_data = True
    
    # Determine colorspace based on file extension and content type
    if is_normal:
        return 'vector3', 'raw', True, True
    elif is_data:
        return 'default', 'raw', True, False
    else:
        # Color texture - check if HDR format
        hdr_extensions = {'.exr', '.hdr', '.hdri', '.tif', '.tiff'}
        ldr_extensions = {'.jpg', '.jpeg', '.png', '.tga', '.bmp'}
        
        if ext in hdr_extensions:
            return 'color3', 'scene_linear', False, False
        elif ext in ldr_extensions:
            return 'color3', 'srgb_texture', False, False
        else:
            # Default to sRGB for unknown color formats
            return 'color3', 'srgb_texture', False, False

def case_insensitive_replace(haystack, needle, replacement):
    """
    Perform case-insensitive string replacement
    
    Args:
        haystack (str): String to search in
        needle (str): String to find
        replacement (str): String to replace with
        
    Returns:
        str: String with replacements made
    """
    if not needle or not haystack:
        return haystack
    
    # Use regex with IGNORECASE flag for case-insensitive replacement
    pattern = re.compile(re.escape(needle), re.IGNORECASE)
    return pattern.sub(replacement, haystack)

def detect_udim_in_path(file_path):
    """
    Check if a file path contains UDIM pattern
    
    Args:
        file_path (str): Path to check
        
    Returns:
        bool: True if UDIM pattern found
    """
    return bool(UDIM_PATTERN.search(file_path))

def replace_udim_token(file_path):
    """
    Replace first UDIM token with <UDIM> placeholder
    
    Args:
        file_path (str): Path containing UDIM token
        
    Returns:
        str: Path with <UDIM> placeholder
    """
    return UDIM_PATTERN.sub('<UDIM>', file_path, count=1)

def get_texture_semantic_type(filename):
    """
    Determine semantic type of texture from filename
    
    Args:
        filename (str): Texture filename
        
    Returns:
        str: Semantic type ('color', 'data', 'normal')
    """
    filename_lower = filename.lower()
    
    if any(token in filename_lower for token in NORMAL_TOKENS):
        return 'normal'
    elif any(token in filename_lower for token in DATA_TOKENS):
        return 'data'
    elif any(token in filename_lower for token in COLOR_TOKENS):
        return 'color'
    else:
        # Default based on common patterns
        return 'color'

def normalize_job_path(folder_path, project_path):
    """
    Replace project path with $JOB variable in a case-insensitive manner
    
    Args:
        folder_path (str): Full folder path
        project_path (str): Project root path to replace
        
    Returns:
        str: Path with $JOB substitution
    """
    if not project_path or not folder_path:
        return folder_path
    
    return case_insensitive_replace(folder_path, project_path, "$JOB")


def slugify(value: str) -> str:
    """
    Create a safe, canonical identifier from a string.
    - lower-case
    - remove trailing UDIM tokens (e.g., _1001)
    - replace non-alphanumeric with underscores
    - collapse multiple underscores
    - trim leading/trailing underscores
    Returns 'material' if empty after cleaning.
    """
    if value is None:
        value = ""
    v = str(value)
    # remove UDIM style suffix to avoid leaking frame tokens into names
    v = re.sub(r"[_\.]?(?:10[0-9]{2}|1[1-9][0-9]{2}|2[0-9]{3})$", "", v)
    v = v.strip().lower()
    v = re.sub(r"[^0-9a-zA-Z]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")
    return v or "material"