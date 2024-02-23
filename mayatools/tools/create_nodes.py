from maya import cmds

targets = (
    'fk_arm_L_rotateY_min',
    'fk_arm_L_rotateY_max',
    'fk_arm_L_rotateZ_min',
    'fk_arm_L_rotateZ_max'
)

values = (
    -40,
    40,
    -45,
    45
)

bshape_node = 'BShape_robe'
driver = 'drv_arm_L'
 

for target, value in zip(targets, values):

    attribute = target.split('_')[3]
    rm_node = cmds.createNode('remapValue', name = f'rm_{target}')
    cmds.setAttr(f'{rm_node}.inputMax', value)
    cmds.connectAttr(f'{driver}.{attribute}', f'{rm_node}.inputValue')
    cmds.connectAttr(f'{rm_node}.outValue', f'{bshape_node}.{target}')

