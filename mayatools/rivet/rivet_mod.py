from ...utils.imports import *
from .. import constants_maya, attribute, display, tools

reload(constants_maya)
reload(attribute)
reload(display)
reload(tools)
from ..constants_maya import *


def face_to_edges(face: str) -> Tuple[str]:
    """Convert a face to a pair of non-shared edges.

    Args:
        face (str): Name of the face.

    Returns:
        Tuple[str]: A tuple containing the names of two non-shared edges.
    """

    edges = cmds.ls(
        cmds.polyListComponentConversion(face, ff=True, te=True), flatten=True
    )

    edge_01 = set(
        cmds.ls(
            cmds.polyListComponentConversion(edges[0], fe=True, tv=True), flatten=True
        )
    )

    for i in range(1, len(edges)):

        edge_02 = set(
            cmds.ls(
                cmds.polyListComponentConversion(
                    edges[i], fromEdge=True, toVertex=True
                ),
                flatten=True,
            )
        )

        if not edge_01 & edge_02:

            return edges[0], edges[i]


def rivet_mesh_setup(
    name: str, edge_a: str, edge_b: str, size: float = 1.0, col: str = "orange"
) -> str:

    rivet = f"{name}_01"
    for i in range(2, 100):
        if cmds.objExists(rivet):
            rivet = f"{name}_{i:02}"

    cmds.spaceLocator(n=rivet)
    rivet_shape = cmds.listRelatives(rivet, s=1)[0]

    mesh = edge_a.split(".")[0]
    shape = cmds.listRelatives(mesh, s=1)[0]

    cmds.setAttr(f"{rivet_shape}.localScaleX", size)
    cmds.setAttr(f"{rivet_shape}.localScaleY", size)
    cmds.setAttr(f"{rivet_shape}.localScaleZ", size)

    display.color_node(rivet, col)

    edge_a_num = int(re.sub(r"[^\d]+", "", edge_a))
    edge_b_num = int(re.sub(r"[^\d]+", "", edge_b))

    cmds.addAttr(
        rivet, ln="pos_u", nn="Pos U", at="float", min=0.0, max=1.0, dv=0.5, k=0
    )
    cmds.addAttr(
        rivet, ln="pos_v", nn="Pos V", at="float", min=0.0, max=1.0, dv=0.5, k=0
    )
    cmds.setAttr(f"{rivet}.pos_u", cb=1, k=0)
    cmds.setAttr(f"{rivet}.pos_v", cb=1, k=0)

    # nodes
    curve_01 = cmds.createNode("curveFromMeshEdge", n=f"{rivet}_{mesh}_01")
    curve_02 = cmds.createNode("curveFromMeshEdge", n=f"{rivet}_{mesh}_02")
    loft = cmds.createNode("loft", n=f"{rivet}_loft")
    posi = cmds.createNode("pointOnSurfaceInfo", n=f"{rivet}_posInfo")
    vec_prod = cmds.createNode("vectorProduct", n=f"{rivet}_vectProd")
    matrix = cmds.createNode("fourByFourMatrix", n=f"{rivet}_4by4Mtx")
    pick_mtx = cmds.createNode("pickMatrix", n=f"{rivet}_pickMtx")

    # set and connect attributes
    # curves
    cmds.setAttr(f"{curve_01}.edgeIndex[0]", edge_a_num)
    cmds.setAttr(f"{curve_02}.edgeIndex[0]", edge_b_num)

    cmds.connectAttr(f"{shape}.worldMesh[0]", f"{curve_01}.inputMesh")
    cmds.connectAttr(f"{shape}.worldMesh[0]", f"{curve_02}.inputMesh")

    # loft
    cmds.setAttr(f"{loft}.inputCurve", size=2)
    cmds.setAttr(f"{loft}.uniform", 1)
    cmds.setAttr(f"{loft}.reverseSurfaceNormals", 1)

    cmds.connectAttr(f"{curve_01}.outputCurve", f"{loft}.inputCurve[0]")
    cmds.connectAttr(f"{curve_02}.outputCurve", f"{loft}.inputCurve[1]")

    # point on surface info
    cmds.setAttr(f"{posi}.turnOnPercentage", 1)

    cmds.connectAttr(f"{loft}.outputSurface", f"{posi}.inputSurface")
    cmds.connectAttr(f"{rivet}.pos_u", f"{posi}.parameterU")
    cmds.connectAttr(f"{rivet}.pos_v", f"{posi}.parameterV")

    # cross product
    cmds.setAttr(f"{vec_prod}.operation", 2)

    cmds.connectAttr(f"{posi}.normal", f"{vec_prod}.input1")
    cmds.connectAttr(f"{posi}.tangentV", f"{vec_prod}.input2")

    # matrix
    cmds.connectAttr(f"{posi}.normalX", f"{matrix}.in00")
    cmds.connectAttr(f"{posi}.normalY", f"{matrix}.in01")
    cmds.connectAttr(f"{posi}.normalZ", f"{matrix}.in02")

    cmds.connectAttr(f"{posi}.tangentVx", f"{matrix}.in10")
    cmds.connectAttr(f"{posi}.tangentVy", f"{matrix}.in11")
    cmds.connectAttr(f"{posi}.tangentVz", f"{matrix}.in12")

    cmds.connectAttr(f"{vec_prod}.outputX", f"{matrix}.in20")
    cmds.connectAttr(f"{vec_prod}.outputY", f"{matrix}.in21")
    cmds.connectAttr(f"{vec_prod}.outputZ", f"{matrix}.in22")

    cmds.connectAttr(f"{posi}.positionX", f"{matrix}.in30")
    cmds.connectAttr(f"{posi}.positionY", f"{matrix}.in31")
    cmds.connectAttr(f"{posi}.positionZ", f"{matrix}.in32")

    # pick matrix
    cmds.setAttr(f"{pick_mtx}.useScale", 0)
    cmds.setAttr(f"{pick_mtx}.useShear", 0)

    cmds.connectAttr(f"{matrix}.output", f"{pick_mtx}.{INPUT_MTX}")

    # rivet
    cmds.connectAttr(f"{pick_mtx}.{OUTPUT_MTX}", f"{rivet}.{OP_MTX}")

    # historical interest
    cmds.setAttr(f"{curve_01}.ihi", 0)
    cmds.setAttr(f"{curve_02}.ihi", 0)
    cmds.setAttr(f"{loft}.ihi", 0)
    cmds.setAttr(f"{posi}.ihi", 0)
    cmds.setAttr(f"{vec_prod}.ihi", 0)
    cmds.setAttr(f"{matrix}.ihi", 0)
    cmds.setAttr(f"{pick_mtx}.ihi", 0)
    cmds.setAttr(f"{rivet_shape}.ihi", 0)

    om.MGlobal.displayInfo(f"{rivet} done.")
    return rivet


