from . import WidgetTemplate
from PySide2.QtWidgets import QCheckBox, QGridLayout

class XYZTransform(WidgetTemplate):
    
    def __init__(self, transform_type: str, parent = None):
        super(XYZTransform, self).__init__(parent)
        
        self._create_widgets(transform_type)
        self._create_layout()
        self._toggle_xyz_checkbox()
        self._create_connections()
        
    def _create_widgets(self, transform_type: str):
        self.check_box_transform = QCheckBox(transform_type)
        self.check_box_x = QCheckBox("X")
        self.check_box_y = QCheckBox("Y")
        self.check_box_z = QCheckBox("Z")

    def _create_layout(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.check_box_transform, 0, 0)
        self.main_layout.addWidget(self.check_box_x, 1, 0)
        self.main_layout.addWidget(self.check_box_y, 1, 1)
        self.main_layout.addWidget(self.check_box_z, 1, 2)
        
    def _create_connections(self):
        self.check_box_transform.stateChanged.connect(self._toggle_xyz_checkbox)
        
        self.check_box_x.stateChanged.connect(self._toggle_transform_checkbox)
        self.check_box_y.stateChanged.connect(self._toggle_transform_checkbox)
        self.check_box_z.stateChanged.connect(self._toggle_transform_checkbox)
        
    def _toggle_xyz_checkbox(self):
        state = self.check_box_transform.isChecked()
        
        if state:
            self.check_box_x.setChecked(state)
            self.check_box_y.setChecked(state)
            self.check_box_z.setChecked(state)
                    
    def _toggle_transform_checkbox(self):
        xyz_checkbox = (self.check_box_x, self.check_box_y, self.check_box_z)
        all_xyz_checked = all(cb.isChecked() for cb in xyz_checkbox)
        self.check_box_transform.setChecked(all_xyz_checked)
        
    def get_value(self):
        checkboxes = (
            self.check_box_transform ,
            self.check_box_x,
            self.check_box_y,
            self.check_box_z
        )
        
        values = []
        for checkbox in checkboxes:
            values.append(checkbox.isChecked())
            
        return values