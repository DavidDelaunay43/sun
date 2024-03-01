from maya import cmds

file_path: str = r'C:\Users\d.delaunay\Documents\petru_gesticule.ma'

for i in range(0, start = 1):
    cmds.file(file_path, i = True, type = 'mayaAscii', ns = f'petru_{i:03}')
