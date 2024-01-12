from ...utils.imports import *
from .. import (
    constants_maya,
    display,
    curve,
    matrix,
    attribute,
    offset,
    mathfuncs,
    vector,
    rig,
    ribbon,
    rivet,
    tools,
    joint
)
reload(constants_maya)
reload(display)
reload(curve)
reload(matrix)
reload(attribute)
reload(offset)
reload(mathfuncs)
reload(vector)
reload(rig)
reload(ribbon)
reload(rivet)
reload(tools)
reload(joint)
from ..constants_maya import *

def create_fk_arm(proxy_arm_jnt: str):
    '''
    '''

    cmds.select(clear = True)
    SIDE = tools.get_side_from_node(proxy_arm_jnt)

    duplicate_joints = cmds.duplicate(proxy_arm_jnt, renameChildren = True)
    cmds.parent(duplicate_joints[0], world = True)
    name_list = "arm", "elbow", "wrist"
    fk_joints = []

    for jnt, name in zip(duplicate_joints, name_list):

        jnt = cmds.rename(jnt, f'{FK}_{name}_{SIDE}')
        display.color_node(jnt, SIDE_COLOR[SIDE])

        circle = curve.octagon_control(normal = 'x')
        curve.parent_shapes([circle, jnt])

        fk_joints.append(jnt)

    joint.joint_to_transform(fk_joints, color = SIDE_COLOR[SIDE], op_mtx = True)

    cmds.parent(fk_joints[3], world = True)
    cmds.setAttr(f'{fk_joints[2]}.rz', 90)
    cmds.parent(fk_joints[3], fk_joints[2])
    offset.offset_parent_matrix(fk_joints[1:])

    offset.move_op_matrix(fk_joints[0])
    attribute.cb_attributes(fk_joints, ats = ['sx', 'sy', 'sz'], lock = True, hide = True)
    attribute.vis_no_keyable(fk_joints)
    
    tools.ensure_group(f'{fk_joints[0]}_{MOVE}', CTRLS)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Fk jnts done.')
    return fk_joints

def create_drv_arm(proxy_arm_jnt: str):
    '''
    '''

    cmds.select(clear = True)
    SIDE = tools.get_side_from_node(proxy_arm_jnt)

    duplicate_joints = cmds.duplicate(proxy_arm_jnt, renameChildren = True)
    name_list = "arm", "elbow", "wrist"
    drv_joints = []

    for jnt, name in zip(duplicate_joints, name_list):

        jnt = cmds.rename(jnt, f'{DRV}_{name}_{SIDE}')
        display.color_node(jnt, 'gold')
        cmds.setAttr(f'{jnt}.radius', 0.5)

        drv_joints.append(jnt)

    tools.ensure_group(drv_joints[0], JOINTS)

    offset.move_op_matrix(drv_joints[0])
    attribute.vis_no_keyable(drv_joints)

    # preserve
    preserve_joint = joint.create_preserve_jnt(drv_joints[0])
    tools.ensure_set(preserve_joint, set_name = 'bind_joints')

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Drv jnts done.')
    return drv_joints

def create_switch_node_arm(drv_jnts: list):
    '''
    '''

    cmds.select(clear = True)
    drv_arm, drv_elbow, _ = drv_jnts
    SIDE = tools.get_side_from_node(drv_arm)

    ctrl = f'switch_arm_{SIDE}'
    curve.star_control(name = ctrl, color = 'pink')

    cmds.matchTransform(ctrl, drv_arm, position = True)

    tools.ensure_group(ctrl, CTRLS)

    value = mathfuncs.distance_btw(drv_arm, drv_elbow) * 0.5
    x_value = value if SIDE == 'L' else value * -1
    y_value = value
    cmds.move(x_value, 0, 0, ctrl, relative = True)
    cmds.move(0, y_value, 0, ctrl, relative = True)
    offset.offset_parent_matrix(ctrl)

    attribute.sep_cb(ctrl, True)
    cmds.addAttr(ctrl, longName = 'switch', niceName = 'Switch', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)
    #cb_attributes(ctrl, lock = True, hide = True)
    attribute.vis_no_keyable(ctrl)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Switch node done.')
    return ctrl

