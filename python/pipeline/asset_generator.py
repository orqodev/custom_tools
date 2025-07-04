import hou

from tools import batch_importer


class AssetGenerator:
    def __init__(self):
        self.select_directory = None
        self.files_name = []

    def run_asset_generator(self):
        obj = hou.node('/obj')
        geo_node = obj.createNode('geo', node_name='batch_import')
        self.batch_import()

        

    def batch_import(self):
        default_directory = f"{hou.text.expandString('$HIP')}"
        self.select_directory = hou.ui.selectFile(start_directory=default_directory,
                                             title="Select the files you want to import",
                                             file_type=hou.fileType.AnyFile, multiple_select=True)
        if self.select_directory:
            self.files_name = self.select_directory.split(';')
        else:
            hou.ui.displayMessage("No file selected, please select a file to import.")
            return
        
        
        

        
        
        
            
            