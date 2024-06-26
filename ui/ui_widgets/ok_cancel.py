from . import WidgetTemplate
from PySide2.QtWidgets import QPushButton, QHBoxLayout

class OkCancel(WidgetTemplate):
    
    def __init__(self, parent = None):
        super(OkCancel, self).__init__(parent)
        
        self._create_widgets()
        self._create_layout()
        
    def _create_widgets(self):
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        # Set object name -> Style
        self.ok_button.setObjectName("ok")
        self.cancel_button.setObjectName("cancel")
    
    def _create_layout(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.ok_button)
        self.main_layout.addWidget(self.cancel_button)