def create_ik_setup_arm(drv_jnts: list):
    '''
    '''
    
    cmds.select(clear = True)
    drv_arm, drv_elbow, drv_wrist = drv_jnts
    SIDE = tools.get_side_from_node(drv_arm)

    ik = cmds.ikHandle(startJoint = drv_arm, endEffector = drv_wrist, solver = 'ikRPsolver', name = f'ik_arm_{SIDE}')[0]
    cmds.setAttr(f'{ik}.v', 0)

    ctrl_ik = curve.octagon_control(name = f'{CTRL}_arm_{SIDE}', normal = 'x', color = SIDE_COLOR[SIDE])
    cmds.matchTransform(ctrl_ik, drv_wrist, position = True, rotation = True)
    tools.ensure_group(ctrl_ik, CTRLS)
    offset.move_op_matrix(ctrl_ik)
    cmds.parent(ik, ctrl_ik)

    pole_vector = vector.pv_cal(drv_jnts)
    pole_vector = cmds.rename(pole_vector, f'pv_arm_{SIDE}')
    cmds.move(0, 0, mathfuncs.distance_btw(drv_arm, drv_elbow) * -1, pole_vector, relative = True)
    display.color_node(pole_vector, SIDE_COLOR[SIDE])
    tools.ensure_group(pole_vector, CTRLS)
    offset.move_op_matrix(pole_vector)
    cmds.poleVectorConstraint(pole_vector, ik)

    attribute.vis_no_keyable([ik, ctrl_ik, pole_vector])
    attribute.cb_attributes(pole_vector, ats = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'], lock = True, hide = True)
    attribute.cb_attributes(ctrl_ik, ats = ['sx', 'sy', 'sz'], lock = True, hide = True)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Ik setup arm done.')
    return ik, ctrl_ik, pole_vector

def create_ik_fk_setup_arm(proxy_arm_jnt: str, sub: int = 5):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_arm_jnt)
    cmds.select(clear = True)

    fk_joints = create_fk_arm(proxy_arm_jnt)
    drv_joints = create_drv_arm(proxy_arm_jnt)
    _, ctrl_ik, pv = create_ik_setup_arm(drv_joints)
    switch_node = create_switch_node_arm(drv_joints)

    rig.switch_ik_fk(fk_joints, drv_joints, switch_node = switch_node, ctrl = ctrl_ik, pv = pv)

    ctrl_start_a, ctrl_end_b, ribbon_assemble_shape = ribbon.limb_ribbon_assemble(*drv_joints, switch_node, preserve_match_rotation = True, orient = 0.0, sub=sub)

    fk_move = cmds.listRelatives(fk_joints[0], parent = True)[0]
    drv_move = cmds.listRelatives(drv_joints[0], parent = True)[0]

    bind_hand, bind_hand_offset = create_bind_hand_02(drv_joints[-1])
    tools.ensure_set(bind_hand)
    deco_mtx, wt_add_mtx = matrix.matrix_constraint([fk_joints[-1], ctrl_ik], bind_hand, r = True)

    reverse_node = cmds.createNode('reverse', name = f'rev_{bind_hand}')
    cmds.connectAttr(f'{switch_node}.switch', f'{reverse_node}.inputX')
    cmds.connectAttr(f'{reverse_node}.outputX', f'{wt_add_mtx}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{switch_node}.switch', f'{wt_add_mtx}.wtMatrix[1].weightIn')

    hand_slide_grp = cmds.group(name = bind_hand_offset.replace('offset', 'slide'), empty = True, world = True)
    tools.ensure_group(hand_slide_grp, SHOW)
    posi_node, _, _, _ = rivet.connect_rivet(hand_slide_grp, ribbon_assemble_shape, 1, 'v')

    rv_node = cmds.createNode('remapValue', name = f'rv_{hand_slide_grp}')
    cmds.setAttr(f'{rv_node}.outputMax', 0)
    cmds.connectAttr(f'{switch_node}.slide', f'{rv_node}.inputValue')
    cmds.connectAttr(f'{hand_slide_grp}.parameter_v', f'{rv_node}.outputMin')
    cmds.connectAttr(f'{rv_node}.outValue', f'{posi_node}.parameterV', force = True)

    reverse_follow_slide_node = cmds.createNode('reverse', name = f'rev_follow_slide_{SIDE}')
    cmds.connectAttr(f'{switch_node}.follow_slide', f'{reverse_follow_slide_node}.inputX')
    cmds.connectAttr(f'{switch_node}.follow_slide', f'{reverse_follow_slide_node}.inputY')
    cmds.connectAttr(f'{switch_node}.follow_slide', f'{reverse_follow_slide_node}.inputZ')

    mult_follow_slide_node = cmds.createNode('multiplyDivide', name = f'mult_follow_slide_{SIDE}')
    cmds.connectAttr(f'{deco_mtx}.{OUTPUT_R}', f'{mult_follow_slide_node}.input1')
    cmds.connectAttr(f'{reverse_follow_slide_node}.output', f'{mult_follow_slide_node}.input2')

    cmds.connectAttr(f'{mult_follow_slide_node}.output', f'{bind_hand}.rotate', force = True)

    cmds.parent(bind_hand_offset, hand_slide_grp)

    # no roll -------------------------------------------------------------------------------------------------------

    loc_hand = cmds.spaceLocator(name = f'{LOC}_hand_{SIDE}')[0]
    cmds.setAttr(f'{loc_hand}.v', 0)
    cmds.matchTransform(loc_hand, drv_joints[-1])
    tools.ensure_group(loc_hand, LOCATORS)
    _, wt_add_mtx = matrix.matrix_constraint([fk_joints[-1], ctrl_ik], loc_hand, t = True, r = True)
    reverse_node = cmds.createNode('reverse', name = f'rev_{loc_hand}')
    cmds.connectAttr(f'{switch_node}.switch', f'{reverse_node}.inputX')
    cmds.connectAttr(f'{reverse_node}.outputX', f'{wt_add_mtx}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{switch_node}.switch', f'{wt_add_mtx}.wtMatrix[1].weightIn')

    rig.no_roll_locs(loc_hand, drv_joints[1], ctrl_end_b)

    # stretch -------------------------------------------------------------------------------------------------------
    drv_move = cmds.listRelatives(drv_joints[0], parent = True)[0]
    rig.stretch_limb(ctrl_ik, drv_move, 'ctrl_main', drv_joints, switch_attribute = f'{switch_node}.switch')

    return fk_move, drv_move, ctrl_ik, pv, ctrl_start_a

