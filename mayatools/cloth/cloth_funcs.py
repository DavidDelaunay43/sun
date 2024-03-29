from maya import cmds, mel
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2.QtCore import (
    Qt
)
from PySide2.QtGui import (
    QIcon
)
from PySide2.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTabWidget
)

# Cloth funcs


ALL_GRP = "ALL"
INIT_MESH_GRP = "initMesh_grp"
CLOTH_GRP = "cloth_grp"
HI_GRP = "hi_grp"


def create_passive_collider(mesh: str, nucleus_node: str) -> tuple:
    """
    Create a passive collider for the specified mesh.

    Parameters:
        mesh (str): The name of the mesh to create the collider for.
        nucleus_node (str): The name of the nucleus node to connect the collider to.

    Returns:
        tuple: A tuple containing the names of the created nRigid node and nRigidShape node.
    """

    nrigid_shape = f'{mesh}_nRigidShape'
    cmds.createNode('nRigid', name = nrigid_shape)
    nrigid_node: str = cmds.listRelatives(nrigid_shape, parent = True)[0]
    nrigid_node = cmds.rename(nrigid_node, f'{mesh}_nRigid')
    cmds.select(clear = True)

    cmds.connectAttr(f'{mesh}.worldMesh[0]', f'{nrigid_shape}.inputMesh')
    cmds.connectAttr('time1.outTime', f'{nrigid_shape}.currentTime')
    cmds.connectAttr(f'{nucleus_node}.startFrame', f'{nrigid_shape}.startFrame')
    
    for i in range(10):
        try:
            cmds.connectAttr(f'{nrigid_shape}.currentState', f'{nucleus_node}.inputPassive[{i}]')
            cmds.connectAttr(f'{nrigid_shape}.startState', f'{nucleus_node}.inputPassiveStart[{i}]')
            break
        except RuntimeError:
            continue

    return nrigid_node, nrigid_shape


def duplicate_mesh(mesh: str, new_name: str) -> str:
    """
    Duplicate a mesh with a new name.

    Parameters:
        mesh (str): The name of the mesh to duplicate.
        new_name (str): The new name for the duplicated mesh.

    Returns:
        str: The name of the duplicated mesh.
    """

    cmds.duplicate(mesh, name = new_name)
    shapes = cmds.listRelatives(new_name, shapes = True)
    for shape in shapes:
        if 'Orig' in shape:
            cmds.delete(shape)
    
    return new_name


def ensure_cloth_groups() -> None:
    """
    Ensure the existence of cloth-related groups in the scene.
    Creates groups if they do not exist.
    """

    ALL_GRP: str = "ALL"

    if cmds.objExists(ALL_GRP):
        return

    group_all: str = cmds.group(empty=True, world=True, name=ALL_GRP)
    group_names = (INIT_MESH_GRP, CLOTH_GRP, HI_GRP)

    for grp_name in group_names:
        grp = cmds.group(empty=True, world=True, name=grp_name)
        cmds.parent(grp, group_all)

    cmds.select(clear = True)


def ensure_nsystem_group(setup_prefix: str) -> str:
    """
    Ensure the existence of a nucleus system group in the scene.

    Parameters:
        setup_prefix (str): Prefix for the name of the nucleus system group.

    Returns:
        str: The name of the nucleus system group.
    """

    nsystem_grp: str = f'{setup_prefix}_nsystem_grp'
    if not cmds.objExists(nsystem_grp):
        cmds.group(empty = True, name = nsystem_grp, parent = CLOTH_GRP)
        cmds.group(empty = True, name = f'{setup_prefix}_nConstraint_grp', parent = nsystem_grp)

    return nsystem_grp


def ensure_colliders_group(setup_prefix: str) -> str:
    """
    Ensure the existence of a colliders group in the scene.

    Parameters:
        setup_prefix (str): Prefix for the name of the colliders group.

    Returns:
        str: The name of the colliders group.
    """

    colliders_grp: str = f'{setup_prefix}_colliders_grp'
    nsystem_grp: str = ensure_nsystem_group(setup_prefix)

    if not cmds.objExists(colliders_grp):
        cmds.group(empty = True, name = colliders_grp, parent = nsystem_grp)

    return colliders_grp


