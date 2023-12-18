from ..utils.imports import *
from .attribute import cb_attributes, rman_attribs
from .display import color_node



def set_specular(material: str, fm: bool, sm: bool):

    ats = "specularFresnelMode", "roughSpecularFresnelMode", "clearcoatFresnelMode", "iridescenceMode"
    for at in ats:
        cmds.setAttr( f"{material}.{at}", fm )
    ats = "specularModelType", "roughSpecularModelType", "clearcoatModelType"
    for at in ats:
        cmds.setAttr( f"{material}.{at}", sm )


def rman_light(
    typ: str = "PxrRectLight", 
    name: str = "RmanLight", 
    rman_version = 25.2
) -> Tuple[str]:
    """Create a RenderMan light of the specified type.

    Args:
        typ (str, optional): Type of RenderMan light to create. Defaults to "PxrRectLight".
        name (str, optional): Name of the light. Defaults to "RmanLight".
        rman_version (float, optional): Version of RenderMan being used. Defaults to 24.4.

    Returns:
        Tuple[str]: Tuple containing the name of the created light.
    """

    cmds.select(clear = True)
    mel.eval(f"""load_rfm("{rman_version}", "rfm2.api.nodes.create_and_select('{typ}')");""")
    light = cmds.ls(selection = True)[0]
    light = cmds.rename(light, name)
    light_shape = cmds.listRelatives(light, shapes = True)[0]

    return light, light_shape


def rman_cube_light(link_ats: bool = True) -> str:
    """Create a cube light composed of six PxrRectLight nodes.

    Args:
        link_ats (bool, optional): Flag indicating whether to link the light attributes on the master light.
            Defaults to True.

    Returns:
        str: Name of the master light node.
    """

    translates = (0, 0, 0.5), (-0.5, 0, 0), (0.5, 0, 0), (0, 0.5, 0), (0, -0.5, 0)
    rotates = (0, 180, 0), (0, 90, 0), (0, -90, 0), (90, 0, 0), (-90, 0, 0)

    ats = (
        "exposure", "intensity", "lightColor", "colorMapSaturation", "enableTemperature",
        "temperature", "primaryVisibility", "emissionFocus", "emissionFocusNormalize",
        "emissionFocusTint", "specular", "diffuse", "intensityNearDist", "coneAngle", 
        "coneSoftness", "enableShadows", "shadowDistance", "shadowFalloff", "shadowFalloffGamma", 
        "areaNormalize", "traceLightPaths", "thinShadow", "visibleInRefractionPath", "cheapCaustics",
        "fixedSampleCount", "importanceMultiplier", "msApprox", "msApproxBleed", "msApproxContribution",
        "visibility", "lodVisibility"
        )
    
    base_name = "Cube_Light"
    suffix = "Master"
    name = f"{base_name}_01"

    for i in range(1, 100):

        if not cmds.objExists(f"{base_name}_{i:02}_{suffix}"):
            name = f"{base_name}_{i:02}"
            break

    master_light, master_shape = rman_light(name = f"{name}_{suffix}")
    cmds.move(0, 0, -0.5, relative = True, objectSpace = True, worldSpaceDistance = True)
    cmds.move(0, 0 ,0, f"{master_light}.scalePivot", f"{master_light}.rotatePivot", absolute = True)
    cb_attributes(master_light, lock = True)

    ctrl = cmds.circle(normal = [0, 1, 0], name = f"ctrl_{master_light}", constructionHistory = False)[0]
    color_node(ctrl, "gold")
    rman_attribs(ctrl, False)
    cmds.parent(master_light, ctrl)
    
    for i, (t, r) in enumerate(zip(translates, rotates), start = 1):

        light, light_shape = rman_light(name = f"{name}_{i:02}")
        cmds.move(*t, relative = True, objectSpace = True, worldSpaceDistance = True)
        cmds.rotate(*r, relative = True, objectSpace = True, forceOrderXYZ = True)

        cmds.parent(light, master_light)
        cb_attributes(light, lock = True)
        
        if link_ats:
            for at in ats:
                cmds.connectAttr(f"{master_shape}.{at}", f"{light_shape}.{at}")

    cmds.select(cl = 1)
    om.MGlobal.displayInfo(f"Renderman cube light : {master_light} done.")

    return master_light


def find_rman_light() -> list:
    """
    """

    shapes = cmds.ls(dagObjects = True, type = "shape")
    rman_lights = []
    light_types = "PxrRectLight", "PxrDiskLight", "PxrDistantLight", "PxrSphereLight", "PxrCylinderLight", "PxrDomeLight"

    for shape in shapes:

        node_type = cmds.nodeType(shape)
        if node_type in light_types:
            light = cmds.listRelatives(shape, parent = True)[0]
            rman_lights.append(light)

    om.MGlobal.displayInfo(f"Renderman lights : {rman_lights}")
    return rman_lights

def find_lpe(lights: Union[str, list[str]]) -> list:
    """
    """

    lights = ensure_list(lights)

    light_groups = set()
    for light in lights:
        light_group = cmds.getAttr(f"{light}.lightGroup")
        if light_group and light_group not in light_groups:
            light_groups.add(light_group)

    om.MGlobal.displayInfo(f"Light groups : {light_groups}")
    return light_groups


