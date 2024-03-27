from maya import cmds
from PySide2.QtWidgets import (
    QDialog,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QLabel,
)
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om


def repath_texture(pxr_texture_node: str, old_string: str, new_string: str):

    file_name = cmds.getAttr(f"{pxr_texture_node}.filename")
    file_name = file_name.replace("\\", "/")
    new_string = new_string.replace("\\", "/")

    file_name = file_name.replace(old_string, new_string)
    om.MGlobal.displayInfo(f"New file name : {file_name}")
    cmds.setAttr(f"{pxr_texture_node}.filename", file_name, type="string")


def repath_textures(old_string="Z:", new_string="//GANDALF/3d4_23_24/COUPDESOLEIL"):

    for node in cmds.ls(type="PxrTexture"):
        om.MGlobal.displayInfo(f"PxrTexture node : {node}")
        repath_texture(node, old_string, new_string)


class RepathDialogUI(QDialog):

    def __init__(self, parent=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(RepathDialogUI, self).__init__(parent)
        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

    def init_ui(self):
        self.setWindowTitle("Repath textures")
        self.setMinimumSize(500, 100)

    def create_widgets(self):
        self._old_string_label = QLabel("Old string :")
        self._new_string_label = QLabel("New string :")
        self._old_string_line_edit = QLineEdit("Z:")
        self._new_string_line_edit = QLineEdit("//GANDALF/3d4_23_24/COUPDESOLEIL")
        self._run_button = QPushButton("Repath textures")

    def create_layout(self):

        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._line_edit_widget = QWidget()
        self._line_edit_layout = QGridLayout()
        self._line_edit_widget.setLayout(self._line_edit_layout)

        self._main_layout.addWidget(self._line_edit_widget)

        self._line_edit_layout.addWidget(self._old_string_label, 0, 0)
        self._line_edit_layout.addWidget(self._new_string_label, 0, 1)
        self._line_edit_layout.addWidget(self._old_string_line_edit, 1, 0)
        self._line_edit_layout.addWidget(self._new_string_line_edit, 1, 1)

        self._main_layout.addWidget(self._run_button)

    def create_connections(self):
        self._run_button.clicked.connect(self.run)

    def run(self):
        old_string = self._old_string_line_edit.text()
        new_string = self._new_string_line_edit.text()

        repath_textures(old_string=old_string, new_string=new_string)
        om.MGlobal.displayInfo(f"Repath textures : {old_string} to {new_string} done.")


RepathDialogUI()
