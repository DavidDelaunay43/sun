from . import WidgetTemplate
from ...utils.constants import USERNAME
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QHBoxLayout

class Infos(WidgetTemplate):
    
    def __init__(self, parent = None):
        super(Infos, self).__init__(parent)
        
        self._create_widgets()
        self._create_layout()
        
    def _create_widgets(self):
        self.username = QLabel(f"User : {USERNAME}")
        self.infos = QLabel("CDS - Esma MTP 23-24")
        
        # Alignement
        self.username.setAlignment(Qt.AlignLeft)
        self.username.setAlignment(Qt.AlignRight)
        
    def _create_layout(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.username)
        self.main_layout.addWidget(self.infos)