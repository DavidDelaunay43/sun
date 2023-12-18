#--------------------------------------------------
from ..utils.reloading import ReloadModule
class RM(ReloadModule):
    @classmethod
    def reload(cls):
        from . import base_dialog
        from ..maya_tools import tools, rig
        cls.reload_mod(base_dialog, tools, rig)
#RM.reload()
#--------------------------------------------------

from .ui_widgets.base_dialog import BaseDialog
from .utils.constants import maya_main_window
from ..maya_tools.tools import return_set_members
from ..maya_tools.rig import cartoon_eye

from PySide2.QtWidgets import QCheckBox, QGridLayout
from functools import partial

class CartoonEyeUI(BaseDialog):
    """
    """
    
    def __init__(self, parent = maya_main_window()):
        super(CartoonEyeUI, self).__init__(parent)
        
        # Create UI
        self.TITLE = "Cartoon Eyes"
        self.SIZE = [450, 220]
        
        self.set_dialog_basics(self.TITLE, self.SIZE)
        self.set_window_icon("sun.svg")
        self.set_style("style.css")
        
        self.create_widgets()
        self.create_layouts()
        
        #self.create_ok_cancel_layout(self.main_layout, 35)
        self.create_apply_close_layout(self.main_layout)
        self.create_infos_layout(self.main_layout)
        
        self.create_connections()
        
        self.show()
    
    # UI FONCTIONS    
    def create_widgets(self):
        
        # check box
        self.check_box_r = QCheckBox("Right")
        self.check_box_l = QCheckBox("Left")
        self.check_box_r.setChecked(True)
        self.check_box_l.setChecked(True)
        
        # buttons
        height = 30
        
        self.get_eye_geo_btn_r = self.create_push_button("Eye geo", height)
        self.get_edge_top_btn_r = self.create_push_button("Edge up", height)
        self.get_edge_bottom_btn_r = self.create_push_button("Edge down", height)
        
        self.eye_geo_line_r = self.create_label("", height)
        self.edge_top_line_r = self.create_label("", height)
        self.edge_bottom_line_r = self.create_label("", height)
        
        self.get_eye_geo_btn_l = self.create_push_button("Eye geo", height)
        self.get_edge_top_btn_l = self.create_push_button("Edge up", height)
        self.get_edge_bottom_btn_l = self.create_push_button("Edge down", height)
        
        self.eye_geo_line_l = self.create_label("", height)
        self.edge_top_line_l = self.create_label("", height)
        self.edge_bottom_line_l = self.create_label("", height)
        
        self.dict_btn = {
            self.get_eye_geo_btn_r: self.eye_geo_line_r,
            self.get_edge_top_btn_r: self.edge_top_line_r,
            self.get_edge_bottom_btn_r: self.edge_bottom_line_r,
            self.get_eye_geo_btn_l: self.eye_geo_line_l,
            self.get_edge_top_btn_l: self.edge_top_line_l,
            self.get_edge_bottom_btn_l: self.edge_bottom_line_l
        }

    def create_layouts(self):
        
        self.main_layout = self.create_layout()
        self.setLayout(self.main_layout)
        self.options_layout = self.create_layout(self.main_layout, "hbox")
        
        self.options_lyt_r = self.create_layout(self.options_layout, "vbox")
        self.options_lyt_r.addWidget(self.check_box_r)
        
        self.widgets_lyt_r = QGridLayout()
        self.options_lyt_r.addLayout(self.widgets_lyt_r)
        
        self.widgets_lyt_r.addWidget(self.get_eye_geo_btn_r, 0, 0)
        self.widgets_lyt_r.addWidget(self.get_edge_top_btn_r, 1 ,0)
        self.widgets_lyt_r.addWidget(self.get_edge_bottom_btn_r, 2 , 0)
        
        self.widgets_lyt_r.addWidget(self.eye_geo_line_r, 0, 1)
        self.widgets_lyt_r.addWidget(self.edge_top_line_r, 1, 1)
        self.widgets_lyt_r.addWidget(self.edge_bottom_line_r, 2 , 1)
        
        
        self.options_lyt_l = self.create_layout(self.options_layout, "vbox")
        self.options_lyt_l.addWidget(self.check_box_l)
        
        self.widgets_lyt_l = QGridLayout()
        self.options_lyt_l.addLayout(self.widgets_lyt_l)
        
        self.widgets_lyt_l.addWidget(self.get_eye_geo_btn_l, 0, 0)
        self.widgets_lyt_l.addWidget(self.get_edge_top_btn_l, 1 ,0)
        self.widgets_lyt_l.addWidget(self.get_edge_bottom_btn_l, 2 , 0)
        
        self.widgets_lyt_l.addWidget(self.eye_geo_line_l, 0, 1)
        self.widgets_lyt_l.addWidget(self.edge_top_line_l, 1, 1)
        self.widgets_lyt_l.addWidget(self.edge_bottom_line_l, 2 , 1)
     
    def create_connections(self):
        
        # UI DISPLAY CONNECTIONS
        self.check_box_r.toggled.connect(self.set_enable_layout)
        self.check_box_l.toggled.connect(self.set_enable_layout)
        
        # MAYA TO UI CONNECTIONS
        for button, label in self.dict_btn.items():
            button.clicked.connect(partial(self.display_label, label))
            
        # RUN
        self.apply_button.clicked.connect(self.run)
        
        def _run_and_close():
            self.run()
            self.close()
            
        self.applyclose_button.clicked.connect(_run_and_close)
             
    def display_label(self, label):
        """
        """
        self.list_members = return_set_members()
        print(self.list_members)
        label.setText(f"{self.list_members}")
                        
    def set_enable_widgets(self, layout, value: bool):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            widget.setEnabled(value)
            
            # Set color display
            if value:
                widget.setObjectName("")
                self.set_style("style.css")
                
            else:
                widget.setObjectName("off")
                self.set_style("style.css")
                    
    def set_enable_layout(self):
        
        bool_value_r = self.check_box_r.isChecked()
        self.set_enable_widgets(self.widgets_lyt_r, bool_value_r)
        
        bool_value_l = self.check_box_l.isChecked()
        self.set_enable_widgets(self.widgets_lyt_l, bool_value_l)

    # LOGIC FUNCTIONS
    def run(self):
        
        checkbox_widgets = {
            self.check_box_r: (self.eye_geo_line_r, self.edge_top_line_r, self.edge_bottom_line_r),
            self.check_box_l: (self.eye_geo_line_l, self.edge_top_line_l, self.edge_bottom_line_l)
        }

        for checkbox, labels in checkbox_widgets.items():
            if checkbox.isChecked():
                infos = self.get_infos(*labels)
                if infos:
                    eye, edgeup, edgedown = infos
                    cartoon_eye(eye[0], edgeup, edgedown)
      
    def get_infos(self, *args):
        
        infos = []
        for arg in args:
            info = arg.text()
            if info != "":
                info = self.ui_string_to_list(info)
                infos.append(info)
            else:
                return None
        return infos