def ensure_init_mesh(deformed_mesh: str) -> str:
    """
    Ensure the existence of an initial mesh for cloth simulation.

    Parameters:
        deformed_mesh (str): The name of the deformed mesh.

    Returns:
        str: The name of the initial mesh.
    """

    ensure_cloth_groups()

    PFX: str = "initMesh"
    init_mesh = f"{PFX}_{deformed_mesh}"

    if cmds.objExists(init_mesh):
        return init_mesh

    duplicate_mesh(deformed_mesh, new_name=init_mesh)
    blendshape = cmds.blendShape(deformed_mesh, init_mesh, name=f"BShape_{init_mesh}")
    if isinstance(blendshape, list):
        blendshape = blendshape[0]
    cmds.setAttr(f"{blendshape}.{deformed_mesh}", 1.0)

    cmds.parent(init_mesh, INIT_MESH_GRP)

    return init_mesh


def create_cloth(simu_nmesh: str, setup_prefix: str) -> tuple:
    """
    Create a cloth simulation setup.

    Parameters:
        simu_nmesh (str): The name of the simulated mesh.
        setup_prefix (str): Prefix for the names of created objects.

    Returns:
        tuple: A tuple containing the names of the created ncloth shape and nucleus node.
    """

    ensure_cloth_groups()
    nsystem_grp: str = ensure_nsystem_group(setup_prefix)

    cmds.select(simu_nmesh)

    mel.eval('createNCloth 0; sets -e -forceElement initialShadingGroup;')
    ncloth_shape: str = cmds.ls(selection = True)[0]
    ncloth_transform: str = cmds.listRelatives(ncloth_shape, parent = True)[0]
    nucleus_node: str = cmds.listConnections(ncloth_shape, type = 'nucleus')[0]
    nucleus_node = cmds.rename(nucleus_node, f'{setup_prefix}_nucleus')

    ncloth_transform = cmds.rename(ncloth_transform, f'{setup_prefix}_ncloth')

    start_frame: float = cmds.playbackOptions(query = True, minTime = True)
    cmds.setAttr(f'{nucleus_node}.startFrame', start_frame)

    cmds.parent(simu_nmesh, nsystem_grp)
    cmds.parent(ncloth_transform, nsystem_grp)
    cmds.parent(nucleus_node, nsystem_grp)

    cmds.select(clear = True)

    return ncloth_shape, nucleus_node


def create_collider_mesh(init_mesh: str, nucleus_node: str, setup_prefix: str, collider_suffix: str) -> None:
    """
    Create a collider mesh.

    Parameters:
        init_mesh (str): The name of the initial mesh.
        nucleus_node (str): The name of the nucleus node to connect the collider to.
        setup_prefix (str): Prefix for the names of created objects.
        collider_suffix (str): Suffix for the name of the collider.
    """

    ensure_cloth_groups()
    setup_colliders_grp: str = ensure_colliders_group(setup_prefix)
    collider_grp: str = cmds.group(empty = True, name = f'{setup_prefix}_collider_{collider_suffix}_grp', parent = setup_colliders_grp)

    collider_mesh: str = duplicate_mesh(init_mesh, new_name = f'{setup_prefix}_collider_{collider_suffix}')
    cmds.parent(collider_mesh, collider_grp)

    blendshape = cmds.blendShape(init_mesh, collider_mesh, name=f"BShape_{collider_mesh}")
    if isinstance(blendshape, list):
        blendshape = blendshape[0]
    cmds.setAttr(f"{blendshape}.{init_mesh}", 1.0)

    nrigid_transform, _ = create_passive_collider(collider_mesh, nucleus_node)
    cmds.parent(nrigid_transform, collider_grp)
    cmds.select(clear = True)


