from ...utils.imports import *
from .. import (
    constants_maya,
    curve,
    display,
    offset,
    matrix,
    rig,
    mathfuncs,
    attribute,
    vector,
    ribbon,
    joint,
    tools
)
reload(constants_maya)
reload(curve)
reload(display)
reload(offset)
reload(matrix)
reload(rig)
reload(mathfuncs)
reload(attribute)
reload(vector)
reload(ribbon)
reload(joint)
reload(tools)
from ..constants_maya import *

def create_fk_leg(proxy_leg_jnt: str):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_leg_jnt)

    duplicate_joints = cmds.duplicate(proxy_leg_jnt, renameChildren = True)
    cmds.parent(duplicate_joints[0], world = True)
    name_list = "leg", "knee", "ankle", "ball", "toe"
    fk_joints = []

    for jnt, name in zip(duplicate_joints, name_list):

        jnt = cmds.rename(jnt, f'{FK}_{name}_{SIDE}')
        display.color_node(jnt, SIDE_COLOR[SIDE])

        if name != 'toe':
            circle = curve.octagon_control(normal = 'x')
            curve.parent_shapes([circle, jnt])

        fk_joints.append(jnt)

    joint.joint_to_transform(fk_joints, color = SIDE_COLOR[SIDE], op_mtx = False)

    offset.move_op_matrix(fk_joints[0])
    attribute.cb_attributes(fk_joints, ats = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'], lock = True, hide = True)
    attribute.vis_no_keyable(fk_joints)

    tools.ensure_group(f'{fk_joints[0]}_{MOVE}', CTRLS)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Fk jnts done.')
    return fk_joints

def create_drv_leg(proxy_leg_jnt: str):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_leg_jnt)

    duplicate_joints = cmds.duplicate(proxy_leg_jnt, renameChildren = True)
    name_list = "leg", "knee", "ankle"
    drv_joints = []

    cmds.delete(duplicate_joints[-1], duplicate_joints[-2])

    for jnt, name in zip(duplicate_joints, name_list):

        jnt = cmds.rename(jnt, f'{DRV}_{name}_{SIDE}')
        display.color_node(jnt, 'gold')
        cmds.setAttr(f'{jnt}.radius', 0.5)

        drv_joints.append(jnt)

    cmds.joint(f'{DRV}_ankle_{SIDE}', edit = True, orientJoint = 'none')
    tools.ensure_group(drv_joints[0], JOINTS)

    offset.move_op_matrix(drv_joints[0])
    attribute.vis_no_keyable(drv_joints)

    # preserve
    preserve_joint = joint.create_preserve_jnt(drv_joints[0])
    tools.ensure_set(preserve_joint, set_name = 'bind_joints')

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Drv jnts done.')
    return drv_joints

def create_drv_foot(proxy_leg_jnt: str):
    '''
    '''

    SIDE = tools.get_side_from_node(proxy_leg_jnt)

    duplicate_joints = cmds.duplicate(proxy_leg_jnt, renameChildren = True)
    cmds.parent(duplicate_joints[2], world = True)
    cmds.delete(duplicate_joints[0])
    duplicate_joints = duplicate_joints[2:6]
    name_list = "ankle", "ball", "toe"
    drv_joints = []

    for jnt, name in zip(duplicate_joints, name_list):

        jnt = cmds.rename(jnt, f'{BIND}_{name}_{SIDE}')
        display.color_node(jnt, 'white')
        cmds.setAttr(f'{jnt}.radius', 0.5)

        drv_joints.append(jnt)

    tools.ensure_group(drv_joints[0], JOINTS)

    offset.move_op_matrix(drv_joints[0])
    attribute.vis_no_keyable(drv_joints)
    tools.ensure_set(drv_joints)

    # -----------------

    # -----------------

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Drv jnts done.')
    return drv_joints

