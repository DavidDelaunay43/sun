from ...utils.imports import *
from ..constants_maya import *
from ..display import color_node
from ..joint import curve_joint
from ..offset import move_op_matrix, offset_parent_matrix, move_hook_op_matrix, offset
from ..tools import ensure_group
from ..matrix import matrix_constraint
from ..curve import control, octagon_control
from ..attribute import cb_attributes, sep_cb
from ..tools import ensure_set


def create_ctrl_options():
    ctrl = f"{CTRL}_options"
    control(shape="plus", color="orange", name=ctrl)
    cb_attributes(ctrl, ats=["v"], nonkeyable=True)
    sep_cb(ctrl, True)

    cmds.addAttr(ctrl, ln="Stretch", nn="Stretch", at="float", min=0, max=1, dv=1, k=1)
    cmds.addAttr(ctrl, ln="Squash", nn="Squash", at="float", min=0, max=1, dv=1, k=1)
    cmds.addAttr(ctrl, ln="Ik_Visibility", nn="Ik Visibility", at="bool", dv=1, k=1)
    cmds.addAttr(ctrl, ln="Fk_Visibility", nn="Fk Visibility", at="bool", dv=1, k=1)
    cmds.addAttr(ctrl, ln="Twist_Chest", nn="Twist Chest", at="float", dv=0, k=1)
    cmds.addAttr(ctrl, ln="Twist_Mid", nn="Twist Mid", at="float", dv=0, k=1)
    cmds.addAttr(ctrl, ln="Twist_Pelvis", nn="Twist Pelvis", at="float", dv=0, k=1)
    cmds.addAttr(
        ctrl, ln="Volume_Activation", nn="Volume Activation", at="bool", dv=1, k=1
    )
    cmds.addAttr(
        ctrl,
        ln="Volume_Factor",
        nn="Volume Factor",
        at="float",
        min=0,
        max=10,
        dv=1,
        k=1,
    )
    cmds.addAttr(
        ctrl,
        ln="Volume_Offset",
        nn="Volume Offset",
        at="float",
        min=-1,
        max=1,
        dv=0,
        k=1,
    )
    cmds.addAttr(
        ctrl,
        ln="Volume_Intensity",
        nn="Volume Intensity",
        at="float",
        min=0,
        max=0.5,
        dv=0,
        k=1,
    )
    cmds.addAttr(
        ctrl,
        ln="Stretch_Volume",
        nn="Stretch Volume",
        at="float",
        min=0,
        max=1,
        dv=1,
        k=1,
    )
    cmds.addAttr(
        ctrl,
        ln="Squash_Volume",
        nn="Squash Volume",
        at="float",
        min=0,
        max=1,
        dv=1,
        k=1,
    )

    return ctrl


