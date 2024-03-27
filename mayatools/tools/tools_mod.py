from ...utils.imports import *
from .. import constants_maya

reload(constants_maya)
from ..constants_maya import *


def bounding_box_override(value):

    def bbox_override(node, value=value):
        cmds.setAttr(f"{node}.overrideEnabled", value)
        cmds.setAttr(f"{node}.overrideLevelOfDetail", value)

    for node in cmds.ls(selection=True):

        if cmds.nodeType(node) == "mesh":
            bbox_override(node, value)

        shapes = cmds.listRelatives(shapes=True)
        for shape in shapes:
            bbox_override(shape, value)


def rename_shape(nodes: Union[str, list]) -> None:
    """ """

    nodes: list = ensure_list(nodes)
    for node in nodes:
        shape: str = cmds.listRelatives(node, shapes=True)
        if not shape:
            continue
        shape: str = shape[0]
        shape_name: str = f"{node}Shape"
        if not shape == shape_name:
            cmds.rename(shape, shape_name)


def equidistant_numbers(num1, num2):
    if num1 > num2:
        num1, num2 = num2, num1

    distance = (num2 - num1) / 4
    result = [num1 + distance * i for i in range(1, 4)]
    return tuple(result)


def get_u_param(pnt=[], crv=None):

    point = om1.MPoint(pnt[0], pnt[1], pnt[2])
    curve_fn = om1.MFnNurbsCurve(get_dag_path(crv))
    param_util = om1.MScriptUtil()
    param_ptr = param_util.asDoublePtr()

    if curve_fn.isPointOnCurve(point):
        curve_fn.getParamAtPoint(point, param_ptr, 0.001, om1.MSpace.kObject)

    else:
        point = curve_fn.closestPoint(point, param_ptr, 0.001, om1.MSpace.kObject)
        curve_fn.getParamAtPoint(point, param_ptr, 0.001, om1.MSpace.kObject)

    param = param_util.getDouble(param_ptr)
    return param


def get_uv_param(point=[0.0, 0.0, 0.0], surface=None):
    point = om1.MPoint(point[0], point[1], point[2])
    surface_fn = om1.MFnNurbsSurface(get_dag_path(surface))

    param_util_u = om1.MScriptUtil()
    param_ptr_u = param_util_u.asDoublePtr()

    param_util_v = om1.MScriptUtil()
    param_ptr_v = param_util_v.asDoublePtr()

    if surface_fn.isPointOnSurface(point):
        surface_fn.getParamAtPoint(point, param_ptr_u, param_ptr_v, False)

    else:
        point = surface_fn.closestPoint(point, param_ptr_u, param_ptr_v)
        surface_fn.getParamAtPoint(point, param_ptr_u, param_ptr_v, False)

    param_u = param_util_u.getDouble(param_ptr_u)
    param_v = param_util_v.getDouble(param_ptr_v)

    return param_u, param_v


def get_dag_path(objectName):

    if isinstance(objectName, list):
        oNodeList = []
        for o in objectName:
            selectionList = om1.MSelectionList()
            selectionList.add(o)
            oNode = om1.MDagPath()
            selectionList.getDagPath(0, oNode)
            oNodeList.append(oNode)
        return oNodeList

    else:
        selectionList = om1.MSelectionList()
        selectionList.add(objectName)
        oNode = om1.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode


def set_historic():
    """ """

    types = (
        "multMatrix",
        "decomposeMatrix",
        "composeMatrix",
        "wtAddMatrix",
        "pickMatrix",
        "pointOnSurfaceInfo",
        "pointOnCurveInfo",
        "plusMinusAverage",
        "multiplyDivide",
        "remapValue",
        "setRange",
        "nonLinear",
        "expression",
        "blendColors",
        "reverse",
        "floatMath",
        "quatToEuler",
        "distanceBetween",
        "dagPose",
        "blinn",
        "projection",
        "colorCorrect",
        "layeredShader",
        "displayLayer",
    )

    for type in types:
        nodes = cmds.ls(type=type)
        for node in nodes:
            try:
                cmds.connectAttr(f"ctrl_main.mode", f"{node}.ihi", force=True)
            except:
                pass


