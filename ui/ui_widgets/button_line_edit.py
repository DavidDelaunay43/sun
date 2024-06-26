from . import WidgetTemplate
from ..utils import get_selection, string_to_list
from PySide2.QtWidgets import QHBoxLayout, QPushButton, QLineEdit

class ButtonLineEdit(WidgetTemplate):
    
    def __init__(self, button_name, parent = None):
        super(ButtonLineEdit, self).__init__(parent)
        
        self._create_widgets(button_name)
        self._create_layout()
        self._create_connections()
        
    def _create_widgets(self, button_name):
        self.button = QPushButton(button_name)
        self.line_edit = QLineEdit()
    
    def _create_layout(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.line_edit)
        
    def _create_connections(self):
        self.button.clicked.connect(self._fill_line_edit)
        
    def _fill_line_edit(self):
        selection = get_selection()
        self.line_edit.setText(f"{selection}")
        
    def get_text(self):
        return string_to_list(self.line_edit.text())