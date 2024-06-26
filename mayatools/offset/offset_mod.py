from ...utils.imports import *
from .. import constants_maya
from .. import display
from .. import tools

reload(constants_maya)
reload(display)
reload(tools)
from ..constants_maya import *


def _outliner_order(node: str) -> list[int]:

    parent_grp = cmds.listRelatives(node, parent=True)
    kids = cmds.listRelatives(parent_grp, children=True)
    om.MGlobal.displayInfo(f"{kids}")

    num = kids.index(node) + 1

    om.MGlobal.displayInfo(f"{node} num is : {num}")

    num_order = len(kids) - num

    return num_order


def _offset_grp(node: str, offset_name: str) -> str:

    offset_grp = cmds.group(empty=True, name=offset_name)
    cmds.matchTransform(offset_grp, node)

    parent_grp = cmds.listRelatives(node, p=1)

    if parent_grp:

        num_order = _outliner_order(node)
        cmds.parent(offset_grp, parent_grp)
        cmds.reorder(offset_grp, r=num_order)

    cmds.parent(node, offset_grp)

    return offset_grp


def _offset_grps(nodes: Union[str, list], offset_names):

    def cond_color(arg, name):

        if name.lower() == MOVE:

            cmds.setAttr(f"{arg}.useOutlinerColor", 1)
            cmds.setAttr(f"{arg}.outlinerColor", 0.6651, 0.56619, 0.92031)

        if name.lower() == HOOK:

            display.color_node(arg, "gold")

        if name.lower() in ["constraint", "constr", "const"]:

            display.color_node(arg, "red")

    nodes = tools.ensure_list(nodes)
    offset_names = tools.ensure_list(offset_names)

    for node in nodes:

        offset_group = _offset_grp(node, f"{node}_{offset_names[0]}")
        cond_color(offset_group, offset_names[0])

        if len(offset_names) > 1:

            for i in range(1, len(offset_names)):

                offset_group = _offset_grp(offset_group, f"{node}_{offset_names[i]}")
                cond_color(offset_group, offset_names[i])

    cmds.select(clear=True)


def offset_parent_matrix(nodes):
    """Bake transform attributes : translate, rotate, scale, jointOrient
    in offsetParentMatrix attribute.

    Arguments :
    nodes : list of strings -- name of the nodes
    """

    nodes = tools.ensure_list(nodes)

    for node in nodes:

        local_matrix = om.MMatrix(
            cmds.xform(node, query=True, matrix=True, worldSpace=False)
        )
        offset_parent_matrix = om.MMatrix(cmds.getAttr(f"{node}.{OP_MTX}"))
        baked_matrix = local_matrix * offset_parent_matrix

        cmds.setAttr(f"{node}.{OP_MTX}", baked_matrix, type="matrix")

        for attribute in [TRANSLATE, ROTATE, SCALE, "jointOrient"]:

            value = 1 if attribute == SCALE else 0

            for axis in "XYZ":

                if cmds.attributeQuery(f"{attribute}{axis}", node=node, exists=True):

                    attribute_name = f"{node}.{attribute}{axis}"
                    cmds.setAttr(attribute_name, value)


