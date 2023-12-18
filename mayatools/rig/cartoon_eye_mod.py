from ...utils.imports import *

from .. import (
    constants_maya,
    curve,
    display,
    joint,
    offset,
    tools
)
reload(constants_maya)
reload(curve)
reload(display)
reload(joint)
reload(offset)
reload(tools)
from ..constants_maya import *

def cartoon_eyelid(eye_geo: str, edge: list, dir: str, world_up_object: str):
    """
    """
    
    cmds.select(clear = True)
    
    SIDE = tools.find_side(eye_geo)
    EYELID = "eyelid"
    
    grp_crv = cmds.group(name = f"{CURVES}_{EYELID}_{dir}_{SIDE}", empty = True)
    grp_drv = cmds.group(name = f"{DRV}_{EYELID}_{dir}_{SIDE}", empty = True)
    grp_bind = cmds.group(name = f"{BIND}_{EYELID}_{dir}_{SIDE}", empty = True)
    grp_loc = cmds.group(name = f"{LOCATORS}_{EYELID}_{dir}_{SIDE}", empty = True)
    
    # Curves
    curve_ = curve.poly_to_curve(edge, degree = 1, name = f"{CRV}_{EYELID}_{dir}_{SIDE}")
    curve_lodef = cmds.duplicate(curve_, name = f"{CRV}_{EYELID}_{dir}_loDef_{SIDE}")[0]
    cmds.rebuildCurve(curve_lodef, constructionHistory = False, replaceOriginal = True, spans = 4, degree = 3)
    display.color_node(curve_, "orange")
    display.color_node(curve_lodef, "blue_elec")
    display.color_node(curve_lodef, "yellow")
    
    dir_dict = {
        "L": "negative",
        "R": "positive"
    }
    
    curve.ensure_direction(curve_, dir_dict.get(SIDE))
    
    # Wire
    wire_node = cmds.wire(curve_, wire = curve_lodef, name = f"wire_{curve_}", dropoffDistance = (0, 20))[0]
    curve_up_basewire = tools.get_base_wire(wire_node)
    
    cmds.parent([curve_, curve_lodef, curve_up_basewire], grp_crv)
    
    # Naming
    names_dict = {
        0: f"{dir}_int",
        1: f"{dir}_int_01",
        2: f"{dir}_mid",
        3: f"{dir}_ext_01",
        4: f"{dir}_ext"
    }
    
    # Driven joints
    drv_joints = []
    joints = joint.distribute_joints_on_curve(curve_, 5)
    for i, jnt in enumerate(joints):
        base_name = names_dict.get(i)
        drv_jnt = cmds.rename(jnt, f"{DRV}_{EYELID}_{base_name}_{SIDE}")
        cmds.setAttr(f"{drv_jnt}.radius", 2.5)
        display.color_node(drv_jnt, "blue_elec")
        offset.offset_parent_matrix(drv_jnt)
        cmds.parent(drv_jnt, grp_drv)
        drv_joints.append(drv_jnt)
    
    # Skin curve 
    skin_cluster = cmds.skinCluster(*drv_joints, curve_lodef, tsb=True, bm = 0, sm = 0, nw = 1, wd = 0, mi = 3, name = f"skinCluster_{curve_lodef}")[0]
    cmds.setAttr(f"{skin_cluster}.maintainMaxInfluences", 1)
    
    # Locators
    cv_num = curve.get_curve_vertex_count(curve_)
    locators = curve.loc_on_curve(curve_, cv_num, name = f"{LOC}_{EYELID}_{dir}_{SIDE}")
    cmds.parent(locators, grp_loc)
    
    # Bind joints
    center_pos = cmds.xform(eye_geo, query = True, rotatePivot = True, worldSpace = True)
    for num, loc in enumerate(locators):
        
        loc_pos = cmds.xform(loc, query = True, rotatePivot = True, worldSpace = True)
        jnt_start, _ = joint.create_bone(center_pos, loc_pos, name = f"{BIND}_{EYELID}_{dir}_{num+1:02}", side = SIDE)
        
        cmds.aimConstraint(loc, jnt_start, mo = 1, weight =1, aimVector = (1,0,0), upVector = (0,1,0), worldUpType = "object", worldUpObject = world_up_object)
        cmds.parent(jnt_start, grp_bind)
        
    return grp_crv, grp_drv, grp_bind, grp_loc

def cartoon_eye(eye_geo: str, edge_up: list, edge_down: str):
    """
    """

    cmds.select(clear = True)
    
    SIDE = tools.find_side(eye_geo)
    ymax = tools.get_ymax(eye_geo)
    
    grp_locs_eye = cmds.group(name = f"{LOCATORS}_Eye_{SIDE}", empty = True)
    
    # Eye locators
    loc_up = tools.create_loc_center(eye_geo, loc_name = f"{LOC}_Eye_{UP}_{SIDE}")
    tools.set_loc_object_size(loc_up, eye_geo, 0.2)
    display.color_node(loc_up, "green")
    cmds.setAttr(f"{loc_up}.ty", ymax)
    cmds.parent(loc_up, grp_locs_eye)
    offset.offset_parent_matrix(loc_up)
    
    grp_crv_up, grp_drv_up, grp_bind_up, grp_loc_up = cartoon_eyelid(eye_geo, edge_up, UP, loc_up)
    grp_crv_down, grp_drv_down, grp_bind_down, grp_loc_down = cartoon_eyelid(eye_geo, edge_down, DOWN, loc_up)
    
    cmds.group(grp_locs_eye,
               grp_crv_up, grp_drv_up, grp_bind_up, grp_loc_up,
               grp_crv_down, grp_drv_down, grp_bind_down, grp_loc_down,
               name = f"{GRP}_Cartoon_Eye_{SIDE}"
               )
    cmds.select(clear = True)