from ...utils.imports import *
from . import (
    arm,
    leg,
    spine
)
from .. import ( 
    matrix,
    offset,
    attribute,
    curve,
    rig
)
reload(arm)
reload(leg)
reload(spine)
reload(matrix)
reload(offset)
reload(attribute)
reload(curve)
reload(rig)

def autorig_body(
        proxy_clavicle_jnt_l: str, proxy_arm_jnt_l: str, 
        proxy_clavicle_jnt_r: str, proxy_arm_jnt_r: str,
        proxy_root: str, proxy_chest: str,
        proxy_leg_jnt_l: str, proxy_leg_jnt_r: str, 
        geo_l: str, geo_r: str,
        arm_sub: int = 5,
        leg_sub: int = 5
        ):
    '''
    '''

    spine.spine_matrix(proxy_root, proxy_chest)
    
    arm.create_clavicle_arm_setup(proxy_clavicle_jnt_l, proxy_arm_jnt_l, sub = arm_sub)
    arm.create_clavicle_arm_setup(proxy_clavicle_jnt_r, proxy_arm_jnt_r, sub = arm_sub)

    leg.create_hip_leg_setup(proxy_root, proxy_leg_jnt_l, proxy_leg_jnt_r, geo_l, geo_r, sub = leg_sub)


