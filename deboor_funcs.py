"""
Functions for generating spline weights.
Usage:
    This modules functions each take curve parameters and output control point weights. The weights are generated using
    a modified version of de Boor's algorithm. These weights can be used to create a weighted sum to find a point or 
    tangent on a spline.
    
    While these functions are written for usage in Autodesk Maya, they don't actually have any Maya-specific libraries.
    Additionally none of these functions actually care about the data type of provided control points. This way these
    functions can support points or matrices or Maya attribute names. The output mapping will use the same control
    point that were provided.
Examples:
    This module does include some Maya examples at the very end. These example functions are intended to be used for 
    testing or serve as a starting point for use elsewhere. They are not designed to be functional auto-riggers.
"""


def defaultKnots(count, degree=3):
    """
    Gets a default knot vector for a given number of cvs and degrees.
    Args:
        count(int): The number of cvs. 
        degree(int): The curve degree. 
    Returns:
        list: A list of knot values.
    """
    knots = [0 for i in range(degree)] + [i for i in range(count - degree + 1)]
    knots += [count - degree for i in range(degree)]
    return [float(knot) for knot in knots]


def pointOnCurveWeights(cvs, t, degree, knots=None):
    """
    Creates a mapping of cvs to curve weight values on a spline curve.
    While all cvs are required, only the cvs with non-zero weights will be returned.
    This function is based on de Boor's algorithm for evaluating splines and has been modified to consolidate weights.
    Args:
        cvs(list): A list of cvs, these are used for the return value.
        t(float): A parameter value. 
        degree(int): The curve dimensions. 
        knots(list): A list of knot values. 
    Returns:
        list: A list of control point, weight pairs.
    """

    order = degree + 1  # Our functions often use order instead of degree
    if len(cvs) <= degree:
        raise CurveException(f'Curves of degree {degree} require at least {degree + 1} cvs')

    knots = knots or defaultKnots(len(cvs), degree)  # Defaults to even knot distribution
    if len(knots) != len(cvs) + order:
        raise CurveException(f'Not enough knots provided. Curves with {len(cvs)} cvs must have a knot vector of length {len(cvs) + order}. '
                             f'Received a knot vector of length {len(knots)}: {knots}. '
                             'Total knot count must equal len(cvs) + degree + 1.')

    # Convert cvs into hash-able indices
    _cvs = cvs
    cvs = [i for i in range(len(cvs))]

    # Remap the t value to the range of knot values.
    min = knots[order] - 1
    max = knots[len(knots) - 1 - order] + 1
    t = (t * (max - min)) + min

    # Determine which segment the t lies in
    segment = degree
    for index, knot in enumerate(knots[order:len(knots) - order]):
        if knot <= t:
            segment = index + order

    # Filter out cvs we won't be using
    cvs = [cvs[j + segment - degree] for j in range(0, degree + 1)]

    # Run a modified version of de Boors algorithm
    cvWeights = [{cv: 1.0} for cv in cvs]
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            right = j + 1 + segment - r
            left = j + segment - degree
            alpha = (t - knots[left]) / (knots[right] - knots[left])

            weights = {}
            for cv, weight in cvWeights[j].items():
                weights[cv] = weight * alpha

            for cv, weight in cvWeights[j - 1].items():
                if cv in weights:
                    weights[cv] += weight * (1 - alpha)
                else:
                    weights[cv] = weight * (1 - alpha)

            cvWeights[j] = weights

    cvWeights = cvWeights[degree]
    return [[_cvs[index], weight] for index, weight in cvWeights.items()]