def bake_pivot(node: str, x="cx", y="ymin", z="cz"):
    """ """

    xmin, ymin, zmin, xmax, ymax, zmax = cmds.exactWorldBoundingBox(node)
    cx, cy, cz = cmds.objectCenter(node)

    coords = {
        "cx": cx,
        "cy": cy,
        "cz": cz,
        "xmin": xmin,
        "ymin": ymin,
        "zmin": zmin,
        "xmax": xmax,
        "ymax": ymax,
        "zmax": zmax,
    }

    pivot_coords = (coords[x], coords[y], coords[z])

    cmds.move(*pivot_coords, node + ".scalePivot", node + ".rotatePivot", absolute=True)
    mel.eval("BakeCustomPivot;")


def auto_control():
    """ """
    for node in cmds.ls(selection=True):
        x_min, x_max, y_min, y_max, z_min, z_max = cmds.exactWorldBoundingBox(node)
        y_height = y_min + (y_max - y_min) / 10
        coord01 = [x_min * 1.1, y_height, z_min * 1.1]
        coord02 = [x_min * 1.1, y_height, z_max * 1.1]
        coord03 = [x_max * 1.1, y_height, z_max * 1.1]
        coord04 = [x_max * 1.1, y_height, z_min * 1.1]
        coords = (coord01, coord02, coord03, coord04, coord01)
        degree = 1
        control = cmds.curve(name=f"ctrl_{node}", degree=degree, point=coords)
        cmds.select(clear=True)
        cmds.setAttr(f"{control}.useOutlinerColor", 1)
        cmds.setAttr(f"{control}.outlinerColor", 1.0, 0.7461085915565491, 0.0)
        cmds.setAttr(f"{control}.overrideEnabled", 1)
        cmds.setAttr(f"{control}.overrideRGBColors", 1)
        cmds.setAttr(f"{control}.overrideColorRGB", 1.0, 0.5246000289916992, 0.0)

        cx, _, cz = cmds.objectCenter(node)
        cmds.setAttr(f"{control}.t", cx, 0, cz)

        grp_geo = cmds.listRelatives(node, children=True)[0]
        cmds.parent(control, node)
        cmds.makeIdentity(control, apply=True, translate=True)
        cmds.parentConstraint(control, grp_geo)
        cmds.scaleConstraint(control, grp_geo)


def get_side_from_node(node: str):
    """ """

    x_coord = cmds.xform(node, query=True, translation=True, worldSpace=True)[0]
    SIDE = "L" if x_coord > 0 else "R"
    return SIDE


def get_hierarchy(node: str):
    """ """

    kids = cmds.listRelatives(node, ad=1)
    kids.reverse()

    nodes = [node]
    for kid in kids:
        nodes.append(kid)

    return nodes


def loc_world():
    """ """

    loc_name = "loc_world"
    if not cmds.objExists(loc_name):
        cmds.spaceLocator(name=loc_name)[0]
        cmds.setAttr(f"{loc_name}.v", 0)
        ensure_group(loc_name, LOCATORS)

    return loc_name


def ensure_set(nodes, set_name="bind_joints"):
    """ """

    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)

    cmds.sets(nodes, addElement=set_name)
    cmds.select(clear=True)


def ensure_group(children: str, parent: str, ctrl_main: bool = True):
    """ """

    cmds.select(clear=True)

    if cmds.objExists(parent):
        try:
            cmds.parent(children, parent)
        except:
            pass
    else:
        grp = cmds.group(empty=True, world=True, name=parent)
        cmds.parent(children, grp)

    if parent in [JOINTS, CTRLS, LOCATORS, IKS]:
        ensure_group(parent, GLOBAL_MOVE)
        if ctrl_main:
            ensure_group(GLOBAL_MOVE, "ctrl_main")
            ensure_group("ctrl_main", "AssetName")
        else:
            ensure_group(GLOBAL_MOVE, "AssetName")

    if parent in [SHOW, HIDE]:
        ensure_group(parent, XTRA)
        ensure_group(XTRA, "AssetName")