def run_autorig_body(arm_sub: int = 5, leg_sub: int = 5):

    autorig_body(
       'pxy:proxy_clavicle_L','pxy:proxy_arm_L', 
       'pxy:proxy_clavicle_R','pxy:proxy_arm_R',
       'pxy:proxy_root','pxy:proxy_chest',
       'pxy:proxy_leg_L','pxy:proxy_leg_R', 
       'pxy:foot_L','pxy:foot_R',
       arm_sub = arm_sub,
       leg_sub = leg_sub
    )

    matrix.matrix_constraint('bind_chest', 'ctrl_clavicle_L_move', mo = True, t = True, r = True)
    matrix.matrix_constraint('bind_chest', 'ctrl_clavicle_R_move', mo = True, t = True, r = True)
    matrix.matrix_constraint('bind_pelvis', 'ctrl_hips_move', t = True, r = True)

    cmds.parent('switch_leg_L', 'switch_leg_R', 'ctrl_root')
    cmds.parent('switch_arm_L', 'switch_arm_R','ctrl_ik_chest')

    offset.offset_parent_matrix(['switch_leg_L', 'switch_leg_R', 'switch_arm_L', 'switch_arm_R'])
    attribute.cb_attributes(['switch_leg_L', 'switch_leg_R', 'switch_arm_L', 'switch_arm_R'], lock = True, hide = True)

    rig.no_roll_locs('drv_leg_L', 'bind_hip_L', 'ctrl_A_ribbon_leg_L_01', invert = True)
    rig.no_roll_locs('drv_leg_R', 'bind_hip_R', 'ctrl_A_ribbon_leg_R_01', invert = True)

    curve.ensure_shape()
    attribute.vis_no_keyable('ctrl_main')

    attribute.sep_cb('ctrl_main', True)
    cmds.addAttr('ctrl_main', ln = 'primary_controls', nn = 'Primary Controls', at = 'long', min = 0, max = 1, dv = 1)
    cmds.setAttr('ctrl_main.primary_controls', k = 0, cb = 1)

    cmds.addAttr('ctrl_main', ln = 'secondary_controls', nn = 'Secondary Controls', at = 'long', min = 0, max = 1, dv = 1)
    cmds.setAttr('ctrl_main.secondary_controls', k = 0, cb = 1)

    primary_nodes = (
        'fk_leg_L_move', 'fk_leg_R_move', 'fk_arm_L_move', 'fk_arm_R_move',
        'pv_leg_L_move', 'pv_leg_R_move', 'pv_arm_L_move', 'pv_arm_R_move',
        'ctrl_root', 'ctrl_fk_mid', 'ctrl_fk_chest',
        'ctrl_ik_pelvis', 'ctrl_ik_mid', 'ctrl_ik_chest',
        'ctrl_hips', 'ctrl_clavicle_L', 'ctrl_clavicle_R'
    )

    for node in primary_nodes:
        cmds.connectAttr('ctrl_main.primary_controls', f'{node}.v') 

    secondary_nodes = (
        'ctrl_Mid_ribbon_arm_L_01', 'ctrl_preserve_elbow_L', 'ctrl_Mid_ribbon_elbow_L_01',
        'ctrl_Mid_ribbon_arm_R_01', 'ctrl_preserve_elbow_R', 'ctrl_Mid_ribbon_elbow_R_01',
        'ctrl_Mid_ribbon_leg_L_01', 'ctrl_preserve_knee_L', 'ctrl_Mid_ribbon_knee_L_01',
        'ctrl_Mid_ribbon_leg_R_01', 'ctrl_preserve_knee_R', 'ctrl_Mid_ribbon_knee_R_01',
        'ctrl_ribbon_spine_01', 'ctrl_ribbon_spine_02', 'ctrl_ribbon_spine_03', 'ctrl_ribbon_spine_04', 'ctrl_ribbon_spine_05'
    )

    for node in secondary_nodes:
        cmds.connectAttr('ctrl_main.secondary_controls', f'{node}.v') 

    attribute.sep_cb('ctrl_main', True)
    cmds.addAttr('ctrl_main', ln = 'show_bind_joints', nn = 'Show Bind Joints', at = 'long', min = 0, max = 1, dv = 0)
    cmds.setAttr('ctrl_main.show_bind_joints', k = 0, cb = 1)
    cmds.addAttr('ctrl_main', ln = 'show_ribbons', nn = 'Show Ribbons', at = 'long', min = 0, max = 1, dv = 0)
    cmds.setAttr('ctrl_main.show_ribbons', k = 0, cb = 1)

    nodes = (
        'bind_hand_L_slide', 'bind_preserve_elbow_L', 'bind_preserve_knee_L',
        'bind_hand_R_slide', 'bind_preserve_elbow_R', 'bind_preserve_knee_R'
    )

    for node in nodes:
        cmds.connectAttr('ctrl_main.s', f'{node}.s')

    binds = (
        'bind_ankle_L',
        'bind_ankle_R',
        'bind_ball_L',
        'bind_ball_R',
        'bind_chest',
        'bind_clavicleEnd_L',
        'bind_clavicleEnd_R',
        'bind_clavicle_L',
        'bind_clavicle_R',
        'bind_hand_L',
        'bind_hand_R',
        'bind_hip_L',
        'bind_hip_R',
        'bind_pelvis',
        'bind_preserve_elbow_L',
        'bind_preserve_elbow_R',
        'bind_preserve_knee_L',
        'bind_preserve_knee_R',
        'bind_rivet_ribbon_arm_L_01_01',
        'bind_rivet_ribbon_arm_L_01_02',
        'bind_rivet_ribbon_arm_L_01_03',
        'bind_rivet_ribbon_arm_L_01_04',
        'bind_rivet_ribbon_arm_L_01_05',
        'bind_rivet_ribbon_arm_R_01_01',
        'bind_rivet_ribbon_arm_R_01_02',
        'bind_rivet_ribbon_arm_R_01_03',
        'bind_rivet_ribbon_arm_R_01_04',
        'bind_rivet_ribbon_arm_R_01_05',
        'bind_rivet_ribbon_elbow_L_01_01',
        'bind_rivet_ribbon_elbow_L_01_02',
        'bind_rivet_ribbon_elbow_L_01_03',
        'bind_rivet_ribbon_elbow_L_01_04',
        'bind_rivet_ribbon_elbow_L_01_05',
        'bind_rivet_ribbon_elbow_R_01_01',
        'bind_rivet_ribbon_elbow_R_01_02',
        'bind_rivet_ribbon_elbow_R_01_03',
        'bind_rivet_ribbon_elbow_R_01_04',
        'bind_rivet_ribbon_elbow_R_01_05',
        'bind_rivet_ribbon_knee_L_01_01',
        'bind_rivet_ribbon_knee_L_01_02',
        'bind_rivet_ribbon_knee_L_01_03',
        'bind_rivet_ribbon_knee_L_01_04',
        'bind_rivet_ribbon_knee_L_01_05',
        'bind_rivet_ribbon_knee_R_01_01',
        'bind_rivet_ribbon_knee_R_01_02',
        'bind_rivet_ribbon_knee_R_01_03',
        'bind_rivet_ribbon_knee_R_01_04',
        'bind_rivet_ribbon_knee_R_01_05',
        'bind_rivet_ribbon_leg_L_01_01',
        'bind_rivet_ribbon_leg_L_01_02',
        'bind_rivet_ribbon_leg_L_01_03',
        'bind_rivet_ribbon_leg_L_01_04',
        'bind_rivet_ribbon_leg_L_01_05',
        'bind_rivet_ribbon_leg_R_01_01',
        'bind_rivet_ribbon_leg_R_01_02',
        'bind_rivet_ribbon_leg_R_01_03',
        'bind_rivet_ribbon_leg_R_01_04',
        'bind_rivet_ribbon_leg_R_01_05',
        'bind_toe_L',
        'bind_toe_R',
    )

    for bind in binds:
        cmds.connectAttr('ctrl_main.show_bind_joints', f'{bind}.v')

    ribbons = (
        'ribbon_leg_L_01_assemble', 'ribbon_arm_L_01_assemble',
        'ribbon_leg_R_01_assemble', 'ribbon_arm_R_01_assemble',
        'ribbon_spine_lowdef'
    )

    for ribbon in ribbons:
        cmds.connectAttr('ctrl_main.show_ribbons', f'{ribbon}.v')

    try:
        cmds.parent('Global_Move', 'ctrl_root')
    except:
        pass