def tangentOnCurveWeights(cvs, t, degree, knots=None):
    """
    Creates a mapping of cvs to curve tangent weight values.
    While all cvs are required, only the cvs with non-zero weights will be returned.
    Args:
        cvs(list): A list of cvs, these are used for the return value.
        t(float): A parameter value. 
        degree(int): The curve dimensions. 
        knots(list): A list of knot values. 
    Returns:
        list: A list of control point, weight pairs.
    """

    order = degree + 1  # Our functions often use order instead of degree
    if len(cvs) <= degree:
        raise CurveException(f'Curves of degree {degree} require at least {degree + 1} cvs')

    knots = knots or defaultKnots(len(cvs), degree)  # Defaults to even knot distribution
    if len(knots) != len(cvs) + order:
        raise CurveException(f'Not enough knots provided. Curves with {len(cvs)} cvs must have a knot vector of length {len(cvs) + order}. '
                             f'Received a knot vector of length {len(knots)}: {knots}. '
                             f'Total knot count must equal len(cvs) + degree + 1.')

    # Remap the t value to the range of knot values.
    min = knots[order] - 1
    max = knots[len(knots) - 1 - order] + 1
    t = (t * (max - min)) + min

    # Determine which segment the t lies in
    segment = degree
    for index, knot in enumerate(knots[order:len(knots) - order]):
        if knot <= t:
            segment = index + order

    # Convert cvs into hash-able indices
    _cvs = cvs
    cvs = [i for i in range(len(cvs))]

    # In order to find the tangent we need to find points on a lower degree curve
    degree = degree - 1
    qWeights = [{cv: 1.0} for cv in range(0, degree + 1)]

    # Get the DeBoor weights for this lower degree curve
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            right = j + 1 + segment - r
            left = j + segment - degree
            alpha = (t - knots[left]) / (knots[right] - knots[left])

            weights = {}
            for cv, weight in qWeights[j].items():
                weights[cv] = weight * alpha

            for cv, weight in qWeights[j - 1].items():
                if cv in weights:
                    weights[cv] += weight * (1 - alpha)
                else:
                    weights[cv] = weight * (1 - alpha)

            qWeights[j] = weights
    weights = qWeights[degree]

    # Take the lower order weights and match them to our actual cvs
    cvWeights = []
    for j in range(0, degree + 1):
        weight = weights[j]
        cv0 = j + segment - degree
        cv1 = j + segment - degree - 1
        alpha = weight * (degree + 1) / (knots[j + segment + 1] - knots[j + segment - degree])
        cvWeights.append([cvs[cv0], alpha])
        cvWeights.append([cvs[cv1], -alpha])

    return [[_cvs[index], weight] for index, weight in cvWeights]


def pointOnSurfaceWeights(cvs, u, v, uKnots=None, vKnots=None, degree=3):
    """
    Creates a mapping of cvs to surface point weight values.
    Args:
        cvs(list): A list of cv rows, these are used for the return value.
        u(float): The u parameter value on the curve.
        v(float): The v parameter value on the curve.
        uKnots(list, optional): A list of knot integers along u.
        vKnots(list, optional): A list of knot integers along v.
        degree(int, optional): The degree of the curve. Minimum is 2.
    Returns:
        list: A list of control point, weight pairs.
    """
    matrixWeightRows = [pointOnCurveWeights(row, u, degree, uKnots) for row in cvs]
    matrixWeightColumns = pointOnCurveWeights([i for i in range(len(matrixWeightRows))], v, degree, vKnots)
    surfaceMatrixWeights = []
    for index, weight in matrixWeightColumns:
        matrixWeights = matrixWeightRows[index]
        surfaceMatrixWeights.extend([[m, (w * weight)] for m, w in matrixWeights])

    return surfaceMatrixWeights


def tangentUOnSurfaceWeights(cvs, u, v, uKnots=None, vKnots=None, degree=3):
    """
    Creates a mapping of cvs to surface tangent weight values along the u axis.
    Args:
        cvs(list): A list of cv rows, these are used for the return value.
        u(float): The u parameter value on the curve.
        v(float): The v parameter value on the curve.
        uKnots(list, optional): A list of knot integers along u.
        vKnots(list, optional): A list of knot integers along v.
        degree(int, optional): The degree of the curve. Minimum is 2.
    Returns:
        list: A list of control point, weight pairs.
    """

    matrixWeightRows = [pointOnCurveWeights(row, u, degree, uKnots) for row in cvs]
    matrixWeightColumns = tangentOnCurveWeights([i for i in range(len(matrixWeightRows))], v, degree, vKnots)
    surfaceMatrixWeights = []
    for index, weight in matrixWeightColumns:
        matrixWeights = matrixWeightRows[index]
        surfaceMatrixWeights.extend([[m, (w * weight)] for m, w in matrixWeights])

    return surfaceMatrixWeights


def tangentVOnSurfaceWeights(cvs, u, v, uKnots=None, vKnots=None, degree=3):
    """
    Creates a mapping of cvs to surface tangent weight values along the v axis.
    Args:
        cvs(list): A list of cv rows, these are used for the return value.
        u(float): The u parameter value on the curve.
        v(float): The v parameter value on the curve.
        uKnots(list, optional): A list of knot integers along u.
        vKnots(list, optional): A list of knot integers along v.
        degree(int, optional): The degree of the curve. Minimum is 2.
    Returns:
        list: A list of control point, weight pairs.
    """
    # Re-order the cvs
    rowCount = len(cvs)
    columnCount = len(cvs[0])
    reorderedCvs = [[cvs[row][col] for row in range(rowCount)] for col in range(columnCount)]
    return tangentUOnSurfaceWeights(reorderedCvs, v, u, uKnots=vKnots, vKnots=uKnots, degree=degree)


