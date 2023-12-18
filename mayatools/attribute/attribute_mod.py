from ...utils.imports import *
from functools import partial

def disconnect_attributes(node: str, attributes: list):
    for at in attributes:
        attribut_complet = f'{node}.{at}'

        connexions = cmds.listConnections(attribut_complet, source=True, destination=True, plugs=True)

        if connexions:
            for connexion in connexions:
                cmds.disconnectAttr(connexion, attribut_complet)
 

def _set_rman_attr(node: str, value: bool):
    """_summary_

    Args:
        node (str): _description_
        value (bool): _description_
    """

    attributes = cmds.listAttr(node, string = "rman*") or []

    for at in attributes:
        try:
            cmds.setAttr(f"{node}.{at}", keyable = value, channelBox = value)
        except:
            pass

def rman_attribs(nodes, value: bool):
    """Display or hide Renderman attributes in the channel box for the specified nodes.

    Args:
        nodes (List[str]): List of node names.
        value (bool): Boolean value indicating whether to display or hide the attributes.

    Returns:
        None
    """
    
    nodes = ensure_list(nodes)
    
    for node in nodes:
        _set_rman_attr(node, value)

        shapes = cmds.listRelatives(node, shapes = True, fullPath = True)

        if shapes:
            [_set_rman_attr(shape, value) for shape in shapes]

    output = "displayed" if value else "hidden"
    om.MGlobal.displayInfo(f"Renderman attributes {output}.")

def dag_rman_attribs(value: bool):

    dag_nodes = cmds.ls(dagObjects = True)    
    rman_attribs(dag_nodes, value)

def sep_cb(nodes: Union[str, list], value: bool = True, style: Literal["hyphen", "underscore"] = "hyphen"):
    """Add or delete separator attribute in channel box.

    Arguments :
    nodes : list of strings -- name of nodes

    Keyword arguments :
    v : boole -- add or delete separator
    """

    nodes = ensure_list(nodes)
    
    styles = {
        "hyphen": "---------------",
        "underscore": "____________"
    }

    sep_string = styles[style]

    for node in nodes:

        separators = cmds.listAttr(node, channelBox = True, keyable = False, visible = True, string = "sep_*")
        num = len(separators) if separators else 0

        if value:
            sep_name = f"sep_{num:02}"
            cmds.addAttr(node, longName = sep_name, niceName = sep_string, attributeType = "enum", enumName = sep_string)
            cmds.setAttr(f"{node}.{sep_name}", cb = 1)
        
        else:
            if separators:
                sep_name = separators[-1]
                cmds.deleteAttr(f"{node}.{sep_name}")

            else:
                om.MGlobal.displayWarning(f"No separator attribute on : {node}")

def cb_attributes(nodes: Union[list, str], ats = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"],
    lock: bool = False, unlock: bool = False, 
    hide: bool = False, show: bool = False, 
    nonkeyable: bool = False, keyable: bool = False):

    nodes = ensure_list(nodes)

    for node in nodes:
        for at in ats:

            if lock:
                cmds.setAttr(f"{node}.{at}", lock = True)

            if unlock:
                cmds.setAttr(f"{node}.{at}", lock = False)

            if hide:
                cmds.setAttr(f"{node}.{at}", channelBox = False, keyable = False)

            if show:
                cmds.setAttr(f"{node}.{at}", channelBox =True)

            if nonkeyable:
                cmds.setAttr(f"{node}.{at}", channelBox = True, keyable = False)

            if keyable:
                cmds.setAttr(f"{node}.{at}", channelBox = True, keyable = True)

vis_no_keyable = partial(cb_attributes, ats = ['v'], nonkeyable = True)
          
def watermark():

    nodes = cmds.ls(selection = True)

    for node in nodes:
        cmds.addAttr(node, ln = 'watermark', nn = 'DAVID', at = 'enum', en = 'DELAUNAY', k=1)
        cmds.setAttr(f"{node}.watermark", lock = True)
        cmds.addAttr(node, ln='watermark_hidden', nn = 'DAVID', at = 'enum', en = 'DELAUNAY', k=0)
        cmds.setAttr(f"{node}.watermark_hidden", lock = True)

        wmk_node = cmds.createNode("unknown", n = f"DAVID_DELAUNAY_{node}")
        cmds.lockNode(wmk_node, lock = True)
