from maya import cmds
from maya.api import OpenMaya as om

def get_weight_num(blendshape_node: str) -> int:
    weight_num = cmds.listAttr(f'{blendshape_node}.w', multi = True)
    if not weight_num:
        return 0
    else:
        return len(weight_num)

def add_target(base_geo: str, deformed_geo: str, blendshape_node: str, alias_name: str = None):
    index: int = get_weight_num(blendshape_node)
    cmds.blendShape(blendshape_node, edit = True, topologyCheck = True, target = [base_geo, index, deformed_geo, 1.0], weight = [index, 0.0], tangentSpace = True)
    if alias_name:
        cmds.aliasAttr(alias_name, f'{blendshape_node}.w[{index}]')
    
    bad_attribute = cmds.listConnections(f'{deformed_geo}.worldMesh[0]', source = False, destination = True, plugs = True)
    if bad_attribute:
        cmds.disconnectAttr(f'{deformed_geo}.worldMesh[0]', bad_attribute[0])

def get_matrix(node: str, matrix: str):
    return om.MMatrix(cmds.getAttr(f'{node}.{matrix}[0]'))

def get_world_matrix(node: str):
    return get_matrix(node, 'worldMatrix')

def get_world_inverse_matrix(node: str):
    return get_matrix(node, 'worldInverseMatrix')

def get_offset_matrix(moving_node: str, static_node: str) -> om.MMatrix:
    moving_node_world_matrix: om.MMatrix = get_world_matrix(static_node)
    static_node_world_inverse_matrix: om.MMatrix = get_world_inverse_matrix(moving_node)
    return moving_node_world_matrix * static_node_world_inverse_matrix

def rotation_matrix_setup(moving_node: str, static_node: str) -> str:

    offset_matrix: om.MMatrix = get_offset_matrix(moving_node, static_node)
    mult_matrix_node: str = cmds.createNode('multMatrix', name = f'multMTX_rotation_{moving_node}')
    decompose_matrix_node: str = cmds.createNode('decomposeMatrix', name = f'decoMTX_rotation_{moving_node}')  

    cmds.setAttr(f'{mult_matrix_node}.matrixIn[0]', offset_matrix, type = 'matrix')
    cmds.connectAttr(f'{moving_node}.worldMatrix[0]', f'{mult_matrix_node}.matrixIn[1]')
    cmds.connectAttr(f'{static_node}.worldInverseMatrix[0]', f'{mult_matrix_node}.matrixIn[2]')

    cmds.connectAttr(f'{mult_matrix_node}.matrixSum', f'{decompose_matrix_node}.inputMatrix')

    return decompose_matrix_node

def finger_blendshape(geo: str, blendshape_node: str, transform_axis: str, transform_value: float, moving_phalanx: str, existing_target: bool = False):
    
    moving_phalanx_up_grp = cmds.listRelatives(moving_phalanx, parent = True)[0]
    static_phalanx = cmds.listRelatives(moving_phalanx_up_grp, parent = True)[0]

    alias_name: str = f'{moving_phalanx}_{transform_axis}'
    deco_mtx_output_attribute: str = f'output{transform_axis[0].upper()}{transform_axis[1:]}' 

    if not existing_target:
        add_target(geo, geo, blendshape_node, alias_name = alias_name)
    
    decompose_matrix_node: str = rotation_matrix_setup(moving_phalanx, static_phalanx)

    remap_value_node: str = cmds.createNode('remapValue', name = f'rv_{alias_name}')
    cmds.connectAttr(f'{decompose_matrix_node}.{deco_mtx_output_attribute}', f'{remap_value_node}.inputValue')
    cmds.setAttr(f'{remap_value_node}.inputMax', transform_value)
    cmds.connectAttr(f'{remap_value_node}.outValue', f'{blendshape_node}.{alias_name}')

def fingers_blendshapes(geo: str, blendshape_node: str, transform_axis: str, transform_value: float, all_moving_phalanx: list, existing_target: bool = False):

    for moving_phalanx in all_moving_phalanx:

        finger_blendshape(geo, blendshape_node, transform_axis, transform_value, moving_phalanx, existing_target = existing_target)