def rivet_mesh(
    faces: Union[str, list[str]],
    name: str = "rivet",
    size: float = 1.0,
    col: str = "orange",
):

    faces = tools.ensure_list(faces)

    for face in faces:
        edge_01, edge_02 = face_to_edges(face)
        rivet_mesh_setup(name, edge_01, edge_02, size=size, col=col)


def rivet_mesh_user(name: str = "rivet", size: float = 1.0, col: str = "orange"):

    selection = cmds.ls(selection=True)
    faces = cmds.filterExpand(selection, selectionMask=34)

    if faces:
        rivet_mesh(faces, name=name, size=size, col=col)


def connect_rivet(
    node: str,
    surface_shape: str,
    parameter: float,
    uv: Literal["u", "v", "uv"] = "v",
    jnt: bool = False,
    delete_shape: bool = False,
) -> tuple:
    """ """

    TAN = uv.capitalize()

    attribute.sep_cb(node)
    if uv in ["u", "v"]:
        cmds.addAttr(
            node, at="float", ln=f"parameter_{uv}", min=0, max=1, dv=parameter, k=1
        )
        cmds.setAttr(f"{node}.parameter_{uv}", cb=1, k=0)

    else:
        cmds.addAttr(
            node, at="float", ln=f"parameter_u", min=0, max=1, dv=parameter, k=1
        )
        cmds.setAttr(f"{node}.parameter_u", cb=1, k=0)
        cmds.addAttr(
            node, at="float", ln=f"parameter_v", min=0, max=1, dv=parameter, k=1
        )
        cmds.setAttr(f"{node}.parameter_v", cb=1, k=0)

    # nodes
    posi = cmds.createNode("pointOnSurfaceInfo", n=f"{node}_posInfo")
    vec_prod = cmds.createNode("vectorProduct", n=f"{node}_vectProd")
    matrix = cmds.createNode("fourByFourMatrix", n=f"{node}_4by4Mtx")
    pick_mtx = cmds.createNode("pickMatrix", n=f"{node}_pickMtx")

    # set and connect attributes
    # point on surface info
    cmds.setAttr(f"{posi}.turnOnPercentage", 1)

    cmds.connectAttr(f"{surface_shape}.worldSpace[0]", f"{posi}.inputSurface")

    # cross product
    cmds.setAttr(f"{vec_prod}.operation", 2)

    cmds.connectAttr(f"{posi}.normal", f"{vec_prod}.input1")
    cmds.connectAttr(f"{posi}.tangent{TAN}", f"{vec_prod}.input2")

    # matrix
    cmds.connectAttr(f"{posi}.normalX", f"{matrix}.in00")
    cmds.connectAttr(f"{posi}.normalY", f"{matrix}.in01")
    cmds.connectAttr(f"{posi}.normalZ", f"{matrix}.in02")

    cmds.connectAttr(f"{posi}.tangent{TAN}x", f"{matrix}.in10")
    cmds.connectAttr(f"{posi}.tangent{TAN}y", f"{matrix}.in11")
    cmds.connectAttr(f"{posi}.tangent{TAN}z", f"{matrix}.in12")

    cmds.connectAttr(f"{vec_prod}.outputX", f"{matrix}.in20")
    cmds.connectAttr(f"{vec_prod}.outputY", f"{matrix}.in21")
    cmds.connectAttr(f"{vec_prod}.outputZ", f"{matrix}.in22")

    cmds.connectAttr(f"{posi}.positionX", f"{matrix}.in30")
    cmds.connectAttr(f"{posi}.positionY", f"{matrix}.in31")
    cmds.connectAttr(f"{posi}.positionZ", f"{matrix}.in32")

    # pick matrix
    cmds.setAttr(f"{pick_mtx}.useScale", 0)
    cmds.setAttr(f"{pick_mtx}.useShear", 0)

    cmds.connectAttr(f"{matrix}.output", f"{pick_mtx}.{INPUT_MTX}")

    # node
    cmds.connectAttr(f"{pick_mtx}.{OUTPUT_MTX}", f"{node}.{OP_MTX}")

    # set node position
    if uv == "u":
        cmds.connectAttr(f"{node}.parameter_u", f"{posi}.parameterU")
        cmds.setAttr(f"{posi}.parameterV", 0.5)

    elif uv == "v":
        cmds.connectAttr(f"{node}.parameter_v", f"{posi}.parameterV")
        cmds.setAttr(f"{posi}.parameterU", 0.5)

    else:
        cmds.connectAttr(f"{node}.parameter_u", f"{posi}.parameterU")
        cmds.connectAttr(f"{node}.parameter_v", f"{posi}.parameterV")

    # create joints
    if jnt:
        cmds.select(node)
        bind_jnt = cmds.joint(n=f"bind_{node}")
        tools.ensure_set(bind_jnt)
        display.color_node(bind_jnt, "white")

    if delete_shape:
        loc_shape = cmds.listRelatives(node, shapes=True)[0]
        cmds.delete(loc_shape)

    # historical interest
    cmds.setAttr(f"{posi}.ihi", 0)
    cmds.setAttr(f"{vec_prod}.ihi", 0)
    cmds.setAttr(f"{matrix}.ihi", 0)
    cmds.setAttr(f"{pick_mtx}.ihi", 0)

    return posi, vec_prod, matrix, pick_mtx


