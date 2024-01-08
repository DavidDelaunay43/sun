from ...utils.imports import *
from .. import (
    curve,
    tools
)
reload(curve)
reload(tools)

def facial_ribbon(edges, face_area: str, offset: float, offset_axis: str):
    """
    """

    # curves
    curve_start = curve.poly_curve_rebuild(edges, constructionHistory = False, 
                        replaceOriginal = True, 
                        rebuildType = 0, 
                        endKnots = 0, 
                        keepRange = 1, 
                        keepEndPoints = True, 
                        keepTangents = True, 
                        spans = 4, 
                        degree = 3, 
                        tolerance = 0.01)
    
    SIDE = tools.get_side_from_node(curve_start)
    
    curve_end = cmds.duplicate(curve_start)

    if offset_axis == 'y':
        cmds.move(0, 0.05, 0, curve_end)

    else: # 'z'
        cmds.move(0, 0, 0.05, curve_end)

    # surface
    rev_normal = 0 if SIDE == 'L' else 1

    ribbon = cmds.loft(curve_start, curve_end, n= f'ribbon_{face_area}_{SIDE}', constructionHistory = False, 
                       uniform = True, 
                       close = False, 
                       autoReverse = True, 
                       degree = 3, 
                       sectionSpans = 1, 
                       reverseSurfaceNormals = False, 
                       polygon = 0, 
                       reverseSurfaceNormals = rev_normal)[0]
    
    u_spans = cmds.getAttr(f"{ribbon}.spansU")
    v_spans = cmds.getAttr(f"{ribbon}.spansV")

    if u_spans == 1 and v_spans !=1:
        u_param = False
        v_param = True

    else: # u_spans != 1 and v_spans ==1
        u_param = True
        v_param = False
