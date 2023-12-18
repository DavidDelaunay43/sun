from ..utils.imports import *
from .constants_maya import *

def find_skin_cluster(mesh):
    """
    Trouver le skin cluster d'un maillage.
    :param mesh: Le maillage dont vous voulez trouver le skin cluster.
    :return: Le nom du skin cluster, ou None si aucun n'est trouvé.
    """
    history = cmds.listHistory(mesh, pruneDagObjects=True)
    
    # Parcourir l'historique pour trouver le skin cluster
    for node in history:
        if cmds.nodeType(node) == 'skinCluster':
            return node
    
    return None

def get_vertices_side(mesh: str, side: str):
    '''
    Renvoie la liste des sommets du côté spécifié du maillage.
    :param mesh: Nom du maillage.
    :param side: Côté souhaité ('L' pour gauche, 'R' pour droite).
    :return: Liste des sommets du côté spécifié.
    '''
    
    vertices = cmds.ls(f'{mesh}.vtx[*]', flatten=True)
    
    # Utiliser une liste de compréhension pour exclure les sommets indésirables
    vertices = [vtx for vtx in vertices if cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0] not in [0.0, -0.0]]

    # Filtrer les sommets en fonction du côté
    if side == 'L':
        vertices = [vtx for vtx in vertices if round(cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0], 3) < 0.0]
    elif side == 'R':
        vertices = [vtx for vtx in vertices if round(cmds.xform(vtx, query=True, translation=True, worldSpace=True)[0], 3) > 0.0]

    return vertices

def exclude_skin_side(side: str, vertices: list):
    '''
    '''
    
    excluded_joints = cmds.ls(f'*{side}*', type = 'joint')
    mesh = vertices[0].split('.')[0]
    mesh_shape = cmds.listRelatives(mesh, shapes = True)[0]
    skin_cluster = find_skin_cluster(mesh_shape)
    
    for jnt in excluded_joints:
        try:
            cmds.skinPercent(skin_cluster, *vertices, transformValue = [jnt, 0.0])
            print('zero')
        except:
            print('fail')

def exclude_skin_sides(mesh: str):
    '''
    '''

    vertices_left = get_vertices_side(mesh, 'L')
    vertices_right = get_vertices_side(mesh, 'R')
    exclude_skin_side('L', vertices_left)
    exclude_skin_side('R', vertices_right)
