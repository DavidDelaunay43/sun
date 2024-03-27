from maya import cmds
import maya.OpenMayaUI as omui
from PySide2.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
)
from shiboken2 import wrapInstance


def transfer_deformation_to_blendshape(
    base_geo: str, deformed_geo: str, blendshape_node: str, controlers: dict
):
    """
    controlers = {
        "ctrl_lattice_eye_L": {
            "tx": [-0.5, 0.5],
            "ty": [-0.5, 0.5],
            "tz": [-0.5, 0.5]
        },
        "ctrl_lattice_eye_R": {
            "tx": [-0.5, 0.5],
            "ty": [-0.5, 0.5],
            "tz": [-0.5, 0.5]
        }
    }
    """

    def transfer(
        base_geo: str,
        deformed_geo: str,
        blendshape_node: str,
        control: str,
        axis: str,
        value: float,
        suffix: str = "",
    ):
        """
        # mettre l'attribut du controleur à sa valeur
        # add target
        # renommer la target
        # créer le remap value et le connecter
        # reset l'attribut du controleur
        # incrémenter i
        """

        base_geo = cmds.listRelatives(base_geo, shapes=True)[0]
        deformed_geo = cmds.listRelatives(deformed_geo, shapes=True)[0]

        weight_num = cmds.listAttr(f"{blendshape_node}.w", multi=True)
        if not weight_num:
            index = 0
        else:
            index = len(weight_num)

        cmds.setAttr(f"{control}.{axis}", value)
        print(base_geo, index, deformed_geo)
        cmds.blendShape(
            blendshape_node,
            edit=True,
            topologyCheck=True,
            target=[base_geo, index, deformed_geo, 1.0],
            weight=[index, 0.0],
            tangentSpace=True,
        )
        cmds.aliasAttr(f"{control}_{axis}{suffix}", f"{blendshape_node}.w[{index}]")

        bad_attribute = cmds.listConnections(
            f"{deformed_geo}.worldMesh[0]", source=False, destination=True, plugs=True
        )
        if bad_attribute:
            cmds.disconnectAttr(f"{deformed_geo}.worldMesh[0]", bad_attribute[0])

        if axis.startswith("s"):
            cmds.setAttr(f"{control}.{axis}", 1)
        else:
            cmds.setAttr(f"{control}.{axis}", 0)

        rm_node = cmds.createNode("remapValue", name=f"rm_{control}_{axis}{suffix}")
        if axis.startswith("s"):
            cmds.setAttr(f"{rm_node}.inputMin", 1)
        cmds.setAttr(f"{rm_node}.inputMax", value)
        cmds.connectAttr(f"{control}.{axis}", f"{rm_node}.inputValue")
        cmds.connectAttr(
            f"{rm_node}.outValue",
            f"{blendshape_node}.{control}_{axis}{suffix}",
            force=True,
        )

    for control, transforms in controlers.items():

        for axis, values in transforms.items():

            if len(values) == 2:
                v_min, v_max = values
                transfer(
                    base_geo,
                    deformed_geo,
                    blendshape_node,
                    control,
                    axis,
                    v_min,
                    suffix="_min",
                )
                transfer(
                    base_geo,
                    deformed_geo,
                    blendshape_node,
                    control,
                    axis,
                    v_max,
                    suffix="_max",
                )

            else:
                value = values[0]
                transfer(base_geo, deformed_geo, blendshape_node, control, axis, value)


def maya_main_window():
    """Return the Maya main window widget as a Python object."""

    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QWidget)


