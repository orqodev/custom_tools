import hou


def batch_importer():
    # Declaring Variables
    default_directory = f"{hou.text.expandString('$HIP')}"
    select_directory = hou.ui.selectFile(start_directory=default_directory,
                                         title="Select the files you want to import",
                                         file_type=hou.fileType.Geometry,
                                         multiple_select=True)


    def create_transformer_node(set_scale=False, scale_value=None, input_node=None):
        transform_node = geo_node.createNode('xform', node_name=asset_name + 'x_form')
        if set_scale:
            transform_node.parm('scale').set(scale_value)
        transform_node.setInput(0, input_node)
        return transform_node


    if select_directory:
        files_name = select_directory.split(';')
        obj = hou.node('/obj')
        geo_node = obj.createNode('geo', node_name='temp_geo')

        merge_node = geo_node.createNode('merge', node_name='mergeAll')
        add_to_merge = 0

        for file_name in files_name:
            file_name = file_name.strip()
            asset = file_name.split('/')

            object = asset[-1].split('.')

            asset_type = object[1]
            asset_name = object[0]
            new_file_loader = None
            transform_node = None
            set_scale = False

            button_pressed, scale_value = hou.ui.readInput(
                f"Do you want to change the scale of {asset_name}.{asset_type}? Please insert the scale if you need it.",
                buttons=("Yes", "No")
            )

            if button_pressed == 0:
                set_scale = True

            if asset_type == "abc":
                new_alembic_loader = geo_node.createNode('alembic', node_name=asset_name)
                new_alembic_loader.parm('fileName').set(file_name)
                unpack_node = geo_node.createNode('unpack', node_name=asset_name + 'unpack')
                unpack_node.setInput(0, new_alembic_loader)
                transform_node = create_transformer_node(set_scale, scale_value, unpack_node)
            else:
                new_file_loader = geo_node.createNode('file', node_name=asset_name)
                new_file_loader.parm('file').set(file_name)
                transform_node = create_transformer_node(set_scale, scale_value, new_file_loader)

            material_node = geo_node.createNode('material', node_name=object[0] + '_mat')
            material_node.setInput(0, transform_node)
            merge_node.setInput(add_to_merge, material_node)
            add_to_merge += 1

        geo_node.layoutChildren()

    else:
        hou.ui.displayMessage("Please, check again. No valid file was selected", buttons=('OK',))