def create_ik_setup_leg(drv_jnts: list):
    '''
    '''

    drv_leg, drv_knee, drv_ankle = drv_jnts
    SIDE = tools.get_side_from_node(drv_leg)

    ik = cmds.ikHandle(startJoint = drv_leg, endEffector = drv_ankle, solver = 'ikRPsolver', name = f'ik_leg_{SIDE}')[0]
    #attribute.cb_attributes(ik, lock = True)

    ctrl_ik = curve.octagon_control(name = f'{CTRL}_leg_{SIDE}', normal = 'y', color = SIDE_COLOR[SIDE])
    display.color_node(ctrl_ik, SIDE_COLOR[SIDE])
    cmds.matchTransform(ctrl_ik, ik, position = True)
    tools.ensure_group(ctrl_ik, CTRLS)
    offset.move_op_matrix(ctrl_ik)
    cmds.parent(ik, ctrl_ik)

    pole_vector = vector.pv_cal(drv_jnts)
    pole_vector = cmds.rename(pole_vector, f'pv_leg_{SIDE}')
    cmds.move(0, 0, mathfuncs.distance_btw(drv_leg, drv_knee), pole_vector, relative = True)
    display.color_node(pole_vector, SIDE_COLOR[SIDE])
    tools.ensure_group(pole_vector, CTRLS)
    offset.move_op_matrix(pole_vector)
    cmds.poleVectorConstraint(pole_vector, ik)

    attribute.vis_no_keyable([ik, ctrl_ik, pole_vector])
    attribute.cb_attributes(pole_vector, ats = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'], lock = True, hide = True)
    attribute.cb_attributes(ctrl_ik, ats = ['sx', 'sy', 'sz'], lock = True, hide = True)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Ik setup leg done.')
    return ik, ctrl_ik, pole_vector

def create_iks_foot(foot_jnts: list):
    '''
    '''

    bind_ankle, bind_ball, bind_toe = foot_jnts
    SIDE = tools.get_side_from_node(bind_ankle)

    ik_ball = cmds.ikHandle(startJoint = bind_ankle, endEffector = bind_ball, solver = 'ikSCsolver', name = f'ik_ball_{SIDE}')[0]
    ik_toe = cmds.ikHandle(startJoint = bind_ball, endEffector = bind_toe, solver = 'ikSCsolver', name = f'ik_toe_{SIDE}')[0]

    cmds.select(clear = True)
    return ik_ball, ik_toe

def create_switch_node_leg(drv_jnts: list):
    '''
    '''

    drv_leg, drv_knee, _ = drv_jnts
    SIDE = tools.get_side_from_node(drv_leg)

    ctrl = f'switch_leg_{SIDE}'
    curve.star_control(name = ctrl, color = 'pink')

    cmds.matchTransform(ctrl, drv_leg, position = True)
    
    tools.ensure_group(ctrl, CTRLS)

    value = mathfuncs.distance_btw(drv_leg, drv_knee) * 0.5
    x_value = value if SIDE == 'L' else value * -1
    cmds.move(x_value, 0, 0, ctrl, relative = True)
    offset.offset_parent_matrix(ctrl)

    attribute.sep_cb(ctrl, True)
    cmds.addAttr(ctrl, longName = 'switch', niceName = 'Switch', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)
    #cb_attributes(ctrl, lock = True, hide = True)
    attribute.vis_no_keyable(ctrl)

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Switch node done.')
    return ctrl

def create_locs_hierarchy_leg(geo: str, foot_jnts: list, ik_leg: str, ik_ball: str, ik_toe: str, ctrl: str):
    '''
    '''

    bind_ankle, bind_ball, _ = foot_jnts
    SIDE = tools.get_side_from_node(bind_ankle)

    names = ('bank_int', 'bank_ext', 'toe', 'heel')

    if SIDE == 'L':
        extremes = (mathfuncs.xmin, mathfuncs.xmax, mathfuncs.zmax, mathfuncs.zmin) 
    if SIDE == 'R':
        extremes = (mathfuncs.xmax, mathfuncs.xmin, mathfuncs.zmax, mathfuncs.zmin)

    locs = []

    for name, extreme in zip(names, extremes):

        loc = cmds.spaceLocator(name = f'{LOC}_{name}_{SIDE}')[0]
        locs.append(loc)
        cmds.matchTransform(loc, bind_ball, position = True)
        display.color_node(loc, 'green')

        cmds.setAttr(f'{loc}.ty', 0)

        if name in ['toe', 'heel']:
            cmds.setAttr(f'{loc}.tz', extreme(geo))

        if name in ['bank_int', 'bank_ext']:
            cmds.setAttr(f'{loc}.tx', extreme(geo))

        
        cmds.makeIdentity(loc, translate = True, apply = True)

    loc_bank_int, loc_bank_ext, loc_toe, loc_heel = locs
    cmds.parent(loc_heel, loc_toe)
    cmds.parent(loc_toe, loc_bank_ext)
    cmds.parent(loc_bank_ext, loc_bank_int)
    cmds.parent(loc_bank_int, ctrl)
    offset.offset_parent_matrix(loc_bank_int)

    pivot_ball = cmds.group(empty = True, name = f'pivot_ball_{SIDE}')
    pivot_toe = cmds.group(empty = True, name = f'pivot_toe_{SIDE}')
    cmds.matchTransform(pivot_ball, bind_ball, position = True)
    cmds.matchTransform(pivot_toe, bind_ball, position = True)

    cmds.parent(ik_leg, pivot_ball)
    cmds.parent(pivot_ball, loc_heel)

    cmds.parent(ik_ball, loc_heel)
    cmds.parent(ik_toe, pivot_toe)
    cmds.parent(pivot_toe, loc_heel)

    cmds.makeIdentity(pivot_ball, translate = True, apply = True)
    cmds.makeIdentity(pivot_toe, translate = True, apply = True)

    offset.offset(pivot_toe)

    cmds.setAttr(f'{loc_bank_int}.v', 0)

    # create attributes
    attribute.sep_cb(ctrl, True)
    cmds.addAttr(ctrl, longName='twist_leg', niceName = 'Twist Leg', attributeType = 'float', keyable = True)
    cmds.addAttr(ctrl, longName = 'foot_roll', niceName = 'Foot Roll', attributeType = 'float', min = -1, max = 1, keyable = True)
    cmds.addAttr(ctrl, longName = 'break_angle', niceName = 'Break Angle', attributeType = 'float', min = -1, max = 1, dv = 0, keyable = True)
    cmds.addAttr(ctrl, longName = 'twist_heel', niceName = 'Twist Heel', attributeType = 'float', min = -1, max = 1, keyable = True)
    cmds.addAttr(ctrl, longName = 'twist_toe', niceName = 'Twist Toe', attributeType = 'float', min = -1, max = 1, keyable = True)
    cmds.addAttr(ctrl, longName = 'flex_toe', niceName = 'Flex Toe', attributeType = 'float', min = -1, max = 1, keyable = True)
    cmds.addAttr(ctrl, longName = 'bank', niceName = 'Bank', attributeType = 'float', min = -50, max = 50, keyable = True)

    # connect attributes
    cmds.connectAttr(f'{ctrl}.twist_leg', f'{ik_leg}.twist')
    
    angle = cmds.getAttr(f'{bind_ball}.jointOrientY')
    angle, angle02 = str(round(90 + angle, 3)), str(round((90 + angle)*2,3))
    bank_factor = 1 if SIDE == 'R' else -1

    twist_heel_exp = f'{loc_heel}.ry = {ctrl}.twist_heel * 60;'
    twist_toe_exp = f'{loc_toe}.ry = {ctrl}.twist_toe * 60;'
    pivot_toe_exp = f'{pivot_toe}.rx = {ctrl}.flex_toe * 40;'

    bank_exp = f'''
    if ({ctrl}.bank <= 0){{
        {loc_bank_int}.rz = {ctrl}.bank * {bank_factor};
        {loc_bank_ext}.rz = 0;
    }}

    else {{
    
        {loc_bank_ext}.rz = {ctrl}.bank * {bank_factor};
        {loc_bank_int}.rz = 0;
    }}
    '''

    foot_roll_exp = f'''
    $break = {ctrl}.break_angle + 1;
    if ({ctrl}.foot_roll <= 0){{
        {loc_toe}.rx = 0;
        {loc_heel}.rx = {ctrl}.foot_roll * {angle};
        {pivot_ball}.rx = 0;
    }}

    else if ({ctrl}.foot_roll >= 0.5){{
        {loc_toe}.rx = ({ctrl}.foot_roll - 0.5) * {angle02};
        {loc_heel}.rx = 0;
        {pivot_ball}.rx = {ctrl}.foot_roll * - {angle02} * $break + {angle02} * $break;
    }}

    else{{
        {loc_toe}.rx = 0;
        {loc_heel}.rx = 0;
        {pivot_ball}.rx = {ctrl}.foot_roll * {angle02} * $break;
    }}

    '''
    
    cmds.expression(string = twist_heel_exp, name = f'Exp_twist_heel_{SIDE}')
    cmds.expression(string = twist_toe_exp, name = f'Exp_twist_toe_{SIDE}')
    cmds.expression(string = pivot_toe_exp, name = f'Exp_flex_toe_{SIDE}')
    cmds.expression(string = bank_exp, name = f'Exp_bank_{SIDE}')
    cmds.expression(string = foot_roll_exp, name = f'Exp_foot_roll_{SIDE}')


    cmds.select(clear = True)

def create_ik_fk_setup_leg(proxy_leg_jnt: str, geo: str, sub: int = 7):
    '''
    '''

    fk_joints = create_fk_leg(proxy_leg_jnt)
    drv_joints_leg = create_drv_leg(proxy_leg_jnt)
    drv_joints_foot = create_drv_foot(proxy_leg_jnt)
    ik, ctrl_ik, pv = create_ik_setup_leg(drv_joints_leg)
    ik_ball, ik_toe = create_iks_foot(drv_joints_foot)
    switch_node = create_switch_node_leg(drv_joints_leg)

    fk_joints_sw = fk_joints[0:-1]
    drv_joints_sw = drv_joints_leg[0:-1]
    drv_joints_sw.extend(drv_joints_foot[0:-1])

    # ankle constraint ankle
    bind_ankle_move = cmds.listRelatives(drv_joints_foot[0], parent = True)[0]
    matrix.matrix_constraint(drv_joints_leg[-1], bind_ankle_move, t = True, r = True, mo = True)

    rig.switch_ik_fk(fk_joints_sw, drv_joints_sw, switch_node = switch_node, ctrl = ctrl_ik, pv = pv)
    cmds.connectAttr(f'{switch_node}.switch', f'{ik_ball}.ikBlend')
    cmds.connectAttr(f'{switch_node}.switch', f'{ik_toe}.ikBlend')

    create_locs_hierarchy_leg(geo, drv_joints_foot, ik, ik_ball, ik_toe, ctrl_ik)

    _, ctrl_end_b, _ = ribbon.limb_ribbon_assemble(*drv_joints_leg, switch_node, compense_translate = False, sub=sub)
    rig.no_roll_locs(drv_joints_foot[0], drv_joints_leg[1], ctrl_end_b)

    fk_move = cmds.listRelatives(fk_joints[0], parent = True)[0]
    drv_move = cmds.listRelatives(drv_joints_leg[0], parent = True)[0]

    # stretch
    drv_move = cmds.listRelatives(drv_joints_leg[0], parent = True)[0]
    rig.stretch_limb(ctrl_ik, drv_move, 'ctrl_main', drv_joints_leg, f'{switch_node}.switch')

    cmds.select(clear = True)
    om.MGlobal.displayInfo('Ik Fk setup leg done.')
    return fk_move, drv_move, ctrl_ik, pv

def create_hip_leg_setup(proxy_root: str, proxy_leg_jnt_l: str, proxy_leg_jnt_r: str, geo_l: str, geo_r: str, sub: int = 7):
    '''
    '''

    bind_hips = joint.curve_joint(name = f'{CTRL}_hips', color = 'white', normal = [0, 1, 0], radius = 2)
    bind_hip_l = cmds.joint(name = f'{BIND}_hip_L')
    bind_hip_r = cmds.joint(name = f'{BIND}_hip_R')

    tools.ensure_group(bind_hips, JOINTS)
    tools.ensure_set([bind_hips, bind_hip_l, bind_hip_r])

    cmds.matchTransform(bind_hips, proxy_root, position = True)
    cmds.matchTransform(bind_hip_l, proxy_leg_jnt_l, position = True)
    cmds.matchTransform(bind_hip_r, proxy_leg_jnt_r, position = True)

    cmds.parent(bind_hip_l, bind_hip_r, bind_hips)

    offset.move_op_matrix(bind_hips)
    attribute.cb_attributes(bind_hips, ats = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'], lock = True, hide = True)

    fk_move_l, drv_move_l, ctrl_ik_l, pv_l = create_ik_fk_setup_leg(proxy_leg_jnt_l, geo_l, sub=sub)
    fk_move_r, drv_move_r, ctrl_ik_r, pv_r = create_ik_fk_setup_leg(proxy_leg_jnt_r, geo_r, sub=sub)

    deco_mtx_fk_move_l = matrix.matrix_constraint(bind_hip_l, fk_move_l, t = True, r = True, mo = True)
    deco_mtx_drv_move_l = matrix.matrix_constraint(bind_hip_l, drv_move_l, t = True, r = True, mo = True)
    deco_mtx_fk_move_r = matrix.matrix_constraint(bind_hip_r, fk_move_r, t = True, r = True, mo = True)
    deco_mtx_drv_move_r = matrix.matrix_constraint(bind_hip_r, drv_move_r, t = True, r = True, mo = True)

    attribute.sep_cb(bind_hips, True)
    cmds.addAttr(bind_hips, longName = 'constraint_rotate', niceName = 'Constraint Rotate', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)

    deco_list = [deco_mtx_fk_move_l, deco_mtx_drv_move_l, deco_mtx_fk_move_r, deco_mtx_drv_move_r]
    grp_move_list = [fk_move_l, drv_move_l, fk_move_r, drv_move_r]

    for deco_mtx, grp_move in zip(deco_list, grp_move_list):
        mult_node = cmds.createNode('multiplyDivide', name = f'mult_{deco_mtx}')
        cmds.connectAttr(f'{deco_mtx}.outputRotate', f'{mult_node}.input1')

        for at in ['X', 'Y', 'Z']:
            cmds.connectAttr(f'{bind_hips}.constraint_rotate', f'{mult_node}.input2{at}')

        cmds.connectAttr(f'{mult_node}.output', f'{grp_move}.rotate', force = True)

    # space follows ---------------------------------------------------------------------------------------------------------------
    locator_world = tools.loc_world()

    attribute.sep_cb(ctrl_ik_l, True)
    cmds.addAttr(ctrl_ik_l, longName = 'leg_follow', niceName = 'Leg Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)
    cmds.addAttr(ctrl_ik_l, longName = 'pv_follow', niceName = 'PV Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)

    ctrl_ik_l_move = cmds.listRelatives(ctrl_ik_l, parent = True)[0]
    pv_l_move = cmds.listRelatives(pv_l, parent = True)[0]

    _, wt_add_mtx_ctrl_ik_l_move = matrix.matrix_constraint([locator_world, bind_hips], ctrl_ik_l_move, t = True, r = True, mo = True)
    _, wt_add_mtx_pv_l_move = matrix.matrix_constraint([locator_world, bind_hips], pv_l_move, t = True, r = True, mo = True)

    rev_node = cmds.createNode('reverse', name = f'rev_{ctrl_ik_l_move}_{pv_l_move}')
    cmds.connectAttr(f'{ctrl_ik_l}.leg_follow', f'{rev_node}.inputX')
    cmds.connectAttr(f'{ctrl_ik_l}.pv_follow', f'{rev_node}.inputY')

    cmds.connectAttr(f'{rev_node}.inputX', f'{wt_add_mtx_ctrl_ik_l_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik_l}.leg_follow', f'{wt_add_mtx_ctrl_ik_l_move}.wtMatrix[1].weightIn')

    cmds.connectAttr(f'{rev_node}.inputY', f'{wt_add_mtx_pv_l_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik_l}.pv_follow', f'{wt_add_mtx_pv_l_move}.wtMatrix[1].weightIn')

    # -------------------------------------------------------------------------------------------------------------------

    attribute.sep_cb(ctrl_ik_r, True)
    cmds.addAttr(ctrl_ik_r, longName = 'leg_follow', niceName = 'Leg Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)
    cmds.addAttr(ctrl_ik_r, longName = 'pv_follow', niceName = 'PV Follow', attributeType = 'long', min = 0, max = 1, dv = 0, keyable = True)

    ctrl_ik_r_move = cmds.listRelatives(ctrl_ik_r, parent = True)[0]
    pv_r_move = cmds.listRelatives(pv_r, parent = True)[0]

    _, wt_add_mtx_ctrl_ik_r_move = matrix.matrix_constraint([locator_world, bind_hips], ctrl_ik_r_move, t = True, r = True, mo = True)
    _, wt_add_mtx_pv_r_move = matrix.matrix_constraint([locator_world, bind_hips], pv_r_move, t = True, r = True, mo = True)

    rev_node = cmds.createNode('reverse', name = f'rev_{ctrl_ik_r_move}_{pv_r_move}')
    cmds.connectAttr(f'{ctrl_ik_r}.leg_follow', f'{rev_node}.inputX')
    cmds.connectAttr(f'{ctrl_ik_r}.pv_follow', f'{rev_node}.inputY')

    cmds.connectAttr(f'{rev_node}.inputX', f'{wt_add_mtx_ctrl_ik_r_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik_r}.leg_follow', f'{wt_add_mtx_ctrl_ik_r_move}.wtMatrix[1].weightIn')

    cmds.connectAttr(f'{rev_node}.inputY', f'{wt_add_mtx_pv_r_move}.wtMatrix[0].weightIn')
    cmds.connectAttr(f'{ctrl_ik_r}.pv_follow', f'{wt_add_mtx_pv_r_move}.wtMatrix[1].weightIn')

    cmds.select(clear = True)