def create_hi_setup(simu_nmesh: str, hi_mesh: str, setup_prefix: str):
    """
    Create a high-resolution setup for cloth simulation.

    Parameters:
        simu_nmesh (str): The name of the simulated mesh.
        hi_mesh (str): The name of the high-resolution mesh.
        setup_prefix (str): Prefix for the names of created objects.
    """

    ensure_cloth_groups()

    hi_grp: str = cmds.group(empty = True, name = f'{setup_prefix}_hi_grp', parent = HI_GRP)
    cmds.parent(hi_mesh, hi_grp)

    simu_driver_mesh = duplicate_mesh(simu_nmesh, new_name = f'{setup_prefix}_simu_driver')
    cmds.parent(simu_driver_mesh, hi_grp)
    
    blendshape = cmds.blendShape(simu_nmesh, simu_driver_mesh, name=f"BShape_{simu_driver_mesh}")
    if isinstance(blendshape, list):
        blendshape = blendshape[0]
    cmds.setAttr(f"{blendshape}.{simu_nmesh}", 1.0)

    wrap_node: str = cmds.cvWrap(hi_mesh, simu_driver_mesh, name=f'cvWrap_{hi_mesh}', radius=0.1)
    cmds.select(clear = True)


def create_full_setup(setup_prefix: str, low_mesh: str, high_mesh: str, colliders: dict = None) -> None:
    """
    Create a full cloth simulation setup.

    Parameters:
        setup_prefix (str): Prefix for the names of created objects.
        low_mesh (str): The name of the low-resolution mesh.
        high_mesh (str): The name of the high-resolution mesh.
        colliders (dict, optional): A dictionary containing collider meshes and their suffixes.
    """
    
    ensure_cloth_groups()
    ensure_nsystem_group(setup_prefix)

    simu_nmesh = duplicate_mesh(low_mesh, new_name = f'{setup_prefix}_simu_nmesh')
    _, nucleus_node = create_cloth(simu_nmesh, setup_prefix)

    himesh = duplicate_mesh(high_mesh, new_name = f'{setup_prefix}_hiMesh')
    create_hi_setup(simu_nmesh = simu_nmesh, hi_mesh = himesh, setup_prefix = setup_prefix)

    if not colliders:
        return
    
    for collider, collider_suffix in colliders.items():
        init_mesh = ensure_init_mesh(deformed_mesh = collider)
        create_collider_mesh(init_mesh, nucleus_node, setup_prefix, collider_suffix)


# Pre-roll funcs


def get_preroll_frames(
    start_anim_frame: float,
    start_pose_offset: float = -5.0,
    inter_pose_offset: float = -25.0, 
    bind_pose_offset: float = -30.0 
) -> dict:

    start_pose_frame: float = start_anim_frame + start_pose_offset
    inter_pose_frame: float = start_anim_frame + inter_pose_offset
    bind_pose_frame: float = start_anim_frame + bind_pose_offset

    preroll_frames_dict ={
        'start_anim_frame': start_anim_frame,
        'start_pose_frame': start_pose_frame,
        'inter_pose_frame': inter_pose_frame,
        'bind_pose_frame': bind_pose_frame
    }

    return preroll_frames_dict


def set_preroll_time_slider(preroll_frames: dict) -> None:

    bind_pose_frame: float = preroll_frames['bind_pose_frame']
    end_frame: float = cmds.playbackOptions(query=True, maxTime=True)
    cmds.playbackOptions(minTime = bind_pose_frame, maxTime = end_frame)


def set_key_frame(controler: str) -> None:

    for attribute in cmds.listAttr(controler, keyable = True):
        cmds.setKeyframe(f'{controler}.{attribute}')


def set_attributes_to_defaults(controler: str) -> None:

    attribute_dict = {
        'translateX': 0.0,
        'translateY': 0.0,
        'translateZ': 0.0,
        'rotateX': 0.0,
        'rotateY': 0.0,
        'rotateZ': 0.0,
        'scaleX': 1.0,
        'scaleY': 1.0,
        'scaleZ': 1.0
    }

    for attribute in cmds.listAttr(controler, keyable = True):
        if not cmds.attributeQuery(attribute, node = controler, keyable = True):
            continue
        
        if not attribute in attribute_dict.keys():
            continue

        default_value: float = attribute_dict[attribute]
        cmds.setAttr(f'{controler}.{attribute}', default_value)


def set_preroll_keys(controlers: list, preroll_frames: dict) -> None:

    # set start pose
    cmds.currentTime(preroll_frames['start_pose_frame'])
    for ctrl in controlers:
        set_key_frame(ctrl)

    # set inter pose
    cmds.currentTime(preroll_frames['inter_pose_frame'])
    for ctrl in controlers:
        set_attributes_to_defaults(ctrl)
        set_key_frame(ctrl)

    # set bind pose
    cmds.currentTime(preroll_frames['bind_pose_frame'])
    for ctrl in controlers:
        set_key_frame(ctrl)


