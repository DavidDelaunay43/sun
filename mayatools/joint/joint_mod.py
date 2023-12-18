from ...utils.imports import *
import maya.OpenMaya as om1
from .. import constants_maya
from .. import curve
from .. import display
from .. import offset
from .. import tools
reload(constants_maya)
reload(curve)
reload(display)
reload(offset)
reload(tools)
from ..constants_maya import *

def create_preserve_jnt(joint: str):
    '''
    '''
    SIDE = tools.get_side_from_node(joint)
    name = joint.split('_')[1]
    cmds.select(clear = True)
    preserve_jnt = cmds.duplicate(joint, renameChildren = True)[0]
    preserve_jnt = cmds.rename(preserve_jnt, f'{BIND}_preserve_{name}_{SIDE}')
    to_delete = cmds.listRelatives(preserve_jnt, children = True)
    cmds.delete(to_delete)

    display.color_node(preserve_jnt, 'white')
    parent_node = cmds.listRelatives(joint, parent = True)[0]
    try:
        cmds.parent(preserve_jnt, parent_node)
    except:
        pass

    mult_node = cmds.createNode('multiplyDivide', name = f'mult_{preserve_jnt}')
    cmds.connectAttr(f'{joint}.r', f'{mult_node}.input1')
    cmds.setAttr(f'{mult_node}.input2', 0.5, 0.5, 0.5)
    cmds.connectAttr(f'{mult_node}.output', f'{preserve_jnt}.r')

    return preserve_jnt

def joint_to_transform(jnt_list: list, color: str = 'white', op_mtx: bool = True):
    '''
    '''
    
    for jnt in jnt_list:
        parent = cmds.listRelatives(jnt, parent = True)
        kid = cmds.listRelatives(jnt, children = True)
        circle = curve.octagon_control(normal = 'x')
        display.color_node(circle, color)
        cmds.matchTransform(circle, jnt)
        
        if parent:
            parent = parent[0]
            cmds.parent(circle, parent)
            if op_mtx:
                offset.offset_parent_matrix(circle)
        if kid:
            kid = kid[0]
            cmds.parent(kid, circle)
            
        cmds.delete(jnt)
        circle = cmds.rename(circle, jnt)
    
def duplicate_joints(jnt: str):
    """
    """

    cmds.duplicate(jnt, renameChildren = True)
    joints = cmds.listRelatives(jnt, allDescendents = True, type = "joint", shapes = False)

def curve_joint(radius: float = 4.0, name = "curve_joint", color = "red", normal = [1, 0, 0]):
    
    cmds.select(clear = True)
    joint = cmds.joint(name = name)

    curve_circle = cmds.circle(normal = normal, 
                        constructionHistory = False, 
                        name = f"{name}_curve", 
                        radius = radius)[0]

    curve.parent_shapes([curve_circle, joint])
    display.color_node(joint, color)

    cmds.select(clear = True)

    return joint

def orient_last_jnt(jnts: Union[str, list]):
    """Orient the last joint in the chain.

    Args:
        jnts (Union[str, List[str]]): Names of the parent joints.

    Returns:
        None
    """

    jnts = ensure_list(jnts)

    for jnt in jnts:
        last_jnt = cmds.listRelatives(jnt, children = True, type = "joint", allDescendents = True)[0]
        cmds.joint(last_jnt, edit = True, orientJoint = "none", children = True, zeroScaleOrient = True)  

def joint_on_curve(curve: str, num: int, name: str = "jnt"):
    """
    """
    
    curve_shape = cmds.listRelatives(curve, shapes = True)[0]
    joint_list = []
    
    for i in range(num):
        
        poci = cmds.createNode("pointOnCurveInfo", name = f"poci_{name}_{i+1:02}")
        cmds.connectAttr(f"{curve_shape}.worldSpace[0]", f"{poci}.inputCurve")
        cmds.setAttr(f"{poci}.turnOnPercentage", 1)
        parameter = (1/(num - 1)) * i
        cmds.setAttr(f"{poci}.parameter", parameter)
        translates = cmds.getAttr(f"{poci}.result.position")[0]
        cmds.delete(poci)
        
        joint = cmds.joint(name = f"{name}_{i+1:02}")
        joint_list.append(joint)
        cmds.setAttr(f"{joint}.translate", *translates, type = "double3")
        
    return joint_list

def distribute_joints_on_curve(curve_name, num_joints):
    """
    """
    
    cmds.select(clear = True)
    
    sel = om1.MSelectionList()
    sel.add(curve_name)
    curve_dag_path = om1.MDagPath()
    sel.getDagPath(0, curve_dag_path)
    
    curve_fn = om1.MFnNurbsCurve(curve_dag_path)
    param_values = []
    curve_length = curve_fn.length()
    
    for i in range(num_joints):
        param = curve_fn.findParamFromLength((i / (num_joints - 1)) * curve_length)
        param_values.append(param)
    
    joints = []
    for param in param_values:
        pos = om1.MPoint()
        curve_fn.getPointAtParam(param, pos, om1.MSpace.kWorld)
        joint = cmds.joint()
        cmds.move(pos.x, pos.y, pos.z, joint, absolute=True)
        joints.append(joint)
        cmds.select(cl=1)
    
    return joints

def create_bone(pos_start, pos_end, name: str = "jnt", side: str = "", color = "white"):
    """
    """
    
    cmds.select(clear = True)
    jnt_start = cmds.joint(position = pos_start, name = f"{name}_start_{side}")
    jnt_end = cmds.joint(position = pos_end, name = f"{name}_end_{side}")
    cmds.joint(jnt_start, edit = True, orientJoint = "xyz", secondaryAxisOrient = "yup")
    cmds.joint(jnt_end, edit = True, orientJoint = "none")
    display.color_node([jnt_start, jnt_end], color)
    cmds.select(clear = True)
    
    return jnt_start, jnt_end