class TransferDialog(QDialog):
    """ """

    def __init__(self, parent=maya_main_window()):
        super(TransferDialog, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

    def init_ui(self):
        self.setWindowTitle("Transfer deformations")

    def create_widgets(self):
        self.base_geo_button = QPushButton("Base geo")
        self.deformed_geo_button = QPushButton("Target geo")
        self.blendshape_node_button = QPushButton("BlendShape node")
        self.controller_button = QPushButton("Controller")

        self.base_geo_lineedit = QLineEdit("")
        self.deformed_geo_lineedit = QLineEdit("")
        self.blendshape_node_lineedit = QLineEdit("")
        self.controller_lineedit = QLineEdit("")

        self.tx_cb = QCheckBox("translateX")
        self.tx_min = QLineEdit("0.0")
        self.tx_max = QLineEdit("0.0")
        self.ty_cb = QCheckBox("translateY")
        self.ty_min = QLineEdit("0.0")
        self.ty_max = QLineEdit("0.0")
        self.tz_cb = QCheckBox("translateZ")
        self.tz_min = QLineEdit("0.0")
        self.tz_max = QLineEdit("0.0")

        self.rx_cb = QCheckBox("rotateX")
        self.rx_min = QLineEdit("0.0")
        self.rx_max = QLineEdit("0.0")
        self.ry_cb = QCheckBox("rotateY")
        self.ry_min = QLineEdit("0.0")
        self.ry_max = QLineEdit("0.0")
        self.rz_cb = QCheckBox("rotateZ")
        self.rz_min = QLineEdit("0.0")
        self.rz_max = QLineEdit("0.0")

        self.sx_cb = QCheckBox("scaleX")
        self.sx_min = QLineEdit("0.0")
        self.sx_max = QLineEdit("0.0")
        self.sy_cb = QCheckBox("scaleY")
        self.sy_min = QLineEdit("0.0")
        self.sy_max = QLineEdit("0.0")
        self.sz_cb = QCheckBox("scaleZ")
        self.sz_min = QLineEdit("0.0")
        self.sz_max = QLineEdit("0.0")

        self.run_button = QPushButton("Run")

        self.cb_tuple = (
            self.tx_cb,
            self.ty_cb,
            self.tz_cb,
            self.rx_cb,
            self.ry_cb,
            self.rz_cb,
            self.sx_cb,
            self.sy_cb,
            self.sz_cb,
        )
        self.min_tuple = (
            self.tx_min,
            self.ty_min,
            self.tz_min,
            self.rx_min,
            self.ry_min,
            self.rz_min,
            self.sx_min,
            self.sy_min,
            self.sz_min,
        )
        self.max_tuple = (
            self.tx_max,
            self.ty_max,
            self.tz_max,
            self.rx_max,
            self.ry_max,
            self.rz_max,
            self.sx_max,
            self.sy_max,
            self.sz_max,
        )

    def create_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.main_layout.addWidget(self.grid_widget)

        self.grid_layout.addWidget(self.base_geo_button, 0, 0)
        self.grid_layout.addWidget(self.base_geo_lineedit, 0, 1)

        self.grid_layout.addWidget(self.deformed_geo_button, 1, 0)
        self.grid_layout.addWidget(self.deformed_geo_lineedit, 1, 1)

        self.grid_layout.addWidget(self.blendshape_node_button, 2, 0)
        self.grid_layout.addWidget(self.blendshape_node_lineedit, 2, 1)

        self.grid_layout.addWidget(self.controller_button, 3, 0)
        self.grid_layout.addWidget(self.controller_lineedit, 3, 1)

        self.grid_layout.addWidget(self.tx_cb, 4, 0)
        self.grid_layout.addWidget(self.tx_min, 4, 1)
        self.grid_layout.addWidget(self.tx_max, 4, 2)
        self.grid_layout.addWidget(self.ty_cb, 5, 0)
        self.grid_layout.addWidget(self.ty_min, 5, 1)
        self.grid_layout.addWidget(self.ty_max, 5, 2)
        self.grid_layout.addWidget(self.tz_cb, 6, 0)
        self.grid_layout.addWidget(self.tz_min, 6, 1)
        self.grid_layout.addWidget(self.tz_max, 6, 2)

        self.grid_layout.addWidget(self.rx_cb, 7, 0)
        self.grid_layout.addWidget(self.rx_min, 7, 1)
        self.grid_layout.addWidget(self.rx_max, 7, 2)
        self.grid_layout.addWidget(self.ry_cb, 8, 0)
        self.grid_layout.addWidget(self.ry_min, 8, 1)
        self.grid_layout.addWidget(self.ry_max, 8, 2)
        self.grid_layout.addWidget(self.rz_cb, 9, 0)
        self.grid_layout.addWidget(self.rz_min, 9, 1)
        self.grid_layout.addWidget(self.rz_max, 9, 2)

        self.grid_layout.addWidget(self.sx_cb, 10, 0)
        self.grid_layout.addWidget(self.sx_min, 10, 1)
        self.grid_layout.addWidget(self.sx_max, 10, 2)
        self.grid_layout.addWidget(self.sy_cb, 11, 0)
        self.grid_layout.addWidget(self.sy_min, 11, 1)
        self.grid_layout.addWidget(self.sy_max, 11, 2)
        self.grid_layout.addWidget(self.sz_cb, 12, 0)
        self.grid_layout.addWidget(self.sz_min, 12, 1)
        self.grid_layout.addWidget(self.sz_max, 12, 2)

        self.main_layout.addWidget(self.run_button)

    def create_connections(self):

        self.base_geo_button.clicked.connect(self.set_label)
        self.deformed_geo_button.clicked.connect(self.set_label)
        self.blendshape_node_button.clicked.connect(self.set_label)
        self.controller_button.clicked.connect(self.set_label)

        self.run_button.clicked.connect(self.run)

    def set_label(self):

        item_dict = {
            "Base geo": self.base_geo_lineedit,
            "Target geo": self.deformed_geo_lineedit,
            "BlendShape node": self.blendshape_node_lineedit,
            "Controller": self.controller_lineedit,
        }

        item = self.sender().text()
        lineedit = item_dict[item]

        selection = cmds.ls(selection=True)
        if selection:
            text = selection[0]
        else:
            text = ""

        lineedit.setText(text)

    def run(self):

        base_geo = self.base_geo_lineedit.text()
        deformed_geo = self.deformed_geo_lineedit.text()
        blendshape_node = self.blendshape_node_lineedit.text()
        controller = self.controller_lineedit.text()

        controller_dict = {controller: {}}

        for cb, min, max in zip(self.cb_tuple, self.min_tuple, self.max_tuple):

            if not cb.isChecked():
                continue

            axis_name = cb.text()
            min_value, max_value = float(min.text()), float(max.text())
            controller_dict[controller][axis_name] = [min_value, max_value]

        print(base_geo, deformed_geo, blendshape_node, controller_dict)
        transfer_deformation_to_blendshape(
            base_geo, deformed_geo, blendshape_node, controller_dict
        )