def ensure_list(arg):

    if isinstance(arg, str):
        return [arg]
    else:
        return arg


def get_increment_name(basename: str):
    """ """

    existing_names = cmds.ls(f"{basename}_*")

    if existing_names:
        existing_nums = [
            int(re.search(rf"{basename}_(\d+)", name).group(1))
            for name in existing_names
        ]
        next_number = max(existing_nums) + 1

    else:
        next_number = 1

    return f"{basename}_{next_number:02}"


def return_set_members():
    """ """

    selection = cmds.ls(selection=True)

    item = selection[0]
    type = cmds.nodeType(item)

    return cmds.sets(item, query=True) if type == "objectSet" else selection


def find_side(object: str):
    """ """

    if isinstance(object, list):
        object = object[0]

    x_coord = cmds.xform(object, query=True, pivots=True, worldSpace=True)[0]
    if x_coord != 0:
        return "L" if x_coord > 0 else "R"


def joint_draw_style(style: str):
    """ """

    styles = {"Bone": 0, "Box": 1, "None": 2}

    joints = cmds.ls(type="joint")
    for joint in joints:
        style_num = styles.get(style)
        cmds.setAttr(f"{joint}.drawStyle", style_num)


def create_loc_center(object: str, loc_name="loc_center"):
    """ """

    locator = cmds.spaceLocator(name=loc_name)[0]
    cmds.matchTransform(locator, object)
    return locator


def set_local_scale(locs, scale: float):
    """ """

    locs = ensure_list(locs)
    scale = (scale, scale, scale)

    for loc in locs:
        loc_shape = cmds.listRelatives(loc, shapes=True)[0]
        cmds.setAttr(f"{loc_shape}.localScale", *scale, type="double3")


# ----------------------------------------------------
def _get_bbox_item(object: str, item):
    return cmds.exactWorldBoundingBox(object)[item]


get_xmin = partial(_get_bbox_item, item=0)
get_ymin = partial(_get_bbox_item, item=1)
get_zmin = partial(_get_bbox_item, item=2)
get_xmax = partial(_get_bbox_item, item=3)
get_ymax = partial(_get_bbox_item, item=4)
get_zmax = partial(_get_bbox_item, item=5)


# ----------------------------------------------------
def _get_bbox_size(object: str, axis: str):
    axis_dict = {
        "x": (get_xmax, get_xmin),
        "y": (get_ymax, get_ymin),
        "z": (get_zmax, get_zmin),
    }

    max, min = axis_dict.get(axis)
    return max(object) - min(object)


get_xsize = partial(_get_bbox_size, axis="x")
get_ysize = partial(_get_bbox_size, axis="y")
get_zsize = partial(_get_bbox_size, axis="z")


# ----------------------------------------------------
def set_loc_object_size(locs, object: str, proportion: float):

    locs = ensure_list(locs)
    object_size = get_ysize(object)

    for loc in locs:
        local_scale = cmds.getAttr(f"{loc}.localScaleX")
        current_proportion = local_scale / object_size
        mult = proportion / current_proportion
        new_local_scale = local_scale * mult
        set_local_scale(loc, new_local_scale)

        """
        loc = 2.0
        obj = 17.0
        prop = 0.2
        
        current_prop = loc/obj
        mult = prop/current
        
        
        
        """


def get_input_node(node_at: str, return_at: bool = False):
    """ """

    info = cmds.connectionInfo(node_at, sourceFromDestination=True)
    node = info.split(".")[0]

    om.MGlobal.displayInfo(f"Connection info : {info}")
    om.MGlobal.displayInfo(f"Input node : {node}")

    return info if return_at else node


def get_base_wire(wire_node: str):
    """ """

    shape_node = get_input_node(f"{wire_node}.baseWire[0]")
    transform_node = cmds.listRelatives(shape_node, parent=True)[0]
    return transform_node
