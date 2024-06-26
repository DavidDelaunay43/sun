from ...utils.imports import *
from .. import constants_maya
from .. import display
from .. import offset
from .. import tools

reload(constants_maya)
reload(display)
reload(offset)
reload(tools)
from ..constants_maya import SHAPES_CTRL


def add_shape(nodes):
    """Add a custom shape to the specified Maya nodes.

    Parameters
    ----------
    nodes : Union[str, List[str]]
        A single node or a list of nodes to which the custom shape will be added.

    Returns
    -------
    None
    """

    nodes: list = tools.ensure_list(nodes)
    for node in nodes:
        ctrl = cmds.circle(normal=[1, 0, 0], constructionHistory=False)[0]
        parent_shapes([ctrl, node])


def remove_shape(nodes: list) -> None:

    nodes: list = tools.ensure_list(nodes)
    for node in nodes:
        shapes = cmds.listRelatives(node, shapes = True, fullPath = True)
        if not shapes:
            return
        for shape in shapes:
            cmds.delete(shape)


def scale_shape(curves, value: float):
    """Scale the specified Maya curves by a given factor.

    Parameters
    ----------
    curves : Union[str, List[str]]
        A single curve or a list of curves to be scaled.
    value : float
        The scaling factor applied to the curves.

    Returns
    -------
    None
    """

    curves: list = tools.ensure_list(curves)
    for curve in curves:
        cvs = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree")
        om.MGlobal.displayInfo(f"{cvs}")
        cmds.select(f"{curve}.cv[0:{cvs-1}]")
        cmds.scale(value, value, value, ws=1)


def shape_vis(nodes, vis: bool):
    """Set the visibility of the shapes associated with the specified Maya nodes.

    Parameters
    ----------
    nodes : Union[str, List[str]]
        A single node or a list of nodes whose associated shapes' visibility will be set.
    vis : bool
        The visibility state to be set for the shapes. True for visible, False for hidden.

    Returns
    -------
    None
    """

    nodes: list = tools.ensure_list(nodes)

    for node in nodes:

        shape = cmds.listRelatives(node, shapes=True)[0]
        cmds.setAttr(f"{shape}.v", vis)


def ensure_shape():
    """ """

    kids: list = cmds.listRelatives("ctrl_main", shapes=True)
    if not kids:
        display.color_node("ctrl_main", "orange")
        circle = cmds.circle(radius=8.0, constructionHistory=False, normal=[0, 1, 0])[0]
        parent_shapes([circle, "ctrl_main"])


def get_cv_coords():
    """Retrieve the world-space coordinates of control vertices for the selected Maya curve.

    Returns
    -------
    None
    """

    nodes: list = cmds.ls(selection=True)

    if not nodes:
        om.MGlobal.displayError("Nothing is selected.")
        return

    node: str = nodes[0]

    num_vtx: int = cmds.getAttr(f"{node}.degree") + cmds.getAttr(f"{node}.spans")
    for i in range(0, num_vtx):
        coord = cmds.xform(
            f"{node}.cv[{i}]", query=True, translation=True, worldSpace=True
        )
        print(coord)


def regular_control(
    side_num: int,
    radius: float = 1.0,
    normal: Literal["x", "y", "z"] = "y",
    name: str = "regluar_control",
    color: str = "yellow",
):
    """Create a regular polygon control curve in Maya.

    Parameters
    ----------
    side_num : int
        Number of sides of the regular polygon.
    radius : float, optional
        Radius of the control curve, default is 1.0.
    normal : {'x', 'y', 'z'}, optional
        Normal direction of the control curve, default is 'y'.
    name : str, optional
        Name of the created control curve, default is 'regular_control'.
    color : str, optional
        Color of the control curve, default is 'yellow'.

    Returns
    -------
    str
        The name of the created control curve.
    """

    points = []
    for i in range(side_num):
        angle = (i / float(side_num)) * (2 * math.pi)
        cos = radius * math.cos(angle)
        sin = radius * math.sin(angle)
        coord_dict = {"x": (0, cos, sin), "y": (cos, 0, sin), "z": (cos, sin, 0)}
        points.append(coord_dict[normal])

    # Ajouter le premier point à la fin pour fermer la courbe
    points.append(points[0])

    # Créer la courbe avec les points calculés
    curve = cmds.curve(d=1, p=points, k=[i for i in range(side_num + 1)], n=name)
    display.color_node(curve, color)
    return curve


square_control = partial(regular_control, side_num=4)
pentagon_control = partial(regular_control, side_num=5)
hexagon_control = partial(regular_control, side_num=6)
heptagon_control = partial(regular_control, side_num=7)
octagon_control = partial(regular_control, side_num=8)


def star_control(name: str = "star_control", color: str = "red", normal=[0, 0, 1]):
    """Create a star-shaped control curve in Maya.

    Parameters
    ----------
    name : str, optional
        Name of the created control curve, default is 'star_control'.
    color : str, optional
        Color of the control curve, default is 'red'.
    normal : List[float], optional
        Normal direction of the control curve, default is [0, 0, 1].

    Returns
    -------
    str
        The name of the created control curve.
    """

    ctrl = cmds.circle(normal=normal, ch=False, name=name)[0]
    cmds.select(
        f"{ctrl}.cv[0]", f"{ctrl}.cv[2]", f"{ctrl}.cv[4]", f"{ctrl}.cv[6]", replace=True
    )
    mel.eval("scale -r -p 0cm 0cm 0cm 0.0699282 0.0699282 0.0699282 ;")
    cmds.select(clear=True)
    display.color_node(ctrl, color)


