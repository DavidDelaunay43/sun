from ...utils.imports import *
from .. import constants_maya
from .. import attribute
from .. import display
reload(constants_maya)
reload(attribute)
reload(display)
from ..constants_maya import *

def matrix_aim_constraint(masters: Union[str, list], target: str,
    r: bool = False, 
    rx: bool = False, 
    ry: bool = False, 
    rz: bool= False,
    av: tuple = (1, 0, 0), 
    uv: tuple = (0, 1, 0),
    mo: bool = True
):
    """Matrix aim constraint.

    Arguments :
    masters : list of strings -- names of the master nodes
    target : string -- name of the target node

    Keyword arguments :
    av : tuple -- aim vector
    uv : tuple -- up vector
    r : boolean -- constrain all rotate axis
    rx : boolean -- constrain rotateX axis
    ry : boolean -- constrain rotateY axis
    rz : boolean -- constrain rotateZ axis
    """

    # create matrix operation nodes
    aim_mtx = cmds.createNode("aimMatrix", name = f"{target}_{AIM_MTX}")
    mult_mtx = cmds.createNode("multMatrix", name = f"{target}_{MULT_MTX}")
    deco_mtx = cmds.createNode("decomposeMatrix", name = f"{target}_{DECO_MTX}")

    # get master nodes
    if isinstance(masters, str):
        aim, up = masters, masters

    else:
        if len(masters) < 2:
            aim, up = masters[0], masters[0]
        else:
            aim, up = masters
            
    # offset
    if cmds.nodeType(target) == 'joint':
        target_const = cmds.group(empty = True, name = f"{target}_const")
        display.color_node(target_const, "red")
        
        cmds.matchTransform(target_const, aim)
        cmds.matchTransform(target_const, target, position = True)
        
        target_parent = cmds.listRelatives(target, parent = True)
        
        if target_parent:
            target_parent = target_parent[0]
            cmds.parent(target_const, target_parent)
            cmds.parent(target, target_const)
        
        cmds.parent(target, target_const)
        target = target_const

    # connections
    cmds.connectAttr(f"{target}.parentMatrix[0]", f"{aim_mtx}.{INPUT_MTX}")
    cmds.connectAttr(f"{aim}.worldMatrix[0]", f"{aim_mtx}.primary.primaryTargetMatrix")
    cmds.connectAttr(f"{up}.worldMatrix[0]", f"{aim_mtx}.secondary.secondaryTargetMatrix")
    
    cmds.connectAttr(f"{aim_mtx}.{OUTPUT_MTX}", f"{mult_mtx}.{MTX_IN0}")
    cmds.connectAttr(f"{target}.parentInverseMatrix", f"{mult_mtx}.{MTX_IN1}")

    cmds.connectAttr(f"{mult_mtx}.{MTX_SUM}", f"{deco_mtx}.{INPUT_MTX}")

    # set attributes
    cmds.setAttr(f"{aim_mtx}.primaryMode", 1)
    cmds.setAttr(f"{aim_mtx}.secondaryMode", 1)

    cmds.setAttr(f"{aim_mtx}.primary.primaryInputAxis", *av)
    cmds.setAttr(f"{aim_mtx}.secondary.secondaryInputAxis", *uv)
    
    values = r, rx, ry, rz
    dec_mtx_attributes = "outputRotate", "outputRotateX", "outputRotateY", "outputRotateZ"
    target_attributes = "r", "rx", "ry", "rz"

    output_string = " "
    for v, dec_at, target_at in zip(values, dec_mtx_attributes, target_attributes):
        if v:
            cmds.connectAttr(f"{deco_mtx}.{dec_at}", f"{target}.{target_at}")
            output_string = f"{target_at}{output_string}"
        if r : 
            break
        
    om.MGlobal.displayInfo(f"Matrix Aim Constraint done : {target} {output_string}")

