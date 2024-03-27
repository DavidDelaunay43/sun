from maya import cmds


def delete_color_sets():

    color_set_nodes = cmds.ls(type="createColorSet")
    if not color_set_nodes:
        return

    for color_set in color_set_nodes:

        if not cmds.objExists(color_set):
            continue

        print(f"Color Set : {color_set}")

        try:
            # identifier si le color set est le premier ou le second
            source_co = cmds.listConnections(
                color_set, source=True, destination=False, plugs=True
            )[0]
            source_co_node = source_co.split(".")[0]
            if cmds.nodeType(source_co_node) == "createColorSet":
                last_color_set = color_set
                first_color_set = source_co_node
                geo_input_co = cmds.listConnections(
                    last_color_set, source=False, destination=True, plugs=True
                )[0]
                skincluster_output_co = cmds.listConnections(
                    first_color_set, source=True, destination=False, plugs=True
                )[0]

            else:  # cmds.nodeType(source_co_node) == 'skinCluster'
                first_color_set = color_set
                skincluster_output_co = cmds.listConnections(
                    first_color_set, source=True, destination=False, plugs=True
                )[0]
                last_color_set = cmds.listConnections(
                    first_color_set, source=False, destination=True, plugs=True
                )[0].split(".")[0]
                geo_input_co = cmds.listConnections(
                    last_color_set, source=False, destination=True, plugs=True
                )[0]

            print(f"connectAttr : {skincluster_output_co} -> {geo_input_co}")
            print(f"delete : {first_color_set}, {last_color_set}")
            print("--------------------------------------------------------")
            cmds.connectAttr(skincluster_output_co, geo_input_co, force=True)
            cmds.delete(first_color_set, last_color_set)
        except:
            pass
