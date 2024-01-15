from ...utils.imports import *
from .. import attribute

def add_main_attributes(node: str) -> None:
    '''
    '''

    MODE: str = 'mode'
    PC: str = 'primaryControls'
    SC: str = 'secondaryControls'
    LC: str = 'latticeControls'

    attribute.sep_cb(node)
    cmds.addAttr(node, longName = MODE, niceName = 'Mode', attributeType = 'enum', enumName = 'Anim:Rig')
    cmds.addAttr(node, longName = PC, niceName = 'Primary Controls', attributeType = 'bool')
    cmds.addAttr(node, longName = SC, niceName = 'Secondary Controls', attributeType = 'bool')
    cmds.addAttr(node, longName = LC, niceName = 'Lattice Controls', attributeType = 'bool')

    attribute.cb_attributes(node, ats = [MODE, PC, SC, LC], nonkeyable = True)
