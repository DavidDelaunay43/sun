from ...utils.imports import *
from .. import constants_maya, curve, tools, rivet

reload(constants_maya)
reload(curve)
reload(tools)
reload(rivet)
from ..constants_maya import SHOW


def remap_scale(jnts: list):
    """ """

    for jnt in jnts:

        rm_node = cmds.createNode("remapValue", name=f"rm_{jnt}")
        cmds.setAttr(f"{rm_node}.inputMax", -65)
        cmds.setAttr(f"{rm_node}.outputMin", 1)
        cmds.setAttr(f"{rm_node}.outMax", 0.745)

        cmds.connectAttr(f"{jnt}.rz", f"{rm_node}.inputValue")
        cmds.connectAttr(f"{rm_node}.outputValue", f"{jnt}.sx")


def facial_ribbon(edges, face_area: str, offset: float, offset_axis: str):
    """ """

    # curves
    curve_start: str = curve.poly_curve_rebuild(
        edges,
        constructionHistory=False,
        replaceOriginal=True,
        rebuildType=0,
        endKnots=0,
        keepRange=1,
        keepEndPoints=True,
        keepTangents=True,
        spans=4,
        degree=3,
        tolerance=0.01,
    )

    SIDE: str = tools.get_side_from_node(curve_start)
    curve_start = cmds.rename(curve_start, f"crv_start_{face_area}_{SIDE}")
    curve_end: str = cmds.duplicate(curve_start, name=f"crv_end_{face_area}_{SIDE}")

    if offset_axis == "y":
        cmds.move(0, 0.05, 0, curve_end)

    else:  # 'z'
        cmds.move(0, 0, 0.05, curve_end)

    # surface
    rev_normal: int = 0 if SIDE == "L" else 1

    ribbon: str = cmds.loft(
        curve_start,
        curve_end,
        n=f"ribbon_{face_area}_{SIDE}",
        constructionHistory=False,
        uniform=True,
        close=False,
        autoReverse=True,
        degree=3,
        sectionSpans=1,
        polygon=0,
        reverseSurfaceNormals=rev_normal,
    )[0]

    u_spans: int = cmds.getAttr(f"{ribbon}.spansU")
    v_spans: int = cmds.getAttr(f"{ribbon}.spansV")

    if u_spans == 1 and v_spans != 1:
        u_param: bool = False
        v_param: bool = True
        isoparm_axis: str = "u"

    else:  # u_spans != 1 and v_spans ==1
        u_param: bool = True
        v_param: bool = False
        isoparm_axis: str = "v"

    # rivets -------------------------------------------------------------------
    rivet_grp: str = cmds.group(
        empty=True, world=True, name=f"rivet_{face_area}_{SIDE}"
    )
    ribbon_shape: str = cmds.listRelatives(ribbon, shapes=True)[0]
    grp_rivets: str = rivet.rivet_nurbs(ribbon_shape, "v", 5, jnt=True)
    tools.ensure_group(grp_rivets, SHOW, ctrl_main=False)

    # isoparm curve ------------------------------------------------------------
    cmds.select(f"{ribbon}.{isoparm_axis}[0.5]", replace=True)
    isoparm_selection: str = cmds.ls(selection=True)[0]
    isoparm_curve: str = cmds.duplicateCurve(
        isoparm_selection,
        name=f"crv_isoparm_{face_area}_{SIDE}",
        constructionHistory=False,
        range=False,
        local=False,
    )
    (
        curve.ensure_direction(isoparm_curve, "positive")
        if SIDE == "L"
        else curve.ensure_direction(isoparm_curve, "negative")
    )


def facial_ribbon_02(
    curve_start: str, curve_end: str, face_area: str, riv_num: int = 5
):
    """ """

    SIDE = tools.get_side_from_node(curve_start)

    # surface
    rev_normal: int = 0 if SIDE == "L" else 1

    ribbon: str = cmds.loft(
        curve_start,
        curve_end,
        n=f"ribbon_{face_area}",
        constructionHistory=False,
        uniform=True,
        close=False,
        autoReverse=True,
        degree=3,
        sectionSpans=1,
        polygon=0,
        reverseSurfaceNormals=rev_normal,
    )[0]

    u_spans: int = cmds.getAttr(f"{ribbon}.spansU")
    v_spans: int = cmds.getAttr(f"{ribbon}.spansV")

    if u_spans == 1 and v_spans != 1:
        u_param: bool = False
        v_param: bool = True
        isoparm_axis: str = "u"

    else:  # u_spans != 1 and v_spans ==1
        u_param: bool = True
        v_param: bool = False
        isoparm_axis: str = "v"

    # rivets -------------------------------------------------------------------
    rivet_grp: str = cmds.group(empty=True, world=True, name=f"rivet_{face_area}")
    ribbon_shape: str = cmds.listRelatives(ribbon, shapes=True)[0]
    grp_rivets: str = rivet.rivet_nurbs(ribbon_shape, "u", riv_num, jnt=True)
    tools.ensure_group(grp_rivets, SHOW, ctrl_main=False)

    # isoparm curve ------------------------------------------------------------
    cmds.select(f"{ribbon}.{isoparm_axis}[0.5]", replace=True)
    isoparm_selection: str = cmds.ls(selection=True)[0]
    isoparm_curve: str = cmds.duplicateCurve(
        isoparm_selection,
        name=f"crv_isoparm_{face_area}",
        constructionHistory=False,
        range=False,
        local=False,
    )[0]
    (
        curve.ensure_direction(isoparm_curve, "positive")
        if SIDE == "L"
        else curve.ensure_direction(isoparm_curve, "negative")
    )
