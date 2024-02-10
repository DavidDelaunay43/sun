import os
from maya import cmds
import maya.OpenMayaUI as omui
from PySide2.QtWidgets import QWidget, QDialog, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QCheckBox
from shiboken2 import wrapInstance

CACHE_DIRECTORY = r'//gandalf/3d4_23_24/COUPDESOLEIL/11_cache'
#CACHE_DIRECTORY = r'E:\__Esma_pipeline\SERVEUR\Template\11_cache'

def ensure_directory(directory: str):
    
    if os.path.exists(directory):
        return
    
    os.makedirs(directory)

def ensure_directory(directory: str):
    
    if os.path.exists(directory):
        return
    
    sh_dir_name = os.path.basename(directory)
    seq_dir = os.path.dirname(directory)
    
    if os.path.exists(seq_dir):
        os.mkdir(os.path.join(seq_dir, sh_dir_name))
        
    else:
        os.makedirs(directory)
        

def only_mseh_in_set(set_name: str):
    
    set_members = cmds.sets(set_name, query = True, nodesOnly = True) or []

    for member in set_members:
        shapes = cmds.listRelatives(member, shapes = True) or []
        if not any(cmds.objectType(shape) == "mesh" for shape in shapes):
            return False

    return True

def get_char_sets() -> list:
    
    object_sets = cmds.ls(type = 'objectSet')
    char_sets = []
    for object_set in object_sets:
        if only_mseh_in_set(object_set):
            if ':' in  object_set:
                char_sets.append(object_set)
                
    return char_sets

def get_time_slider_range() -> tuple:
    start_frame: float = cmds.playbackOptions(query = True, minTime = True)
    end_frame: float = cmds.playbackOptions(query = True, maxTime = True)

    return start_frame, end_frame

def get_abc_file_name(set_name: str) -> str:
    
    char_name = set_name.split(':')[0]
    
    scene_name: str = os.path.basename(cmds.file(query = True, sceneName = True))
    prefix, seq_num, sh_num, department, _, _ = scene_name.split('_')
    alembic_file_name: str = '_'.join([prefix, seq_num, sh_num, char_name, department]) + '.abc'
    
    return alembic_file_name

def export_abc(start: int, end: int, char_set: str, directory: str):
    
    ensure_directory(directory)
    
    set_members: list = cmds.sets(char_set, query = True, nodesOnly = True)
    roots: str = ''
    for geo in set_members:
        roots += f'-root {geo} '
        
    abc_file_name: str = get_abc_file_name(char_set)
    abc_file_path: str = os.path.join(directory, abc_file_name)
    
    job_arg: str = f'-frameRange {start} {end} -uvWrite -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa {roots} -file {abc_file_path}'
    cmds.AbcExport(jobArg = job_arg)

def export_alembics(start: int, end: int, char_sets: str, directory: str):
    
    for char_set in char_sets:
        export_abc(start, end, char_set, directory)
    
def maya_main_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QWidget) 

class ExportAbcDialog(QDialog):
    
    def __init__(self, parent = maya_main_window()):
        super(ExportAbcDialog, self).__init__(parent)
        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()
        
    def init_ui(self):
        self.setWindowTitle('Export Alembic')
        
    def create_widgets(self):
        
        start, end = get_time_slider_range()
        
        self.start_lineedit = QLineEdit(str(start))
        self.end_lineedit = QLineEdit(str(end))
        
        self.cb_char_sets = []
        for char_set in get_char_sets():
            cb_char_set = QCheckBox(char_set)
            cb_char_set.setChecked(True)
            self.cb_char_sets.append(cb_char_set)
        
        self.run_btn = QPushButton('Export Alembic')
    
    def create_layout(self):
        
        self.main_layout = QVBoxLayout(self)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.main_layout.addWidget(self.grid_widget)
        
        self.grid_layout.addWidget(self.start_lineedit, 0, 0)
        self.grid_layout.addWidget(self.end_lineedit, 0, 1)
        
        for index, cb_char_set in enumerate(self.cb_char_sets, start = 1):
            self.grid_layout.addWidget(cb_char_set, index, 0)
        
        self.main_layout.addWidget(self.run_btn)
        
    def create_connections(self):
        
        self.run_btn.clicked.connect(self.run)
    
    def run(self):
        
        scene_name: str = os.path.basename(cmds.file(query = True, sceneName = True))
        _, seq_num, sh_num, _, _, _ = scene_name.split('_')
        
        char_sets = []
        for cb_char_set in self.cb_char_sets:
            if cb_char_set.isChecked():
                char_sets.append(cb_char_set.text())
        
        start, end = self.start_lineedit.text(), self.end_lineedit.text()
        scene_name: str = os.path.basename(cmds.file(query = True, sceneName = True))
        _, seq_num, sh_num, _, _, _ = scene_name.split('_')
        directory = os.path.join(CACHE_DIRECTORY, seq_num, sh_num)
        export_alembics(start, end, char_sets, directory)
        
ExportAbcDialog()