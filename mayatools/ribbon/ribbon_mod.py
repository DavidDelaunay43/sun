from ...utils.imports import *
from ..constants_maya import *
from ..curve import control, shape_vis, scale_shape

from .. import (
    constants_maya,
    attribute,
    curve,
    joint,
    mathfuncs,
    matrix,
    offset,
    rivet,
    tools,
    display,
)
reload(constants_maya)
reload(attribute)
reload(curve)
reload(joint)
reload(mathfuncs)
reload(matrix)
reload(offset)
reload(rivet)
reload(tools)
reload(display)
from ..constants_maya import *

def ribbon(sub: int = 5, name: str = "ribbon", sinus: bool = False, color: str = "yellow", base_translate: float = 0.0):
    """Create a ribbon with controls and deformers.

    Args:
        sub (int): The subdivision level of the ribbon. Defaults to 5.
        name (str): The base name for the ribbon and its components. Defaults to "ribbon".
        sinus (bool): Flag indicating whether to apply a sine deformer. Defaults to False.
        color (str): The color of the ribbon controls. Defaults to "red".

    Returns:
        tuple: A tuple containing the global controller, two end controls of the ribbon (ctrl_a, ctrl_b),
        and the group containing all the ribbon components (grp_ribbon).
    """
    
    # naming
    name = tools.get_increment_name(name)

    om.MGlobal.displayInfo(f'Ribbon Subdivisions : {sub}')

    # ribbon surface
    surface = cmds.nurbsPlane(name = name, axis = [0, 1, 0], lengthRatio = sub, patchesV = sub, width = 2, constructionHistory = False)[0]
    surface_shape = cmds.listRelatives(surface, shapes = True)[0]
    #cmds.select(f'{surface}.cv[0:3][0:{sub+2}]')
    #mel.eval('rotate -r -p 0cm 0cm 0cm -os -fo 0 -90 0 ;')
    cmds.setAttr(f'{surface}.ry', -90)
    cmds.makeIdentity(surface, apply = True, r = True)
    
    cmds.select(clear = True)
    cmds.setAttr(f'{surface}.tx', base_translate)

    XMIN, XMAX = mathfuncs.xmin(surface), mathfuncs.xmax(surface)
    XCENTER = cmds.objectCenter(surface_shape)[0]

    # create groups
    show_grp = cmds.group(empty = True, name = f"{SHOW}_{name}")
    hide_grp = cmds.group(empty = True, name = f"{HIDE}_{name}")
    cmds.setAttr(f'{hide_grp}.visibility', 0)

    tools.ensure_group(show_grp, SHOW)
    tools.ensure_group(hide_grp, HIDE)
    
    # create controls
    ctrl_global = f"{CTRL}_global_{name}"

    ctrl_a = f"{CTRL}_A_{name}"
    ctrl_b = f"{CTRL}_B_{name}"
    ctrl_mid = f"{CTRL}_Mid_{name}"
    ctrl_mid_move = f"{CTRL}_Mid_{name}_{MOVE}"

    curve.control("squashed octagon", name = ctrl_global, color = color)
    curve.control("square", name = ctrl_a, color = color)
    curve.control("square", name = ctrl_b, color = color)
    curve.control("sphere", name = ctrl_mid, color = color)
    cmds.group(name = ctrl_mid_move, empty = True, world = True)

    attribute.vis_no_keyable([ctrl_a, ctrl_b, ctrl_mid, ctrl_global])

    shape_vis([ctrl_a, ctrl_b, ctrl_global], 0)

    cmds.setAttr(f"{ctrl_a}.tx", XMIN)
    cmds.setAttr(f"{ctrl_b}.tx", XMAX)
    cmds.setAttr(f'{ctrl_mid}.tx', XCENTER)
    cmds.setAttr(f'{ctrl_mid_move}.tx', XCENTER)
    cmds.setAttr(f'{ctrl_global}.tx', XCENTER)

    cmds.parent(ctrl_a, ctrl_global)
    cmds.parent(ctrl_b, ctrl_global)
    cmds.parent(ctrl_mid, ctrl_mid_move)
    cmds.parent(ctrl_mid_move, ctrl_global)
    cmds.parent(surface, ctrl_global)
    
    offset.offset_parent_matrix([ctrl_a, ctrl_b, ctrl_mid_move])
    attribute.cb_attributes(ctrl_mid, ats = ["rx", "ry", "rz", "sx", "sy", "sz"], lock = True, hide = True)

    # constrain ctrl_mid
    pma_node = cmds.createNode("plusMinusAverage", name = f"{ctrl_mid}_pma")
    cmds.setAttr(f"{pma_node}.operation", 3)
    cmds.connectAttr(f"{ctrl_a}.{TRANSLATE}", f"{pma_node}.input3D[0]")
    cmds.connectAttr(f"{ctrl_b}.{TRANSLATE}", f"{pma_node}.input3D[1]")
    cmds.connectAttr(f'{pma_node}.output3Dx', f"{ctrl_mid}_{MOVE}.tx", force = True)
    cmds.connectAttr(f'{pma_node}.output3Dy', f"{ctrl_mid}_{MOVE}.ty", force = True)
    cmds.connectAttr(f'{pma_node}.output3Dz', f"{ctrl_mid}_{MOVE}.tz", force = True)

    # create rivets & joints
    grp_rivets = rivet.rivet_nurbs(surface, "v", rivet_num = sub, size = 0.4, jnt = True)
    cmds.parent(grp_rivets, show_grp)

    rivets = cmds.listRelatives(grp_rivets, children = True, shapes = False)
    print(f'RIVETS {rivets}')
    for riv in rivets:
        #cmds.connectAttr(f"{ctrl_global}.{SCALE}", f"{rivet}.{SCALE}")
        matrix.matrix_constraint(ctrl_global, riv, mo = False, s = True)

    # Deformers
    # blendshape
    copy = cmds.duplicate(surface)
    bshp = cmds.rename(copy, f"{BSHP}_{name}")
    cmds.parent(bshp, hide_grp)

    bshp_node = cmds.blendShape(bshp, surface, n = f"{BSHP}_{name}")[0]
    cmds.setAttr(f"{bshp_node}.{bshp}", 1)

    # curve & wire deformer
    curve_pos = [(XMIN, 0, 0), (XCENTER, 0, 0), (XMAX, 0, 0)]
    curve_master = cmds.curve(n = f"crv_{name}", d = 2, p = curve_pos)
    cmds.wire(bshp, w = curve_master, dds = (0, 20))
    curve_basewire = f"{curve_master}BaseWire"
    cmds.parent(curve_master, hide_grp)
    cmds.parent(curve_basewire, hide_grp)

    curve_shape = cmds.listRelatives(curve_master, shapes = True)[0]

    # control points
    ctrl_pnt_a = cmds.group(n = f"controlPoint_A_{name}", em = 1, w = 1)
    ctrl_pnt_b = cmds.group(n = f"controlPoint_B_{name}", em = 1,w = 1)
    ctrl_pnt_mid = cmds.group(n = f"controlPoint_Mid_{name}", em = 1,w = 1)
    ctrl_pnt_mid_move = cmds.group(n = f"controlPoint_Mid_{name}_{MOVE}", em = 1, w = 1)

    cmds.setAttr(f"{ctrl_pnt_a}.tx", XMIN)
    cmds.setAttr(f"{ctrl_pnt_b}.tx", XMAX)
    cmds.setAttr(f'{ctrl_pnt_mid}.tx', XCENTER)
    cmds.setAttr(f'{ctrl_pnt_mid_move}.tx', XCENTER)
    offset.offset_parent_matrix([ctrl_pnt_a, ctrl_pnt_b, ctrl_pnt_mid_move])
    
    cmds.parent(ctrl_pnt_mid, ctrl_pnt_mid_move)
    cmds.parent(ctrl_pnt_a, hide_grp)
    cmds.parent(ctrl_pnt_b, hide_grp)
    cmds.parent(ctrl_pnt_mid_move, hide_grp)

    cmds.matchTransform(ctrl_pnt_a, ctrl_a, pos = 1)
    cmds.matchTransform(ctrl_pnt_b, ctrl_b, pos = 1)
    offset.offset_parent_matrix([ctrl_pnt_a, ctrl_pnt_b])

    # create decompose matrix nodes
    deco_mtx_a = cmds.createNode("decomposeMatrix", n = f"{ctrl_pnt_a}_{DECO_MTX}")
    deco_mtx_mid = cmds.createNode("decomposeMatrix", n = f"{ctrl_pnt_mid}_{DECO_MTX}")
    deco_mtx_b = cmds.createNode("decomposeMatrix", n = f"{ctrl_pnt_b}_{DECO_MTX}")

    # connections controls & control points
    cmds.connectAttr(f"{ctrl_a}.t", f"{ctrl_pnt_a}.t")
    cmds.connectAttr(f"{ctrl_b}.t", f"{ctrl_pnt_b}.t")
    cmds.connectAttr(f"{ctrl_mid}.t", f"{ctrl_pnt_mid}.t")
    cmds.connectAttr(f"{ctrl_mid_move}.t", f"{ctrl_pnt_mid_move}.t")

    cmds.connectAttr(f"{ctrl_pnt_a}.{W_MTX}", f"{deco_mtx_a}.{INPUT_MTX}")
    cmds.connectAttr(f"{ctrl_pnt_mid}.{W_MTX}", f"{deco_mtx_mid}.{INPUT_MTX}")
    cmds.connectAttr(f"{ctrl_pnt_b}.{W_MTX}", f"{deco_mtx_b}.{INPUT_MTX}")

    cmds.connectAttr(f"{deco_mtx_a}.{OUTPUT_T}", f"{curve_shape}.controlPoints[0]")
    cmds.connectAttr(f"{deco_mtx_mid}.{OUTPUT_T}", f"{curve_shape}.controlPoints[1]")
    cmds.connectAttr(f"{deco_mtx_b}.{OUTPUT_T}", f"{curve_shape}.controlPoints[2]")

    # twist deformer
    twist_deformer, twist_def_handle = cmds.nonLinear(bshp, type = "twist", name = f"twist_{name}")
    cmds.rotate(0, 0, "90deg", twist_def_handle)
    cmds.parent(twist_def_handle, hide_grp)

    cmds.connectAttr(f"{ctrl_a}.rx", f"{twist_deformer}.endAngle")
    cmds.connectAttr(f"{ctrl_b}.rx", f"{twist_deformer}.startAngle")

    # sine deformer
    if sinus:
        pass

    tools.ensure_group(ctrl_global, CTRLS)

    cmds.select(cl = 1)
    om.MGlobal.displayInfo(f"Ribbon {surface} done.")

    return ctrl_global, ctrl_a, ctrl_b, surface, grp_rivets

