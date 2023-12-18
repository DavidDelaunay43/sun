#--------------------------------------------------
from ..utils.reloading import ReloadModule
class RM(ReloadModule):
    @classmethod
    def reload(cls):
        from . import ui_widgets
        from ..maya_tools import matrix
        cls.reload_mod(ui_widgets, matrix)
RM.reload()
#--------------------------------------------------

from .ui_widgets import BaseDialog, XYZTransform, ButtonLineEdit, OkCancel, XYZFloat
from .utils import maya_main_window, WindowManager
from ..maya_tools.matrix import aim_matrix_on_selection

from PySide2.QtWidgets import QCheckBox, QVBoxLayout

class AimMatrixUI(BaseDialog):
    """
    """
    
    @classmethod
    def show_dialog(cls):
        WindowManager.show_dialog(cls)
    
    def __init__(self, parent = maya_main_window()):
        super(AimMatrixUI, self).__init__(parent)
        
        # Create UI
        self.set_dialog_basics("Aim Matrix Constraints", [350, 300])
        self.set_window_icon("sun.svg")
        self.set_style("style.css")
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        
        self.checkbox_offset = QCheckBox("Maintain Offset")
        self.rotate_widget = XYZTransform("Rotate", parent = self)
        self.aim_vector_widget = XYZFloat(" Aim vector ", (0, 0, 1), parent = self)
        self.up_vector_widget = XYZFloat("  Up vector  ", (0, 1, 0), parent = self)
        self.wup_widget = ButtonLineEdit("World up object", parent = self)
        self.ok_cancel_widget = OkCancel(parent = self)
        
        # Defaults
        self.checkbox_offset.setChecked(True)
        self.rotate_widget.check_box_transform.setChecked(True)
        
    def create_layouts(self):
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.checkbox_offset)
        self.main_layout.addWidget(self.rotate_widget)
        self.main_layout.addWidget(self.aim_vector_widget)
        self.main_layout.addWidget(self.up_vector_widget)
        self.main_layout.addWidget(self.wup_widget)
        self.main_layout.addWidget(self.ok_cancel_widget)
        
    def create_connections(self):
        
        self.ok_cancel_widget.ok_button.clicked.connect(self.run)
        self.ok_cancel_widget.cancel_button.clicked.connect(self.close)
        
    def run(self):
        
        mo = self.checkbox_offset.isChecked()
        r, rx, ry, rz = self.rotate_widget.get_value()
        aim_vector = self.aim_vector_widget.get_value()
        up_vector = self.up_vector_widget.get_value()
        print(f"aim_matrix_on_selection({r}, {rx}, {ry}, {rz}, {aim_vector}, {up_vector})")
        aim_matrix_on_selection(r, rx, ry, rz, aim_vector, up_vector, mo)