class CurveException(BaseException):
    """ Raised to indicate invalid curve parameters. """


# ------- EXAMPLES -------- #


import math
from maya import cmds


def _testCube(radius=1.0, color=(1,1,1), name='cube', position=(0,0,0)):
    """ Creates a cube for testing purposes. """
    radius *= 2
    cube = cmds.polyCube(name=name, h=radius, w=radius, d=radius)[0]
    shader = cmds.shadingNode('lambert', asShader=True)
    cmds.setAttr(f'{shader}.color', *color)
    cmds.setAttr(f'{shader}.ambientColor', 0.1, 0.1, 0.1)
    shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr(f'{shader}.outColor', f"{shadingGroup}.surfaceShader", force=True)
    cmds.sets(cube, fe=shadingGroup)
    cmds.xform(cube, t=position)
    return cube


def _testSphere(radius=1.0, color=(1,1,1), name='sphere', position=(0,0,0)):
    """ Creates a sphere for testing purposes. """
    sphere = cmds.polySphere(name=name, radius=radius)[0]
    shader = cmds.shadingNode('lambert', asShader=True)
    cmds.setAttr(f'{shader}.ambientColor', 0.1, 0.1, 0.1)
    cmds.setAttr(f'{shader}.color', *color)
    shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr(f'{shader}.outColor', f'{shadingGroup}.surfaceShader', force=True)
    cmds.sets(sphere, fe=shadingGroup)
    cmds.xform(sphere, t=position)
    return sphere



def _testMatrixOnCurve(count=4, p_count=None, degree=3):
    """
    Creates an example curve with the given cv and point counts.
    
    Args:
        count (int): The amount of cvs. 
        p_count (int): The amount of points to attach to the curve.
        degree (int): The degree of the curve.
    """

    p_count = p_count or count * 4
    c_radius = 1.0
    p_radius = 0.5
    spacing = c_radius * 5

    # Create the control points
    cv_matrices = []
    for i in range(count):
        cv = _testSphere(c_radius, color=(0.7, 1, 1), name=f'cv{i}', position=(i * spacing, 0, 0))
        cv_matrices.append(f'{cv}.worldMatrix[0]')

    # Attach the cubes
    for i in range(p_count):
        t = i / (float(p_count) - 1)
        p_node = _testCube(p_radius, color=(0, 0.5, 1), name=f'p{i}')

        # Create the position matrix
        point_matrix_weigths = pointOnCurveWeights(cv_matrices, t, degree=degree)
        point_matrix_node = cmds.createNode('wtAddMatrix', name=f'pointMatrix0{i + 1}')
        for index, (matrix, weight) in enumerate(point_matrix_weigths):
            cmds.connectAttr(matrix, f'{point_matrix_node}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{point_matrix_node}.wtMatrix[{index}].weightIn', weight)

        # Create the tangent matrix
        tangent_matrix_weigths = tangentOnCurveWeights(cv_matrices, t, degree=degree)
        tangent_matrix_node = cmds.createNode('wtAddMatrix', name=f'tangentMatrix0{i + 1}')
        for index, (matrix, weight) in enumerate(tangent_matrix_weigths):
            cmds.connectAttr(matrix, f'{tangent_matrix_node}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{tangent_matrix_node}.wtMatrix[{index}].weightIn', weight)

        # Create an aim matrix node
        aim_matrix_node = cmds.createNode('aimMatrix', name=f'aimMatrix0{i + 1}')
        cmds.connectAttr(f'{point_matrix_node}.matrixSum', f'{aim_matrix_node}.inputMatrix')
        cmds.connectAttr(f'{tangent_matrix_node}.matrixSum', f'{aim_matrix_node}.primaryTargetMatrix')
        cmds.setAttr(f'{aim_matrix_node}.primaryMode', 1)
        cmds.setAttr(f'{aim_matrix_node}.primaryInputAxis', 1, 0, 0)
        cmds.setAttr(f'{aim_matrix_node}.secondaryInputAxis', 0, 1, 0)
        cmds.setAttr(f'{aim_matrix_node}.secondaryMode', 0)

        # Remove scale
        pick_matrix_node = cmds.createNode('pickMatrix', name=f'noScale0{i + 1}')
        cmds.connectAttr(f'{aim_matrix_node}.outputMatrix', f'{pick_matrix_node}.inputMatrix')
        cmds.setAttr(f'{pick_matrix_node}.useScale', False)
        cmds.setAttr(f'{pick_matrix_node}.useShear', False)

        cmds.connectAttr(f'{pick_matrix_node}.outputMatrix', f'{p_node}.offsetParentMatrix')


