from maya import cmds

def delete_color_sets():

    color_set_nodes = cmds.ls(type = 'createColorSet')
    if not color_set_nodes:
        return
    
    