def set_preroll(controlers: list, preroll_values: list):

    preroll_frames: dict = get_preroll_frames(*preroll_values)
    set_preroll_time_slider(preroll_frames)
    set_preroll_keys(controlers, preroll_frames)


# User interface


def maya_main_window():
    """Return the Maya main window widget as a Python object."""

    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QWidget)


ICON_PATH = 'C:/Users/d.delaunay/Documents/maya_dev/scripts/sun/mayatools/cloth/ncloth.svg'
STYLE_PATH = 'C:/Users/d.delaunay/Documents/maya_dev/scripts/sun/mayatools/cloth/style.css'


class PrerollWidget(QWidget):

    def __init__(self, parent=None):
        super(PrerollWidget, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()


    def init_ui(self):
        size = (300, 400)
        self.setMinimumSize(*size)


    def create_widgets(self):
        start_frame: float = cmds.playbackOptions(query = True, minTime = True)
        self.start_frame_label = QLabel(f'Start frame')
        self.start_frame_lineedit = QLineEdit(f'{start_frame}')

        self.start_pose_offset_label = QLabel('Start pose offset')
        self.start_pose_offset_lineedit = QLineEdit(f'{-5.0}')
        
        self.inter_pose_offset_label = QLabel('Inter pose offset')
        self.inter_pose_offset_lineedit = QLineEdit(f'{-25.0}')
        
        self.bind_pose_offset_label = QLabel('Bind pose offset')
        self.bind_pose_offset_lineedit = QLineEdit(f'{-30.0}')

        self.info_label = QLabel('Select controlers')
        self.run_button = QPushButton('Preroll')


    def create_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.main_layout.addWidget(self.grid_widget)

        self.grid_layout.addWidget(self.start_frame_label, 0, 0)
        self.grid_layout.addWidget(self.start_frame_lineedit, 0, 1)
        self.grid_layout.addWidget(self.start_pose_offset_label, 1, 0)
        self.grid_layout.addWidget(self.start_pose_offset_lineedit, 1, 1)
        self.grid_layout.addWidget(self.inter_pose_offset_label, 2, 0)
        self.grid_layout.addWidget(self.inter_pose_offset_lineedit, 2, 1)
        self.grid_layout.addWidget(self.bind_pose_offset_label, 3, 0)
        self.grid_layout.addWidget(self.bind_pose_offset_lineedit, 3, 1)

        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.run_button)


    def create_connections(self):
        self.run_button.clicked.connect(self.preroll)


    def preroll(self):
        start_frame = float(self.start_frame_lineedit.text())
        start_pose_offset = float(self.start_pose_offset_lineedit.text())
        inter_pose_offset = float(self.inter_pose_offset_lineedit.text())
        bind_pose_offset = float(self.bind_pose_offset_lineedit.text())

        preroll_values = [start_frame, start_pose_offset, inter_pose_offset, bind_pose_offset]

        controlers: list = cmds.ls(selection = True)
        set_preroll(controlers, preroll_values)


