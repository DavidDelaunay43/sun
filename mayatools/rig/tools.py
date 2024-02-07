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