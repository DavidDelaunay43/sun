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
    rivet,
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


def spine_ribbon(start: str, end: str, suffix: str = ""):
    """ """

    # POSITIONS
    start_pos = cmds.xform(start, query=True, translation=True, worldSpace=True)
    end_pos = cmds.xform(end, query=True, translation=True, worldSpace=True)

    distance = math.dist(start_pos, end_pos)
    pivot_nurbs = start_pos[0], start_pos[1] + distance * 0.5, start_pos[2]

    # NUBRS
    ribbon_surface = cmds.nurbsPlane(
        pivot=pivot_nurbs,
        axis=[0, 0, 1],
        lengthRatio=distance,
        degree=3,
        u=1,
        v=2,
        constructionHistory=False,
        name=f"ribbon_{suffix}",
    )[0]
    cmds.rebuildSurface(
        ribbon_surface,
        degreeU=7,
        degreeV=7,
        spansU=1,
        spansV=2,
        constructionHistory=False,
    )

    tools.bake_pivot(ribbon_surface, x="cx", y="ymin", z="cz")
    offset.offset_parent_matrix(ribbon_surface)

    rivet_group = rivet.rivet_nurbs(ribbon_surface, "v", 5, True)
    rivets = cmds.listRelatives(rivet_group, children=True)

    # ranger le ribbon et les rivets dans xtranodes
    tools.ensure_group(ribbon_surface, XTRA)
    tools.ensure_group(rivet_group, XTRA)

    # CREATE CTRLS
    RADIUS = distance * 0.25
    positions = start_pos, pivot_nurbs, end_pos
    names = f"pelvis_{suffix}", f"mid_{suffix}", f"chest_{suffix}"
    joints = []

    for pos, name in zip(positions, names):
        cmds.select(clear=True)
        joint = cmds.joint(name=f"{CTRL}_{name}", position=pos)
        ctrl = cmds.circle(
            name=f"{CTRL}_{name}_01",
            normal=[0, 1, 0],
            radius=RADIUS,
            constructionHistory=False,
        )[0]
        curve.parent_shapes([ctrl, joint])
        display.color_node(joint, "gold")
        joints.append(joint)

    ctrl_pelvis, ctrl_mid, ctrl_chest = joints

    ctrl_root = cmds.circle(
        name=f"ctrl_root_{suffix}",
        normal=[0, 1, 0],
        radius=RADIUS * 2,
        constructionHistory=False,
    )[0]
    display.color_node(ctrl_root, "orange")
    cmds.setAttr(f"{ctrl_root}.{TRANSLATE}", *start_pos)
    offset.offset_parent_matrix(ctrl_root)

    # faire contrainte scale du root sur les rivets
    for riv in rivets:
        matrix.matrix_constraint(ctrl_root, riv, s=True, mo=True)

    # CREATE FK CTRLS
    fk_spine_start = cmds.circle(
        name=f"{FK}_start_{suffix}",
        normal=[0, 1, 0],
        radius=RADIUS * 1.5,
        constructionHistory=False,
    )[0]
    fk_spine_mid = cmds.circle(
        name=f"{FK}_mid_{suffix}",
        normal=[0, 1, 0],
        radius=RADIUS * 1.5,
        constructionHistory=False,
    )[0]
    fk_spine_end = cmds.circle(
        name=f"{FK}_end_{suffix}",
        normal=[0, 1, 0],
        radius=RADIUS * 1.5,
        constructionHistory=False,
    )[0]

    # définir les positions des contrôleurs FK
    dist = mathfuncs.distance_btw(start, end) * 0.25

    cmds.matchTransform(fk_spine_start, start, position=True)
    cmds.matchTransform(fk_spine_mid, start, position=True)
    cmds.matchTransform(fk_spine_end, start, position=True)

    cmds.move(0, dist, 0, fk_spine_start, relative=True)
    cmds.move(0, dist * 2, 0, fk_spine_mid, relative=True)
    cmds.move(0, dist * 3, 0, fk_spine_end, relative=True)

    display.color_node([fk_spine_start, fk_spine_end, fk_spine_mid], "blue")

    cmds.parent(fk_spine_end, fk_spine_mid)
    cmds.parent(fk_spine_mid, fk_spine_start)

    # ranger le root et les fk dans un groupe
    cmds.parent(fk_spine_start, ctrl_root)
    offset.offset_parent_matrix([fk_spine_start, fk_spine_mid, fk_spine_end])
    ctrls_grp = cmds.group(ctrl_root, name=f"Ctrls_{suffix}")
    tools.ensure_group(ctrls_grp, CTRLS)

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    cmds.parent(ctrl_pelvis, ctrl_root)

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Créer les groupes contraintes
    ctrl_chest_const_fk_spine_end = cmds.group(
        empty=True, name=f"{ctrl_chest}_{CONST}_{fk_spine_end}"
    )
    ctrl_chest_const_fk_spine_mid = cmds.group(
        empty=True, name=f"{ctrl_chest}_{CONST}_{fk_spine_mid}"
    )
    ctrl_chest_const_fk_spine_start = cmds.group(
        empty=True, name=f"{ctrl_chest}_{CONST}_{fk_spine_start}"
    )

    # déplacer les groupes contraintes
    cmds.matchTransform(ctrl_chest_const_fk_spine_end, fk_spine_end, position=True)
    cmds.matchTransform(ctrl_chest_const_fk_spine_mid, fk_spine_mid, position=True)
    cmds.matchTransform(ctrl_chest_const_fk_spine_start, fk_spine_start, position=True)

    # parenter les groupes contraintes
    cmds.parent(ctrl_chest_const_fk_spine_start, ctrl_root)
    cmds.parent(ctrl_chest_const_fk_spine_mid, ctrl_chest_const_fk_spine_start)
    cmds.parent(ctrl_chest_const_fk_spine_end, ctrl_chest_const_fk_spine_mid)

    # cleaner les transforms
    offset.offset_parent_matrix(
        [
            ctrl_chest_const_fk_spine_end,
            ctrl_chest_const_fk_spine_mid,
            ctrl_chest_const_fk_spine_start,
        ]
    )

    # parenter le joint
    cmds.parent(ctrl_chest, ctrl_chest_const_fk_spine_end)
    offset.offset_parent_matrix(ctrl_chest)

    # colorer les groupes contraintes
    display.color_node(
        [
            ctrl_chest_const_fk_spine_end,
            ctrl_chest_const_fk_spine_mid,
            ctrl_chest_const_fk_spine_start,
        ],
        "red",
    )

    # connecter les ctrl et fk aux groupes contraintes
    cmds.connectAttr(
        f"{fk_spine_end}.{ROTATE}", f"{ctrl_chest_const_fk_spine_end}.{ROTATE}"
    )
    cmds.connectAttr(
        f"{fk_spine_mid}.{ROTATE}", f"{ctrl_chest_const_fk_spine_mid}.{ROTATE}"
    )
    cmds.connectAttr(
        f"{fk_spine_start}.{ROTATE}", f"{ctrl_chest_const_fk_spine_start}.{ROTATE}"
    )

    # -------------------------------------------------------------------------------------------------------------------------------------------------
    # Créer les groupes contraintes
    ctrl_spine_const_ctrl_chest = cmds.group(
        empty=True, name=f"{ctrl_pelvis}_{CONST}_{ctrl_chest}"
    )
    ctrl_spine_const_ctrl_pelvis = cmds.group(
        empty=True, name=f"{ctrl_pelvis}_{CONST}_{ctrl_pelvis}"
    )
    ctrl_spine_const_fk_spine_mid = cmds.group(
        empty=True, name=f"{ctrl_pelvis}_{CONST}_{fk_spine_mid}"
    )
    ctrl_spine_const_fk_spine_start = cmds.group(
        empty=True, name=f"{ctrl_pelvis}_{CONST}_{fk_spine_start}"
    )

    # déplacer les groupes contraintes
    cmds.matchTransform(ctrl_spine_const_ctrl_chest, ctrl_mid, position=True)
    cmds.matchTransform(ctrl_spine_const_ctrl_pelvis, ctrl_mid, position=True)
    cmds.matchTransform(ctrl_spine_const_fk_spine_mid, fk_spine_mid, position=True)
    cmds.matchTransform(ctrl_spine_const_fk_spine_start, fk_spine_start, position=True)

    # parenter les groupes contraintes
    cmds.parent(ctrl_spine_const_fk_spine_start, ctrl_root)
    cmds.parent(ctrl_spine_const_fk_spine_mid, ctrl_spine_const_fk_spine_start)
    cmds.parent(ctrl_spine_const_ctrl_pelvis, ctrl_spine_const_fk_spine_mid)
    cmds.parent(ctrl_spine_const_ctrl_chest, ctrl_spine_const_ctrl_pelvis)

    # cleaner les transforms
    offset.offset_parent_matrix(
        [ctrl_spine_const_fk_spine_mid, ctrl_spine_const_ctrl_chest]
    )

    # parenter le joint
    cmds.parent(ctrl_mid, ctrl_spine_const_ctrl_chest)

    # colorer les groupes contraintes
    display.color_node(
        [
            ctrl_spine_const_ctrl_chest,
            ctrl_spine_const_ctrl_pelvis,
            ctrl_spine_const_fk_spine_mid,
            ctrl_spine_const_fk_spine_start,
        ],
        "red",
    )

    # connecter les ctrl et fk aux groupes contraintes
    cmds.connectAttr(
        f"{fk_spine_mid}.{ROTATE}", f"{ctrl_spine_const_fk_spine_mid}.{ROTATE}"
    )
    cmds.connectAttr(
        f"{fk_spine_start}.{ROTATE}", f"{ctrl_spine_const_fk_spine_start}.{ROTATE}"
    )

    div_node = cmds.createNode("multiplyDivide", name=f"div_{fk_spine_mid}")
    cmds.setAttr(f"{div_node}.input2X", 0.5)
    cmds.setAttr(f"{div_node}.input2Y", 0.5)
    cmds.setAttr(f"{div_node}.input2Z", 0.5)

    cmds.connectAttr(f"{ctrl_chest}.{TRANSLATE}", f"{div_node}.input1")
    cmds.connectAttr(f"{div_node}.output", f"{ctrl_spine_const_ctrl_chest}.{TRANSLATE}")

    # skinner le ribbon
    cmds.skinCluster(
        ctrl_pelvis,
        ctrl_mid,
        ctrl_chest,
        ribbon_surface,
        maximumInfluences=3,
        name=f"skinCluster_{ribbon_surface}",
    )

    # squash and stretch ------------------------------------------------------------------------------------------------------------------
    attribute.sep_cb(ctrl_chest, True)
    cmds.addAttr(
        ctrl_chest,
        longName="preserve_volume",
        niceName="Preserve Volume",
        attributeType="float",
        minValue=0,
        maxValue=1,
        defaultValue=0,
        keyable=True,
    )

    loc_spine_start = cmds.spaceLocator(name=f"{LOC}_{suffix}_start")[0]
    loc_spine_end = cmds.spaceLocator(name=f"{LOC}_{suffix}_end")[0]

    loc_spine_start_shape = cmds.listRelatives(loc_spine_start, children=True)[0]
    loc_spine_end_shape = cmds.listRelatives(loc_spine_end, children=True)[0]

    cmds.matchTransform(loc_spine_start, start, position=True)
    cmds.matchTransform(loc_spine_end, end, position=True)

    cmds.makeIdentity(loc_spine_start, apply=True, translate=True)
    cmds.makeIdentity(loc_spine_end, apply=True, translate=True)
    grp_locs_spine = cmds.group(loc_spine_end, loc_spine_start, name=f"Locs_{suffix}")
    tools.ensure_group(grp_locs_spine, XTRA)
    display.color_node([loc_spine_end, loc_spine_start], "red")

    cmds.connectAttr(f"{ctrl_chest}.{TRANSLATE}", f"{loc_spine_end}.{TRANSLATE}")

    # distance between
    distance_between = cmds.createNode("distanceBetween", name=f"distB_locs_{suffix}")
    cmds.connectAttr(
        f"{loc_spine_start_shape}.worldPosition[0]", f"{distance_between}.point1"
    )
    cmds.connectAttr(
        f"{loc_spine_end_shape}.worldPosition[0]", f"{distance_between}.point2"
    )

    # remap value node
    remap_value_node = cmds.createNode("remapValue", name=f"rmValue_{suffix}_volume")
    cmds.connectAttr(f"{ctrl_chest}.preserve_volume", f"{remap_value_node}.inputValue")
    cmds.connectAttr(f"{distance_between}.distance", f"{remap_value_node}.outputMin")

    default_distance = cmds.getAttr(f"{distance_between}.distance")
    cmds.setAttr(f"{remap_value_node}.outputMax", default_distance)

    # multiply divide
    div_node = cmds.createNode("multiplyDivide", name=f"div_{suffix}_scale_factor")
    cmds.setAttr(f"{div_node}.operation", 2)
    cmds.connectAttr(f"{distance_between}.distance", f"{div_node}.input2X")
    cmds.connectAttr(f"{distance_between}.distance", f"{div_node}.input2Y")
    cmds.connectAttr(f"{distance_between}.distance", f"{div_node}.input2Z")

    cmds.connectAttr(f"{remap_value_node}.outValue", f"{div_node}.input1X")
    cmds.connectAttr(f"{remap_value_node}.outValue", f"{div_node}.input1Y")
    cmds.connectAttr(f"{remap_value_node}.outValue", f"{div_node}.input1Z")

    # set range
    set_range_spine = cmds.createNode("setRange", name=f"setRange_{suffix}")
    set_range_spine_mid = cmds.createNode("setRange", name=f"setRange_{suffix}_mid")

    cmds.connectAttr(f"{div_node}.output", f"{set_range_spine}.value")
    cmds.connectAttr(f"{div_node}.output", f"{set_range_spine_mid}.value")

    cmds.setAttr(f"{set_range_spine}.min", -14, -14, -14, type="double3")
    cmds.setAttr(f"{set_range_spine}.max", 16, 16, 16, type="double3")
    cmds.setAttr(f"{set_range_spine}.oldMin", -9, -9, -9, type="double3")
    cmds.setAttr(f"{set_range_spine}.oldMax", 11, 11, 11, type="double3")

    cmds.setAttr(f"{set_range_spine_mid}.min", -16, -16, -16, type="double3")
    cmds.setAttr(f"{set_range_spine_mid}.max", 18, 18, 18, type="double3")
    cmds.setAttr(f"{set_range_spine_mid}.oldMin", -9, -9, -9, type="double3")
    cmds.setAttr(f"{set_range_spine_mid}.oldMax", 11, 11, 11, type="double3")

    # lister les joints
    bind_joints = [cmds.listRelatives(rivet, children=True)[-1] for rivet in rivets]
    bind_01, bind_02, bind_03, bind_04, bind_05 = bind_joints

    # connecter aux scales des bind joints
    cmds.connectAttr(f"{div_node}.outputX", f"{bind_01}.scaleX")
    cmds.connectAttr(f"{div_node}.outputZ", f"{bind_01}.scaleZ")

    cmds.connectAttr(f"{div_node}.outputX", f"{bind_05}.scaleX")
    cmds.connectAttr(f"{div_node}.outputZ", f"{bind_05}.scaleZ")

    cmds.connectAttr(f"{set_range_spine_mid}.outValueX", f"{bind_03}.scaleX")
    cmds.connectAttr(f"{set_range_spine_mid}.outValueZ", f"{bind_03}.scaleZ")

    cmds.connectAttr(f"{set_range_spine}.outValueX", f"{bind_02}.scaleX")
    cmds.connectAttr(f"{set_range_spine}.outValueZ", f"{bind_02}.scaleZ")

    cmds.connectAttr(f"{set_range_spine}.outValueX", f"{bind_04}.scaleX")
    cmds.connectAttr(f"{set_range_spine}.outValueZ", f"{bind_04}.scaleZ")

    # cacher les locators
    locs = rivets
    locs += [loc_spine_start, loc_spine_end]
    for loc in locs:
        shape = cmds.listRelatives(loc, shapes=True)[0]
        cmds.setAttr(f"{shape}.lodVisibility", 0)

    print(f"{suffix} ribbon done.")
