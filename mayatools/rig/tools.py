from ...utils.imports import *


def blendshape_setup(weigth_name: str):

    loc_01, loc_02, bshape_node = cmds.ls(selection=True)
    dist_b = cmds.createNode("distanceBetween", name=f"distB_locs_{weigth_name}")
    cmds.connectAttr(f"{loc_01}.worldPosition[0]", f"{dist_b}.point1")
    cmds.connectAttr(f"{loc_02}.worldPosition[0]", f"{dist_b}.point2")
    distance = cmds.getAttr(f"{dist_b}.distance")

    rm_node = cmds.createNode("remapValue", name=f"rm_{weigth_name}")
    cmds.connectAttr(f"{dist_b}.distance", f"{rm_node}.inputValue")
    cmds.setAttr(f"{rm_node}.inputMin", distance)
    cmds.setAttr(f"{rm_node}.inputMax", 0.1)
    cmds.connectAttr(f"{rm_node}.outValue", f"{bshape_node}.{weigth_name}")


def rivet_geo():
    """ """

    rivet, geo = cmds.ls(selection=True)
    cmds.select(clear=True)
    bind = cmds.joint(name=rivet.replace("rivet", "ctrl"))
    cmds.matchTransform(bind, rivet)
    cmds.parent(bind, rivet)
    cmds.makeIdentity(bind, apply=True, t=1, r=1)
    cmds.skinCluster(bind, geo, mi=1)


def create_blendshapes(base_string: str, bshape_string: str):
    """ """

    for geo in cmds.ls(sl=1):

        shape = cmds.listRelatives(geo, shapes=True)[0]

        deform_geo = geo.replace(base_string, bshape_string)
        bshape_node = cmds.blendShape(deform_geo, geo, name=f"BShape_{geo}")[0]
        cmds.setAttr(bshape_node + "." + deform_geo, 1)
        cmds.setAttr(f"{bshape_node}.{deform_geo}", 1)

        skin_cluster = cmds.listConnections(shape, type="skinCluster", connections=True)
        if skin_cluster:
            skin_cluster = skin_cluster[-1]
            cmds.reorderDeformers(skin_cluster, bshape_node)
