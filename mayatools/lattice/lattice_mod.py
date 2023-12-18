from ...utils.imports import *

def lattice_points():
    '''
    '''

    point_list = []
    for i in range(2):
        for j in range(2):
            for k in range(2):
                point_list.append(f"[{i}][{j}][{k}]")
    return point_list

def constraint_points(lattice_shape: str):
    '''
    '''

    points = lattice_points()
    for i, point in enumerate(points):
        master_grp = cmds.group(empty = True, name = f'master_{i:02}', world = True)
        coord = cmds.xform(f'{lattice_shape}.pt{point}', query = True, translation = True, worldSpace = True)
        cmds.setAttr(f'{master_grp}.t', *coord)
        cmds.connectAttr(f'{master_grp}.t', f'{lattice_shape}.controlPoints[{i}]')
