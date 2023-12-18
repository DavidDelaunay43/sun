from ...utils.imports import *

from .. import (
    constants_maya,
    attribute,
    curve,
    display,
    joint,
    mathfuncs,
    matrix,
    offset,
    tools,
    rivet
)
reload(constants_maya)
reload(attribute)
reload(curve)
reload(display)
reload(joint)
reload(mathfuncs)
reload(matrix)
reload(offset)
reload(tools)
reload(rivet)
from ..constants_maya import *

def blend_colors(fk_jnt: str, ik_jnt: str, name: str = "blendColors") -> str:
    """Blend colors between two joints.

    Args:
        fk_jnt (str): The name of the first joint.
        ik_jnt (str): The name of the second joint.
        name (str): The name for the blendColors node. Defaults to "blendColors".

    Returns:
        str: The name of the blendColors node.
    """

    bc_node = cmds.shadingNode("blendColors", n = name, asUtility = 1)
    ats = ("blender", "color1R", "color1G", "color1B", "color2R", "color2G", "color2B")
    
    for at in ats:
        cmds.setAttr(f"{bc_node}.{at}", 0)

    cmds.connectAttr(f"{fk_jnt}.rotate", f"{bc_node}.color2")
    cmds.connectAttr(f"{bc_node}.output", f"{ik_jnt}.rotate")

    return bc_node

def pair_blend(fk_jnt: str, ik_jnt: str, name: str = "pairBlend") -> str:
    """Create a pairBlend node to blend rotation between two joints.

    Args:
        fk_jnt (str): The name of the first joint.
        ik_jnt (str): The name of the second joint.
        name (str): The name for the pairBlend node. Defaults to "pairBlend".

    Returns:
        str: The name of the pairBlend node.
    """

    pb_node = cmds.createNode("pairBlend", n = name)

    cmds.connectAttr(f"{fk_jnt}.rotate", f"{pb_node}.inRotate1")
    cmds.connectAttr(f"{pb_node}.outRotate", f"{ik_jnt}.rotate")

    return pb_node

def get_ik(jnt: str):
    """
    """

    if not cmds.nodeType(jnt) == "joint":
        om.MGlobal.displayError(f"{jnt} is not a joint.")
        return

    nodes = cmds.listConnections(jnt, type = "ikHandle")

    if nodes:
        ik = nodes[0]
        return ik

    else:
        om.MGlobal.displayError(f"{jnt} is not driven by ik handle.")

def switch_ik_fk(fk_joints: list, ik_joints: list, toggle_node: str = "blendColors", switch_node: str = "", ctrl = "", pv = "") -> list[str]:
    """Create switch nodes to blend between FK and IK joints for multiple limbs.

    Args:
        fks (List[str]): A list of names of FK joints.
        iks (List[str]): A list of names of IK joints.
        toggle_node (str): The type of switch node to create. Can be "blendColors" or "pairBlend". Defaults to "blendColors".

    Returns:
        List[str]: A list of names of the created switch nodes.
    """

    ik_handle = get_ik(ik_joints[0])
    cmds.connectAttr(f"{switch_node}.{SWITCH}", f"{ik_handle}.ikBlend")

    tgl_nodes = []    
    for fk_joint, ik_joint in zip(fk_joints, ik_joints):

        limb_name = fk_joint.split("_", 1)[-1]
        tgl_node = f"Switch_{limb_name}"

        if toggle_node == "blendColors":
            bc_node = blend_colors(fk_joint, ik_joint, name = tgl_node)
            cmds.connectAttr(f"{switch_node}.switch", f"{bc_node}.blender")

        else:
            pb_node = pair_blend(fk_joint, ik_joint, name = tgl_node)
            cmds.connectAttr(f"{switch_node}.switch", f"{pb_node}.weight")

        tgl_nodes.append(tgl_node)

    # -------
    base_name = fk_joints[0].split('_')[1]
    reverse_node = cmds.createNode('reverse', name = f'rev_switch_{base_name}')
    cmds.connectAttr(f'{switch_node}.switch', f'{reverse_node}.inputX')
    cmds.connectAttr(f'{switch_node}.switch', f'{ik_joints[0]}.v')
    try:
        cmds.connectAttr(f'{switch_node}.switch', f'{ctrl}.v')
        cmds.connectAttr(f'{switch_node}.switch', f'{pv}.v')
    except:
        pass

    cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_joints[0]}.v')

    # -------

    return tgl_nodes

