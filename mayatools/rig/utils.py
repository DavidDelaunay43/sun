from maya import cmds, mel

def auto_blendshape(prefix: str = ''):
    
    for geo in cmds.ls(selection = True):
        base_geo = f'{prefix}_{geo}'
        cmds.select(base_geo, geo, replace = True)
        mel.eval(f'blendShape -automatic -n "BShape_{geo}";')
        cmds.setAttr('BShape_' + geo + '.' + base_geo, 1)
        cmds.select(clear = True)
