from ...utils.imports import *

def matrix_to_translation(matrix: om.MMatrix):
    transform_matrix = om.MTransformationMatrix(matrix)
    translation = transform_matrix.translation(om.MSpace.kWorld)
    return translation

def matrix_to_euler(matrix: om.MMatrix) -> om.MEulerRotation:
    transform_matrix = om.MTransformationMatrix(matrix)
    rotation = transform_matrix.rotation()
    euler_rotation_degrees = om.MEulerRotation(
        om.MAngle(rotation.x).asDegrees(),
        om.MAngle(rotation.y).asDegrees(),
        om.MAngle(rotation.z).asDegrees()
    )
    return euler_rotation_degrees

def transfert_rotation_by_matrix(source_node: str, destination_node: str):
    target_world_mtx = om.MMatrix(cmds.getAttr(f"{destination_node}.worldMatrix[0]"))
    master_world_inverse_mtx = om.MMatrix(cmds.getAttr(f"{source_node}.worldInverseMatrix[0]"))
    offset_mtx = target_world_mtx * master_world_inverse_mtx

    offset_mtx = offset_mtx.inverse()

    euler_rotation = matrix_to_euler(offset_mtx)
    cmds.setAttr(f'{destination_node}.r', *euler_rotation)

def fk_to_ik(fk_nodes: tuple, ik_nodes: tuple, switch_node: str, namespace: str = None):
    """
    """

    fk_end, loc_pv = fk_nodes
    ctrl_end, pv = ik_nodes

    if 'ankle' in fk_end:
        fk_end = f'{fk_end}_match'

    if not cmds.objExists(switch_node):
        fk_end, loc_pv = f'{namespace}:{fk_end}', f'{namespace}:{loc_pv}'
        ctrl_end, pv = f'{namespace}:{ctrl_end}', f'{namespace}:{pv}'
        switch_node = f'{namespace}:{switch_node}'

    cmds.setAttr(f'{switch_node}.switch', 1) # switch en mode ik

    cmds.matchTransform(ctrl_end, fk_end, position = True)
    transfert_rotation_by_matrix(fk_end, ctrl_end)
    cmds.matchTransform(pv, loc_pv, position = True)

def ik_to_fk(ik_nodes: tuple, fk_nodes: tuple, switch_node: str, namespace: str = None):
    """
    """

    drv_start, drv_mid, ctrl_end = ik_nodes
    fk_start, fk_mid, fk_end = fk_nodes

    if 'leg' in ctrl_end:
        ctrl_end = f'{ctrl_end}_match'
    print(ctrl_end, 'CTRL END')

    if not cmds.objExists(switch_node):
        drv_start, drv_mid, ctrl_end = f'{namespace}:{drv_start}', f'{namespace}:{drv_mid}', f'{namespace}:{ctrl_end}'
        fk_start, fk_mid, fk_end = f'{namespace}:{fk_start}', f'{namespace}:{fk_mid}', f'{namespace}:{fk_end}'
        switch_node = f'{namespace}:{switch_node}'

    r_start = cmds.getAttr(f'{drv_start}.r')[0]
    r_mid = cmds.getAttr(f'{drv_mid}.r')[0]

    cmds.setAttr(f'{switch_node}.switch', 0) # switch en mode fk

    # on transfert les rotations sur les deux premières articulations
    
    cmds.setAttr(f'{fk_start}.r', *r_start)
    cmds.setAttr(f'{fk_mid}.r', *r_mid)

    transfert_rotation_by_matrix(ctrl_end, fk_end)

fk_to_ik_arm_r = partial(fk_to_ik, fk_nodes = ('fk_wrist_R', 'loc_pv_arm_R'), ik_nodes = ('ctrl_arm_R', 'pv_arm_R'), switch_node = 'switch_arm_R')
fk_to_ik_arm_l = partial(fk_to_ik, fk_nodes = ('fk_wrist_L', 'loc_pv_arm_L'), ik_nodes = ('ctrl_arm_L', 'pv_arm_L'), switch_node = 'switch_arm_L')

fk_to_ik_leg_r = partial(fk_to_ik, fk_nodes = ('fk_ankle_R', 'loc_pv_leg_R'), ik_nodes = ('ctrl_leg_R', 'pv_leg_R'), switch_node = 'switch_leg_R')
fk_to_ik_leg_l = partial(fk_to_ik, fk_nodes = ('fk_ankle_L', 'loc_pv_leg_L'), ik_nodes = ('ctrl_leg_L', 'pv_leg_L'), switch_node = 'switch_leg_L')

ik_to_fk_arm_r = partial(ik_to_fk, ik_nodes = ('drv_arm_R', 'drv_elbow_R', 'ctrl_arm_R'), fk_nodes = ('fk_arm_R', 'fk_elbow_R', 'fk_wrist_R'), switch_node = 'switch_arm_R')
ik_to_fk_arm_l = partial(ik_to_fk, ik_nodes = ('drv_arm_L', 'drv_elbow_L', 'ctrl_arm_L'), fk_nodes = ('fk_arm_L', 'fk_elbow_L', 'fk_wrist_L'), switch_node = 'switch_arm_L')

ik_to_fk_leg_r = partial(ik_to_fk, ik_nodes = ('drv_leg_R', 'drv_knee_R', 'ctrl_leg_R'), fk_nodes = ('fk_leg_R', 'fk_knee_R', 'fk_ankle_R'), switch_node = 'switch_leg_R')
ik_to_fk_leg_l = partial(ik_to_fk, ik_nodes = ('drv_leg_L', 'drv_knee_L', 'ctrl_leg_L'), fk_nodes = ('fk_leg_L', 'fk_knee_L', 'fk_ankle_L'), switch_node = 'switch_leg_L')
