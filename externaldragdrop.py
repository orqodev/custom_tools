import hou
import os
from modules import misc_utils
from tools import lops_asset_builder as lab


def dropAccept(file_list):
    # Quick import for houdini files
    extensions = [".hip",".hiplc","bgeo.sc"]
    if len(file_list) == 1 and os.path.splitext(file_list[0])[1] in extensions:
        hou.hipFile.merge(file_list[0])
    is_solaris_active =  misc_utils._is_in_solaris()
    if is_solaris_active:
        lab.create_component_builder(file_list[0])
    return True