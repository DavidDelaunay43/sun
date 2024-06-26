def reload_modules():
    from importlib import reload
    
    from ..utils import constants, ui_tools
    modules = constants, ui_tools
    for module in modules:
        reload(module)      
reload_modules()

from ...utils.constants import ICON_PATH, USERNAME, STYLE_PATH
from ..utils.ui_tools import string_to_list

import os
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout

class BaseDialog(QDialog):
    """
    """
    
    def set_style(self, filename):
        """
        """
        style_path = os.path.join(STYLE_PATH, filename)
        with open(style_path, 'r') as file:
            style = file.read()
        self.setStyleSheet(style)

    def set_dialog_basics(self, title = "Dialog", size = [200, 200], sizeable = False):
        """
        """
        
        self.setWindowTitle(title)
        self.setMinimumSize(*size) if sizeable else self.setFixedSize(*size)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
    def set_window_icon(self, icon_filename):
        """
        """
        
        icon_path = os.path.join(ICON_PATH, icon_filename)
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        
    def create_widgets(self):
        pass
    
    def create_layout(self, parent_layout = None, layout_type = "vbox", widgets = [], stretch = False):
        """
        """
        
        layout_types = {
            "hbox": QHBoxLayout,
            "vbox": QVBoxLayout
        }
        
        layout = layout_types.get(layout_type)(self)
        if stretch:
            layout.addStretch()
        
        for widget in widgets:
            layout.addWidget(widget)
            
        if parent_layout:
            parent_layout.addLayout(layout)
            
        return layout
    
    def create_push_button(self, button_name = "", height = None, object_name = None):
        """
        """
        
        push_button = QPushButton(button_name)
        if object_name:
            push_button.setObjectName(object_name)
        
        if height:
            push_button.setFixedHeight(int(height))
        
        return push_button
    
    def create_label(self, label_name = "", height = None, object_name = None):
        """
        """
        
        label = QLabel(label_name)
        if object_name:
            label.setObjectName(object_name)
        
        if height:
            label.setFixedHeight(int(height))
        
        return label
    
    def create_ok_cancel_layout(self, parent_layout = None, height = 30):
        """
        """
        
        self.ok_button = self.create_push_button("OK", height, "ok")
        self.cancel_button = self.create_push_button("Cancel", height, "cancel")
        self.cancel_button.clicked.connect(self.close)
        
        self.ok_cancel_layout = self.create_layout(parent_layout, "hbox", [self.ok_button, self.cancel_button])
        
        return self.ok_cancel_layout
    
    def create_apply_close_layout(self, parent_layout = None, height = 30):
        """
        """
        
        self.applyclose_button = self.create_push_button("Apply and Close", height, "ok")
        self.apply_button = self.create_push_button("Apply", height, "ok")
        self.close_button = self.create_push_button("Close", height, "cancel")
        self.close_button.clicked.connect(self.close)
        
        self.ok_apply_close_layout = self.create_layout(parent_layout, "hbox", [self.applyclose_button, self.apply_button, self.close_button])
        
        return self.ok_apply_close_layout
        
    
    def create_infos_layout(self, parent_layout = None, height = 16):
        """
        """
        
        self.user_label = self.create_label(f"User : {USERNAME}", height, "infos")
        self.user_label.setAlignment(Qt.AlignLeft)
        self.user_label.setAlignment(Qt.AlignBottom)
        
        text = "Coup de Soleil - Scripts - Esma MTP 2023-2024"
        self.info_label = self.create_label(text, height, "infos")
        self.info_label.setAlignment(Qt.AlignRight)
        self.info_label.setAlignment(Qt.AlignBottom)
        
        self.infos_layout = self.create_layout(parent_layout, "hbox", widgets = [self.user_label, self.info_label])
        
    def ui_string_to_list(self, string: str):
        return string_to_list(string)