def stretch_limb(ctrl: str, loc_start_parent: str, global_move: str, jnts: list, switch_attribute: str = ""):
    """Apply stretch functionality to a limb.

    Args:
        ctrl (str): Name of the control for the limb.
        loc_start_parent (str): Name of the parent locator for the start position.
        global_move (str): Name of the global move transform node.
        jnts (List[str]): List of names of joints in the limb.

    Note:
        - The `ctrl` and the last joint in `jnts` must have the same pivot.
    """

    # add attributes on ctrl

    attribute.sep_cb(ctrl, True)
    at_stretch = "stretch"
    cmds.addAttr(ctrl, ln = at_stretch, nn = "Stretch", at = "long", min = 0, max = 1, k=1)
    cmds.setAttr(f"{ctrl}.{at_stretch}", cb = 1, k = 0)

    # get joints and naming
    jnt_start, jnt_mid, jnt_end = jnts

    start_name = jnt_start.split("_", 1)[1]
    end_name = jnt_end.split("_", 1)[1]

    # create locators and set positions
    loc_start = f"{LOC}_stretch_start_{start_name}"
    loc_end = f"{LOC}_stretch_end_{end_name}"

    cmds.spaceLocator(n = loc_start)
    cmds.spaceLocator(n = loc_end)

    locs_grp = cmds.group(loc_start, loc_end, n = f"Grp_{LOC}_stretch_{start_name}")
    cmds.setAttr(f"{locs_grp}.visibility", 0)
    tools.ensure_group(locs_grp, LOCATORS)

    # constrain locators
    matrix.matrix_constraint(loc_start_parent, loc_start, mo = 0, t = 1, r = 1)
    matrix.matrix_constraint(ctrl, loc_end, mo = 0, t = 1, r = 1)

    # distance between locators
    loc_start_shp = cmds.listRelatives(loc_start, s = 1)[0] 
    loc_end_shp = cmds.listRelatives(loc_end, s = 1)[0]

    dist_btw = cmds.createNode("distanceBetween", n = f"distBtw_locs_{start_name}_{end_name}")

    cmds.connectAttr( f"{loc_start_shp}.worldPosition[0]", f"{dist_btw}.point1" )
    cmds.connectAttr( f"{loc_end_shp}.worldPosition[0]", f"{dist_btw}.point2" )

    # get missing distance and default distance
    missing_distance = mathfuncs.missing_dist(jnt_start, jnt_mid, jnt_end)
    dist = cmds.getAttr(f"{dist_btw}.distance")
    default_dist = f"{missing_distance + dist}"

    # create stretch expression
    exp_string = f"""// STRETCH EXPRESSION {jnt_start, jnt_mid, jnt_end}

    float $distance = {dist_btw}.distance;

    float $default_distance = {default_dist};

    float $global_relative_scale = {global_move}.scaleY * $default_distance;
    float $stretch = $distance / $global_relative_scale;
        
    if ($distance < $global_relative_scale){{
        $stretch = 1;
    }}

    if ({ctrl}.{at_stretch} == 1 && {switch_attribute} == 1){{
        $stretch = $stretch;
    }}
    
    else{{
        $stretch = 1;
    }}

    {jnt_start}.sx = $stretch;
    {jnt_mid}.sx = $stretch;
    {jnt_end}.sx = $stretch;
    """

    cmds.expression(string = exp_string, name = f"Exp_Stretch_{start_name}")

    cmds.select(clear = True)
    om.MGlobal.displayInfo( f"Stretch done on : {jnt_start} {jnt_mid} {jnt_end}." )

