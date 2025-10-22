import hou

### RBL KB3D Converter_v001 (copied to V3)

###SET DEFAULT VALUES, NO SPACES ALLOWED####
default_matlib_name = "Converted_Material_Library"
default_basecol_name = "basecolor"
default_metallic_name = "metallic"
default_roughness_name = "roughness"
default_normal_name = "normal"
default_displacement_name = "height"
default_emission_name = "emissive"
default_opacity_name = "opacity"
default_transmission_name = "refraction"


# Keeping original function for compatibility
from tools.material_tools.TexToMtlX_V2.KB3D_converter import run_kb3d_converter  # re-export legacy entrypoint
