from maya import cmds

def replace_skin_mesh() -> None:
    
    old_mesh, new_mesh = cmds.ls(selection=True)
    
    old_shape: str = cmds.listRelatives(old_mesh, shapes=True)[0]
    new_shape: str = cmds.listRelatives(new_mesh, shapes=True)[0]
    
    old_skin_cluster: str = cmds.listConnections(old_shape, type='skinCluster')[0]
    print(old_skin_cluster)
    influnces: list = cmds.skinCluster(old_skin_cluster, query=True, influence=True)
    print(influnces)
    
    cmds.skinCluster(influnces, new_mesh)
    #new_skin_cluster: str = cmds.listConnections(new_shape, type='skinCluster')[0]
    #cmds.copySkinWeights(destinationSkin=new_skin_cluster, sourceSkin=old_skin_cluster, influenceAssociation='oneToOne')
    
replace_skin_mesh()