def _testMatrixOnCircularCurve(count=4, pCount=None, degree=3):
    """
    Creates an example circular curve with the given cv and point counts.
    
    Args:
        count (int): The amount of cvs. 
        pCount (int): The amount of points to attach to the curve.
        degree (int): The degree of the curve.
    """

    pCount = pCount or count * 4
    cRadius = 1.0
    pRadius = 0.5
    spacing = cRadius * 5

    # Create the control points
    cvMatrices = []
    for i in range(count):
        t = i / float(count)
        x = math.cos(t * math.pi * 2)
        y = math.sin(t * math.pi * 2)
        cv = _testSphere(cRadius, color=(0.7, 1, 1), name=f'cv{i}', position=(x * spacing, 0, y * spacing))
        cvMatrices.append(f'{cv}.worldMatrix[0]')

    # Modify the control point list so that they loop
    cvMatrices = cvMatrices + cvMatrices[:3]
    knots = [i for i in range(len(cvMatrices) + degree + 1)]
    knots = [float(knot) for knot in knots]

    # Attach the cubes
    for i in range(pCount):
        t = i / (float(pCount) - 1)
        pNode = _testCube(pRadius, color=(0, 0.5, 1), name=f'p{i}')

        # Create the position matrix
        pointMatrixWeights = pointOnCurveWeights(cvMatrices, t, degree=degree, knots=knots)
        pointMatrixNode = cmds.createNode('wtAddMatrix', name=f'pointMatrix0{i + 1}')
        pointMatrix = f'{pointMatrixNode}.matrixSum'
        for index, (matrix, weight) in enumerate(pointMatrixWeights):
            cmds.connectAttr(matrix, f'{pointMatrixNode}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{pointMatrixNode}.wtMatrix[{index}].weightIn', weight)

        # Create the tangent matrix
        tangentMatrixWeights = tangentOnCurveWeights(cvMatrices, t, degree=degree, knots=knots)
        tangentMatrixNode = cmds.createNode('wtAddMatrix', name=f'tangentMatrix0{i + 1}')
        tangentMatrix = f'{tangentMatrixNode}.matrixSum'
        for index, (matrix, weight) in enumerate(tangentMatrixWeights):
            cmds.connectAttr(matrix, f'{tangentMatrixNode}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{tangentMatrixNode}.wtMatrix[{index}].weightIn', weight)

        # Create an aim matrix node
        aimMatrixNode = cmds.createNode('aimMatrix', name=f'aimMatrix0{i + 1}')
        cmds.connectAttr(pointMatrix, f'{aimMatrixNode}.inputMatrix')
        cmds.connectAttr(tangentMatrix, f'{aimMatrixNode}.primaryTargetMatrix')
        cmds.setAttr(f'{aimMatrixNode}.primaryMode', 1)
        cmds.setAttr(f'{aimMatrixNode}.primaryInputAxis', 1, 0, 0)
        cmds.setAttr(f'{aimMatrixNode}.secondaryInputAxis', 0, 1, 0)
        cmds.setAttr(f'{aimMatrixNode}.secondaryMode', 0)
        aimMatrixOutput = f'{aimMatrixNode}.outputMatrix'

        # Remove scale
        pickMatrixNode = cmds.createNode('pickMatrix', name=f'noScale0{i + 1}')
        cmds.connectAttr(aimMatrixOutput, f'{pickMatrixNode}.inputMatrix')
        cmds.setAttr(f'{pickMatrixNode}.useScale', False)
        cmds.setAttr(f'{pickMatrixNode}.useShear', False)
        outputMatrix = f'{pickMatrixNode}.outputMatrix'

        cmds.connectAttr(outputMatrix, f'{pNode}.offsetParentMatrix')


