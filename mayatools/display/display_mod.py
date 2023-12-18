from ...utils.imports import *

def color_node(nodes: Union[str, list], 
    input_col: Literal["blue", "blue_elec", "gold", "green", "magenta", "orange", "pink", "red", "yellow", "white"]
):
    """Color the nodes in the viewport and outliner.

    Args:
        nodes (Union[str, List[str]]): Names of the nodes.
        input_col (Literal["blue", "gold", "green", "magenta", "orange", "red", "yellow", "white"]): Color to apply.

    Returns:
        None
    """

    nodes = ensure_list(nodes)

    colors = {
        "blue": ((0.26279, 0.61957, 0.99998), (0.0, 0.801, 1.0)),
        "blue_elec": ((0.588, 0.611, 1.0), (0.0, 0.18, 1.0)),
        "gold": ((1.0, 0.7461085915565491, 0.0), (1.0, 0.5246000289916992, 0.0)),
        "green": ((0.0, 1.0, 0.0), (0.0, 1.0, 0.0)),
        "magenta": ((0.913, 0.441, 0.478), (0.954, 0.0, 0.152)),
        "orange": ((1.0, 0.476, 0.187), (1.0, 0.35, 0.0)),
        "pink": ((0.892, 0.589, 0.745), (0.948, 0.238, 0.633)),
        "red": ((1.0, 0.4, 0.4), (1.0, 0.195, 0.0)),
        "yellow": ((0.9906, 0.99258, 0.38934), (1.0, 1.0, 0.12479)),
        "white": ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0))
    }

    if input_col in colors:
        out_col, ov_col = colors[input_col]

        for node in nodes:
            cmds.setAttr(f"{node}.useOutlinerColor", 1)
            cmds.setAttr(f"{node}.outlinerColor", *out_col)
            cmds.setAttr(f"{node}.overrideEnabled", 1)
            cmds.setAttr(f"{node}.overrideRGBColors", 1)
            cmds.setAttr(f"{node}.overrideColorRGB", *ov_col)

def joint_rad(jnts: Union[str, list], factor: float):

    jnts = ensure_list(jnts)

    for jnt in jnts:

        rad = cmds.getAttr(f"{jnt}.radius")
        new_rad = rad * factor

        cmds.setAttr(f"{jnt}.radius", new_rad)

def lod_vis(nodes: Union[str, list], v: bool):
    """Enable or disable LOD visibility on nodes.

    Args:
        nodes (Union[str, list[str]]): Names of the nodes.
        v (bool): Boolean value indicating whether to enable or disable LOD visibility.

    Returns:
        None
    """

    nodes = ensure_list(nodes)

    for node in nodes:
        shape = cmds.listRelatives(node, shapes = True)[0]

        if shape:
            cmds.setAttr(f"{node}.lodVisibility", v)

        else:
            cmds.setAttr(f"{shape}.lodVisibility", v)

def loc_size(locs: Union[str, list], size: float):
    """Edit the localScale attribute on the shape of the locators.

    Args:
        locs (Union[str, list[str]]): Names of the locators.
        size (float): Value for the localScale attribute.

    Returns:
        None
    """

    locs = ensure_list(locs)

    size = (size, size, size)

    for loc in locs:
        loc_shape = cmds.listRelatives(loc, shapes = True)[0]
        cmds.setAttr(f"{loc_shape}.localScale", *size)