def spine_ribbon(start: str, end: str, suffix: str = ''):
    '''
    '''

    # POSITIONS
    start_pos = cmds.xform(start, query = True, translation = True, worldSpace = True)
    end_pos = cmds.xform(end, query = True, translation = True, worldSpace = True)

    distance = math.dist(start_pos, end_pos)
    pivot_nurbs = start_pos[0], start_pos[1] + distance * 0.5, start_pos[2]

    # NUBRS
    ribbon_surface = cmds.nurbsPlane(pivot = pivot_nurbs, axis = [0, 0, 1], lengthRatio = distance, degree = 3, u = 1, v = 2, constructionHistory = False, name = f'ribbon_{suffix}')[0]
    cmds.rebuildSurface(ribbon_surface, degreeU = 7, degreeV = 7, spansU = 1, spansV = 2, constructionHistory = False)

    tools.bake_pivot(ribbon_surface, x = 'cx', y = 'ymin', z = 'cz')
    offset.offset_parent_matrix(ribbon_surface)

    rivet_group = rivet.rivet_nurbs(ribbon_surface, 'v', 5, True)
    rivets = cmds.listRelatives(rivet_group, children = True)

    # ranger le ribbon et les rivets dans xtranodes
    tools.ensure_group(ribbon_surface, XTRA)
    tools.ensure_group(rivet_group, XTRA)

    # CREATE CTRLS
    RADIUS = distance * 0.25
    positions = start_pos, pivot_nurbs, end_pos
    names = f'pelvis_{suffix}', f'mid_{suffix}', f'chest_{suffix}'
    joints = []

    for pos, name in zip(positions, names):
        cmds.select(clear = True)
        joint = cmds.joint(name = f'{CTRL}_{name}', position = pos)
        ctrl = cmds.circle(name = f'{CTRL}_{name}_01', normal = [0, 1 , 0], radius = RADIUS, constructionHistory = False)[0]
        curve.parent_shapes([ctrl, joint])
        display.color_node(joint, 'gold')
        joints.append(joint)

    ctrl_pelvis, ctrl_mid, ctrl_chest = joints

    ctrl_root = cmds.circle(name = f'ctrl_root_{suffix}', normal = [0, 1 , 0], radius = RADIUS * 2, constructionHistory = False)[0]
    display.color_node(ctrl_root, 'orange')
    cmds.setAttr(f'{ctrl_root}.{TRANSLATE}', *start_pos)
    offset.offset_parent_matrix(ctrl_root)

    # faire contrainte scale du root sur les rivets
    for riv in rivets:
        matrix.matrix_constraint(ctrl_root, riv, s = True, mo = True)

    # CREATE FK CTRLS
    fk_spine_start = cmds.circle(name = f'{FK}_start_{suffix}', normal = [0, 1 , 0], radius = RADIUS * 1.5, constructionHistory = False)[0]
    fk_spine_mid = cmds.circle(name = f'{FK}_mid_{suffix}', normal = [0, 1 , 0], radius = RADIUS * 1.5, constructionHistory = False)[0]
    fk_spine_end = cmds.circle(name = f'{FK}_end_{suffix}', normal = [0, 1 , 0], radius = RADIUS * 1.5, constructionHistory = False)[0]

    # définir les positions des contrôleurs FK
    dist = mathfuncs.distance_btw(start, end) * 0.25

    cmds.matchTransform(fk_spine_start, start, position = True)
    cmds.matchTransform(fk_spine_mid, start, position = True)
    cmds.matchTransform(fk_spine_end, start, position = True)

    cmds.move(0, dist, 0, fk_spine_start, relative = True)
    cmds.move(0, dist * 2, 0, fk_spine_mid, relative = True)
    cmds.move(0, dist * 3, 0, fk_spine_end, relative = True)

    display.color_node([fk_spine_start, fk_spine_end, fk_spine_mid], 'blue')

    cmds.parent(fk_spine_end, fk_spine_mid)
    cmds.parent(fk_spine_mid, fk_spine_start)

    # ranger le root et les fk dans un groupe
    cmds.parent(fk_spine_start, ctrl_root)
    offset.offset_parent_matrix([fk_spine_start, fk_spine_mid, fk_spine_end])
    ctrls_grp = cmds.group(ctrl_root, name = f'Ctrls_{suffix}')
    tools.ensure_group(ctrls_grp, CTRLS)

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    cmds.parent(ctrl_pelvis, ctrl_root)

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Créer les groupes contraintes
    ctrl_chest_const_fk_spine_end = cmds.group(empty = True, name = f'{ctrl_chest}_{CONST}_{fk_spine_end}')
    ctrl_chest_const_fk_spine_mid = cmds.group(empty = True, name = f'{ctrl_chest}_{CONST}_{fk_spine_mid}')
    ctrl_chest_const_fk_spine_start = cmds.group(empty = True, name = f'{ctrl_chest}_{CONST}_{fk_spine_start}')

    # déplacer les groupes contraintes
    cmds.matchTransform(ctrl_chest_const_fk_spine_end, fk_spine_end, position = True)
    cmds.matchTransform(ctrl_chest_const_fk_spine_mid ,fk_spine_mid, position = True)
    cmds.matchTransform(ctrl_chest_const_fk_spine_start, fk_spine_start, position = True)

    # parenter les groupes contraintes
    cmds.parent(ctrl_chest_const_fk_spine_start, ctrl_root)
    cmds.parent(ctrl_chest_const_fk_spine_mid, ctrl_chest_const_fk_spine_start)
    cmds.parent(ctrl_chest_const_fk_spine_end, ctrl_chest_const_fk_spine_mid)

    # cleaner les transforms
    offset.offset_parent_matrix([ctrl_chest_const_fk_spine_end, ctrl_chest_const_fk_spine_mid, ctrl_chest_const_fk_spine_start])

    # parenter le joint
    cmds.parent(ctrl_chest, ctrl_chest_const_fk_spine_end)
    offset.offset_parent_matrix(ctrl_chest)

    # colorer les groupes contraintes
    display.color_node([ctrl_chest_const_fk_spine_end, ctrl_chest_const_fk_spine_mid, ctrl_chest_const_fk_spine_start], 'red')

    # connecter les ctrl et fk aux groupes contraintes
    cmds.connectAttr(f'{fk_spine_end}.{ROTATE}', f'{ctrl_chest_const_fk_spine_end}.{ROTATE}')
    cmds.connectAttr(f'{fk_spine_mid}.{ROTATE}', f'{ctrl_chest_const_fk_spine_mid}.{ROTATE}')
    cmds.connectAttr(f'{fk_spine_start}.{ROTATE}', f'{ctrl_chest_const_fk_spine_start}.{ROTATE}')

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Créer les groupes contraintes
    ctrl_spine_const_ctrl_chest = cmds.group(empty = True, name = f'{ctrl_pelvis}_{CONST}_{ctrl_chest}')
    ctrl_spine_const_ctrl_pelvis = cmds.group(empty = True, name = f'{ctrl_pelvis}_{CONST}_{ctrl_pelvis}')
    ctrl_spine_const_fk_spine_mid = cmds.group(empty = True, name = f'{ctrl_pelvis}_{CONST}_{fk_spine_mid}')
    ctrl_spine_const_fk_spine_start = cmds.group(empty = True, name = f'{ctrl_pelvis}_{CONST}_{fk_spine_start}')

    # déplacer les groupes contraintes
    cmds.matchTransform(ctrl_spine_const_ctrl_chest, ctrl_mid, position = True)
    cmds.matchTransform(ctrl_spine_const_ctrl_pelvis, ctrl_mid, position = True)
    cmds.matchTransform(ctrl_spine_const_fk_spine_mid, fk_spine_mid, position = True)
    cmds.matchTransform(ctrl_spine_const_fk_spine_start, fk_spine_start, position = True)

    # parenter les groupes contraintes
    cmds.parent(ctrl_spine_const_fk_spine_start, ctrl_root)
    cmds.parent(ctrl_spine_const_fk_spine_mid, ctrl_spine_const_fk_spine_start)
    cmds.parent(ctrl_spine_const_ctrl_pelvis, ctrl_spine_const_fk_spine_mid)
    cmds.parent(ctrl_spine_const_ctrl_chest, ctrl_spine_const_ctrl_pelvis)

    # cleaner les transforms
    offset.offset_parent_matrix([ctrl_spine_const_fk_spine_mid, ctrl_spine_const_ctrl_chest])

    # parenter le joint
    cmds.parent(ctrl_mid, ctrl_spine_const_ctrl_chest)

    # colorer les groupes contraintes
    display.color_node([ctrl_spine_const_ctrl_chest, ctrl_spine_const_ctrl_pelvis, ctrl_spine_const_fk_spine_mid, ctrl_spine_const_fk_spine_start], 'red')

    # connecter les ctrl et fk aux groupes contraintes
    cmds.connectAttr(f'{fk_spine_mid}.{ROTATE}', f'{ctrl_spine_const_fk_spine_mid}.{ROTATE}')
    cmds.connectAttr(f'{fk_spine_start}.{ROTATE}', f'{ctrl_spine_const_fk_spine_start}.{ROTATE}')

    div_node = cmds.createNode('multiplyDivide', name = f'div_{fk_spine_mid}')
    cmds.setAttr(f'{div_node}.input2X', 0.5)
    cmds.setAttr(f'{div_node}.input2Y', 0.5)
    cmds.setAttr(f'{div_node}.input2Z', 0.5)

    cmds.connectAttr(f'{ctrl_chest}.{TRANSLATE}', f'{div_node}.input1')
    cmds.connectAttr(f'{div_node}.output', f'{ctrl_spine_const_ctrl_chest}.{TRANSLATE}')

    # skinner le ribbon
    cmds.skinCluster(ctrl_pelvis, ctrl_mid, ctrl_chest, ribbon_surface, maximumInfluences = 3, name = f'skinCluster_{ribbon_surface}')

    # squash and stretch ------------------------------------------------------------------------------------------------------------------
    attribute.sep_cb(ctrl_chest, True)
    cmds.addAttr(ctrl_chest, longName = 'preserve_volume', niceName = 'Preserve Volume', attributeType = 'float', minValue = 0, maxValue = 1, defaultValue = 0, keyable = True)

    loc_spine_start = cmds.spaceLocator(name = f'{LOC}_{suffix}_start')[0]
    loc_spine_end = cmds.spaceLocator(name = f'{LOC}_{suffix}_end')[0]

    loc_spine_start_shape = cmds.listRelatives(loc_spine_start, children = True)[0]
    loc_spine_end_shape = cmds.listRelatives(loc_spine_end, children = True)[0]

    cmds.matchTransform(loc_spine_start, start, position = True)
    cmds.matchTransform(loc_spine_end, end, position = True)

    cmds.makeIdentity(loc_spine_start, apply = True, translate = True)
    cmds.makeIdentity(loc_spine_end, apply = True, translate = True)
    grp_locs_spine = cmds.group(loc_spine_end, loc_spine_start, name = f"Locs_{suffix}")
    tools.ensure_group(grp_locs_spine, XTRA)
    display.color_node([loc_spine_end, loc_spine_start], 'red')

    cmds.connectAttr(f'{ctrl_chest}.{TRANSLATE}', f'{loc_spine_end}.{TRANSLATE}')

    # distance between
    distance_between = cmds.createNode('distanceBetween', name = f'distB_locs_{suffix}')
    cmds.connectAttr(f'{loc_spine_start_shape}.worldPosition[0]', f'{distance_between}.point1')
    cmds.connectAttr(f'{loc_spine_end_shape}.worldPosition[0]', f'{distance_between}.point2')

    # remap value node
    remap_value_node = cmds.createNode('remapValue', name = f'rmValue_{suffix}_volume')
    cmds.connectAttr(f'{ctrl_chest}.preserve_volume', f'{remap_value_node}.inputValue')
    cmds.connectAttr(f'{distance_between}.distance', f'{remap_value_node}.outputMin')
    
    default_distance = cmds.getAttr(f'{distance_between}.distance')
    cmds.setAttr(f'{remap_value_node}.outputMax', default_distance)

    # multiply divide
    div_node = cmds.createNode('multiplyDivide', name = f'div_{suffix}_scale_factor')
    cmds.setAttr(f'{div_node}.operation', 2)
    cmds.connectAttr(f'{distance_between}.distance', f'{div_node}.input2X')
    cmds.connectAttr(f'{distance_between}.distance', f'{div_node}.input2Y')
    cmds.connectAttr(f'{distance_between}.distance', f'{div_node}.input2Z')

    cmds.connectAttr(f'{remap_value_node}.outValue', f'{div_node}.input1X')
    cmds.connectAttr(f'{remap_value_node}.outValue', f'{div_node}.input1Y')
    cmds.connectAttr(f'{remap_value_node}.outValue', f'{div_node}.input1Z')

    # set range
    set_range_spine = cmds.createNode('setRange', name = f'setRange_{suffix}')
    set_range_spine_mid = cmds.createNode('setRange', name = f'setRange_{suffix}_mid')

    cmds.connectAttr(f'{div_node}.output', f'{set_range_spine}.value')
    cmds.connectAttr(f'{div_node}.output', f'{set_range_spine_mid}.value')

    cmds.setAttr(f'{set_range_spine}.min', -14, -14, -14, type = 'double3')
    cmds.setAttr(f'{set_range_spine}.max', 16, 16, 16, type = 'double3')
    cmds.setAttr(f'{set_range_spine}.oldMin', -9, -9, -9, type = 'double3')
    cmds.setAttr(f'{set_range_spine}.oldMax', 11, 11, 11, type = 'double3')

    cmds.setAttr(f'{set_range_spine_mid}.min', -16, -16, -16, type = 'double3')
    cmds.setAttr(f'{set_range_spine_mid}.max', 18, 18, 18, type = 'double3')
    cmds.setAttr(f'{set_range_spine_mid}.oldMin', -9, -9, -9, type = 'double3')
    cmds.setAttr(f'{set_range_spine_mid}.oldMax', 11, 11, 11, type = 'double3')

    # lister les joints
    bind_joints = [cmds.listRelatives(rivet, children = True)[-1] for rivet in rivets]
    bind_01, bind_02, bind_03, bind_04, bind_05 = bind_joints

    # connecter aux scales des bind joints
    cmds.connectAttr(f'{div_node}.outputX', f'{bind_01}.scaleX')
    cmds.connectAttr(f'{div_node}.outputZ', f'{bind_01}.scaleZ')

    cmds.connectAttr(f'{div_node}.outputX', f'{bind_05}.scaleX')
    cmds.connectAttr(f'{div_node}.outputZ', f'{bind_05}.scaleZ')

    cmds.connectAttr(f'{set_range_spine_mid}.outValueX', f'{bind_03}.scaleX')
    cmds.connectAttr(f'{set_range_spine_mid}.outValueZ', f'{bind_03}.scaleZ')

    cmds.connectAttr(f'{set_range_spine}.outValueX', f'{bind_02}.scaleX')
    cmds.connectAttr(f'{set_range_spine}.outValueZ', f'{bind_02}.scaleZ')

    cmds.connectAttr(f'{set_range_spine}.outValueX', f'{bind_04}.scaleX')
    cmds.connectAttr(f'{set_range_spine}.outValueZ', f'{bind_04}.scaleZ')

    # cacher les locators
    locs = rivets
    locs += [loc_spine_start, loc_spine_end]
    for loc in locs:
        shape = cmds.listRelatives(loc, shapes = True)[0]
        cmds.setAttr(f'{shape}.lodVisibility', 0)

    print(f'{suffix} ribbon done.')

