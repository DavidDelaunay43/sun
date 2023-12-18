from ..utils.imports import *
from .constants_maya import TRANSLATE

@type_check()
def pv_cal(jnts: list, mult: float = 1.0) -> str:
    """Create Pole Vector Locator : 

    Arguments :
    jnts = list of strings : 3 items -> name of the three joints

    Keyword arguments : 
    mult = float : distance 
    """

    jnt_a, jnt_b, jnt_c = jnts
    a = om.MVector(cmds.xform(jnt_a, query = True, translation = True, worldSpace = True))
    b = om.MVector(cmds.xform(jnt_b, query = True, translation = True, worldSpace = True))
    c = om.MVector(cmds.xform(jnt_c, query = True, translation = True, worldSpace = True))
    om.MGlobal.displayInfo(f"{a, b, c}")
    
    start_to_end = c - a
    start_to_mid = b - a
    dot = start_to_mid * start_to_end

    projection = float(dot) / float(start_to_end.length())
    start_to_end_normalized = start_to_end.normal()
    projection_vector = start_to_end_normalized * projection
    arrow_vector = start_to_mid - projection_vector
    arrow_vector = arrow_vector * mult
    pv_pos = arrow_vector + b
    om.MGlobal.displayInfo(f"{pv_pos}")

    loc = cmds.spaceLocator()[0]

    cmds.setAttr(f"{loc}.{TRANSLATE}", *pv_pos)
    
    om.MGlobal.displayInfo("Pole vector locator done.")

    return loc