class SetupWidget(QWidget):

    def __init__(self, parent=None):
        super(SetupWidget, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.collider_dict = {}

    def init_ui(self):
        size = (300, 400)
        self.setMinimumSize(*size)

    def create_widgets(self):
        self.setup_name_label = QLabel('Setup name')
        self.setup_name_lineedit = QLineEdit()

        self.simu_nmesh_button = QPushButton('Simu nMesh')
        self.simu_nmesh_lineedit = QLineEdit()

        self.himesh_button = QPushButton('High Mesh')
        self.himesh_lineedit = QLineEdit()

        self.add_collider_button = QPushButton('Add collider')

        self.collider_mesh_label = QLabel('Collider mesh')
        self.collider_name_label = QLabel('Collider name')

        self.create_setup_button = QPushButton('Create setup')

    def create_layout(self):
        self.main_layout = QVBoxLayout(self)

        self.grid_widget = QWidget()
        self.main_layout.addWidget(self.grid_widget)
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.grid_layout.addWidget(self.setup_name_label, 0, 0)
        self.grid_layout.addWidget(self.setup_name_lineedit, 0, 1)
        self.grid_layout.addWidget(self.simu_nmesh_button, 1, 0)
        self.grid_layout.addWidget(self.simu_nmesh_lineedit, 1, 1)
        self.grid_layout.addWidget(self.himesh_button, 2, 0)
        self.grid_layout.addWidget(self.himesh_lineedit, 2, 1)

        # Ajouter le label et le bouton dans un QHBoxLayout
        collider_button_layout = QHBoxLayout()
        collider_button_layout.addWidget(self.add_collider_button)
        self.main_layout.addLayout(collider_button_layout)

        self.collider_widget = QWidget()
        self.main_layout.addWidget(self.collider_widget)
        self.collider_layout = QGridLayout()
        self.collider_widget.setLayout(self.collider_layout)
        self.collider_layout.addWidget(self.collider_mesh_label, 0, 0, Qt.AlignTop)
        self.collider_layout.addWidget(self.collider_name_label, 0, 1, Qt.AlignTop)

        self.main_layout.addWidget(self.create_setup_button)

    def create_connections(self):
        self.simu_nmesh_button.clicked.connect(self.update_lineedit)
        self.himesh_button.clicked.connect(self.update_lineedit)
        self.create_setup_button.clicked.connect(self.create_setup)
        self.add_collider_button.clicked.connect(self.add_collider)

    def add_collider(self):
        collider_mesh_lineedit = QLineEdit()
        collider_name_lineedit = QLineEdit()

        for i in range(1, 10):
            if self.collider_layout.itemAtPosition(i, 0):
                continue

            self.collider_layout.addWidget(collider_mesh_lineedit, i, 0, Qt.AlignTop)
            self.collider_layout.addWidget(collider_name_lineedit, i, 1, Qt.AlignTop)

        self.collider_dict[collider_mesh_lineedit] = collider_name_lineedit

    def update_lineedit(self):
        button_label_dict = {
            self.simu_nmesh_button: self.simu_nmesh_lineedit,
            self.himesh_button: self.himesh_lineedit
        }

        lineedit: QLineEdit = button_label_dict[self.sender()]

        selection = cmds.ls(selection=True)
        if not selection:
            return

        node_name: str = selection[0]
        lineedit.setText(node_name)

    def create_setup(self):
        setup_prefix = self.setup_name_lineedit.text()
        low_mesh = self.simu_nmesh_lineedit.text()
        high_mesh = self.himesh_lineedit.text()

        collider_dict = {}
        for key, value in self.collider_dict.items():
            collider_dict[key.text()] = value.text()

        create_full_setup(setup_prefix, low_mesh, high_mesh, colliders=collider_dict)


class ClothUi(QDialog):


    def __init__(self, parent = maya_main_window()):
        super(ClothUi, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

        self.setup_widgets = []


    def init_ui(self):
        self.setWindowTitle('Cloth Setup')
        size = (350, 450)
        self.resize(*size)

        with open(STYLE_PATH, 'r') as file:
            style = file.read()
        self.setStyleSheet(style)

        self.setWindowIcon(QIcon(ICON_PATH))


    def create_widgets(self):
        self.add_setup_btn = QPushButton('Add Setup')
        self.pre_roll_widget = PrerollWidget(self)


    def create_layout(self):

        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.cloth_widget = QWidget()
        self.preroll_widget = QWidget()

        self.cloth_layout = QVBoxLayout(self.cloth_widget)
        self.preroll_layout = QVBoxLayout(self.preroll_widget)

        self.tab_widget.addTab(self.cloth_widget, 'Cloth')
        self.tab_widget.addTab(self.preroll_widget, 'Preroll')

        # cloth layout
        self.cloth_layout.addWidget(self.add_setup_btn)
        self.setup_widget = QWidget()
        self.setup_layout = QHBoxLayout(self.setup_widget)
        self.cloth_layout.addWidget(self.setup_widget)

        # preroll layout
        self.preroll_layout.addWidget(self.pre_roll_widget)


    def create_connections(self):
        self.add_setup_btn.clicked.connect(self.add_setup_widget)


    def add_setup_widget(self):
        setup_widget = SetupWidget(self)
        self.setup_layout.addWidget(setup_widget)
        setup_widget.show()
        self.setup_widgets.append(setup_widget)


ClothUi()
