import re
from maya import cmds

RENDERING_NODE_TYPES = [
    'd_openexr',
    'PxrPathTracer',
    'rmanBakingGlobals',
    'rmanDisplay',
    'rmanDisplayChannel',
    'rmanGlobals'
]

def delete_duplicated_rman_nodes():

    for node_type in RENDERING_NODE_TYPES:

        for node in cmds.ls(type = node_type):

            if bool(re.search(r'\d', node)):
                print(node)
                cmds.delete(node)

delete_duplicated_rman_nodes()

from maya import cmds

def set_catmull_clark():
    for mesh in cmds.ls(type = 'mesh'):
        try:
            cmds.setAttr(f'{mesh}.rman_subdivScheme', 1)
        except:
            continue

set_catmull_clark()