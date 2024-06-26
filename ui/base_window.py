import maya.cmds as cmds
from functools import partial
from ..mayatools import attribute, curve, offset, rivet


class MainWindow:


    def __init__(self):
        self.window = "MainWindow"
        self.dock_ui = "MainWindowDock"
        self.title = "Maya tools"
        self.width = 300
        self.b_width = self.width * 0.525
        self.size = (300, 150)
        self.create()


    def create(self):
        if (cmds.window (self.window, exists = 1)):
            cmds.deleteUI (self.window)
        if (cmds.dockControl (self.dock_ui, exists = 1)):
            cmds.deleteUI (self.dock_ui)
        
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, menuBar=1, resizeToFitChildren=1)

        # Menu
        cmds.menu(label = 'Help', tearOff = 1)
        cmds.menuItem (label = 'Documentation')
        
        self.main_layout = cmds.columnLayout(adjustableColumn=True)
                
        cmds.separator (h = 7, style = 'none', w = self.size[0]+20)
        cmds.text (l = "Maya tools", font = 'boldLabelFont')
        cmds.separator (h = 7, style = 'none', w = self.size[0]+20)
        
        # ATTRIBUTE
        self.attribute_layout = cmds.frameLayout(label='Attribute', collapsable=True, width=self.size[0], parent=self.main_layout)
        # Separator
        cmds.text(label = 'Channel Box Separator')
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3])
        cmds.button(label = 'Add', width = self.b_width , command = partial(self.sep_cb, v=1))
        cmds.button(label = 'Remove', width = self.b_width, command = partial(self.sep_cb, v=0))
        # Transform attributes
        self.transform_atributes_layout = cmds.columnLayout(parent=self.attribute_layout)
        self.cbs_translate = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['TranslateX', 'TranslateY', 'TranslateZ']) 
        self.cbs_rotate = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['RotateX', 'RotateY', 'RotateZ'])  
        self.cbs_scale = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['ScaleX', 'ScaleY', 'ScaleZ'])
        cmds.separator(h=5, style = 'in')
        self.cb_grp_ats01 = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['Lock', 'NonKeyable', 'Hide'])
        self.cb_grp_ats02 = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['Unlock', 'Keyable', 'Show'])
        cmds.button(label = 'Transform Attributes', parent=self.attribute_layout, command=self.transform_attributes)

        # CLOTH
        cmds.frameLayout(label='Cloth', collapsable=True, width=self.size[0], parent=self.main_layout)

        # CURVE
        self.curve_layout = cmds.frameLayout(label='Curve', collapsable=True, width=self.size[0], parent=self.main_layout)
        # Shapes
        cmds.text(label = 'Shapes')
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3])
        cmds.button(label = 'Add', width = self.b_width, command = self.add_shape)
        cmds.button(label = 'Remove', width = self.b_width, command = self.remove_shape)
        # Controls
        cmds.text(label = 'Controls', parent = self.curve_layout)
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.curve_layout)
        cmds.button(label = 'Create control', width = self.b_width,command = self.create_control)
        self.optionmenu_control = cmds.optionMenu(width = self.b_width)
        cmds.menuItem('Sphere')
        cmds.menuItem('Square')
        cmds.menuItem('Star')

        # DISPLAY
        cmds.frameLayout(label='Display', collapsable=True, width=self.size[0], parent=self.main_layout)

        # JOINT
        cmds.frameLayout(label='Joint', collapsable=True, width=self.size[0], parent=self.main_layout)

        # MATRIX
        cmds.frameLayout(label='Matrix', collapsable=True, width=self.size[0], parent=self.main_layout)

        # OFFSET
        self.offset_layout = cmds.frameLayout(label='Offset', collapsable=True, width=self.size[0], parent=self.main_layout)
        # Offset parent matrix
        cmds.text(label = 'Offset Parent Matrix', parent = self.offset_layout)
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.offset_layout)
        cmds.button(label = 'Transforms -> OPMatrix', width = self.b_width, command = self.bake_transforms_to_offset_parent_matrix)
        cmds.button(label = 'OPMatrix -> Transforms', width = self.b_width, command = self.offset_parent_matrix_to_transforms)

        # RIBBON
        cmds.frameLayout(label='Ribbon', collapsable=True, width=self.size[0], parent=self.main_layout)

        # RIG
        cmds.frameLayout(label='Rig', collapsable=True, width=self.size[0], parent=self.main_layout)

        # RIVET
        self.rivet_layout = cmds.frameLayout(label='Rivet', collapsable=True, width=self.size[0], parent=self.main_layout)
        cmds.button(label = 'Create Rivet', width = self.width, command = self.create_rivet)
        
        # Show
        cmds.dockControl (self.dock_ui, l = 'Maya tools', area = 'right', content = self.window, allowedArea = ['right', 'left'])
        cmds.refresh()
        cmds.dockControl (self.dock_ui, e = 1, r = 1, w = self.size[0]+20)


    def sep_cb(self, button: str, v: bool) -> None:
        attribute.sep_cb(cmds.ls(selection=True), value = v)

    def transform_attributes(self, button: str) -> None:
        """tx: bool = cmds.checkBoxGrp(self.cbs_translate, query=True, v1=True)
        ty: bool = cmds.checkBoxGrp(self.cbs_translate, query=True, v2=True)
        tz: bool = cmds.checkBoxGrp(self.cbs_translate, query=True, v3=True)
        rx: bool = cmds.checkBoxGrp(self.cbs_rotate, query=True, v1=True)
        ry: bool = cmds.checkBoxGrp(self.cbs_rotate, query=True, v2=True)
        rz: bool = cmds.checkBoxGrp(self.cbs_rotate, query=True, v3=True)
        sx: bool = cmds.checkBoxGrp(self.cbs_scale, query=True, v1=True)
        sy: bool = cmds.checkBoxGrp(self.cbs_scale, query=True, v2=True)
        sz: bool = cmds.checkBoxGrp(self.cbs_scale, query=True, v3=True)"""
        tx, ty, tz = cmds.checkBoxGrp(self.cbs_translate, query=True, valueArray3=True)
        rx, ry, rz = cmds.checkBoxGrp(self.cbs_rotate, query=True, valueArray3=True)
        sx, sy, sz = cmds.checkBoxGrp(self.cbs_scale, query=True, valueArray3=True)
        ats_dict = {
            'tx': tx,
            'ty': ty,
            'tz': tz,
            'rx': rx,
            'ry': ry,
            'rz': rz,
            'sx': sx,
            'sy': sy,
            'sz': sz
        }
        attributes = []
        for key, value in ats_dict.items():
            if value:
                attributes.append(key)

        lock: bool = cmds.checkBoxGrp(self.cb_grp_ats01, query=True, v1=True)
        nonkeyable: bool = cmds.checkBoxGrp(self.cb_grp_ats01, query=True, v2=True)
        hide: bool = cmds.checkBoxGrp(self.cb_grp_ats01, query=True, v3=True)
        unlock: bool = cmds.checkBoxGrp(self.cb_grp_ats02, query=True, v1=True)
        keyable: bool = cmds.checkBoxGrp(self.cb_grp_ats02, query=True, v2=True)
        show: bool = cmds.checkBoxGrp(self.cb_grp_ats02, query=True, v3=True)
        
        attribute.cb_attributes(cmds.ls(selection=True), attributes, lock, unlock, hide, show, nonkeyable, keyable)


    def add_shape(self, button: str) -> None:
        curve.add_shape(cmds.ls(selection=True))


    def remove_shape(self, button: str) -> None:
        curve.remove_shape(cmds.ls(selection=True))


    def create_control(self, button: str) -> None:
        shape: str = cmds.optionMenu(self.optionmenu_control, query = True, value = True).lower()
        curve.control(shape = shape)


    def bake_transforms_to_offset_parent_matrix(self, button: str) -> None:
        offset.offset_parent_matrix(cmds.ls(selection=True))


    def offset_parent_matrix_to_transforms(self, button: str) -> None:
        offset.op_matrix_to_transforms(cmds.ls(selection=True))


    def create_rivet(self, button: str) -> None:
        rivet.rivet_mesh_user()
#
#
MainWindow()
