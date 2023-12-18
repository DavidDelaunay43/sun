from . import WidgetTemplate
from PySide2.QtWidgets import QLabel, QLineEdit, QGridLayout

class XYZFloat(WidgetTemplate):
    
    def __init__(self, widget_name: str, xyz, parent = None):
        super(XYZFloat, self).__init__(parent)
        
        self._create_widgets(widget_name, *xyz)
        self._create_layout()
        
    def _create_widgets(self, name: str, x, y, z):
        self._label = QLabel(name)
        self._field_x = QLineEdit()
        self._field_y = QLineEdit()
        self._field_z = QLineEdit()
        
        # Defaults
        x, y, z = str(float(x)), str(float(y)), str(float(z))
        
        self._field_x.setText(x)
        self._field_y.setText(y)
        self._field_z.setText(z)
    
    def _create_layout(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self._label, 0, 0)
        self.main_layout.addWidget(self._field_x, 0, 1)
        self.main_layout.addWidget(self._field_y, 0, 2)
        self.main_layout.addWidget(self._field_z, 0, 3)
    
    def get_value(self):
        fields = (
           self._field_x,
            self._field_y,
            self._field_z
        )
        
        values = []
        for field in fields:
            values.append(float(field.text()))
        
        return tuple(values)