def foot_locs(foot_mesh: str, ball: str, side: str) -> list[str]:
    """
    """

    bbox = cmds.exactWorldBoundingBox(foot_mesh)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox

    coord_heel = (xmax-xmin)*0.5, ymin, zmin
    coord_toe = (xmax-xmin)*0.5, ymin, zmax
    coord_ball = cmds.xform(ball, q = 1, t = 1, ws = 1)
    coord_int = xmin, ymin, (zmax-zmin)*0.5
    coord_ext = xmax, ymin, (zmax-zmin)*0.5

    coords = coord_heel, coord_toe, coord_int, coord_ext
    names = f"heel{side}", f"toe{side}", f"ball{side}",f"int{side}", f"ext{side}"

    for i, (cd, name) in enumerate(zip(coords, names)):

        loc = f"loc_{name}"
        cmds.spaceLocator(n = loc)

        if i < len(names) - 1:
            next_loc = f"loc_{names[i+1]}"
            cmds.parent(loc, next_loc)

        cmds.move(*cd, r = 1, os = 1, wd = 1)
        cmds.makeIdentity(loc, t = 1, a = 1)

        display.loc_size(loc, 0.2)
        display.color_node(loc, "green")

def no_roll_locs(jnt_pivot: str, jnt_const: str, ribbon_ctrl: Union[None, str], invert: bool = False, delete_shape: bool = False):
    """
    """

    master_matrix = cmds.getAttr(f'{jnt_pivot}.worldMatrix[0]')
    target_matrix = cmds.getAttr(f'{ribbon_ctrl}.worldMatrix[0]')

    if master_matrix != target_matrix:
        master_no_roll = cmds.group(empty = True, name = f'master_no_roll_{jnt_pivot}')
        cmds.matchTransform(master_no_roll, ribbon_ctrl, position = True, rotation = True)
        cmds.parent(master_no_roll, jnt_pivot)
        offset.offset_parent_matrix(master_no_roll)
        jnt_pivot = master_no_roll

    piv_name = jnt_pivot.split("_", 1)[-1]

    # create locators
    loc_base = cmds.spaceLocator(n = f"loc_base_{piv_name}")[0]
    loc_deco = cmds.spaceLocator(n = f"loc_deco_{piv_name}")[0]
    loc_info = cmds.spaceLocator(n = f"loc_info_{piv_name}")[0]
    loc_target = cmds.spaceLocator(n = f"loc_target_{piv_name}")[0]

    locs = [loc_base, loc_deco, loc_info, loc_target]
    display.color_node(locs, "green")
    no_roll_grp = cmds.group(loc_base, loc_target, n = f"Grp_noRoll_{piv_name}")
    cmds.setAttr(f'{no_roll_grp}.v', 0)

    # set locators transforms
    cmds.parent(loc_deco, loc_base)
    cmds.parent(loc_info, loc_base)
    cmds.matchTransform(loc_base, jnt_pivot)
    cmds.setAttr(f"{loc_deco}.tz", 4)
    cmds.matchTransform(loc_target, loc_deco)

    # set transforms to default
    offset.offset_parent_matrix(locs)

    # create constraints
    matrix.matrix_constraint(loc_target, loc_deco, mo = 1, ty = 1, tz = 1)
    matrix.matrix_constraint(jnt_const, loc_base, mo = 1, t = 1, r = 1)
    matrix.matrix_constraint(jnt_pivot, loc_target, mo = 1, t = 1, r = 1)
    matrix.matrix_aim_constraint(loc_deco, loc_info, av = (0, 0, 1), rx = 1)

    # Ribbon control connection
    if ribbon_ctrl:
        if invert:
            mult_node = cmds.createNode('multDoubleLinear', name = f'mult_invert_{loc_info}')
            cmds.setAttr(f'{mult_node}.input2', -1)
            cmds.connectAttr(f"{loc_info}.rx", f"{mult_node}.input1", force = True)
            cmds.connectAttr(f'{mult_node}.output', f'{ribbon_ctrl}.rx', force = True)

        else:
            cmds.connectAttr(f"{loc_info}.rx", f"{ribbon_ctrl}.rx", force = True)

    tools.ensure_group(no_roll_grp, LOCATORS)

    if delete_shape:
        for loc in locs:
            loc_shape = cmds.listRelatives(loc, shapes = True)[0]
            cmds.delete(loc_shape)

    om.MGlobal.displayInfo(f"No roll set up {piv_name} done.")
    return no_roll_grp

def no_roll_quat(master: str, target: str) -> str:
    """
    """

    # create nodes
    mult_mtx = cmds.createNode("multMatrix", name = f"{target}_{MULT_MTX}")
    deco_mtx = cmds.createNode("decomposeMatrix", name = f"{target}_{DECO_MTX}")
    quat_euler = cmds.createNode("quatToEuler", name = f"{target}_quatEuler")

    # connections
    cmds.connectAttr(f"{master}.{W_MTX}", f"{mult_mtx}.{MTX_IN0}")
    cmds.connectAttr(f"{target}.{PI_MTX}", f"{mult_mtx}.{MTX_IN1}")

    cmds.connectAttr(f"{mult_mtx}.{MTX_SUM}", f"{deco_mtx}.{INPUT_MTX}")

    cmds.connectAttr(f"{deco_mtx}.outputQuatX", f"{quat_euler}.inputQuatX")
    cmds.connectAttr(f"{deco_mtx}.outputQuatW", f"{quat_euler}.inputQuatW")

    cmds.connectAttr(f"{quat_euler}.outputRotateX", f"{target}.rx", force = True)

    return quat_euler
