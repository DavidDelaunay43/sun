from maya.api import OpenMaya as om

def createNode(node_type: str, name: str = None) -> om.MObject:
    
    fn_dependency_node = om.MFnDependencyNode()
    fn_dependency_node.create(node_type)
    node = fn_dependency_node.object()
    if name:
        fn_dependency_node.setName(name)
    return node

def multMatrix(name: str = None) -> om.MObject:
    return createNode('multMatrix', name)

def decomposeMatrix(name: str = None) -> om.MObject:
    return createNode('decomposeMatrix', name)

def composeMatrix(name: str = None) -> om.MObject:
    return createNode('composeMatrix', name)

def aimMatrix(name: str = None) -> om.MObject:
    return createNode('aimMatrix', name)

def pickMatrix(name: str = None) -> om.MObject:
    return createNode('pickMatrix', name)

def wtAddMatrix(name: str = None) -> om.MObject:
    return createNode('wtAddMatrix', name)

def floatMath(name: str = None) -> om.MObject:
    return createNode('floatMath', name)

def plusMinusAverage(name: str = None) -> om.MObject:
    return createNode('plusMinusAverage', name)

def multiplyDivide(name: str = None) -> om.MObject:
    return createNode('multiplyDivide', name)

def remapValue(name: str = None) -> om.MObject:
    return createNode('remapValue', name)

def condition(name: str = None) -> om.MObject:
    return createNode('condition', name)