def rivet_nurbs(
    nurbs_surface: str,
    uv: Literal["u", "v"],
    rivet_num: int = 0,
    jnt: bool = False,
    size: float = 1.0,
    col: str = "orange",
    delete_shape: bool = False,
) -> str:
    """Create vectorial rivets on a NURBS surface.

    Args:
        surface (str): Name of the NURBS surface.
        uv (Literal["u", "v"]): Specifies whether the rivets should be created along the "u" or "v" axis.
        rivet_num (int): Number of rivets to create.

    Keyword Args:
        jnt (bool): Specifies whether to create joints at the rivet positions.
        size (float): Size of the rivets.
        col (str): Color of the rivets.

    Returns:
        None
    """

    # identify nurbs surface
    if cmds.nodeType(nurbs_surface) == "transform":
        surface = nurbs_surface
        surface_shape = cmds.listRelatives(surface, s=1)[0]

    elif cmds.nodeType(nurbs_surface) == "nurbsSurface":
        surface_shape = nurbs_surface
        surface = cmds.listRelatives(surface_shape, p=1)[0]

    rivets_grp = cmds.group(n=f"Grp_rivets_{surface}", em=1)

    # set spacing operators
    increment = round(1 / rivet_num, 3)
    offset = round(increment * 0.5, 3)

    for i in range(1, rivet_num + 1):
        # create rivet
        rivet = f"rivet_{surface}_{i:02}"
        cmds.spaceLocator(n=rivet)
        shape = cmds.listRelatives(rivet, shapes=True)[0]
        cmds.setAttr(f"{shape}.v", 0)
        cmds.parent(rivet, rivets_grp)

        display.color_node(rivet, col)
        display.loc_size(rivet, size)

        parameter = round(increment * i - offset, 3)
        connect_rivet(rivet, surface_shape, parameter, uv, jnt, delete_shape)

    cmds.select(cl=1)
    om.MGlobal.displayInfo(f"Rivets done on {surface}.")

    return rivets_grp
