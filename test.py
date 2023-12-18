import maya.cmds as cmds
from importlib import reload

from .maya_tools import attribute
from .maya_tools import curve

reload(attribute)
reload(curve)

def exec_attribute():
    mesh_obj = cmds.polyCube(ch = False)[0]
    attribute.dag_rman_attribs(False)
    attribute.sep_cb(mesh_obj, True, style = "hyphen")
    attribute.sep_cb(mesh_obj, True, style = "underscore")
    
def exec_curve():
    curve.control()
    curve.control(shape = "square", name = "ctrl_ribbon", color = "red")
    
#exec_curve()

from .maya_tools.attribute import sep_cb

def add_finger_ats(node: str):

    sep_cb(node, True) # -------------------------------------------------------------------------------------------------

    ats = (
        'index_01_rz_rz',
        'index_02_rz_rz',
        'index_03_rz_rz',
        'middle_01_rz_rz',
        'middle_02_rz_rz',
        'middle_03_rz_rz',
        'ring_01_rz_rz',
        'ring_02_rz_rz',
        'ring_03_rz_rz',
        'pinkie_01_rz_rz',
        'pinkie_02_rz_rz',
        'pinkie_03_rz_rz'
    )

    for at in ats:
        cmds.addAttr(node, ln = at, nn = at, min = 0, dv = 1, at = 'float')
        cmds.setAttr(f'{node}.{at}', cb = 1, k = 0)

    sep_cb(node, True) # -------------------------------------------------------------------------------------------------

    ats = (
        'index_01_rz_rx',
        'index_02_rz_rx',
        'index_03_rz_rx',
        'middle_01_rz_rx',
        'middle_02_rz_rx',
        'middle_03_rz_rx',
        'ring_01_rz_rx',
        'ring_02_rz_rx',
        'ring_03_rz_rx',
        'pinkie_01_rz_rx',
        'pinkie_02_rz_rx',
        'pinkie_03_rz_rx'
    )

    values = (
        -0.75,
        -0.75,
        -0.75,
        -0.25,
        -0.25,
        -0.25,
        0.25,
        0.25,
        0.25,
        0.75,
        0.75,
        0.75
    )

    for at, v in zip(ats, values):
        cmds.addAttr(node, ln = at, nn = at, dv = v, at = 'float')
        cmds.setAttr(f'{node}.{at}', cb = 1, k = 0)

    sep_cb(node, True) # -------------------------------------------------------------------------------------------------

    ats = (
        'index_01_ry_ry',
        'middle_03_ry_ry',
        'ring_01_ry_ry',
        'pinkie_01_ry_ry',
        'index_01_ry_sz',
        'middle_03_ry_sz',
        'ring_01_ry_sz',
        'pinkie_01_ry_sz'
    )

    values = (
        1,
        1,
        1,
        1,
        -7.5,
        -2.5,
        2.5,
        7.5
    )

    for at, v in zip(ats, values):
        cmds.addAttr(node, ln = at, nn = at, dv = v, at = 'float')
        cmds.setAttr(f'{node}.{at}', cb = 1, k = 0)

    sep_cb(node, True) # -------------------------------------------------------------------------------------------------

    ats = (
        'index_01_sx_sx',
        'index_02_sx_sx',
        'index_03_sx_sx',
        'middle_01_sx_sx',
        'middle_02_sx_sx',
        'middle_03_sx_sx',
        'ring_01_sx_sx',
        'ring_02_sx_sx',
        'ring_03_sx_sx',
        'pinkie_01_sx_sx',
        'pinkie_02_sx_sx',
        'pinkie_03_sx_sx'
    )

    for at in ats:
        cmds.addAttr(node, ln = at, nn = at, min = 0, dv = 1, at = 'float')
        cmds.setAttr(f'{node}.{at}', cb = 1, k = 0)

    sep_cb(node, True) # -------------------------------------------------------------------------------------------------

add_finger_ats('ctrl_master_fingers_L')