def _testMatrixOnSurface(cvs=3, uCount=None, vCount=None, degree=3):
    """
    Creates an example surface with the given cv and point counts.
    
    Args:
        cvs (int): The amount of cvs. 
        uCount (int): The amount of points in u to attach to the surface.
        vCount (int): The amount of points in v to attach to the surface.
        degree (int): The degree of the curve.
    """

    uCount = uCount or cvs * 4
    vCount = vCount or cvs * 4
    cRadius = 1.0
    pRadius = 0.25
    spacing = cRadius * 5

    # Create the control points
    cvMatrices = []
    for u in range(cvs):
        uMatrices = []
        for v in range(cvs):
            cv = _testSphere(cRadius, color=(0.7, 1, 1), name=f'cv{u}x{v}', position=(u * spacing, 0, v * spacing))
            uMatrices.append(f'{cv}.worldMatrix[0]')
        cvMatrices.append(uMatrices)

    # Attach the cubes
    for i in range(uCount):
        u = i / (float(uCount) - 1)

        for j in range(vCount):
            v = j / (float(vCount) - 1)
            pNode = _testCube(pRadius, color=(0, 0.5, 1), name=f'p{u}x{v}')

            # Create the position matrix
            pointMatrixWeights = pointOnSurfaceWeights(cvMatrices, u, v, degree=degree)
            pointMatrixNode = cmds.createNode('wtAddMatrix', name=f'pointMatrix0{i * vCount + j + 1}')
            pointMatrix = f'{pointMatrixNode}.matrixSum'
            for index, (matrix, weight) in enumerate(pointMatrixWeights):
                cmds.connectAttr(matrix, f'{pointMatrixNode}.wtMatrix[{index}].matrixIn')
                cmds.setAttr(f'{pointMatrixNode}.wtMatrix[{index}].weightIn', weight)

            # Create the tangent u matrix
            tangentUMatrixWeights = tangentUOnSurfaceWeights(cvMatrices, u, v, degree=degree, dimension=0)
            tangentUMatrixNode = cmds.createNode('wtAddMatrix', name=f'tangentUMatrix0{i * vCount + j + 1}')
            tangentUMatrix = f'{tangentUMatrixNode}.matrixSum'
            for index, (matrix, weight) in enumerate(tangentUMatrixWeights):
                cmds.connectAttr(matrix, f'{tangentUMatrixNode}.wtMatrix[{index}].matrixIn')
                cmds.setAttr(f'{tangentUMatrixNode}.wtMatrix[{index}].weightIn', weight)

            # Create the tangent v matrix
            tangentVMatrixWeights = tangentUOnSurfaceWeights(cvMatrices, u, v, degree=degree, dimension=1)
            tangentVMatrixNode = cmds.createNode('wtAddMatrix', name=f'tangentVMatrix0{i * vCount + j + 1}')
            tangentVMatrix = f'{tangentVMatrixNode}.matrixSum'
            for index, (matrix, weight) in enumerate(tangentVMatrixWeights):
                cmds.connectAttr(matrix, f'{tangentVMatrixNode}.wtMatrix[{index}].matrixIn')
                cmds.setAttr(f'{tangentVMatrixNode}.wtMatrix[{index}].weightIn', weight)

            # Create an aim matrix node
            aimMatrixNode = cmds.createNode('aimMatrix', name=f'aimMatrix0{i * vCount + j + 1}')
            cmds.connectAttr(pointMatrix, f'{aimMatrixNode}.inputMatrix')
            cmds.connectAttr(tangentUMatrix, f'{aimMatrixNode}.primaryTargetMatrix')
            cmds.connectAttr(tangentVMatrix, f'{aimMatrixNode}.secondaryTargetMatrix')
            cmds.setAttr(f'{aimMatrixNode}.primaryMode', 1)
            cmds.setAttr(f'{aimMatrixNode}.primaryInputAxis', 1, 0, 0)
            cmds.setAttr(f'{aimMatrixNode}.secondaryMode', 1)
            cmds.setAttr(f'{aimMatrixNode}.secondaryInputAxis', 0, 1, 0)
            aimMatrixOutput = f'{aimMatrixNode}.outputMatrix'

            # Remove scale
            pickMatrixNode = cmds.createNode('pickMatrix', name=f'noScale0{i * vCount + j + 1}')
            cmds.connectAttr(aimMatrixOutput, f'{pickMatrixNode}.inputMatrix')
            cmds.setAttr(f'{pickMatrixNode}.useScale', False)
            cmds.setAttr(f'{pickMatrixNode}.useShear', False)
            outputMatrix = f'{pickMatrixNode}.outputMatrix'

            cmds.connectAttr(outputMatrix, f'{pNode}.offsetParentMatrix')
            