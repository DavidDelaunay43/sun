from maya import cmds


def ensure_list(arg):

    if isinstance(arg, str):
        return [arg]
    else:
        return arg


def lock_attributes(nodes: list, attributes: list):
    '''
    '''

    nodes = ensure_list(nodes)

    for node in nodes:
        for attribute in attributes:
            cmds.setAttr(f'{node}.{attribute}', lock = True)


def create_locators():
    '''
    '''

    loc_root = 'loc_root'
    loc_chest = 'loc_chest'
    
    loc_clavicle = 'loc_clavicle'
    loc_shoulder = 'loc_shoulder'
    loc_elbow = 'loc_elbow'
    loc_wrist = 'loc_wrist'

    loc_leg = 'loc_leg'
    loc_knee = 'loc_knee'
    loc_ankle = 'loc_ankle'
    loc_ball = 'loc_ball'
    lot_toe = 'loc_toe'

    locs = {
        loc_root: (0.0, 15.0, 0.0),
        loc_chest: (0.0, 20.0, 0.0),
        loc_clavicle: (0.0, 19.0, 0.0),
        loc_shoulder: (1.0, 20.0, 0.0),
        loc_elbow: (7.0, 20.0, 0.0),
        loc_wrist: (13.0, 20.0, 0.0),
        loc_leg: (0.0, 15.0, 0.0),
        loc_knee: (0.0, 8.0, 0.0),
        loc_ankle: (0.0, 1.0, 0.0),
        loc_ball: (0.5, 0.2, 1.5),
        lot_toe: (0.5, 0.2, 4.0)
    }
    
    gloabl_grp = cmds.group(empty = True, world = True, name = 'Global_locs')

    for loc, transforms in locs.items():
        cmds.spaceLocator(name = loc)
        cmds.setAttr(f'{loc}.t', *transforms)
        cmds.parent(loc, gloabl_grp)
        lock_attributes(loc, ['sx', 'sy', 'sz'])

        if loc not in ('loc_root', 'loc_chest'):
            cmds.setAttr(f'{loc}.displayLocalAxis', True)

    # spine locs
    cmds.parent(loc_chest, loc_root)
    lock_attributes(loc_chest, ['tx', 'tz'])

    # arm locs
    cmds.parent(loc_elbow, loc_shoulder)
    cmds.parent(loc_wrist, loc_elbow)

    lock_attributes(loc_shoulder, ['rx', 'ry'])
    lock_attributes(loc_elbow, ['ty', 'rx', 'ry', 'rz'])
    lock_attributes(loc_wrist, ['ty'])

    # leg locs

    cmds.select(clear = True)

    # expression locs
    string = f'''
    {loc_wrist}.tz = {loc_elbow}.tz * -1;
    {loc_ankle}.tz = {loc_knee}.tz * -1;
    '''
    cmds.expression(name = 'Exp_locs', string = string)


create_locators()