def find_all_lpe() -> list:
    """
    """

    lights = find_rman_light()
    lpes = find_lpe(lights)

    return lpes


def pxr_surface(geo: str, name: str = "", pfx: str = "PxrSurf_") -> str:
    """
    """

    if cmds.nodeType(geo) == "mesh":
        shape = geo
    else:
        shape = cmds.listRelatives(geo, shapes = True)[0]

    shader_name = f"{pfx}{name}"
    shading_grp_name = f"{shader_name}_SG"
    pxr_surface = cmds.shadingNode("PxrSurface", asShader = True, name = shader_name)
    shading_grp = cmds.shadingNode("shadingEngine", asShader = True, name = shading_grp_name)

    cmds.disconnectAttr(f"{shape}.instObjGroups", "initialShadingGroup.dagSetMembers", nextAvailable = True)
    cmds.connectAttr(f"{shape}.instObjGroups", f"{shading_grp}.dagSetMembers", nextAvailable = True)
    cmds.connectAttr(f"{pxr_surface}.outColor", f"{shading_grp}.rman__surface")    
    cmds.connectAttr("lambert1.outColor", f"{shading_grp}.surfaceShader")

    om.MGlobal.displayInfo(f"PxrSurface created on {shape}")
    return pxr_surface

           
def pxr_material(geo: str, name: str = "", *attributes):
    """
    """
    pxr_surface = pxr_surface(geo, name = name)
    rman_attributes = cmds.listAttr(pxr_surface, connectable = True)

    for attribute in attributes:
        
        if attribute in rman_attributes:
            print("ok.")


def get_connected_attributes(node: str):
    """
    """

    connected_attributes = []
    attributes = cmds.listAttr(node, connectable = True)

    for attribute in attributes:
        if cmds.listConnections(f"{node}.{attribute}", destination = False, source = True):
            connected_attributes.append(attribute)

    return connected_attributes


def get_input_node(node_at: str, return_at: bool = False):
    """
    """

    info = cmds.connectionInfo(node_at, sourceFromDestination = True)
    node = info.split(".")[0]

    om.MGlobal.displayInfo(f"Connection info : {info}")
    om.MGlobal.displayInfo(f"Input node : {node}")

    return info if return_at else node


def get_remap_attributes(node: str):
    """
    """

    connected_attributes = get_connected_attributes(node)
    
    remap_attributes = []
    input_nodes = []

    for attribute in connected_attributes:
        node_at = f"{node}.{attribute}"
        input_node = get_input_node(node_at, return_at = True)

        if cmds.nodeType(input_node) != "PxrTexture":
            remap_attributes.append(attribute)
            input_nodes.append(input_node)

    return remap_attributes, input_nodes


def bake_patterns():
    """
    """
    
    mel_commands = """if (`currentRenderer` != "renderman") 
    {
        setCurrentRenderer("renderman");
    }
    rmanBakeStartCmd(0);
    """

    mel.eval(mel_commands)


def bake_node(name: str = "",
    atlas_style: Literal["none", "mari", "mudbox", "zbrush"] = "none",
    file_type: Literal["texture", "openexr", "tiff"] = "openexr", 
    data_type: Literal["half", "float"] = "half", 
    file_name: str = ""
) -> str:
    """
    file type : display : texture, openexr, tiff
    data type : display type : half, float
    """

    styles = {"none":0, "mari":1, "mudbox":2, "zbrush":3}
    style_int = styles.get(atlas_style)

    bake_node = cmds.shadingNode("PxrBakeTexture", asTexture = True, name = name)
    cmds.setAttr(f"{bake_node}.atlasStyle", style_int)
    cmds.setAttr(f"{bake_node}.display", file_type, type = "string")
    cmds.setAttr(f"{bake_node}.displayType", data_type, type = "string")
    cmds.setAttr(f"{bake_node}.filename", file_name, type = "string")

    cmds.setAttr(f"{bake_node}.resolutionX", 4096)
    cmds.setAttr(f"{bake_node}.resolutionY", 4096)

    return bake_node


def bake_auto(shader_node: str, inherits_tex_params: bool = True, override: bool = False):
    """
    """
    remap_attributes, input_nodes = get_remap_attributes(shader_node)

    for attribute, input_node_at in zip(remap_attributes, input_nodes):

        node_at  = f"{shader_node}.{attribute}"

        root_dir = cmds.workspace(query = True, rootDirectory = True)
        file_name = f"{root_dir}sourceimages/{attribute}_bake.exr"

        # create and connect PxrBakeTexture node
        bake_node = bake_node(name = f"PxrBake_{attribute}", atlas_style = "none", file_name = file_name)

        cmds.disconnectAttr(input_node_at, node_at)
        cmds.connectAttr(input_node_at, f"{bake_node}.inputRGB")
        cmds.connectAttr(f"{bake_node}.resultRGB", node_at, force = True)
        
        # create, set and connect baked texture
        tex_node = cmds.shadingNode("PxrTexture", asTexture = True, name = f"{attribute}_bake")
        cmds.setAttr(f"{tex_node}.atlasStyle", 0)
        cmds.setAttr(f"{tex_node}.filename", file_name, type = "string")

    #
    bake_patterns()

    #
