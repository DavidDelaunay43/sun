from ...utils.imports import *


def equidistant_numbers(num1, num2):
    if num1 > num2:
        num1, num2 = num2, num1

    distance = (num2 - num1) / 4
    result = [num1 + distance * i for i in range(1, 4)]
    return tuple(result)


def geo_bbox(geo: str) -> Tuple[float]:

    bbox = cmds.exactWorldBoundingBox(geo)
    x_dist = bbox[3] - bbox[0]
    y_dist = bbox[4] - bbox[1]
    z_dist = bbox[5] - bbox[2]
    om.MGlobal.displayInfo(
        f"Dimensions of {geo} : x = {x_dist}, y= {y_dist}, z= {z_dist}"
    )

    return x_dist, y_dist, z_dist


def _get_extreme_value(geo: str, index: int):
    """ """

    bbox = cmds.exactWorldBoundingBox(geo)
    return bbox[index]


xmin = partial(_get_extreme_value, index=0)
ymin = partial(_get_extreme_value, index=1)
zmin = partial(_get_extreme_value, index=2)
xmax = partial(_get_extreme_value, index=3)
ymax = partial(_get_extreme_value, index=4)
zmax = partial(_get_extreme_value, index=5)


def distance_btw(start: str, end: str) -> float:
    """Calculates the distance between two nodes.

    Args:
        start (str): Name of the start node.
        end (str): Name of the end node.

    Returns:
        float: Distance between the two nodes.
    """

    start_pos = cmds.xform(start, query=True, pivots=True, worldSpace=True)
    end_pos = cmds.xform(end, query=True, pivots=True, worldSpace=True)

    start_pos = [round(x, 3) for x in start_pos[0:3]]
    end_pos = [round(x, 3) for x in end_pos[0:3]]

    om.MGlobal.displayInfo(f"{start_pos, end_pos}")
    dist = math.dist(start_pos, end_pos)
    om.MGlobal.displayInfo(f"Distance between {start} and {end} : {dist}")

    return dist


def missing_dist(start: str, mid: str, end: str) -> float:
    """Calculates the missing distance between joints.

    Args:
        start (str): Name of the first joint.
        mid (str): Name of the second joint.
        end (str): Name of the last joint.

    Returns:
        float: Missing distance between the joints.
    """

    dist_01 = distance_btw(start, mid)
    dist_02 = distance_btw(mid, end)
    dist_03 = distance_btw(start, end)

    om.MGlobal.displayInfo(f"{dist_01}, {dist_02}, {dist_03}")
    missing_dist = round(dist_01 + dist_02 - dist_03, 3)
    om.MGlobal.displayInfo(f"{missing_dist}")

    return missing_dist
