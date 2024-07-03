from maya import cmds
import maya.api.OpenMaya as om


def ignore_namespace(node: str) -> str:
    """
    """
    if ':' in node:
        node = node.split(':')[-1]

    return node


def blendshape(driver_mesh: str, deformed_mesh: str) -> str:
    """
    """

    blendshape_node = cmds.blendShape(driver_mesh, deformed_mesh, name = f'BShape_{deformed_mesh}')
    if isinstance(blendshape_node, list):
        blendshape_node = blendshape_node[0]
    cmds.setAttr(f"{blendshape_node}.{ignore_namespace(driver_mesh)}", 1.0)

    return blendshape_node


def duplicate_mesh(mesh: str, new_name: str) -> str:
    """
    Duplicate a mesh with a new name.

    Parameters:
        mesh (str): The name of the mesh to duplicate.
        new_name (str): The new name for the duplicated mesh.

    Returns:
        str: The name of the duplicated mesh.
    """

    om.MGlobal.displayInfo(f'Mesh to duplicate : {mesh}')
    cmds.duplicate(mesh, name = new_name)
    shapes = cmds.listRelatives(new_name, shapes = True, fullPath = True)
    for shape in shapes:
        if cmds.getAttr(f'{shape}.intermediateObject') == 1:
            cmds.delete(shape)

        else:
            cmds.rename(shape, f'{new_name}Shape')

    return new_name


def duplicate_blendshape(driver_mesh: str, deformed_mesh: str, new_name: str):
    pass