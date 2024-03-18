import maya.cmds as cmds
from typing import Literal

def find_alembic_node(node: str):
    
    shape = cmds.listRelatives(node, shapes = True, fullPath = True)
    if not shape:
        cmds.error(f'No shape found under : {node}')
    shape = shape[0]
    list = cmds.listConnections(shape)
    for item in list:
        if cmds.nodeType(item) == 'AlembicNode':
            return item
        
    cmds.error(f'Found no alembic node connected to : {shape}')

def offset_alembic(alembic_node: str, fps: Literal["24 fps", "16fps", "12fps", "8fps", "6fps"] = "24 fps"):

    fps_dict = {
        "24 fps": 1, 
        "16fps": 1.5, 
        "12fps": 2, 
        "8fps": 3, 
        "6fps": 4
    }

    old_expression_node = cmds.listConnections(alembic_node, type = 'expression')
    if old_expression_node:
        cmds.delete(old_expression_node)

    fps_factor: int = fps_dict[fps]
    exp_string: str = f'offset = frame % {fps_factor};'
    cmds.expression(object = alembic_node, string = exp_string)
    print(f'Alembic node : {alembic_node} switched on {fps}')

class FpsWindow():

    def __init__(self):

        self.title = "Change FPS"

        if cmds.workspaceControl(self.title, exists = True): 
            cmds.workspaceControl(self.title, edit = True, floating = True) 
            cmds.deleteUI(self.title, window = True)
        
        cmds.workspaceControl(self.title, retain = False, floating = False, height = 110, width = 300)
        cmds.columnLayout(adjustableColumn = True)
        self.fps_menu = cmds.textScrollList(allowMultiSelection = False, height = 80, append = ("24 fps", "16fps", "12fps", "8fps", "6fps"), selectItem = '24 fps' )

        cmds.button(label = "OK", command = self.changefps)
        cmds.showWindow(self.title)

    def changefps(self, button):

        fps_selection = cmds.textScrollList(self.fps_menu, query=True, si = True)
        fps_selection = fps_selection[0]

        selection: list = cmds.ls(selection = True)

        for node in selection:

            alembic_node = find_alembic_node(node)
            offset_alembic(alembic_node, fps = fps_selection)

        cmds.select(clear = True)

FpsWindow()
