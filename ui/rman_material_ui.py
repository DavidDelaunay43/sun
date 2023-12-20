from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, QGridLayout, QLabel, QCheckBox, QLineEdit, QHBoxLayout,
                               QRadioButton)
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
from shiboken2 import wrapInstance
from functools import partial
from ..utils.imports import *
from ..mayatools import renderman
reload(renderman)

class RmanMaterialWindowUI(QMainWindow):

    def __init__(self, parent = wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(RmanMaterialWindowUI, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

    def create_widgets(self):

        self.create_radio_button = QRadioButton('CREATE')
        self.create_radio_button.setChecked(True)
        self.edit_radio_button = QRadioButton('EDIT')

        self.prefix_label = QLabel('Prefix :')
        self.prefix_line_edit = QLineEdit('PS_')
        self.shader_label = QLabel('Shader name :')
        self.shader_line_edit = QLineEdit()

        self.lobe_label = QLabel('LOBE')
        self.linearize_label = QLabel('linearize')
        self.grader_label = QLabel('GRADER')

        attributes = (
            'diffuseGain',
            'diffuseColor',
            'specularFaceColor',
            'specularEdgeColor',
            'specularRoughness',
            'roughSpecularFaceColor',
            'roughSpecularEdgeColor',
            'roughSpecularRoughness',
            'clearcoatFaceColor',
            'clearcoatEdgeColor',
            'clearcoatRoughness',
            'subsurfaceGain',
            'subsurfaceColor',
            'subsurfaceDmfp',
            'subsurfaceDmfpColor',
            'refractionGain',
            'relectionGain',
            'refractionGain',
            'glassRoughness',
            'glassIor',
            'bumpNormal',
            'presence',
            'displace'
        )

        self.lobe_list = []
        self.linearize_list = []
        self.grader_list = []
        for at in attributes:
            lobe_cb = QCheckBox(at)
            self.lobe_list.append(lobe_cb)

            linearize_cb = QCheckBox()
            self.linearize_list.append(linearize_cb)
            linearize_cb.setChecked(True) if 'Color' in at else None
            linearize_cb.setEnabled(False)

            grader_cb = QCheckBox()
            self.grader_list.append(grader_cb)
            grader_cb.setEnabled(False)

        self.run_button = QPushButton('Run')

    def create_layout(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout = QVBoxLayout(self.central_widget)

        self.mode_widget = QWidget()
        self.mode_layout = QHBoxLayout(self.mode_widget)
        self.main_layout.addWidget(self.mode_widget)

        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout(self.top_widget)
        self.main_layout.addWidget(self.top_widget)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.main_layout.addWidget(self.grid_widget)

        self.mode_layout.addWidget(self.create_radio_button)
        self.mode_layout.addWidget(self.edit_radio_button)

        self.top_layout.addWidget(self.prefix_label)
        self.top_layout.addWidget(self.prefix_line_edit)
        self.top_layout.addWidget(self.shader_label)
        self.top_layout.addWidget(self.shader_line_edit)

        self.grid_layout.addWidget(self.lobe_label, 0, 0)
        self.grid_layout.addWidget(self.linearize_label, 0, 1)
        self.grid_layout.addWidget(self.grader_label, 0, 2)

        for i, (lobe_cb, linearize_cb, grader_cb) in enumerate(zip(self.lobe_list, self.linearize_list, self.grader_list), start = 1):
            self.grid_layout.addWidget(lobe_cb, i, 0)
            self.grid_layout.addWidget(linearize_cb, i, 1)
            self.grid_layout.addWidget(grader_cb, i, 2)

        self.main_layout.addWidget(self.run_button)

    def create_connections(self):
        self.run_button.clicked.connect(self.run)

        for lobe_cb, linearize_cb, grader_cb in zip(self.lobe_list, self.linearize_list, self.grader_list):
            lobe_cb.stateChanged.connect(partial(self.update_cb_state, lobe_cb, linearize_cb, grader_cb))

    def update_cb_state(self, lobe_cb, linearize_cb, grader_cb, state):
        if state == Qt.Checked:
            linearize_cb.setEnabled(True)
            grader_cb.setEnabled(True)
        else:
            linearize_cb.setEnabled(False)
            grader_cb.setEnabled(False)

    def get_lobes(self):
        lobe_list_return = []
        for lobe_cb, linearize_cb, grader_cb in zip(self.lobe_list, self.linearize_list, self.grader_list):
            if not lobe_cb.isChecked():
                continue
            linearize_state = linearize_cb.isChecked()
            grader_state = grader_cb.isChecked()

            lobe_list_return.append((lobe_cb.text(), linearize_state, grader_state))

        return lobe_list_return

    def run(self):
        om.MGlobal.displayInfo('Run...')
        lobe_info_list = self.get_lobes()
        lobe_list, linearize_list, grader_list = [], [], []
        prefix, shader_name = self.prefix_line_edit.text(), self.shader_line_edit.text()
        shader_node_name = f'{prefix}{shader_name}'
        geo = cmds.ls(selection = True)
        om .MGlobal.displayInfo(f'SHADER NODE : {shader_node_name} | GEO : {geo}')
        for lobe_info in lobe_info_list:
            lobe, linearize, grader = lobe_info[0], lobe_info[1], lobe_info[2]
            om.MGlobal.displayInfo(f'LOBE : {lobe} | LINEARIZE : {linearize} | grader : {grader}')
            lobe_list.append(lobe)
            linearize_list.append(linearize)
            grader_list.append(grader)

        renderman.pxr_material(geo = geo, 
                               name = shader_node_name, 
                               attributes = lobe_list, 
                               linearizes = linearize_list, 
                               graders = grader_list)