def matrix_constraint(masters: Union[str, list], target: str, 
    t: bool = False, r: bool = False, s: bool = False, 
    tx: bool = False, ty: bool = False, tz: bool = False, 
    rx: bool = False, ry: bool = False, rz: bool = False, 
    sx: bool = False, sy: bool = False, sz: bool = False, 
    mo: bool = False, w: bool = False, at: bool = False
):
    """Apply a matrix constraint.

    Args:
        masters (Union[str, List[str]]): Names of the master nodes. It can be a single string or a list of strings.
        target (str): Name of the target node.

    Keyword Args:
        t (bool): Constrain all translate axes.
        r (bool): Constrain all rotate axes.
        s (bool): Constrain all scale axes.
        tx (bool): Constrain the translateX axis.
        ty (bool): Constrain the translateY axis.
        tz (bool): Constrain the translateZ axis.
        rx (bool): Constrain the rotateX axis.
        ry (bool): Constrain the rotateY axis.
        rz (bool): Constrain the rotateZ axis.
        sx (bool): Constrain the scaleX axis.
        sy (bool): Constrain the scaleY axis.
        sz (bool): Constrain the scaleZ axis.
        mo (bool): Maintain offset.
        w (bool): Enable weight control by adding a wtAddMatrixNode.
        at (bool): Create an attribute for weight control.

    Returns:
        None
    """

    def offset(master: str, target: str) -> str:
        """Calculate the offset matrix between a master node and a target node.

        Args:
            master (str): Name of the master node.
            target (str): Name of the target node.

        Returns:
            str: Name of the created offset matrix node.
        """

        mult_mtx = cmds.createNode("multMatrix", name = f"{target}_{master}_{MULT_MTX}")

        target_world_mtx = om.MMatrix(cmds.getAttr(f"{target}.worldMatrix[0]"))
        master_world_inverse_mtx = om.MMatrix(cmds.getAttr(f"{master}.worldInverseMatrix[0]"))
        offset_mtx = target_world_mtx * master_world_inverse_mtx

        cmds.setAttr(f"{mult_mtx}.{MTX_IN0}", offset_mtx, type = "matrix")
        cmds.connectAttr(f"{master}.{W_MTX}", f"{mult_mtx}.{MTX_IN1}")
        cmds.connectAttr(f"{target}.{PI_MTX}", f"{mult_mtx}.{MTX_IN2}")

        return mult_mtx

    masters = ensure_list(masters)

    num = len(masters)
    deco_mtx = cmds.createNode("decomposeMatrix", name = f"{target}_{DECO_MTX}")

    return_node = deco_mtx

    if not w and num == 1:
        master = masters[0]

        if mo:
            mult_mtx = offset(master, target)

        else:
            mult_mtx = cmds.createNode("multMatrix", name = f"{target}_{master}_{MULT_MTX}")
            cmds.connectAttr(f"{master}.worldMatrix[0]", f"{mult_mtx}.{MTX_IN0}")
            cmds.connectAttr(f"{target}.parentInverseMatrix[0]", f"{mult_mtx}.{MTX_IN1}")
    
        cmds.connectAttr(f"{mult_mtx}.{MTX_SUM}", f"{deco_mtx}.{INPUT_MTX}")

    else:
        wt_add_mtx = cmds.createNode("wtAddMatrix", name = f"{target}_{WTADD_MTX}")

        for i, master in enumerate(masters):

            default_value = 1 / num
            mult_mtx = offset(master, target)
            cmds.connectAttr(f"{mult_mtx}.{MTX_SUM}", f"{wt_add_mtx}.wtMatrix[{i}].matrixIn")
            cmds.setAttr(f"{wt_add_mtx}.wtMatrix[{i}].weightIn", default_value)

            if at:
                at_nn, at_ln = f"W{i:02} {master}", f"w{i:02}_{master}"

                if i == 0:
                    attribute.sep_cb([target], add=1)

                cmds.addAttr(target, longName = at_ln, 
                                niceName = at_nn, 
                                attributeType = "float", 
                                defaultValue = default_value, 
                                min = 0, max = 1, k = True)
                
                cmds.setAttr(f"{target}.{at_ln}", channelBox = True, keyable = False)
                cmds.connectAttr(f"{target}.{at_ln}", f"{wt_add_mtx}.wtMatrix[{i}].weightIn")

            return_node = [deco_mtx, wt_add_mtx]

        cmds.connectAttr(f"{wt_add_mtx}.{MTX_SUM}", f"{deco_mtx}.{INPUT_MTX}")

    values = t, r, s, tx, ty, tz, rx, ry, rz, sx, sy, sz

    dec_matrix_at = (
        OUTPUT_T, OUTPUT_R, OUTPUT_S, 
        OUTPUT_TX, OUTPUT_TY, OUTPUT_TZ,
        OUTPUT_RX, OUTPUT_RY, OUTPUT_RZ,
        OUTPUT_SX, OUTPUT_SY, OUTPUT_SZ
        )

    target_at = (
        TRANSLATE, ROTATE, SCALE,
        TX, TY, TZ,
        RX, RY, RZ,
        SX, SY, SZ
        )

    output_string = " "

    for v, dm_at, t_at, in zip(values, dec_matrix_at, target_at):
        
        if v:
            cmds.connectAttr(f"{deco_mtx}.{dm_at}", f"{target}.{t_at}")
            output_string = f"{t_at}{output_string}"

    om.MGlobal.displayInfo(f"Matrix Constraint done : {target} {output_string}")
    return return_node
    
def aim_matrix_on_selection(
    r: bool = False, 
    rx: bool = False, 
    ry: bool = False, 
    rz: bool= False,
    av: tuple = (1, 0, 0), 
    uv: tuple = (0, 1, 0),
    mo: bool = True
):
    """
    """
    
    nodes = cmds.ls(selection = True)
    if not nodes or len(nodes) < 2:
        om.MGlobal.displayError("Error in selection.")
        return
    else:
        masters, target = nodes[0:-1], nodes[-1]
        matrix_aim_constraint(masters, target, r, rx, ry, rz, av, uv, mo)

def matrix_on_selection(
    t: bool = False, r: bool = False, s: bool = False, 
    tx: bool = False, ty: bool = False, tz: bool = False, 
    rx: bool = False, ry: bool = False, rz: bool = False, 
    sx: bool = False, sy: bool = False, sz: bool = False, 
    mo: bool = False, w: bool = False, at: bool = False
    ):
    """
    """
    
    nodes = cmds.ls(selection = True)
    if not nodes or len(nodes) < 2:
        om.MGlobal.displayError("Error in selection.")
        return
    else:
        masters, target = nodes[0:-1], nodes[-1]
        matrix_constraint(masters, target, t, r, s, tx, ty, tz, rx, ry, rz, sx, sy, sz, mo, w, at)