def spine_matrix(start: str, end: str):
    """ """

    # POSITIONS
    import math

    start_pos = cmds.xform(start, query=True, translation=True, worldSpace=True)
    end_pos = cmds.xform(end, query=True, translation=True, worldSpace=True)
    distance = math.dist(start_pos, end_pos)
    mid_pos = start_pos[0], start_pos[1] + distance * 0.5, start_pos[2]
    mid_pos_bottom = start_pos[0], start_pos[1] + distance * 0.25, start_pos[2]
    mid_pos_top = start_pos[0], start_pos[1] + distance * 0.75, start_pos[2]

    # NUBRS
    width = 1.4
    ribbon_surface = cmds.nurbsPlane(
        pivot=mid_pos,
        axis=[0, 0, 1],
        lengthRatio=distance,
        width=width,
        degree=3,
        u=1,
        v=2,
        constructionHistory=False,
        name="ribbon_spine_lowdef",
    )[0]
    cmds.rebuildSurface(
        ribbon_surface,
        degreeU=1,
        degreeV=3,
        spansU=1,
        spansV=2,
        constructionHistory=False,
    )
    ribbon_surace_shape = cmds.listRelatives(ribbon_surface, shapes=True)[0]
    ensure_group(ribbon_surface, SHOW, ctrl_main=False)

    # Create controlers
    ctrl_ik_pelvis = cmds.circle(
        name="ctrl_ik_pelvis", constructionHistory=False, normal=[0, 1, 0]
    )[0]
    ctrl_ik_mid = cmds.circle(
        name="ctrl_ik_mid", constructionHistory=False, normal=[0, 1, 0]
    )[0]
    ctrl_ik_chest = cmds.circle(
        name="ctrl_ik_chest", constructionHistory=False, normal=[0, 1, 0]
    )[0]

    ctrl_tangent_pelvis = cmds.circle(
        name="ctrl_tangent_pelvis",
        constructionHistory=False,
        normal=[0, 0, 1],
        radius=0.25,
        centerX=2.0,
    )[0]
    ctrl_tangent_chest = cmds.circle(
        name="ctrl_tangent_chest",
        constructionHistory=False,
        normal=[0, 0, 1],
        radius=0.25,
        centerX=2.0,
    )[0]

    # ----- SINE --------------------------------------------------------
    ctrl_ik_pelvis_master = cmds.group(
        empty=True, name=f"{ctrl_ik_pelvis}_master", parent=ctrl_ik_pelvis
    )
    ctrl_tangent_pelvis_master = cmds.group(
        empty=True, name=f"{ctrl_tangent_pelvis}_master", parent=ctrl_tangent_pelvis
    )
    ctrl_ik_mid_master = cmds.group(
        empty=True, name=f"{ctrl_ik_mid}_master", parent=ctrl_ik_mid
    )
    ctrl_tangent_chest_master = cmds.group(
        empty=True, name=f"{ctrl_tangent_chest}_master", parent=ctrl_tangent_chest
    )
    ctrl_ik_chest_master = cmds.group(
        empty=True, name=f"{ctrl_ik_chest}_master", parent=ctrl_ik_chest
    )
    # ----- SINE --------------------------------------------------------

    ctrl_fk_mid = cmds.circle(
        name="ctrl_fk_mid", constructionHistory=False, normal=[0, 1, 0], radius=1.5
    )[0]

    ctrl_root = octagon_control(radius=4.0, color="orange", name="ctrl_root")
    ctrl_fk_chest = octagon_control(radius=4.0, color="blue", name="ctrl_fk_chest")

    ctrl_options = create_ctrl_options()
    cmds.matchTransform(ctrl_options, ctrl_fk_mid, position=True)
    cmds.parent(ctrl_options, ctrl_fk_mid)
    offset_parent_matrix(ctrl_options)
    cb_attributes(ctrl_options, lock=True, hide=True)

    # transform controlers
    cmds.setAttr(f"{ctrl_root}.t", *start_pos)
    cmds.setAttr(f"{ctrl_ik_pelvis}.t", *start_pos)

    cmds.setAttr(f"{ctrl_fk_mid}.t", *mid_pos)
    cmds.setAttr(f"{ctrl_ik_mid}.t", *mid_pos)

    cmds.setAttr(f"{ctrl_fk_chest}.t", *end_pos)
    cmds.setAttr(f"{ctrl_ik_chest}.t", *end_pos)

    cmds.setAttr(f"{ctrl_tangent_pelvis}.t", *start_pos)
    cmds.setAttr(f"{ctrl_tangent_chest}.t", *mid_pos_top)

    # hierarchize controlers
    cmds.parent(ctrl_ik_mid, ctrl_ik_pelvis, ctrl_fk_mid, ctrl_root)
    cmds.parent(ctrl_fk_chest, ctrl_fk_mid)
    cmds.parent(ctrl_ik_chest, ctrl_fk_chest)
    cmds.parent(ctrl_tangent_pelvis, ctrl_ik_pelvis)
    cmds.parent(ctrl_tangent_chest, ctrl_ik_chest)
    ensure_group(ctrl_root, CTRLS, ctrl_main=False)

    # offset controllers
    offset([ctrl_fk_mid, ctrl_fk_chest])
    offset_parent_matrix([ctrl_root, ctrl_ik_chest, ctrl_ik_pelvis])
    move_op_matrix(ctrl_tangent_chest)
    move_hook_op_matrix([ctrl_tangent_pelvis, ctrl_ik_mid])

    ctrl_fk_mid_offset = f"{ctrl_fk_mid}_{OFFSET}"
    ctrl_fk_chest_offset = f"{ctrl_fk_chest}_{OFFSET}"
    ctrl_tangent_chest_move = f"{ctrl_tangent_chest}_{MOVE}"
    ctrl_tangent_pelvis_move = f"{ctrl_tangent_pelvis}_{MOVE}"
    ctrl_tangent_pelvis_hook = f"{ctrl_tangent_pelvis}_{HOOK}"
    ctrl_ik_mid_move = f"{ctrl_ik_mid}_{MOVE}"
    ctrl_ik_mid_hook = f"{ctrl_ik_mid}_{HOOK}"

    cmds.setAttr(f"{ctrl_tangent_pelvis_hook}.t", *mid_pos_bottom)

    # color controlers
    color_node([ctrl_ik_pelvis, ctrl_ik_mid, ctrl_ik_chest], "gold")
    color_node([ctrl_tangent_pelvis, ctrl_tangent_chest], "yellow")
    color_node(ctrl_root, "orange")
    color_node([ctrl_fk_mid, ctrl_fk_chest], "blue")

    # LOCATORS ------------------------------------------------------------------------------------------------
    loc_info_squash_chest = cmds.spaceLocator(name=f"{LOC}_info_squash_chest")[0]
    loc_info_squash_initial_length = cmds.spaceLocator(
        name=f"{LOC}_info_squash_initial_length"
    )[0]
    loc_info_axis_mid_spine = cmds.spaceLocator(name=f"{LOC}_info_axis_mid_spine")[0]
    loc_info_pelvis = cmds.spaceLocator(name=f"{LOC}_info_pelvis")[0]
    loc_info_axis_mid_ik_pelvis = cmds.spaceLocator(
        name=f"{LOC}_info_axis_mid_ik_pelvis"
    )[0]
    grp_locs = cmds.group(
        loc_info_squash_chest,
        loc_info_squash_initial_length,
        loc_info_axis_mid_spine,
        loc_info_pelvis,
        loc_info_axis_mid_ik_pelvis,
        name="Locs_spine",
    )
    ensure_group(grp_locs, SHOW)

    cmds.setAttr(f"{loc_info_squash_chest}.t", *end_pos)
    cmds.setAttr(f"{loc_info_squash_initial_length}.t", *end_pos)
    cmds.setAttr(f"{loc_info_axis_mid_spine}.t", *start_pos)
    cmds.setAttr(f"{loc_info_axis_mid_ik_pelvis}.t", *start_pos)
    cmds.setAttr(f"{loc_info_pelvis}.t", *start_pos)

    offset_parent_matrix(
        [loc_info_squash_chest, loc_info_squash_initial_length, loc_info_pelvis]
    )
    move_hook_op_matrix(loc_info_axis_mid_spine)
    loc_info_axis_mid_spine_move = f"{loc_info_axis_mid_spine}_{MOVE}"
    loc_info_axis_mid_spine_hook = f"{loc_info_axis_mid_spine}_{HOOK}"
    offset_parent_matrix(loc_info_axis_mid_spine_hook)
    move_op_matrix(loc_info_axis_mid_ik_pelvis)
    loc_info_axis_mid_ik_pelvis_move = f"{loc_info_axis_mid_ik_pelvis}_{MOVE}"

    cmds.setAttr(f"{loc_info_squash_initial_length}.t", *end_pos)

    matrix_constraint(ctrl_ik_chest, loc_info_squash_chest, t=True, r=True, s=True)

    # CURVE ----------------------------------------------------------------------------------------------------
    curve_squash_offset = cmds.curve(
        name=f"{CRV}_squash_offset", degree=1, point=([0, 0, 0], [1, 1, 1]), knot=[0, 1]
    )
    curve_squash_offset_shape = cmds.listRelatives(curve_squash_offset, shapes=True)[0]
    curve_squash_offset_shape = cmds.rename(
        curve_squash_offset_shape, f"{curve_squash_offset}Shape"
    )
    ensure_group(curve_squash_offset, SHOW, ctrl_main=False)

    # connect locs to curve
    cmds.connectAttr(
        f"{loc_info_squash_chest}.worldPosition[0]",
        f"{curve_squash_offset_shape}.controlPoints[0]",
    )
    cmds.connectAttr(
        f"{loc_info_squash_initial_length}.worldPosition[0]",
        f"{curve_squash_offset_shape}.controlPoints[1]",
    )

    # create matrix nodes ------------------------------------------------------------------------------------------------
    compose_matrix_pos = cmds.createNode("composeMatrix", name="compMtx_pos_offset")
    compose_matrix_neg = cmds.createNode("composeMatrix", name="compMtx_neg_offset")
    cmds.setAttr(f"{compose_matrix_pos}.inputTranslateX", width * 0.5)
    cmds.setAttr(f"{compose_matrix_neg}.inputTranslateX", width * -0.5)

    point_dict = {
        0: [compose_matrix_neg, ctrl_ik_pelvis_master],
        1: [compose_matrix_neg, ctrl_tangent_pelvis_master],
        2: [compose_matrix_neg, ctrl_ik_mid_master],
        3: [compose_matrix_neg, ctrl_tangent_chest_master],
        4: [compose_matrix_neg, ctrl_ik_chest_master],
        5: [compose_matrix_pos, ctrl_ik_pelvis_master],
        6: [compose_matrix_pos, ctrl_tangent_pelvis_master],
        7: [compose_matrix_pos, ctrl_ik_mid_master],
        8: [compose_matrix_pos, ctrl_tangent_chest_master],
        9: [compose_matrix_pos, ctrl_ik_chest_master],
    }

    for i in range(0, 10):
        at = f"controlPoints[{i}]"
        compose_mtx_at = f"{point_dict[i][0]}.outputMatrix"
        ctrl_at = f"{point_dict[i][1]}.worldMatrix[0]"

        mutl_mtx = cmds.createNode("multMatrix", name=f"multMtx_point_{i}")
        cmds.connectAttr(compose_mtx_at, f"{mutl_mtx}.matrixIn[0]")
        cmds.connectAttr(ctrl_at, f"{mutl_mtx}.matrixIn[1]")

        deco_mtx = cmds.createNode("decomposeMatrix", name=f"decMtx_point_{i}")
        cmds.connectAttr(f"{mutl_mtx}.matrixSum", f"{deco_mtx}.inputMatrix")
        cmds.connectAttr(f"{deco_mtx}.outputTranslate", f"{ribbon_surace_shape}.{at}")

    # -----------------------------------------------------------------------------------------------------------------
    # create nodes
    rebulid_surface_node = cmds.createNode(
        "rebuildSurface", name="rebuildSurface_spine_ribbon"
    )
    curve_from_surface_iso_node = cmds.createNode(
        "curveFromSurfaceIso", name="curveFromSurfaceIso_spine_ribbon"
    )
    curve_info_node = cmds.createNode(
        "curveInfo", name="curveInfo_spine_ribbon_isoparm"
    )

    # configure nodes
    ats = (
        "rebuildType",
        "spansU",
        "spansV",
        "degreeU",
        "degreeV",
        "direction",
        "endKnots",
        "keepRange",
        "keepCorners",
    )

    values = (0, 1, 2, 3, 7, 1, 1, 0, 0)

    for at, value in zip(ats, values):
        cmds.setAttr(f"{rebulid_surface_node}.{at}", value)

    cmds.setAttr(f"{curve_from_surface_iso_node}.isoparmValue", 0.5)
    cmds.setAttr(f"{curve_from_surface_iso_node}.isoparmDirection", 1)  # V

    # connect atributes
    cmds.connectAttr(
        f"{ribbon_surace_shape}.worldSpace[0]", f"{rebulid_surface_node}.inputSurface"
    )
    cmds.connectAttr(
        f"{rebulid_surface_node}.outputSurface",
        f"{curve_from_surface_iso_node}.inputSurface",
    )
    cmds.connectAttr(
        f"{curve_from_surface_iso_node}.outputCurve", f"{curve_info_node}.inputCurve"
    )

    # curves ------------------------------------------------------------------------------------------------------------
    curve_isoparm = cmds.curve(
        name=f"{CRV}_ribbon_isoparm", degree=3, point=([0, 0, 0]), knot=[0, 0, 0]
    )
    curve_isoparm_shape = cmds.listRelatives(curve_isoparm, shapes=True)[0]
    curve_isoparm_shape = cmds.rename(curve_isoparm_shape, f"{curve_isoparm}Shape")
    ensure_group(curve_isoparm, SHOW, ctrl_main=False)

    attach_curve_node = cmds.createNode("attachCurve", name="attachCurve_spine")
    rebuild_curve_node = cmds.createNode(
        "rebuildCurve", name="rebuildCurve_extended_ribbon"
    )

    cmds.setAttr(f"{attach_curve_node}.blendBias", 1)
    cmds.setAttr(f"{attach_curve_node}.parameter", 1)

    cmds.setAttr(f"{rebuild_curve_node}.spans", 6)
    cmds.setAttr(f"{rebuild_curve_node}.endKnots", 1)  # multiple end knots
    cmds.setAttr(f"{rebuild_curve_node}.keepRange", 0)
    cmds.setAttr(f"{rebuild_curve_node}.keepTangents", 0)

    cmds.connectAttr(
        f"{curve_from_surface_iso_node}.outputCurve", f"{curve_isoparm_shape}.create"
    )
    cmds.connectAttr(
        f"{curve_isoparm_shape}.worldSpace[0]", f"{attach_curve_node}.inputCurve1"
    )
    cmds.connectAttr(
        f"{curve_squash_offset_shape}.worldSpace[0]", f"{attach_curve_node}.inputCurve2"
    )
    cmds.connectAttr(
        f"{attach_curve_node}.outputCurve", f"{rebuild_curve_node}.inputCurve"
    )

    ################################################################################################
    curve_divide_by_initial_length_node = cmds.createNode(
        "floatMath", name="curve_divide_by_initial_length"
    )
    cmds.setAttr(
        f"{curve_divide_by_initial_length_node}.operation", 3
    )  # operation : Divide
    cmds.connectAttr(
        f"{loc_info_axis_mid_spine_move}.ty",
        f"{curve_divide_by_initial_length_node}.floatA",
    )
    cmds.connectAttr(
        f"{loc_info_axis_mid_spine_move}.ty",
        f"{curve_divide_by_initial_length_node}.floatB",
    )

    # bind joints ------------------------------------------------------------------------------------------------------
    average_node = cmds.createNode("plusMinusAverage", name="average_scale_pelvis_mid")
    cmds.setAttr(f"{average_node}.operation", 3)
    cmds.connectAttr("decMtx_point_2.outputScale", f"{average_node}.input3D[0]")
    cmds.connectAttr("decMtx_point_5.outputScale", f"{average_node}.input3D[1]")

    binds_grp = cmds.group(empty=True, name="Grp_binds_spine")
    ensure_group(binds_grp, SHOW)
    rv_values = (0.15, 0.3, 0.5, 0.7, 0.85)
    for i in range(1, 6):
        joint = curve_joint(
            color="pink",
            name=f"{CTRL}_ribbon_spine_{i:02}",
            normal=[0, 1, 0],
            radius=width * 0.5,
        )
        ensure_set(joint)
        twist_scale_grp = cmds.group(empty=True, name=f"{joint}_twist_scale")
        offset_grp = cmds.group(empty=True, name=f"{joint}_offset")
        cmds.parent(joint, twist_scale_grp)
        cmds.parent(twist_scale_grp, offset_grp)
        cmds.parent(offset_grp, binds_grp)

        cmds.setAttr(f"{joint}.radius", 0.5)
        cmds.setAttr(f"{joint}.displayLocalAxis", 1)
        cmds.setAttr(
            f"{twist_scale_grp}.offsetParentMatrix",
            [0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            type="matrix",
        )

        # translate
        poci_node = cmds.createNode("pointOnCurveInfo", name=f"poci_{joint}")
        cmds.setAttr(f"{poci_node}.parameter", i / 6)
        cmds.connectAttr(f"{rebuild_curve_node}.outputCurve", f"{poci_node}.inputCurve")
        cmds.connectAttr(f"{poci_node}.position", f"{offset_grp}.translate")

        blender_node = cmds.createNode(
            "blendColors", name=f"blender_stretch_factor_{i:02}"
        )
        cmds.connectAttr(f"{ctrl_options}.Stretch", f"{blender_node}.blender")

        # rotate
        posi_node = cmds.createNode("pointOnSurfaceInfo", name=f"posi_{joint}")
        vector_prod_node = cmds.createNode("vectorProduct", name=f"vp_{joint}")
        fbf_matrix_node = cmds.createNode(
            "fourByFourMatrix", name=f"fbf_matrix_{joint}"
        )
        deco_mtx_node = cmds.createNode("decomposeMatrix", name=f"deco_mtx_{joint}")

        cmds.setAttr(f"{posi_node}.parameterU", 0.5)
        cmds.connectAttr(
            f"{rebulid_surface_node}.outputSurface", f"{posi_node}.inputSurface"
        )

        cmds.connectAttr(f"{posi_node}.normal", f"{vector_prod_node}.input1")
        cmds.connectAttr(f"{posi_node}.tangentV", f"{vector_prod_node}.input2")
        cmds.setAttr(f"{vector_prod_node}.operation", 2)

        cmds.connectAttr(f"{posi_node}.normalX", f"{fbf_matrix_node}.in00")
        cmds.connectAttr(f"{posi_node}.normalY", f"{fbf_matrix_node}.in01")
        cmds.connectAttr(f"{posi_node}.normalZ", f"{fbf_matrix_node}.in02")
        cmds.connectAttr(f"{posi_node}.tangentVx", f"{fbf_matrix_node}.in10")
        cmds.connectAttr(f"{posi_node}.tangentVy", f"{fbf_matrix_node}.in11")
        cmds.connectAttr(f"{posi_node}.tangentVz", f"{fbf_matrix_node}.in12")
        cmds.connectAttr(f"{vector_prod_node}.outputX", f"{fbf_matrix_node}.in20")
        cmds.connectAttr(f"{vector_prod_node}.outputY", f"{fbf_matrix_node}.in21")
        cmds.connectAttr(f"{vector_prod_node}.outputZ", f"{fbf_matrix_node}.in22")
        cmds.connectAttr(f"{posi_node}.positionX", f"{fbf_matrix_node}.in30")
        cmds.connectAttr(f"{posi_node}.positionY", f"{fbf_matrix_node}.in31")
        cmds.connectAttr(f"{posi_node}.positionZ", f"{fbf_matrix_node}.in32")

        cmds.connectAttr(f"{fbf_matrix_node}.output", f"{deco_mtx_node}.inputMatrix")
        cmds.connectAttr(f"{deco_mtx_node}.outputRotate", f"{offset_grp}.rotate")

        # translate & rotate
        exp = f"""
        $stretch = ctrl_options.Stretch;
        $ty = loc_info_axis_mid_spine_move.ty;
        $arclen = curveInfo_spine_ribbon_isoparm.arcLength;

        $no_stretch = {i/6} * $ty; 
        $div_param = $no_stretch / $arclen;
        float $out_neg_stretch_factor;

        if ($div_param < {i/6}) {{
            $out_neg_stretch_factor = $div_param;
        }}

        else {{
            $out_neg_stretch_factor = {i/6};
        }}

        {blender_node}.color1R = {i/6};
        {blender_node}.color2R = $out_neg_stretch_factor;
        """
        cmds.expression(
            string=exp,
            name=f"Exp_position_{joint}",
            alwaysEvaluate=True,
            unitConversion="all",
        )

        divide_node = cmds.createNode("floatMath", name=f"div_point_{joint}")
        cmds.setAttr(f"{divide_node}.operation", 3)  # operation : Divide
        cmds.connectAttr(f"{blender_node}.outputR", f"{divide_node}.floatA")
        cmds.connectAttr(
            f"{curve_divide_by_initial_length_node}.outFloat", f"{divide_node}.floatB"
        )
        cmds.connectAttr(f"{divide_node}.outFloat", f"{poci_node}.parameter")
        cmds.connectAttr(f"{divide_node}.outFloat", f"{posi_node}.parameterV")

        # scale
        cmds.connectAttr(f"{average_node}.output3Dx", f"{offset_grp}.sz")
        cmds.connectAttr(f"{average_node}.output3Dy", f"{offset_grp}.sy")
        cmds.connectAttr(f"{average_node}.output3Dz", f"{offset_grp}.sx")

        # twist scale grp
        rv_node = cmds.createNode("remapValue", name=f"rv_{joint}")
        cmds.setAttr(f"{rv_node}.inputValue", rv_values[i - 1])
        cmds.setAttr(f"{rv_node}.outputMin", 1)

        cmds.setAttr(f"{rv_node}.value[0].value_Interp", 3)
        cmds.setAttr(f"{rv_node}.value[1].value_Interp", 3)
        cmds.setAttr(f"{rv_node}.value[2].value_Interp", 3)
        cmds.setAttr(f"{rv_node}.value[3].value_Interp", 3)
        cmds.setAttr(f"{rv_node}.value[4].value_Interp", 3)

        cmds.setAttr(f"{rv_node}.value[0].value_FloatValue", 0)
        cmds.setAttr(f"{rv_node}.value[1].value_FloatValue", 0.5)
        cmds.setAttr(f"{rv_node}.value[2].value_FloatValue", 1)
        cmds.setAttr(f"{rv_node}.value[3].value_FloatValue", 0.5)
        cmds.setAttr(f"{rv_node}.value[4].value_FloatValue", 0)

        cmds.setAttr(f"{rv_node}.value[0].value_Position", 0)
        cmds.setAttr(f"{rv_node}.value[1].value_Position", 0.25)
        cmds.setAttr(f"{rv_node}.value[2].value_Position", 0.5)
        cmds.setAttr(f"{rv_node}.value[3].value_Position", 0.75)
        cmds.setAttr(f"{rv_node}.value[4].value_Position", 1)

        cmds.connectAttr(f"{rv_node}.outValue", f"{twist_scale_grp}.sx")
        cmds.connectAttr(f"{rv_node}.outValue", f"{twist_scale_grp}.sz")

    # locators connections --------------------------------------------------------------------------------------------------
    dist_btw_node = cmds.createNode(
        "distanceBetween", name=f"distB_{loc_info_axis_mid_spine}_{loc_info_pelvis}"
    )
    loc_info_axis_mid_spine_shape = cmds.listRelatives(
        loc_info_axis_mid_spine, shapes=True
    )[0]
    loc_info_pelvis_shape = cmds.listRelatives(loc_info_pelvis, shapes=True)[0]
    cmds.connectAttr(
        f"{loc_info_axis_mid_spine_shape}.worldPosition[0]", f"{dist_btw_node}.point1"
    )
    cmds.connectAttr(
        f"{loc_info_pelvis_shape}.worldPosition[0]", f"{dist_btw_node}.point2"
    )
    """
    on a deux locators : info_axis_mid_spine et info_pelvis
    d'abord on les contraint
    puis on connecte leur shape pour contraindre les translate Y des 
        ctrl_tangent_pelvis_hook
        ctrl_tangent_chest_move
    """
    # constrain loc_info_axis_mid_spine -----------------------------------------------------------------------------------------
    exp = f"""
    $ouput_tx = {ctrl_ik_chest}.translateX + {ctrl_fk_chest}.translateX;
    $ouput_ty = ({ctrl_ik_chest}.translateY + {ctrl_fk_chest}.translateY);
    $ouput_tz = {ctrl_ik_chest}.translateZ + {ctrl_fk_chest}.translateZ;

    {loc_info_axis_mid_spine}.translateX = $ouput_tx;
    {loc_info_axis_mid_spine}.translateY = $ouput_ty;
    {loc_info_axis_mid_spine}.translateZ = $ouput_tz;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{loc_info_axis_mid_spine}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # constrain loc_info_axis_mid_spine_move ------------------------------------------------------------------------------------
    exp = f"""
    $ouput_tx = {ctrl_fk_mid_offset}.translateX + {ctrl_fk_chest_offset}.translateX;
    $ouput_ty = ({ctrl_fk_mid_offset}.translateY + {ctrl_fk_chest_offset}.translateY) * {ctrl_root}.scaleY;
    $ouput_tz = {ctrl_fk_mid_offset}.translateZ + {ctrl_fk_chest_offset}.translateZ;

    {loc_info_axis_mid_spine_move}.translateX = $ouput_tx;
    {loc_info_axis_mid_spine_move}.translateY = $ouput_ty;
    {loc_info_axis_mid_spine_move}.translateZ = $ouput_tz;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{loc_info_axis_mid_spine_move}",
        alwaysEvaluate=True,
        unitConversion="all",
    )
    cmds.connectAttr(f"{ctrl_root}.s", f"{loc_info_axis_mid_spine_move}.s")

    # constrain loc_info_axis_mid_spine_hook ---------------------------------------------------------------------------------------
    matrix_constraint(ctrl_root, loc_info_axis_mid_spine_hook, t=True, r=True)

    # constrain loc_info_pelvis ----------------------------------------------------------------------------------------------------
    matrix_constraint(ctrl_ik_pelvis, loc_info_pelvis, t=True, r=True, s=True)

    # constrain loc_info_axis_mid_ik_pelvis -----------------------------------------------------------------------------------------
    cmds.aimConstraint(
        loc_info_axis_mid_spine,
        loc_info_axis_mid_ik_pelvis,
        maintainOffset=False,
        aimVector=(0, 1, 0),
        upVector=(1, 0, 0),
        worldUpType="objectrotation",
        worldUpVector=(1, 0, 0),
        worldUpObject=ctrl_ik_pelvis,
    )
    # matrix_aim_constraint([loc_info_axis_mid_spine, ctrl_ik_pelvis], loc_info_axis_mid_ik_pelvis, r = True, av = (0, 1, 0), uv = (1, 0, 0), mo = False)

    exp = f"""
    {loc_info_axis_mid_ik_pelvis}.sy = {dist_btw_node}.distance / {loc_info_axis_mid_spine_move}.ty;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{loc_info_axis_mid_ik_pelvis}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # constrain loc_info_axis_mid_ik_pelvis_move -------------------------------------------------------------------------------------
    matrix_constraint(
        ctrl_ik_pelvis, loc_info_axis_mid_ik_pelvis_move, t=True, r=True, s=True
    )

    # constrain loc_info_squash_initial_length -------------------------------------------------------------------------------------
    compo_mtx_node = cmds.createNode(
        "composeMatrix", name=f"compoMtx_{loc_info_squash_initial_length}"
    )
    mult_mtx_node = cmds.createNode(
        "multMatrix", name=f"multMtx_{loc_info_squash_initial_length}"
    )
    deco_mtx_node = cmds.createNode(
        "decomposeMatrix", name=f"deoMtx_{loc_info_squash_initial_length}"
    )
    rev_node = cmds.createNode("reverse", name=f"rev_squash_{ctrl_options}")

    cmds.connectAttr(f"{ctrl_options}.Squash", f"{rev_node}.inputX")

    cmds.connectAttr(
        f"{deco_mtx_node}.{OUTPUT_T}", f"{loc_info_squash_initial_length}.t"
    )
    cmds.connectAttr(
        f"{deco_mtx_node}.{OUTPUT_R}", f"{loc_info_squash_initial_length}.r"
    )
    cmds.connectAttr(
        f"{deco_mtx_node}.{OUTPUT_S}", f"{loc_info_squash_initial_length}.s"
    )

    cmds.connectAttr(f"{mult_mtx_node}.matrixSum", f"{deco_mtx_node}.inputMatrix")

    cmds.connectAttr(f"{compo_mtx_node}.outputMatrix", f"{mult_mtx_node}.matrixIn[0]")
    cmds.connectAttr(f"{ctrl_ik_chest}.worldMatrix[0]", f"{mult_mtx_node}.matrixIn[1]")
    cmds.connectAttr(
        f"{loc_info_squash_initial_length}.parentInverseMatrix[0]",
        f"{mult_mtx_node}.matrixIn[2]",
    )

    exp = f"""
    $mult_squash_min = {loc_info_axis_mid_spine_move}.ty;
    $diff_initiallen_arclen = {loc_info_axis_mid_spine_move}.ty - {curve_info_node}.arcLength;

    float $if_squash_max_value;
    if ({curve_info_node}.arcLength < $mult_squash_min){{
        $if_squash_max_value = 1;
    }}
    else{{
        $if_squash_max_value = 0;
    }}

    float $mult_by_0_if_chest_sup_max_value = $diff_initiallen_arclen * $if_squash_max_value;

    float $if_squash;
    if ({ctrl_options}.Squash <= 1){{
        $if_squash = {rev_node}.outputX;
    }}
    else {{
        $if_squash = 1;
    }}

    {compo_mtx_node}.inputTranslateY = $if_squash_max_value * $if_squash;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{loc_info_squash_initial_length}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # controls connections -------------------------------------------------------------------------------------------------
    # ctrl_ik_mid_move
    cmds.connectAttr(f"{ctrl_fk_mid}.t", f"{ctrl_ik_mid_move}.t")
    cmds.connectAttr(f"{ctrl_fk_mid}.ry", f"{ctrl_ik_mid_move}.ry")

    # ctrl_ik_mid_hook
    compo_mtx_node = cmds.createNode(
        "composeMatrix", name=f"{ctrl_fk_mid_offset}_compoMtx"
    )
    mult_mtx_node = cmds.createNode("multMatrix", name=f"{ctrl_ik_mid_hook}_multMtx")
    deco_mtx_node = cmds.createNode(
        "decomposeMatrix", name=f"{ctrl_ik_mid_hook}_decoMtx"
    )

    cmds.connectAttr(f"{ctrl_fk_mid_offset}.ty", f"{compo_mtx_node}.inputTranslateY")

    cmds.connectAttr(f"{compo_mtx_node}.outputMatrix", f"{mult_mtx_node}.matrixIn[0]")
    cmds.connectAttr(
        f"{loc_info_axis_mid_ik_pelvis}.worldMatrix[0]", f"{mult_mtx_node}.matrixIn[1]"
    )
    cmds.connectAttr(
        f"{ctrl_ik_mid_hook}.parentInverseMatrix[0]", f"{mult_mtx_node}.matrixIn[2]"
    )

    cmds.connectAttr(f"{mult_mtx_node}.matrixSum", f"{deco_mtx_node}.inputMatrix")
    cmds.connectAttr(f"{deco_mtx_node}.outputTranslate", f"{ctrl_ik_mid_hook}.t")
    cmds.connectAttr(f"{deco_mtx_node}.outputRotate", f"{ctrl_ik_mid_hook}.r")

    # ctrl_tangent_pelvis_move
    cmds.addAttr(
        ctrl_fk_mid, ln="Rotation_Tangent", nn="Rotation Tangent", at="bool", dv=1, k=1
    )
    cmds.addAttr(
        ctrl_fk_mid,
        ln="Rotation_Tangent_Factor",
        nn="Rotation Tangent Factor",
        at="float",
        min=0,
        dv=0,
        k=1,
    )

    exp = f"""
    $ty = loc_info_axis_mid_spine.ty;
    float $out_tangent_x;
    float $out_tangent_z;

    if ({ctrl_fk_mid}.Rotation_Tangent == 1){{
        $out_tangent_x = {ctrl_fk_mid}.rx * {ctrl_fk_mid}.Rotation_Tangent_Factor * -1 * $ty;
        $out_tangent_z = {ctrl_fk_mid}.rz * {ctrl_fk_mid}.Rotation_Tangent_Factor * $ty;
    }}
    else {{
        $out_tangent_x = 0;
        $out_tangent_z = 0;
    }}

    {ctrl_tangent_pelvis_move}.tx = $out_tangent_x;
    {ctrl_tangent_pelvis_move}.tz = $out_tangent_z;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{ctrl_tangent_pelvis_move}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # ctrl_tangent_pelvis_hook
    cmds.addAttr(
        ctrl_root,
        ln="Tangent_Factor_Down",
        nn="Tangent Factor Down",
        at="float",
        min=0.005,
        max=0.75,
        dv=0.25,
        k=1,
    )
    cmds.addAttr(
        ctrl_root,
        ln="Tangent_Visibility",
        nn="Tangent Visibility",
        at="bool",
        dv=1,
        k=1,
    )
    cmds.addAttr(
        ctrl_ik_mid,
        ln="Rotation_Factor",
        nn="Rotation Factor",
        at="float",
        min=-1,
        max=1,
        dv=0.02,
        k=1,
    )

    exp = f"""
    {ctrl_tangent_pelvis_hook}.tx = {ctrl_ik_mid}.rz * {ctrl_ik_mid}.Rotation_Factor;
    {ctrl_tangent_pelvis_hook}.ty = ({dist_btw_node}.distance * {ctrl_root}.Tangent_Factor_Down) / {ctrl_root}.sy;
    {ctrl_tangent_pelvis_hook}.tz = {ctrl_ik_mid}.rx * {ctrl_ik_mid}.Rotation_Factor * -1;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{ctrl_tangent_pelvis_hook}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # ctrl_tangent_chest_move
    # cmds.addAttr(ctrl_ik_mid, ln = 'Rotation_Factor', nn = 'Rotation Factor', at = 'float', min = -1, max = 1, dv = 0.02, k = 1)
    cmds.addAttr(
        ctrl_fk_chest,
        ln="Tangent_Factor_Up",
        nn="Tangent Factor Up",
        at="float",
        min=0.0,
        max=0.75,
        dv=0.005,
        k=1,
    )

    exp = f"""
    {ctrl_tangent_chest_move}.tx = {ctrl_ik_mid}.rz * {ctrl_ik_mid}.Rotation_Factor * -1;
    {ctrl_tangent_chest_move}.ty = {ctrl_root}.sy * ({dist_btw_node}.distance * -1 * {ctrl_fk_chest}.Tangent_Factor_Up);
    {ctrl_tangent_chest_move}.tz = {ctrl_ik_mid}.rx * {ctrl_ik_mid}.Rotation_Factor;
    """
    cmds.expression(
        string=exp,
        name=f"Exp_{ctrl_tangent_chest_move}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    # control visibility -------------------------------------------------------------------------------------------------------------------
    vis_list = (
        "Fk_Visibility",
        "Fk_Visibility",
        "Ik_Visibility",
        "Ik_Visibility",
        "Ik_Visibility",
    )
    ctrl_list = ctrl_fk_chest, ctrl_fk_mid, ctrl_ik_chest, ctrl_ik_mid, ctrl_ik_pelvis
    for ctrl, vis in zip(ctrl_list, vis_list):
        shape = cmds.listRelatives(ctrl, shapes=True)[0]
        cmds.connectAttr(f"{ctrl_options}.{vis}", f"{shape}.v")

    # VOLUME JOINTS
    exp = """
    $squash = ctrl_options.Squash;
    $stretch = ctrl_options.Stretch;
    $twist_chest = ctrl_options.Twist_Chest;
    $twist_pelvis = ctrl_options.Twist_Pelvis;
    $volume_activation = ctrl_options.Volume_Activation;
    $volume_factor = ctrl_options.Volume_Factor;
    $volume_offset = ctrl_options.Volume_Offset;
    $volume_intensity = ctrl_options.Volume_Intensity;
    $stretch_volume = ctrl_options.Stretch_Volume;
    $squash_volume = ctrl_options.Squash_Volume;

    // Volume Activation -----------------------------------------
    float $out_volume_activation;
    if ($volume_activation == 1){
        $out_volume_activation = curveInfo_spine_ribbon_isoparm.arcLength / loc_info_axis_mid_spine_move.translateY;
    }

    else {
        $out_volume_activation = 1;
    }

    // Stretch Volume ---------------------------------------------
    float $out_stretch_volume;
    if ($stretch_volume == 1){
        $out_stretch_volume = 1;
    }
    else {
        $out_stretch_volume = $stretch;
    }

    float $out_stretch_volume_02;
    if ($out_stretch_volume == 1){
        $out_stretch_volume_02 = 1 / $out_volume_activation;;
    }
    else {
        $out_stretch_volume_02 = 1;
    }

    // Squash Volume ---------------------------------------------
    float $out_squash_volume;
    if ($squash_volume == 1){
        $out_squash_volume = 1;
    }
    else {
        $out_squash_volume = $squash;
    }

    float $out_squash_volume_02;
    if ($out_squash_volume == 1){
        $out_squash_volume_02 = $out_stretch_volume_02;
    }
    else {
        $out_squash_volume_02 = 1;
    }

    // Factor Volume -----------------------------------------------
    float $factor_volume_XZ = $out_squash_volume_02 * $volume_factor;

    // Intensity Volume ---------------------------------------------
    float $neg_volume_intensity = ($volume_intensity * -1) + 1;

    // Offset Volume ------------------------------------------------
    float $half_volume_offset = $volume_offset * 0.5;


    // CONNECTIONS --------------------------------------------------
    rv_ctrl_ribbon_spine_01.outputMax = $factor_volume_XZ;
    rv_ctrl_ribbon_spine_02.outputMax = $factor_volume_XZ;
    rv_ctrl_ribbon_spine_03.outputMax = $factor_volume_XZ;
    rv_ctrl_ribbon_spine_04.outputMax = $factor_volume_XZ;
    rv_ctrl_ribbon_spine_05.outputMax = $factor_volume_XZ;

    rv_ctrl_ribbon_spine_01.inputMin = $volume_intensity;
    rv_ctrl_ribbon_spine_02.inputMin = $volume_intensity;
    rv_ctrl_ribbon_spine_03.inputMin = $volume_intensity;
    rv_ctrl_ribbon_spine_04.inputMax = $neg_volume_intensity;
    rv_ctrl_ribbon_spine_05.inputMax = $neg_volume_intensity;

    rv_ctrl_ribbon_spine_01.inputValue = ($volume_offset * 0.5 ) + 0.15;
    rv_ctrl_ribbon_spine_02.inputValue = ($volume_offset * 0.5 ) + 0.3;
    rv_ctrl_ribbon_spine_03.inputValue = ($volume_offset * 0.5 ) + 0.5;
    rv_ctrl_ribbon_spine_04.inputValue = ($volume_offset * 0.5 ) + 0.7;
    rv_ctrl_ribbon_spine_05.inputValue = ($volume_offset * 0.5 ) + 0.85;

    ctrl_ribbon_spine_01_twist_scale.rotateY = ctrl_options.Twist_Chest*0.15 + ctrl_options.Twist_Pelvis*0.85 + ctrl_options.Twist_Mid*0.25;
    ctrl_ribbon_spine_02_twist_scale.rotateY = ctrl_options.Twist_Chest*0.3 + ctrl_options.Twist_Pelvis*0.7 + ctrl_options.Twist_Mid*0.5;
    ctrl_ribbon_spine_03_twist_scale.rotateY = ctrl_options.Twist_Chest*0.5 + ctrl_options.Twist_Pelvis*0.5 + ctrl_options.Twist_Mid*1;
    ctrl_ribbon_spine_04_twist_scale.rotateY = ctrl_options.Twist_Chest*0.7 + ctrl_options.Twist_Pelvis*0.3 + ctrl_options.Twist_Mid*0.5;
    ctrl_ribbon_spine_05_twist_scale.rotateY = ctrl_options.Twist_Chest*0.85 + ctrl_options.Twist_Pelvis*0.15 + ctrl_options.Twist_Mid*0.25;
    """
    cmds.expression(
        string=exp, name="Exp_volume_joints", alwaysEvaluate=True, unitConversion="all"
    )

    #
    bind_pelvis = cmds.joint(name=f"{BIND}_pelvis")
    cmds.select(clear=True)
    bind_chest = cmds.joint(name=f"{BIND}_chest")
    ensure_group(bind_pelvis, SHOW, ctrl_main=False)
    ensure_group(bind_chest, SHOW, ctrl_main=False)
    cmds.setAttr(f"{bind_pelvis}.t", *start_pos)
    # cmds.setAttr(f'{bind_chest}.t', *start_pos)
    cmds.setAttr(f"{bind_pelvis}.displayLocalAxis", True)
    cmds.setAttr(f"{bind_chest}.displayLocalAxis", True)
    color_node([bind_chest, bind_pelvis], "white")
    move_op_matrix([bind_pelvis, bind_chest])
    bind_pelvis_move = f"{bind_pelvis}_{MOVE}"
    bind_chest_move = f"{bind_chest}_{MOVE}"

    ensure_set([bind_pelvis, bind_chest])

    # constrain bind_pelvis_move
    deco_mtx = matrix_constraint(
        ctrl_ik_pelvis, bind_pelvis_move, t=True, r=True, s=True
    )
    add_node = cmds.createNode("addDoubleLinear", name="add_twist_pelvis")
    cmds.connectAttr(f"{ctrl_options}.Twist_Pelvis", f"{add_node}.input1")
    cmds.connectAttr(f"{deco_mtx}.outputRotateY", f"{add_node}.input2")
    cmds.connectAttr(f"{add_node}.output", f"{bind_pelvis_move}.ry", force=True)

    # constrain bind_chest_move
    poci_node = cmds.createNode("pointOnCurveInfo", name=f"poci_{joint}")
    cmds.setAttr(f"{poci_node}.parameter", i / 6)
    cmds.connectAttr(f"{rebuild_curve_node}.outputCurve", f"{poci_node}.inputCurve")
    cmds.connectAttr(f"{poci_node}.position", f"{bind_chest_move}.translate")

    blender_node = cmds.createNode("blendColors", name=f"blender_stretch_factor_{i:02}")
    cmds.connectAttr(f"{ctrl_options}.Stretch", f"{blender_node}.blender")

    exp = f"""
    $stretch = ctrl_options.Stretch;
    $ty = loc_info_axis_mid_spine_move.ty;
    $arclen = curveInfo_spine_ribbon_isoparm.arcLength;

    $no_stretch = 1 * $ty; 
    $div_param = $no_stretch / $arclen;
    float $out_neg_stretch_factor;

    if ($div_param < 1) {{
        $out_neg_stretch_factor = $div_param;
    }}

    else {{
        $out_neg_stretch_factor = 1;
    }}

    {blender_node}.color1R = 1;
    {blender_node}.color2R = $out_neg_stretch_factor;
    {poci_node}.parameter = {blender_node}.outputR / ($ty/$ty);
    """
    cmds.expression(
        string=exp,
        name=f"Exp_position_{bind_chest_move}",
        alwaysEvaluate=True,
        unitConversion="all",
    )

    cmds.connectAttr("decMtx_point_4.outputScale", f"{bind_chest_move}.s")
    cmds.connectAttr("decMtx_point_4.outputRotateX", f"{bind_chest_move}.rx")
    cmds.connectAttr("decMtx_point_4.outputRotateZ", f"{bind_chest_move}.rz")

    add_node = cmds.createNode("addDoubleLinear", name="add_twist_chest")
    cmds.connectAttr(f"{ctrl_options}.Twist_Chest", f"{add_node}.input1")
    cmds.connectAttr(f"decMtx_point_4.outputRotateY", f"{add_node}.input2")
    cmds.connectAttr(f"{add_node}.output", f"{bind_chest_move}.ry", force=True)

    cmds.setAttr(f"{ribbon_surface}.v", 0)
    cmds.setAttr(f"{loc_info_axis_mid_ik_pelvis}.v", 0)
    cmds.setAttr(f"{loc_info_axis_mid_spine}.v", 0)
    cmds.setAttr(f"{loc_info_pelvis}.v", 0)
    cmds.setAttr(f"{loc_info_squash_chest}.v", 0)
    cmds.setAttr(f"{loc_info_squash_initial_length}.v", 0)
    cmds.setAttr(f"{curve_isoparm}.v", 0)
    cmds.setAttr(f"{curve_squash_offset}.v", 0)

    cmds.setAttr(f"{ctrl_options}.Stretch_Volume", cb=False, k=False)
    cmds.setAttr(f"{ctrl_options}.Squash_Volume", cb=False, k=False)

    # add intermediate fk controls
    root_pivot_group = cmds.group(empty=True, name="grp_root_pivot")
    color_node(root_pivot_group, "green")
    cmds.matchTransform(root_pivot_group, ctrl_root)

    ctrl_fk_bottom = octagon_control(
        radius=1.5, name=f"{CTRL}_{FK}_bottom", color="blue"
    )
    cmds.matchTransform(ctrl_fk_bottom, ctrl_tangent_pelvis, position=True)
    cmds.parent(ctrl_fk_bottom, ctrl_root)
    offset_parent_matrix(ctrl_fk_bottom)
    cmds.parent(ctrl_fk_mid_offset, root_pivot_group)
    cmds.parent(root_pivot_group, ctrl_fk_bottom)
    color_node(ctrl_fk_bottom, "blue")
    cmds.connectAttr(f"{ctrl_options}.Fk_Visibility", f"{ctrl_fk_bottom}.v")

    # ----------------------------------------------------------------------------------

    mid_pivot_group = cmds.group(empty=True, name="grp_mid_pivot")
    color_node(mid_pivot_group, "green")
    cmds.matchTransform(mid_pivot_group, ctrl_fk_mid)

    ctrl_fk_top = octagon_control(radius=1.5, name=f"{CTRL}_{FK}_top", color="blue")
    cmds.matchTransform(ctrl_fk_top, ctrl_tangent_chest, position=True)
    cmds.parent(ctrl_fk_top, ctrl_fk_mid)
    offset_parent_matrix(ctrl_fk_top)
    cmds.parent(ctrl_fk_chest_offset, mid_pivot_group)
    cmds.parent(mid_pivot_group, ctrl_fk_top)
    color_node(ctrl_fk_top, "blue")
    cmds.connectAttr(f"{ctrl_options}.Fk_Visibility", f"{ctrl_fk_top}.v")

    # ----- SINE --------------------------------------------------------
    sep_cb(ctrl_options, True)
    cmds.addAttr(ctrl_options, ln="sine", nn="Sine", at="long", min=0, max=1, dv=1, k=1)
    cmds.addAttr(
        ctrl_options,
        ln="direction_x",
        nn="Direction X",
        at="long",
        min=0,
        max=1,
        dv=0,
        k=1,
    )
    cmds.addAttr(
        ctrl_options,
        ln="direction_z",
        nn="Direction Z",
        at="long",
        min=0,
        max=1,
        dv=0,
        k=1,
    )
    cmds.addAttr(ctrl_options, ln="amplitude", nn="Amplitude", at="float", dv=0, k=1)
    cmds.addAttr(
        ctrl_options, ln="wavelength", nn="Wavelength", at="float", min=0.1, dv=2, k=1
    )
    cmds.addAttr(ctrl_options, ln="offset", nn="Offset", at="float", dv=0, k=1)
    cmds.addAttr(
        ctrl_options, ln="dropoff", nn="Dropoff", at="float", min=0, max=1, dv=1, k=1
    )

    sine_exp = f"""// Exp_sine_spine

    $sine = {ctrl_options}.sine;
    $x = {ctrl_options}.direction_x;
    $z = {ctrl_options}.direction_z;
    $ampli = {ctrl_options}.amplitude;
    $wave = {ctrl_options}.wavelength;
    $offset = {ctrl_options}.offset;
    $dropoff = {ctrl_options}.dropoff * -1 + 1;

    {ctrl_ik_pelvis_master}.tx = sin(-1 * $wave + $offset) * $ampli * $sine * $dropoff * $x;
    {ctrl_tangent_pelvis_master}.tx = sin(-0.5 * $wave + $offset) * $ampli * $sine * $x;
    {ctrl_ik_mid_master}.tx = sin(0 * $wave + $offset) * $ampli * $sine * $x;
    {ctrl_tangent_chest_master}.tx = sin(0.5 * $wave + $offset) * $ampli * $sine * $x;
    {ctrl_ik_chest_master}.tx = sin(1 * $wave + $offset) * $ampli * $sine * $dropoff * $x;

    {ctrl_ik_pelvis_master}.tz = sin(-1 * $wave + $offset) * $ampli * $sine * $dropoff * $z;
    {ctrl_tangent_pelvis_master}.tz = sin(-0.5 * $wave + $offset) * $ampli * $sine * $z;
    {ctrl_ik_mid_master}.tz = sin(0 * $wave + $offset) * $ampli * $sine * $z;
    {ctrl_tangent_chest_master}.tz = sin(0.5 * $wave + $offset) * $ampli * $sine * $z;
    {ctrl_ik_chest_master}.tz = sin(1 * $wave + $offset) * $ampli * $sine * $dropoff * $z;
    """
    cmds.expression(string=sine_exp, name="Exp_sine_spine")

    om.MGlobal.displayInfo("Spine Matrix done.")