def bone_ribbon(start: str, end: str, orient: float = 0.0, color: str = 'yellow', sub: int = 5, base_translate: float = 0.0):
    """Create a ribbon between two specified joints in 3D space.

    Args:
        start (str): The name of the starting joint of the ribbon.
        end (str): The name of the end joint of the ribbon.

    Returns:
        tuple: A tuple containing the two controllers (ctrl_a, ctrl_b) of the created ribbon.
    """

    SIDE = tools.get_side_from_node(start)
    fac_dict = {'L': 0.5, 'R': -0.5}
    rot_dict = {'L': 0, 'R': 180}
    om.MGlobal.displayInfo(f'SIDE : {SIDE}')
    
    # naming
    limb_name = start.split("_", 1)[1] if '_' in start else start
    ribbon_name = f"ribbon_{limb_name}"

    ctrl_global, ctrl_a, ctrl_b, surface, grp_rivets = ribbon(sub = sub, name = ribbon_name, color = color, base_translate = base_translate)

    # set ribbon scale
    dist_jnts =  mathfuncs.distance_btw(start, end)
    size_ribbon = sub * 2

    scale_factor = dist_jnts / size_ribbon

    ats = "sx", "sy", "sz"
    for at in ats:
        cmds.setAttr(f"{ctrl_global}.{at}", scale_factor)
        cmds.setAttr(f"{ctrl_global}.{at}", lock = 1)

    fac = fac_dict[SIDE]

    # set ribbon position and orientation
    cmds.matchTransform(ctrl_global, start)
    cmds.move(dist_jnts * fac, ctrl_global, x = 1, objectSpace = 1, r = 1, wd = 1)

    if SIDE == 'R':
        rotx = cmds.getAttr(f'{ctrl_global}.rx')-180
        cmds.rotate(rotx, ctrl_global, x = True, objectSpace = True)
        cmds.select(ctrl_global)
        mel.eval('rotate -r -os -fo 0 -180 0 ; select -cl  ;')

    # constrain ribbon
    matrix.matrix_constraint(start, ctrl_global, mo = True, t = True, r = True)

    return ctrl_a, ctrl_b, scale_factor, surface, grp_rivets