def op_matrix_to_transforms(nodes):
    """ """

    nodes = tools.ensure_list(nodes)

    for node in nodes:

        local_matrix = om.MMatrix(
            cmds.xform(node, query=True, matrix=True, worldSpace=False)
        )
        offset_parent_matrix = om.MMatrix(cmds.getAttr(f"{node}.{OP_MTX}"))
        matrix = local_matrix * offset_parent_matrix

        deco_matrix = cmds.createNode("decomposeMatrix", name=f"{node}_{DECO_MTX}_TMP")
        cmds.setAttr(f"{deco_matrix}.{INPUT_MTX}", matrix, type="matrix")
        translates = cmds.getAttr(f"{deco_matrix}.{OUTPUT_T}")[0]
        rotates = cmds.getAttr(f"{deco_matrix}.{OUTPUT_R}")[0]
        scales = cmds.getAttr(f"{deco_matrix}.{OUTPUT_S}")[0]
        cmds.delete(deco_matrix)

        cmds.setAttr(f"{node}.{TRANSLATE}", *translates, type="double3")
        cmds.setAttr(f"{node}.{ROTATE}", *rotates, type="double3")
        cmds.setAttr(f"{node}.{SCALE}", *scales, type="double3")
        cmds.setAttr(
            f"{node}.{OP_MTX}",
            (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
            type="matrix",
        )

        cmds.select(node)


offset = partial(_offset_grps, offset_names=OFFSET)
move = partial(_offset_grps, offset_names=MOVE)
hook = partial(_offset_grps, offset_names=HOOK)
const = partial(_offset_grps, offset_names="const")
move_hook = partial(_offset_grps, offset_names=[MOVE, HOOK])
move_offset = partial(_offset_grps, offset_names=[MOVE, OFFSET])
hook_offset = partial(_offset_grps, offset_names=[HOOK, OFFSET])
move_hook_offset = partial(_offset_grps, offset_names=[MOVE, HOOK, OFFSET])


def move_op_matrix(nodes):
    """ """
    nodes = tools.ensure_list(nodes)
    for node in nodes:
        move(node)
        offset_parent_matrix(node)
        offset_parent_matrix(f"{node}_{MOVE}")


def hook_op_matrix(nodes):
    """ """

    nodes = tools.ensure_list(nodes)
    for node in nodes:
        hook(node)
        offset_parent_matrix(node)
        offset_parent_matrix(f"{node}_{HOOK}")


def move_hook_op_matrix(nodes):
    """ """

    nodes = tools.ensure_list(nodes)
    for node in nodes:
        move_hook(node)
        offset_parent_matrix(node)
        offset_parent_matrix(f"{node}_{HOOK}")


def _find_last_offset(node: str):
    """ """

    all_parents = cmds.ls(node, long=True)
    if all_parents:
        parents_list = all_parents[0].split("|")
        for parent in parents_list:
            if node in parent:
                return parent


def _find_offsetted_node(offset_group: str):
    """ """

    node, _ = offset_group.rsplit("_", 1)
    if cmds.objExists(node):
        return node


def _is_offset(node: str):
    offset_names = [MOVE, HOOK, OFFSET]
    for offset_name in offset_names:
        return offset_name in node


def _get_offset_name(node: str):
    offset_names = [MOVE, HOOK, OFFSET]
    for offset_name in offset_names:
        return offset_name if offset_name in node else None


def offset_to_op_matrix(nodes, delete=True):
    """ """

    nodes = tools.ensure_list(nodes)

    for node in nodes:

        if _is_offset(node):
            node = _find_offsetted_node(node)

        last_offset = _find_last_offset(node)

        child_last_offset = cmds.listRelatives(last_offset, children=True)[0]
        parent_last_offset = cmds.listRelatives(last_offset, parent=True)

        if parent_last_offset:
            cmds.parent(child_last_offset, parent_last_offset[0])
        else:
            cmds.parent(child_last_offset, world=True)

        offset_parent_matrix(child_last_offset)
        cmds.delete(last_offset) if delete else None

        om.MGlobal.displayInfo(
            f"{last_offset} transforms transfered to {child_last_offset}.{OP_MTX}"
        )
        values = cmds.getAttr(f"{child_last_offset}.{OP_MTX}")
        om.MGlobal.displayInfo(f"Transform values : {values}")


def op_matrix_to_offset(nodes):
    """ """

    nodes = tools.ensure_list(nodes)

    for node in nodes:

        if _is_offset(node):
            node = _find_offsetted_node(node)

        last_offset = _find_last_offset(node)
        last_offset_name = _get_offset_name(last_offset)
        op_matrix_to_transforms(last_offset)
        offset(last_offset)
        new_offset = f"{last_offset}_{OFFSET}"
        rename_new_offset = new_offset.replace(f"_{last_offset_name}", "")
        new_offset = cmds.rename(new_offset, rename_new_offset)

        om.MGlobal.displayInfo(
            f"{last_offset}.{OP_MTX} values transfered to {new_offset} transforms."
        )
