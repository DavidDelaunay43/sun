from ...utils.imports import *
from .. import (
    constants_maya
)

reload(constants_maya)
from ..constants_maya import *

def transfer_deformation_to_blendshape(
    base_geo: str,
    deformed_geo: str,
    blenshape_node: str,
    controlers: dict
):
    '''
    controlers = {
        "ctrl_lattice_eye_L": {
            "tx": (-0.5, 0.5),
            "ty": (-0.5, 0.5),
            "tz": (-0.5, 0.5)
        },
        "ctrl_lattice_eye_R": {
            "tx": (-0.5, 0.5),
            "ty": (-0.5, 0.5),
            "tz": (-0.5, 0.5)
        }
    }
    '''
    
    i: int = cmds.listAttr(f'{blenshape_node}.w', multi = True)
    for control, transforms in controlers.items():
        
        for axis, values in transforms.items():
            
            print(f'{control}.{axis} : {values}')
            
            if len(values) == 2:
                v_min, v_max = values
            else:
                value = values[0]
            
            # mettre l'attribut du controleur à sa valeur
            # add target
            # renommer la target
            # reset l'attribut du controleur
            # créer le remap value et le connecter
            # incrémenter i
            
            if len(values) == 2:
                cmds.setAttr(f'{control}.{axis}', v_min)
                cmds.blendShape(blenshape_node, edit = True, topologyCheck = True, target = [base_geo, i, deformed_geo, 0], tangentSpace = True)
                cmds.aliasAttr(f'{control}_{axis}_min', f'{blenshape_node}.w[{i}]')
                cmds.setAttr(f'{control}.{axis}', 1) if axis.startswith('s') else cmds.setAttr(f'{control}.{axis}', 0)
                
                rm_node = cmds.createNode('remapValue', name = f'rm_{control}_{axis}_min')
                cmds.setAttr(f'{rm_node}.inputMax', v_min)
                cmds.connectAttr(f'{control}.{axis}', f'{rm_node}.inputValue')
                cmds.connectAttr(f'{rm_node}.outValue', f'{blenshape_node}.{control}_{axis}_min')
                
                i += 1
                
                cmds.setAttr(f'{control}.{axis}', v_min)
                cmds.blendShape(blenshape_node, edit = True, topologyCheck = True, target = [base_geo, i, deformed_geo, 0], tangentSpace = True)
                cmds.aliasAttr(f'{control}_{axis}_max', f'{blenshape_node}.w[{i}]')
                cmds.setAttr(f'{control}.{axis}', 1) if axis.startswith('s') else cmds.setAttr(f'{control}.{axis}', 0)
                
                rm_node = cmds.createNode('remapValue', name = f'rm_{control}_{axis}_max')
                cmds.setAttr(f'{rm_node}.inputMax', v_max)
                cmds.connectAttr(f'{control}.{axis}', f'{rm_node}.inputValue')
                cmds.connectAttr(f'{rm_node}.outValue', f'{blenshape_node}.{control}_{axis}_max')
                
                i += 1
                
            else:
                cmds.setAttr(f'{control}.{axis}', value)
                cmds.blendShape(blenshape_node, edit = True, topologyCheck = True, target = [base_geo, i, deformed_geo, 0], tangentSpace = True)
                cmds.aliasAttr(f'{control}_{axis}', f'{blenshape_node}.w[{i}]')
                cmds.setAttr(f'{control}.{axis}', 1) if axis.startswith('s') else cmds.setAttr(f'{control}.{axis}', 0)
                
                rm_node = cmds.createNode('remapValue', name = f'rm_{control}_{axis}')
                cmds.setAttr(f'{rm_node}.inputMax', value)
                cmds.connectAttr(f'{control}.{axis}', f'{rm_node}.inputValue')
                cmds.connectAttr(f'{rm_node}.outValue', f'{blenshape_node}.{control}_{axis}')
                
                i += 1