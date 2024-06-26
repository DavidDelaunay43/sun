from . import WidgetTemplate
from PySide2.QtWidgets import QPushButton, QHBoxLayout

class ApplyClose(WidgetTemplate):
    
    def __init__(self, parent = None):
        super(ApplyClose, self).__init__(parent)
        
        self._create_widgets()
        self._create_layout()
        self._create_connections()
        
    def _create_widgets(self):
        self.apply_close_button = QPushButton("Apply")
        self.apply_button = QPushButton("Apply")
        self.close_button = QPushButton("Close")
        
        # Set object name -> Style
        self.apply_close_button.setObjectName("ok")
        self.apply_button.setObjectName("ok")
        self.close_button.setObjectName("cancel")
    
    def _create_layout(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.apply_close_button)
        self.main_layout.addWidget(self.apply_button)
        self.main_layout.addWidget(self.close_button)

    def _create_connections(self):
        self.close_button.clicked.connect(self.close)
