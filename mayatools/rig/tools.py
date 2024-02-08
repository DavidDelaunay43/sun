from ...utils.imports import *

def rivet_geo():
    '''
    '''

    rivet, geo = cmds.ls(selection = True)
    cmds.select(clear = True)
    bind = cmds.joint(name = rivet.replace('rivet', 'ctrl'))
    cmds.matchTransform(bind, rivet)
    cmds.parent(bind, rivet)
    cmds.makeIdentity(bind, apply = True, t=1, r=1)
    cmds.skinCluster(bind, geo, mi=1)

def create_blendshapes(bshape_prefix: str):
    '''
    '''

    for geo in cmds.ls(sl=1):
        
        shape = cmds.listRelatives(geo, shapes = True)[0]
        skin_cluster = cmds.listConnections(shape, type='skinCluster', connections = True)[-1]
        
        deform_geo = f'{bshape_prefix}{geo}'
        bshape_node = cmds.blendShape(deform_geo, geo, name = f'BShape_{geo}')[0]
        cmds.setAttr(bshape_node + '.' + deform_geo, 1)
        cmds.setAttr(f'{bshape_node}.{deform_geo}', 1)
        cmds.reorderDeformers(skin_cluster, bshape_node)
