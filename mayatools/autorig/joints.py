from maya import cmds
from typing import Literal


def orient_joint(joint: str, orient_jnt: Literal['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'] = 'xyz', secondary_axis_orient: Literal['xup', 'xdown', 'yup', 'ydown', 'zup', 'zdown'] = 'xup'):
    '''
    '''

    kids = cmds.listRelatives(joint, children = True)
    if kids:
        if cmds.nodeType(kids[0]) == 'joint':
            cmds.joint(joint, edit = True, orientJoint = orient_jnt, secondaryAxisOrient = secondary_axis_orient)
            return
        
    cmds.joint(joint, edit = True, orientJoint = 'none')


def set_preferred_angle(joint: str, orient_jnt: Literal['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'] = 'xyz', secondary_axis_orient: Literal['xup', 'xdown', 'yup', 'ydown', 'zup', 'zdown'] = 'xup'):
    '''
    '''

    axis = orient_jnt[1].capitalize()

    value_dict = {
        'u': 10,
        'd': -10
    }
    orientation = secondary_axis_orient[1]
    value = value_dict[orientation]

    cmds.setAttr(f'{joint}.preferredAngleX', 0)
    cmds.setAttr(f'{joint}.preferredAngleY', 0)
    cmds.setAttr(f'{joint}.preferredAngleZ', 0)

    cmds.setAttr(f'{joint}.preferredAngle{axis}', value)


def set_joint_orient_angle(joints: list, orient_jnt: Literal['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'] = 'xyz', secondary_axis_orient: Literal['xup', 'xdown', 'yup', 'ydown', 'zup', 'zdown'] = 'xup'):
    '''
    '''

    for joint in joints:
        orient_joint(joint, orient_jnt, secondary_axis_orient)

        kids = cmds.listRelatives(joint, children = True)
        if kids:
            if cmds.nodeType(kids[0]) == 'joint':
                set_preferred_angle(joint, orient_jnt, secondary_axis_orient)


set_joint_orient_angle(cmds.ls(sl=1))