def create_clavicle(proxy_clavicle_jnt: str) -> tuple[str, str]:
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_clavicle_jnt)
    cmds.select(clear = True)

    bind_clavicle = cmds.duplicate(proxy_clavicle_jnt, renameChildren = True)[0]
    bind_clavicle_end = cmds.listRelatives(bind_clavicle, children = True)[0]
    bind_clavicle = cmds.rename(bind_clavicle, f'{BIND}_clavicle_{SIDE}')
    bind_clavicle_end = cmds.rename(bind_clavicle_end, f'{BIND}_clavicleEnd_{SIDE}')
    tools.ensure_set([bind_clavicle, bind_clavicle_end])

    # compense rotate on clavicle end --------------------------------------------------
    mult_node = cmds.createNode('multiplyDivide', name = f'mult_rotate_{bind_clavicle_end}')
    cmds.setAttr(f'{mult_node}.input2', -1, -1, -1, type = 'float3')
    cmds.connectAttr(f'{bind_clavicle}.r', f'{mult_node}.input1')
    cmds.connectAttr(f'{mult_node}.output', f'{bind_clavicle_end}.r')
    # ----------------------------------------------------------------------------------

    display.color_node([bind_clavicle, bind_clavicle_end], 'white')
    tools.ensure_group(bind_clavicle, JOINTS)
    offset.move_op_matrix(bind_clavicle)

    ctrl = curve.octagon_control(name = f'{CTRL}_clavicle_{SIDE}', normal = 'x', color = SIDE_COLOR[SIDE])
    cmds.matchTransform(ctrl, bind_clavicle, position = True)
    if SIDE == 'R':
        cmds.setAttr(f'{ctrl}.ry', 180)
    tools.ensure_group(ctrl, CTRLS)
    offset.move_op_matrix(ctrl)

    matrix.matrix_constraint(ctrl, f'{bind_clavicle}_{MOVE}', t = True, r = True, mo = True)
    attribute.cb_attributes(ctrl, ats = ['sx', 'sy', 'sz'], lock = True, hide = True)
    attribute.sep_cb(ctrl, True)

    cmds.addAttr(ctrl, longName = 'constraint_rotate', niceName = 'Constraint Rotate', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)

    return ctrl, bind_clavicle

def create_bind_hand(proxy_wrist_jnt: str):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_wrist_jnt)
    
    bind_hand = cmds.joint(name = f'{BIND}_hand_{SIDE}')
    cmds.matchTransform(bind_hand, proxy_wrist_jnt)
    cmds.makeIdentity(bind_hand, apply = True, rotate = True)
    
    display.color_node(bind_hand, 'white')
    tools.ensure_group(bind_hand, JOINTS)
    offset.move_op_matrix(bind_hand)

    return bind_hand, f'{bind_hand}_{MOVE}'