def control(shape: str = "sphere", name: str = "control", color: str = "yellow"):
    """ """

    # ctrl_name = get_increment_name(name)

    if shape not in SHAPES_CTRL:
        raise ValueError(f"Invalid shape: {shape}")

    vertex_coords = SHAPES_CTRL[shape]

    degree = 1
    if shape in ["star"]:
        degree = 3

    name = cmds.curve(name=name, degree=degree, point=vertex_coords)
    display.color_node(name, color)
    cmds.select(clear=True)
    return name


def poly_to_curve(
    edge,
    form: int = 0,
    degree: int = 1,
    conform_preview: int = 1,
    ch: bool = False,
    name: str = "polyToCurve",
) -> str:
    """Convert a polygon edge to a NURBS curve in Maya.

    Parameters
    ----------
    edge : str
        The polygon edge to be converted to a curve.
    form : int, optional
        Form of the resulting curve (0 for linear, 1 for smooth), default is 0.
    degree : int, optional
        Degree of the resulting curve, default is 1.
    conform_preview : int, optional
        Conformity to the smooth mesh preview (0 for off, 1 for on), default is 1.
    ch : bool, optional
        Preserve construction history, default is False.
    name : str, optional
        Name of the created curve, default is "polyToCurve".

    Returns
    -------
    str
        The name of the created curve.
    """

    om.MGlobal.displayInfo(f"Polygon edge to convert : {edge}")

    cmds.select(edge)
    mel.eval(
        f"polyToCurve -form {form} -degree {degree} -conformToSmoothMeshPreview {conform_preview};"
    )

    curve = cmds.ls(selection=True)[0]
    curve = cmds.rename(curve, name)

    if not ch:
        cmds.delete(curve, constructionHistory=True)

    return curve


def poly_curve_rebuild(
    edge,
    name="polyToCurveReb",
    ch: bool = False,
    rpo: bool = True,
    rt: int = 0,
    end: int = 0,
    kr: int = 1,
    kep: bool = True,
    kt: bool = True,
    s: int = 4,
    d: int = 3,
    tol: float = 0.01,
) -> str:

    curve = poly_to_curve(edge)

    cmds.rebuildCurve(
        curve,
        constructionHistory=ch,
        replaceOriginal=rpo,
        rebuildType=rt,
        endKnots=end,
        keepRange=kr,
        keepEndPoints=kep,
        keepTangents=kt,
        spans=s,
        degree=d,
        tolerance=tol,
    )

    return curve


def parent_shapes(nodes: list):
    """Parent the shapes of nodes under the last transform node.

    Arguments:
    nodes (List[str]): List of node names. The last node in the list will be the parent node.

    Returns:
    None
    """

    shape_nodes = nodes[:-1]
    parent_grp = nodes[-1]

    for node in shape_nodes:

        shape = cmds.listRelatives(node, shapes=True)[0]
        cmds.parent(shape, parent_grp, relative=True, shape=True)
        cmds.delete(node)


def get_curve_length(curve_name: str):
    """Get the length of a NURBS curve in Maya.

    Parameters
    ----------
    curve_name : str
        The name of the NURBS curve.

    Returns
    -------
    float
        The length of the NURBS curve.
    """

    sel = om.MSelectionList()
    sel.add(curve_name)
    curve_dag_path = om.MDagPath()
    sel.getDagPath(0, curve_dag_path)

    curve_fn = om.MFnNurbsCurve(curve_dag_path)
    curve_length = curve_fn.length()

    return curve_length


def get_curve_vertex_count(curve: str) -> int:
    """Get the total number of vertices on a NURBS curve in Maya.

    Parameters
    ----------
    curve : str
        The name of the NURBS curve.

    Returns
    -------
    int
        The total number of vertices on the NURBS curve.
    """

    degree: int = cmds.getAttr(f"{curve}.degree")
    span: int = cmds.getAttr(f"{curve}.spans")
    return degree + span


def loc_on_curve(curve: str, num: int, name: str = "loc", scale=0.02):
    """ """

    curve_shape: str = cmds.listRelatives(curve, shapes=True)[0]
    loc_list: list = []

    for i in range(num):

        poci = cmds.createNode("pointOnCurveInfo", name=f"poci_{name}_{i+1:02}")
        cmds.connectAttr(f"{curve_shape}.worldSpace[0]", f"{poci}.inputCurve")
        cmds.setAttr(f"{poci}.turnOnPercentage", 1)
        parameter = (1 / (num - 1)) * i
        cmds.setAttr(f"{poci}.parameter", parameter)

        loc = cmds.spaceLocator(name=f"{name}_{i+1:02}")[0]
        tools.set_local_scale(loc, scale)
        display.color_node(loc, "red")
        loc_list.append(loc)
        cmds.connectAttr(f"{poci}.result.position", f"{loc}.translate")

    return loc_list


def ensure_direction(curve: str, direction: Literal["positive", "negative"]):
    """Ensure the direction of a NURBS curve in Maya.

    Parameters
    ----------
    curve : str
        The name of the NURBS curve.
    direction : Literal["positive", "negative"]
        The desired direction of the curve, either "positive" or "negative".

    Returns
    -------
    None
    """

    num_cvs: int = get_curve_vertex_count(curve)
    xpos_zero = cmds.pointPosition(f"{curve}.cv[0]")[0]
    xpos_end = cmds.pointPosition(f"{curve}.cv[{num_cvs-1}]")[0]

    pos_to_neg = xpos_zero < xpos_end and direction == "positive"
    neg_to_pos = xpos_zero > xpos_end and direction == "negative"

    if pos_to_neg or neg_to_pos:
        cmds.reverseCurve(curve, constructionHistory=False)
