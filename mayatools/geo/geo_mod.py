from ...utils.imports import *

def create_cube_under_joint(joint: str):
    '''
    '''
    
    cube = cmds.polyCube(constructionHistory = False, name = f'cube_{joint}')[0]
    cmds.matchTransform(cube, joint, position = True, rotation = True)
    cmds.parent(cube, joint)
    
def create_cubes_under_joints(joints: list):
    '''
    '''
    
    for joint in joints:
        create_cube_under_joint(joint)
        

nodes = cmds.ls(selection = True)
create_cubes_under_joints(nodes)