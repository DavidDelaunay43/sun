import os
import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om

def export_abc(mesh: str, root: str, output_directory: str, start: int, end: int, uv_write: bool, world_space: bool):
    '''
    '''
    
    uv_write = '-uvWrite' if uv_write else ''
    world_space = '-worldSpace' if world_space else ''
    
    output_file_path = f'{os.path.join(output_directory, mesh)}.abc'
    job_arg = f'-frameRange {start} {end} {uv_write} {world_space} -dataFormat ogawa -root {root} -file {output_file_path}'
    cmds.AbcExport(jobArg = job_arg)
    
    om.MGlobal.displayInfo(f'Export Abc file : {output_file_path}')
    
def export_abc_selection(output_directory: str, start: int, end: int, uv_write: bool, world_space: bool):
    '''
    '''
    
    meshes = cmds.ls(selection = True)
    roots = cmds.ls(selection = True, long = True)
    [export_abc(mesh, root, output_directory, start, end, uv_write, world_space) for mesh, root in zip(meshes, roots)]

def import_abc(directory: str, mesh: str):
    '''
    '''
    
    abc_file_path = directory + f'/{mesh}.abc'
    mel.eval(f'AbcImport -mode -import -connect "{mesh}" "{abc_file_path}";')
    
    om.MGlobal.displayInfo(f'Import Abc file : {abc_file_path}')
    
def import_abc_selection(directory: str):
    '''
    '''
    
    meshes = cmds.ls(selection = True)
    [import_abc(directory, mesh) for mesh in meshes]
