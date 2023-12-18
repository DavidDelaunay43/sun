from .ui_widgets import BaseDialog, XYZTransform, OkCancel
from .utils import maya_main_window, WindowManager
from ..mayatools import matrix

from PySide2.QtWidgets import QCheckBox, QVBoxLayout

class MatrixUI(BaseDialog):
    """
    """
    
    @classmethod       
    def show_dialog(cls):
        WindowManager.show_dialog(cls)
    
    def __init__(self, parent = maya_main_window()):
        super(MatrixUI, self).__init__(parent)
        
        # Create UI
        self.set_dialog_basics("Matrix Constraints", [300, 280])
        self.set_window_icon("sun.svg")
        self.set_style("style.css")
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        
        self.checkbox_offset = QCheckBox("Maintain Offset")
        self.translate_widget = XYZTransform("Translate", parent = self)
        self.rotate_widget = XYZTransform("Rotate", parent = self)
        self.scale_widget = XYZTransform("Scale", parent = self)
        self.ok_cancel_widget = OkCancel(parent = self)
        
        # Defaults
        self.checkbox_offset.setChecked(True)
        self.translate_widget.check_box_transform.setChecked(True)
    
    def create_layouts(self):
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.checkbox_offset)
        self.main_layout.addWidget(self.translate_widget)
        self.main_layout.addWidget(self.rotate_widget)
        self.main_layout.addWidget(self.scale_widget)
        self.main_layout.addWidget(self.ok_cancel_widget)
        
    def create_connections(self):
        self.ok_cancel_widget.ok_button.clicked.connect(self.run)
        self.ok_cancel_widget.cancel_button.clicked.connect(self.close)
        
    def get_checkbox_value(self):
        
        checkboxes = (
            self.translate_widget.check_box_transform,
            self.rotate_widget.check_box_transform,
            self.scale_widget.check_box_transform,
            self.translate_widget.check_box_x,
            self.translate_widget.check_box_y,
            self.translate_widget.check_box_z,
            self.rotate_widget.check_box_x,
            self.rotate_widget.check_box_y,
            self.rotate_widget.check_box_z,
            self.scale_widget.check_box_x,
            self.scale_widget.check_box_y,
            self.scale_widget.check_box_z,
            self.checkbox_offset
        )
        
        values = []
        for checkbox in checkboxes:
            values.append(checkbox.isChecked())
            
        return values
            
    def run(self):

        t, r, s, tx, ty, tz, rx, ry, rz, sx, sy, sz, mo = self.get_checkbox_value()
        matrix.matrix_on_selection(t, r, s, tx, ty, tz, rx, ry, rz, sx, sy, sz, mo)