def preserve_joint(start: str, end: str):

    # naming
    end_name = end.split("_", 1)[1]

    # create preserve joint
    preserve_jnt = joint.curve_joint(name = f"bind_preserve_{end_name}")
    cmds.matchTransform(preserve_jnt, end)
    cmds.makeIdentity(preserve_jnt, r = 1, a = 1)
    offset.move(preserve_jnt)
    offset.offset_parent_matrix(f"{preserve_jnt}_{MOVE}")
    attribute.cb_attributes(preserve_jnt, ats = ["rx", "ry", "rz", "sx", "sy", "sz"], lock = True, hide = True)

    # constrain preserve joint
    matrix.matrix_constraint(end, f"{preserve_jnt}_{MOVE}", t = 1, mo = 0)

    # constrain by expression
    string_exp = f""" // Exp Preserve Joint {end}

    // ctrl
    {preserve_jnt}_move.ry = ({start}.ry + {end}.ry) * 0.5;
    {preserve_jnt}_move.rz = {start}.rz;

    """

    cmds.expression(s = string_exp, n = f"Exp_Preserve_{end_name}", ae = 1, uc = "all")
    om.MGlobal.displayInfo(f"Preserve joint done on {end}.")

    return preserve_jnt

def preserve_joint_02(start: str, end: str, match_rotation: bool = False, color: str = 'yellow'):
    '''
    '''

    cmds.select(clear = True)
    # naming
    end_name = end.split("_", 1)[1]

    # create joint
    preserve_jnt = cmds.joint(name = f'bind_preserve_{end_name}')
    cmds.matchTransform(preserve_jnt, end)
    cmds.makeIdentity(preserve_jnt, apply = True, rotate = True)
    display.color_node(preserve_jnt, 'white')
    tools.ensure_group(preserve_jnt, JOINTS)
    offset.move_op_matrix(preserve_jnt)

    # create ctrl
    if match_rotation:
        #preserve_ctrl = cmds.circle(normal = [1, 0, 0], constructionHistory = False, name = f'{CTRL}_preserve_{end_name}')[0]
        preserve_ctrl = curve.control("sphere", f'{CTRL}_preserve_{end_name}')
        cmds.matchTransform(preserve_ctrl, end, rotation = True)

    else:
        #preserve_ctrl = cmds.circle(normal = [0, 1, 0], constructionHistory = False, name = f'{CTRL}_preserve_{end_name}')[0]
        preserve_ctrl = curve.control("sphere", f'{CTRL}_preserve_{end_name}')
        cmds.matchTransform(preserve_ctrl, end, position = True)

    attribute.vis_no_keyable(preserve_ctrl)
    display.color_node(preserve_ctrl, color)
    tools.ensure_group(preserve_ctrl, CTRLS)
    offset.move_hook_op_matrix(preserve_ctrl)

    # create constraints
    matrix.matrix_constraint(preserve_ctrl, f'{preserve_jnt}_{MOVE}', t = True)
    matrix.matrix_constraint(start, f'{preserve_ctrl}_{HOOK}', r = True, mo = True)
    matrix.matrix_constraint(end, f'{preserve_ctrl}_{MOVE}', t = True)

    # create connections
    average_node = cmds.createNode('plusMinusAverage', name = f'average_{preserve_jnt}')
    div_node = cmds.createNode('multiplyDivide', name = f'div_{preserve_ctrl}')

    cmds.setAttr(f'{average_node}.operation', 3)
    cmds.setAttr(f'{div_node}.input2X', 0.5)

    cmds.connectAttr(f'{start}.rotateY', f'{average_node}.input1D[0]')
    cmds.connectAttr(f'{end}.rotateY', f'{average_node}.input1D[1]')
    cmds.connectAttr(f'{end}.rotateY', f'{div_node}.input1X')

    #cmds.connectAttr(f'{start}.rotateZ', f'{preserve_jnt}.rotateZ')
    cmds.connectAttr(f'{average_node}.output1D', f'{preserve_jnt}.rotateY')

    if match_rotation:
        cmds.connectAttr(f'{div_node}.outputX', f'{preserve_ctrl}_{MOVE}.rotateY')
    else:
        cmds.connectAttr(f'{div_node}.outputX', f'{preserve_ctrl}_{MOVE}.rotateX')


    om.MGlobal.displayInfo(f'Preserve joint done on : {start} and {end}.')

    attribute.cb_attributes(preserve_ctrl, ats = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'], lock = True, hide = True)

    return preserve_ctrl

def preserve_control(start: str, end: str, match_rotation: bool = False, color: str = 'yellow'):
    '''
    '''

    SIDE = tools.get_side_from_node(start)

    cmds.select(clear = True)
    # naming
    end_name = end.split("_", 1)[1]

    # create ctrl
    if match_rotation:
        preserve_ctrl = curve.control("sphere", f'{CTRL}_preserve_{end_name}')
        cmds.matchTransform(preserve_ctrl, end, rotation = True)

    else:
        preserve_ctrl = control("sphere", f'{CTRL}_preserve_{end_name}')
        cmds.matchTransform(preserve_ctrl, end, position = True)

    attribute.vis_no_keyable(preserve_ctrl)
    display.color_node(preserve_ctrl, color)
    tools.ensure_group(preserve_ctrl, CTRLS)
    offset.move_hook_op_matrix(preserve_ctrl)

    cmds.matchTransform(f'{preserve_ctrl}_{HOOK}', end)

    if SIDE == 'R':
        cmds.setAttr(f'{preserve_ctrl}_{HOOK}.r', 90, 0 , -90)
        
    offset.offset_parent_matrix(f'{preserve_ctrl}_{HOOK}')
    matrix.matrix_constraint(start, f'{preserve_ctrl}_{HOOK}', r = True, mo = True)
    matrix.matrix_constraint(end, f'{preserve_ctrl}_{MOVE}', t = True)

    # create connections
    div_node = cmds.createNode('multiplyDivide', name = f'div_{preserve_ctrl}')
    cmds.setAttr(f'{div_node}.input2X', 0.5)
    cmds.connectAttr(f'{end}.rotateY', f'{div_node}.input1X')

    if match_rotation:
        cmds.connectAttr(f'{div_node}.outputX', f'{preserve_ctrl}_{MOVE}.rotateY')
    else:
        cmds.connectAttr(f'{div_node}.outputX', f'{preserve_ctrl}_{MOVE}.rotateX')


    om.MGlobal.displayInfo(f'Preserve joint done on : {start} and {end}.')

    attribute.cb_attributes(preserve_ctrl, ats = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'], lock = True, hide = True)

    return preserve_ctrl

def limb_ribbon(
    ik_start: str, 
    ik_mid: str, 
    ik_end: str,
    orient: float = 90.0,
    preserve_match_rotation: bool = False,
    color: str = 'yellow', 
    sub: int = 5
    ):
    """
    """

    # create ribbons
    ctrl_start_a, ctrl_end_a, scale_factor, _, _ = bone_ribbon(ik_start, ik_mid, orient = orient, color = color, sub=sub)
    ctrl_start_b, ctrl_end_b, _, _, _ = bone_ribbon(ik_mid, ik_end, orient = orient, color = color, sub=sub)
    matrix.matrix_constraint(ik_start, ctrl_start_a, t = 1, mo = 1)
    matrix.matrix_constraint(ik_end, ctrl_end_b, t = 1, mo = 1)

    # add preserve joint
    preserve_ctrl = preserve_joint_02(ik_start, ik_mid, match_rotation = preserve_match_rotation, color = color)
    matrix.matrix_constraint(preserve_ctrl, ctrl_end_a, t = 1, mo = 1)
    matrix.matrix_constraint(preserve_ctrl, ctrl_start_b, t = 1, mo = 1)

    scale_shape(preserve_ctrl, scale_factor)

    om.MGlobal.displayInfo(f"Limb ribbons done on {ik_start}, {ik_mid} and {ik_end}.")
    return ctrl_start_a, ctrl_end_b

def limb_ribbon_assemble(
        ik_start: str,
        ik_mid: str,
        ik_end: str,
        switch_node: str,
        preserve_match_rotation: bool = False,
        orient: float = 90.0,
        color: str = 'yellow',
        compense_translate: bool = True, 
        sub: int = 5
    ):
    '''
    '''

    # create ribbons
    ctrl_start_a, ctrl_end_a, scale_factor, surface_a, grp_rivets_a = bone_ribbon(ik_start, ik_mid, orient = orient, color = color, sub=sub, base_translate = sub*-1)
    ctrl_start_b, ctrl_end_b, _, surface_b, grp_rivets_b = bone_ribbon(ik_mid, ik_end, orient = orient, color = color, sub=sub, base_translate = sub*1)
    matrix.matrix_constraint(ik_start, ctrl_start_a, t = 1, mo = 1)
    matrix.matrix_constraint(ik_end, ctrl_end_b, t = 1, mo = 1)

    preserve_ctrl = preserve_control(ik_start, ik_mid, match_rotation = preserve_match_rotation, color = color)
    matrix.matrix_constraint(preserve_ctrl, ctrl_end_a, t = 1, mo = 1)
    matrix.matrix_constraint(preserve_ctrl, ctrl_start_b, t = 1, mo = 1)
    scale_shape(preserve_ctrl, scale_factor)

    ribbon_assemble = assemble_ribbon(surface_a, surface_b, grp_rivets_a, grp_rivets_b, switch_node, sub = sub)
    ribbon_assemble_shape = cmds.listRelatives(ribbon_assemble, shapes = True)[0]

    # CREATE PRESERVE JOINT ---------------------------------------------------------------------------------------------------------------
    preserve_jnt = cmds.joint(name = f'bind_preserve_{ik_mid.split("_", 1)[1]}')
    tools.ensure_set(preserve_jnt)
    display.color_node(preserve_jnt, 'white')
    tools.ensure_group(preserve_jnt, SHOW)
    posi_node, _, _, _ = rivet.connect_rivet(preserve_jnt, ribbon_assemble_shape, 0.5, 'v')

    # connect on slide
    rv_node = cmds.createNode('remapValue', name = f'rv_{preserve_jnt}')
    cmds.setAttr(f'{rv_node}.outputMax', 0)
    cmds.connectAttr(f'{switch_node}.slide', f'{rv_node}.inputValue')
    cmds.connectAttr(f'{preserve_jnt}.parameter_v', f'{rv_node}.outputMin')
    cmds.connectAttr(f'{rv_node}.outValue', f'{posi_node}.parameterV', force = True)

    # compense translate
    if compense_translate:
        rv_node_translate = cmds.createNode('remapValue', name = f'rv_translate_{preserve_jnt}')
        cmds.setAttr(f'{rv_node_translate}.inputMin', -120)
        cmds.setAttr(f'{rv_node_translate}.inputMax', 120)
        cmds.setAttr(f'{rv_node_translate}.outputMin', 0.19)
        cmds.setAttr(f'{rv_node_translate}.outputMax', -0.19)
        cmds.connectAttr(f'{ik_mid}.ry', f'{rv_node_translate}.inputValue')


        rv_node_slide_translate = cmds.createNode('remapValue', name = f'rv_slide_translate_{preserve_jnt}')
        cmds.setAttr(f'{rv_node_slide_translate}.inputMax', 0.1)
        cmds.setAttr(f'{rv_node_slide_translate}.outputMax', 0)
        cmds.connectAttr(f'{switch_node}.slide', f'{rv_node_slide_translate}.inputValue')
        cmds.connectAttr(f'{rv_node_translate}.outValue', f'{rv_node_slide_translate}.outputMin')

        cmds.connectAttr(f'{rv_node_slide_translate}.outValue', f'{preserve_jnt}.tz')

    # connect rotate
    cmds.connectAttr(f'{ik_start}.rz', f'{preserve_jnt}.rz')

    om.MGlobal.displayInfo('Limb Ribbon Assemnle done.')

    return ctrl_start_a, ctrl_end_b, ribbon_assemble_shape

def assemble_ribbon(ribbon_a: str, ribbon_b: str, grp_rivets_a: str, grp_rivets_b: str, switch_node: str, sub: int):
    '''
    '''

    attribute.sep_cb(switch_node)
    cmds.addAttr(switch_node, ln = 'slide', nn = 'Slide', at = 'float', min = 0, max = 1, dv = 0, k = 1)
    cmds.addAttr(switch_node, ln = 'follow_slide', nn = 'Follow Slide', at = 'float', min = 0, max = 1, dv = 0, k = 1)

    ribbon_assemble = cmds.duplicate(ribbon_a)
    ribbon_assemble = cmds.rename(ribbon_assemble, f'{ribbon_a}_assemble')
    ribbon_assemble_shape, ribbon_assemble_shape_orig = cmds.listRelatives(ribbon_assemble, shapes = True)
    cmds.delete(ribbon_assemble_shape_orig)

    cmds.setAttr(f'{ribbon_a}.v', 0)
    cmds.setAttr(f'{ribbon_b}.v', 0)

    ribbon_a_shape = cmds.listRelatives(ribbon_a, shapes = True)[0]
    ribbon_b_shape = cmds.listRelatives(ribbon_b, shapes = True)[0]

    attach_surface = cmds.createNode('attachSurface', name = f'attachSurface_{ribbon_a}_{ribbon_b}')
    cmds.setAttr(f'{attach_surface}.directionU', 0)
    cmds.connectAttr(f'{ribbon_a_shape}.worldSpace[0]', f'{attach_surface}.inputSurface1')
    cmds.connectAttr(f'{ribbon_b_shape}.worldSpace[0]', f'{attach_surface}.inputSurface2')

    rebuild_surface = cmds.createNode('rebuildSurface', name = f'rebuildSurface_{ribbon_assemble}')
    cmds.setAttr(f'{rebuild_surface}.spansU', 0)
    cmds.setAttr(f'{rebuild_surface}.spansV', sub * 2)
    cmds.connectAttr(f'{attach_surface}.outputSurface', f'{rebuild_surface}.inputSurface')

    cmds.connectAttr(f'{rebuild_surface}.outputSurface', f'{ribbon_assemble_shape}.create')

    rivets_a = cmds.listRelatives(grp_rivets_a, children = True)
    rivets_b = cmds.listRelatives(grp_rivets_b, children = True)

    rivets = rivets_a + rivets_b

    for i, rivet in enumerate(rivets):

        param = i * (1/len(rivets)) + (1/(len(rivets)*2))

        try:
            cmds.setAttr(f'{rivet}.parameter_v', param)
        except:
            cmds.setAttr(f'{rivet}.parameter_u', param)

        posi_node = cmds.listConnections(rivet, type = 'pointOnSurfaceInfo')[0]
        cmds.connectAttr(f'{ribbon_assemble_shape}.worldSpace[0]', f'{posi_node}.inputSurface', force = True)

        rv_node = cmds.createNode('remapValue', name = f'rv_slide_{rivet}')
        cmds.setAttr(f'{rv_node}.outputMax', 0)
        cmds.connectAttr(f'{switch_node}.slide', f'{rv_node}.inputValue')
        try:
            cmds.connectAttr(f'{rivet}.parameter_v', f'{rv_node}.outputMin')
        except:
            cmds.connectAttr(f'{rivet}.parameter_u', f'{rv_node}.outputMin')
        cmds.connectAttr(f'{rv_node}.outValue', f'{posi_node}.parameterV', force = True)

    # CORRECTIF !!!!!
    for i, rivet in enumerate(rivets_a, start = 0):

        posi_node_base = cmds.createNode('pointOnSurfaceInfo', name = f'posi_base_{rivet}')
        cmds.setAttr(f'{posi_node_base}.turnOnPercentage', 1)

        param = i * (1/len(rivets_a)) + (1/(len(rivets_a)*2))

        try:
            cmds.setAttr(f'{posi_node_base}.parameterU', 0.5)
            cmds.setAttr(f'{posi_node_base}.parameterV', param)

        except:
            cmds.setAttr(f'{posi_node_base}.parameterV', 0.5)
            cmds.setAttr(f'{posi_node_base}.parameterU', param)
        
        cmds.connectAttr(f'{ribbon_a_shape}.worldSpace[0]', f'{posi_node_base}.inputSurface')

        rv_node = cmds.listConnections(rivet, type = 'remapValue')[0]
        posi_node = cmds.listConnections(rv_node, type = 'pointOnSurfaceInfo')[0]
        vect_prod_node = cmds.listConnections(posi_node, type = 'vectorProduct')[0]
        matrix_node = cmds.listConnections(vect_prod_node, type = 'fourByFourMatrix')[0]

        attribute.disconnect_attributes(matrix_node, ['in00', 'in01', 'in02', 'in10', 'in11', 'in12', 'in30', 'in31', 'in32'])
        attribute.disconnect_attributes(vect_prod_node, ['input1', 'input2'])

        expression = f'''
        float $slide = {switch_node}.slide;

        if ($slide == 0){{
            {matrix_node}.in30 = {posi_node_base}.positionX;
            {matrix_node}.in31 = {posi_node_base}.positionY;
            {matrix_node}.in32 = {posi_node_base}.positionZ;

            {matrix_node}.in00 = {posi_node_base}.normalX;
            {matrix_node}.in01 = {posi_node_base}.normalY;
            {matrix_node}.in02 = {posi_node_base}.normalZ;

            {matrix_node}.in10 = {posi_node_base}.tangentVx;
            {matrix_node}.in11 = {posi_node_base}.tangentVy;
            {matrix_node}.in12 = {posi_node_base}.tangentVz;

            {vect_prod_node}.input1X = {posi_node_base}.normalX;
            {vect_prod_node}.input1Y = {posi_node_base}.normalY;
            {vect_prod_node}.input1Z = {posi_node_base}.normalZ;

            {vect_prod_node}.input2X = {posi_node_base}.tangentVx;
            {vect_prod_node}.input2Y = {posi_node_base}.tangentVy;
            {vect_prod_node}.input2Z = {posi_node_base}.tangentVz;
        }}

        else {{
            {matrix_node}.in30 = {posi_node}.positionX;
            {matrix_node}.in31 = {posi_node}.positionY;
            {matrix_node}.in32 = {posi_node}.positionZ;

            {matrix_node}.in00 = {posi_node}.normalX;
            {matrix_node}.in01 = {posi_node}.normalY;
            {matrix_node}.in02 = {posi_node}.normalZ;

            {matrix_node}.in10 = {posi_node}.tangentVx;
            {matrix_node}.in11 = {posi_node}.tangentVy;
            {matrix_node}.in12 = {posi_node}.tangentVz;

            {vect_prod_node}.input1X = {posi_node}.normalX;
            {vect_prod_node}.input1Y = {posi_node}.normalY;
            {vect_prod_node}.input1Z = {posi_node}.normalZ;

            {vect_prod_node}.input2X = {posi_node}.tangentVx;
            {vect_prod_node}.input2Y = {posi_node}.tangentVy;
            {vect_prod_node}.input2Z = {posi_node}.tangentVz;
        }}
        '''
        cmds.expression(string = expression, name = f'Exp_cond_slide_{rivet}')

    for i, rivet in enumerate(rivets_b, start = 0):

        posi_node_base = cmds.createNode('pointOnSurfaceInfo', name = f'posi_base_{rivet}')
        cmds.setAttr(f'{posi_node_base}.turnOnPercentage', 1)

        param = i * (1/len(rivets_b)) + (1/(len(rivets_b)*2))

        try:
            cmds.setAttr(f'{posi_node_base}.parameterU', 0.5)
            cmds.setAttr(f'{posi_node_base}.parameterV', param)

        except:
            cmds.setAttr(f'{posi_node_base}.parameterV', 0.5)
            cmds.setAttr(f'{posi_node_base}.parameterU', param)
        
        cmds.connectAttr(f'{ribbon_b_shape}.worldSpace[0]', f'{posi_node_base}.inputSurface')

        rv_node = cmds.listConnections(rivet, type = 'remapValue')[0]
        posi_node = cmds.listConnections(rv_node, type = 'pointOnSurfaceInfo')[0]
        vect_prod_node = cmds.listConnections(posi_node, type = 'vectorProduct')[0]
        matrix_node = cmds.listConnections(vect_prod_node, type = 'fourByFourMatrix')[0]

        attribute.disconnect_attributes(matrix_node, ['in00', 'in01', 'in02', 'in10', 'in11', 'in12', 'in30', 'in31', 'in32'])
        attribute.disconnect_attributes(vect_prod_node, ['input1', 'input2'])

        expression = f'''
        float $slide = {switch_node}.slide;

        if ($slide == 0){{
            {matrix_node}.in30 = {posi_node_base}.positionX;
            {matrix_node}.in31 = {posi_node_base}.positionY;
            {matrix_node}.in32 = {posi_node_base}.positionZ;

            {matrix_node}.in00 = {posi_node_base}.normalX;
            {matrix_node}.in01 = {posi_node_base}.normalY;
            {matrix_node}.in02 = {posi_node_base}.normalZ;

            {matrix_node}.in10 = {posi_node_base}.tangentVx;
            {matrix_node}.in11 = {posi_node_base}.tangentVy;
            {matrix_node}.in12 = {posi_node_base}.tangentVz;

            {vect_prod_node}.input1X = {posi_node_base}.normalX;
            {vect_prod_node}.input1Y = {posi_node_base}.normalY;
            {vect_prod_node}.input1Z = {posi_node_base}.normalZ;

            {vect_prod_node}.input2X = {posi_node_base}.tangentVx;
            {vect_prod_node}.input2Y = {posi_node_base}.tangentVy;
            {vect_prod_node}.input2Z = {posi_node_base}.tangentVz;
        }}

        else {{
            {matrix_node}.in30 = {posi_node}.positionX;
            {matrix_node}.in31 = {posi_node}.positionY;
            {matrix_node}.in32 = {posi_node}.positionZ;

            {matrix_node}.in00 = {posi_node}.normalX;
            {matrix_node}.in01 = {posi_node}.normalY;
            {matrix_node}.in02 = {posi_node}.normalZ;

            {matrix_node}.in10 = {posi_node}.tangentVx;
            {matrix_node}.in11 = {posi_node}.tangentVy;
            {matrix_node}.in12 = {posi_node}.tangentVz;

            {vect_prod_node}.input1X = {posi_node}.normalX;
            {vect_prod_node}.input1Y = {posi_node}.normalY;
            {vect_prod_node}.input1Z = {posi_node}.normalZ;

            {vect_prod_node}.input2X = {posi_node}.tangentVx;
            {vect_prod_node}.input2Y = {posi_node}.tangentVy;
            {vect_prod_node}.input2Z = {posi_node}.tangentVz;
        }}
        '''
        cmds.expression(string = expression, name = f'Exp_cond_slide_{rivet}')

    cmds.setAttr(f'{ribbon_a}.v', 0)
    cmds.setAttr(f'{ribbon_b}.v', 0)

    # SINE
    attribute.sep_cb(switch_node)
    cmds.addAttr(switch_node, ln = 'sine', nn = 'Sine', at = 'bool', k = 1)
    cmds.addAttr(switch_node, ln = 'amplitude', nn = 'Amplitude', at = 'float', dv = 0, k = 1)
    cmds.addAttr(switch_node, ln = 'wavelength', nn = 'Wavelength', at = 'float', min = 0.1, dv = 2, k = 1)
    cmds.addAttr(switch_node, ln = 'offset', nn = 'Offset', at = 'float', dv = 0, k = 1)
    cmds.addAttr(switch_node, ln = 'dropoff', nn = 'Dropoff', at = 'float', min = -1, max = 1, dv = 1, k = 1)

    attribute.sep_cb(switch_node, True)

    cmds.addAttr(switch_node, ln = 'translate_sine', nn = 'Translate', at = 'float', dv = 0, k = 1) # ty
    cmds.addAttr(switch_node, ln = 'scale_length_sine', nn = 'Scale Length', at = 'float', dv = 1, k = 1) # sx
    cmds.addAttr(switch_node, ln = 'scale_heigth_sine', nn = 'Scale Heigth', at = 'float', dv = 1, k = 1) # sy
    cmds.addAttr(switch_node, ln = 'rotate_foward_sine', nn = 'Rotate Forward', at = 'float', dv = 0, k = 1) # rz
    cmds.addAttr(switch_node, ln = 'rotate_side_sine', nn = 'Rotate Side', at = 'float', dv = 0, k = 1) # ry

    bshape_ribbon_a = f'BShape_{ribbon_a}'
    bshape_ribbon_b = f'BShape_{ribbon_b}'

    cmds.select(f'{bshape_ribbon_a}.cv[0:3][0:{sub+2}]', replace = True)
    cmds.select(f'{bshape_ribbon_b}.cv[0:3][0:{sub+2}]', toggle = True)

    sine_node, sine_handle = cmds.nonLinear(type = 'sine', name = f'sine_{bshape_ribbon_a}_{bshape_ribbon_b}')
    cmds.setAttr(f'{sine_handle}.v', 0)
    tools.ensure_group(sine_handle, HIDE)
    cmds.setAttr(f'{sine_handle}.rz', 90)

    ats = ('wavelength', 'offset', 'dropoff', 'amplitude')
    for at in ats:
        cmds.connectAttr(f'{switch_node}.{at}', f'{sine_node}.{at}')

    cmds.connectAttr(f'{switch_node}.sine', f'{sine_node}.envelope')

    offset.offset_parent_matrix(sine_handle)
    ats_switch = ('translate_sine', 'scale_length_sine', 'scale_heigth_sine', 'rotate_foward_sine', 'rotate_side_sine')
    ats_sine = ("ty", "sy", "sx", "rz", "ry")

    for at_switch, at_sine in zip(ats_switch, ats_sine):
        cmds.connectAttr(f'{switch_node}.{at_switch}', f'{sine_handle}.{at_sine}')

    return ribbon_assemble