def create_bind_hand_02(proxy_wrist_jnt: str):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_wrist_jnt)
    
    bind_hand = cmds.joint(name = f'{BIND}_hand_{SIDE}')
    cmds.matchTransform(bind_hand, proxy_wrist_jnt)
    cmds.makeIdentity(bind_hand, apply = True, rotate = True)
    
    display.color_node(bind_hand, 'white')
    tools.ensure_group(bind_hand, SHOW)
    offset.offset(bind_hand)

    # preserve
    preserve_joint = joint.create_preserve_jnt(bind_hand)
    tools.ensure_set(preserve_joint, set_name = 'bind_joints')

    return bind_hand, f'{bind_hand}_{OFFSET}'

def create_clavicle_arm_setup(proxy_clavicle_jnt: str, proxy_arm_jnt: str, sub: int = 5):
    '''
    '''
    
    cmds.select(clear = True)

    ctrl_clavicle, bind_clavicle = create_clavicle(proxy_clavicle_jnt)
    
    fk_move, drv_move, ctrl_ik, pv, ctrl_start_a = create_ik_fk_setup_arm(proxy_arm_jnt, sub=sub)

    deco_mtx_fk_move = matrix.matrix_constraint(bind_clavicle, fk_move, t = True, r = True, mo = True)
    deco_mtx_drv_move = matrix.matrix_constraint(bind_clavicle, drv_move, t = True, r = True, mo = True)

    deco_list = [deco_mtx_fk_move, deco_mtx_drv_move]
    grp_move_list = [fk_move, drv_move]

    for deco_mtx, grp_move in zip(deco_list, grp_move_list):
        mult_node = cmds.createNode('multiplyDivide', name = f'mult_{deco_mtx}')
        cmds.connectAttr(f'{deco_mtx}.outputRotate', f'{mult_node}.input1')

        for at in ['X', 'Y', 'Z']:
            cmds.connectAttr(f'{ctrl_clavicle}.constraint_rotate', f'{mult_node}.input2{at}')

        cmds.connectAttr(f'{mult_node}.output', f'{grp_move}.rotate', force = True)

    drv_start = cmds.listRelatives(drv_move, children = True)[0]

    rig.no_roll_locs(drv_start, bind_clavicle, ctrl_start_a, invert = True)

    # space follows ----------------------------------------------------------------------------------------------------------------------------
    locator_world = tools.loc_world()

    attribute.sep_cb(ctrl_ik, True)
    cmds.addAttr(ctrl_ik, longName = 'arm_follow', niceName = 'Arm Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)
    cmds.addAttr(ctrl_ik, longName = 'pv_follow', niceName = 'PV Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)

    ctrl_ik_move = cmds.listRelatives(ctrl_ik, parent = True)[0]
    pv_move = cmds.listRelatives(pv, parent = True)[0]

    _, wt_add_mtx_ctrl_ik_move = matrix.matrix_constraint([locator_world, ctrl_clavicle], ctrl_ik_move, t = True, r = True, mo = True)
    _, wt_add_mtx_pv_move = matrix.matrix_constraint([locator_world, ctrl_clavicle], pv_move, t = True, r = True, mo = True)

    rev_node = cmds.createNode('reverse', name = f'rev_{ctrl_ik_move}_{pv_move}')
    cmds.connectAttr(f'{ctrl_ik}.arm_follow', f'{rev_node}.inputX')
    cmds.connectAttr(f'{ctrl_ik}.pv_follow', f'{rev_node}.inputY')

    cmds.connectAttr(f'{rev_node}.inputX', f'{wt_add_mtx_ctrl_ik_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik}.arm_follow', f'{wt_add_mtx_ctrl_ik_move}.wtMatrix[1].weightIn')

    cmds.connectAttr(f'{rev_node}.inputY', f'{wt_add_mtx_pv_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik}.pv_follow', f'{wt_add_mtx_pv_move}.wtMatrix[1].weightIn')

    cmds.select(clear = True)

def create_clavicles_arms_setup(proxy_clavicle_jnt_l: str, proxy_arm_jnt_l: str, proxy_clavicle_jnt_r: str, proxy_arm_jnt_r: str, sub: int = 5):

    create_clavicle_arm_setup(proxy_clavicle_jnt_l, proxy_arm_jnt_l, sub=sub)
    create_clavicle_arm_setup(proxy_clavicle_jnt_r, proxy_arm_jnt_r, sub=sub)
