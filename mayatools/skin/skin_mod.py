from ...utils.imports import *
from ..constants_maya import *


def find_skin_cluster(mesh):
    """
    Trouver le skin cluster d'un maillage.
    :param mesh: Le maillage dont vous voulez trouver le skin cluster.
    :return: Le nom du skin cluster, ou None si aucun n'est trouvé.
    """
    history = cmds.listHistory(mesh, pruneDagObjects=True)

    # Parcourir l'historique pour trouver le skin cluster
    for node in history:
        if cmds.nodeType(node) == "skinCluster":
            return node

    return None


def get_vertices_side(mesh: str, side: str):
    """
    Renvoie la liste des sommets du côté spécifié du maillage.
    :param mesh: Nom du maillage.
    :param side: Côté souhaité ('L' pour gauche, 'R' pour droite).
    :return: Liste des sommets du côté spécifié.
    """

    vertices = cmds.ls(f"{mesh}.vtx[*]", flatten=True)

    # Utiliser une liste de compréhension pour exclure les sommets indésirables
    vertices = [
        vtx
        for vtx in vertices
        if cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0]
        not in [0.0, -0.0]
    ]

    # Filtrer les sommets en fonction du côté
    if side == "L":
        vertices = [
            vtx
            for vtx in vertices
            if round(
                cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0], 3
            )
            < 0.0
        ]
    elif side == "R":
        vertices = [
            vtx
            for vtx in vertices
            if round(
                cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0], 3
            )
            > 0.0
        ]

    return vertices


def exclude_skin_side(side: str, vertices: list):
    """ """

    excluded_joints = cmds.ls(f"*{side}*", type="joint")
    mesh = vertices[0].split(".")[0]
    mesh_shape = cmds.listRelatives(mesh, shapes=True)[0]
    skin_cluster = find_skin_cluster(mesh_shape)

    for jnt in excluded_joints:
        try:
            cmds.skinPercent(skin_cluster, *vertices, transformValue=[jnt, 0.0])
            print("zero")
        except:
            print("fail")


def exclude_skin_sides(mesh: str):
    """ """

    vertices_left = get_vertices_side(mesh, "L")
    vertices_right = get_vertices_side(mesh, "R")
    exclude_skin_side("L", vertices_left)
    exclude_skin_side("R", vertices_right)


def get_influences(mesh: str) -> tuple:
    """ """
    skin_cluster = cmds.listConnections(mesh, type="skinCluster")

    if not skin_cluster:
        return (None, None)

    else:
        skin_cluster = skin_cluster[0]

    influences = cmds.skinCluster(skin_cluster, query=True, inf=True)
    om.MGlobal.displayInfo(f"{influences}")
    return skin_cluster, influences


def copy_skin(source_mesh: str, destination_mesh: str):
    """ """

    if cmds.nodeType(source_mesh) != "mesh":
        om.MGlobal.displayError(f"{source_mesh} is not a mesh.")
        return

    source_skin_cluster, influences = get_influences(source_mesh)

    if not source_skin_cluster:
        om.MGlobal.displayInfo(f"No skinCluster found on {source_mesh}")
        return

    max_influences = cmds.skinCluster(
        source_skin_cluster, query=True, maximumInfluences=True
    )

    if not influences:
        om.MGlobal.displayError(f"No influences found on {source_mesh}")
        return

    if cmds.nodeType(destination_mesh) != "mesh":
        om.MGlobal.displayError(f"{destination_mesh} is not a mesh.")
        return

    cmds.skinCluster(influences, destination_mesh, maximumInfluences=max_influences)

    cmds.select(source_mesh, destination_mesh, replace=True)
    copy_skin_mel = "copySkinWeights -noMirror -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation oneToOne -influenceAssociation oneToOne -normalize;select -cl;"
    mel.eval(copy_skin_mel)


def remove_orig_shapes(geo_list: list) -> list:
    """ """

    return_geos = []
    for geo in geo_list:
        if not "Orig" in geo:
            return_geos.append(geo)

    return return_geos


def get_mesh_children(group: str) -> list:
    """ """

    mesh = cmds.listRelatives(group, allDescendents=True, type="mesh")
    if not mesh:
        om.MGlobal.displayError(f"No mesh under node : {group}")
        return

    return mesh


def replace_geos(source_group: str, destination_group: str):
    """ """

    all_source_geos = get_mesh_children(source_group)
    all_destination_geos = get_mesh_children(destination_group)

    source_geos = remove_orig_shapes(all_source_geos)
    destination_geos = remove_orig_shapes(all_destination_geos)

    """for source_mesh, destination_mesh in zip(source_geos, destination_geos):
        copy_skin(source_mesh = source_mesh, destination_mesh = destination_mesh)"""

    for source_mesh in source_geos:

        match = source_mesh.split(":")[-1]

        for destination_mesh in destination_geos:
            if match in destination_mesh:
                om.MGlobal.displayInfo(f"SOURCE MESH : {source_mesh}")
                om.MGlobal.displayInfo(f"DESINTATION MESH : {destination_mesh}")
                copy_skin(source_mesh=source_mesh, destination_mesh=destination_mesh)

            else:
                continue
