import maya.cmds as cmds
from functools import partial
from ..mayatools import attribute, curve, offset, ribbon, rivet


class MainWindow:


    window = 'MainWindow'
    dock_ui = 'MainWindowDock'
    title = 'Maya tools'
    width = 300
    height = 150
    b_width = width * 0.525
    b4_width = width * 0.27
    size = (width, height)
    layout_bgc = (0.2,0.2,0.2)
    sep_bgc = (0.9, 0.9, 0.9)
    red = (0.9, 0.5, 0.5)
    green = (0.5, 0.9, 0.5)
    blue = (0.6, 0.7, 0.9)
    sep_str = '- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -'


    def __init__(self):
        self.create_ui()


    def create_ui(self):
        if (cmds.window (self.window, exists = True)):
            cmds.deleteUI (self.window)
        if (cmds.dockControl (self.dock_ui, exists = True)):
            cmds.deleteUI (self.dock_ui)
        
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, menuBar=True, resizeToFitChildren=True)

        # Menu
        cmds.menu(label = 'Help', tearOff = True)
        cmds.menuItem (label = 'Documentation')
        
        self.base_layout = cmds.scrollLayout()
        self.main_layout = cmds.columnLayout(adjustableColumn=True)
                
        cmds.separator (h = 7, style = 'none', w = self.size[0]+20)
        cmds.text (l = "Maya tools", font = 'boldLabelFont')
        cmds.separator (h = 7, style = 'none', w = self.size[0]+20)
        
        # ATTRIBUTE
        self.attribute_layout = cmds.frameLayout(label='Attribute', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        # Separator
        cmds.text(label = 'Channel Box Separator', align = 'left', font = 'boldLabelFont')
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3])
        cmds.button(label = 'Add', width = self.b_width, bgc=self.green, command = partial(self.sep_cb, v=1))
        cmds.button(label = 'Remove', width = self.b_width, bgc=self.red, command = partial(self.sep_cb, v=0))
        cmds.text(label = self.sep_str, parent = self.attribute_layout)
        # Transform attributes
        cmds.text(label='Transform Attributes', align='left', font = 'boldLabelFont', parent=self.attribute_layout)
        self.transform_atributes_layout = cmds.columnLayout(parent=self.attribute_layout)
        self.cbs_translate = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['TranslateX', 'TranslateY', 'TranslateZ']) 
        self.cbs_rotate = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['RotateX', 'RotateY', 'RotateZ'])  
        self.cbs_scale = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['ScaleX', 'ScaleY', 'ScaleZ'])
        cmds.separator(h=5, bgc=self.sep_bgc, style = 'in')
        #self.cb_grp_ats01 = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['Lock', 'NonKeyable', 'Hide'])
        #self.cb_grp_ats02 = cmds.checkBoxGrp(numberOfCheckBoxes=3, labelArray3=['Unlock', 'Keyable', 'Show'])
        cmds.rowColumnLayout(numberOfColumns = 3, rowSpacing = [3,3], columnSpacing = [3,3])
        cmds.radioCollection()
        cmds.radioButton('Lock')
        cmds.radioButton('Unlock')
        cmds.radioCollection()
        cmds.radioButton('Nonkeyable')
        cmds.radioButton('Keyable')
        cmds.radioCollection()
        cmds.radioButton('Hide')
        cmds.radioButton('Show')
        cmds.button(label = 'Transform Attributes', parent=self.attribute_layout, bgc=self.blue, command=self.transform_attributes)
        cmds.text(label = self.sep_str, parent = self.attribute_layout)
        # Proxy attributes
        cmds.text(label = 'Proxy Attribute', align = 'left', font = 'boldLabelFont', parent = self.attribute_layout)
        self.proxy_attribute_layout = cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.attribute_layout)
        cmds.text(label = 'Proxy Node :', align='left')
        cmds.text(label = 'Attribute :', align='left')
        self.textfield_proxy_node = cmds.textField(width=self.b_width)
        self.textfield_attribute = cmds.textField(width=self.b_width)
        cmds.button(label='Add Proxy Attribute', parent=self.attribute_layout, bgc=self.blue, command=self.proxy_attribute)
        #cmds.text(label = self.sep_str, parent = self.attribute_layout)

        # CLOTH
        cmds.frameLayout(label='Cloth', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)

        # CURVE
        self.curve_layout = cmds.frameLayout(label='Curve', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        # Shapes
        cmds.text(label = 'Shapes', align = 'left', font = 'boldLabelFont')
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3])
        cmds.button(label = 'Add', width = self.b_width, bgc=self.green, command = self.add_shape)
        cmds.button(label = 'Remove', width = self.b_width, bgc=self.red, command = self.remove_shape)
        cmds.text(label = self.sep_str, parent = self.curve_layout)
        # Controls
        cmds.text(label = 'Controls', align = 'left', font = 'boldLabelFont', parent = self.curve_layout)
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.curve_layout)
        cmds.button(label = 'Create control', width = self.b_width, bgc=self.blue, command = self.create_control)
        self.optionmenu_control = cmds.optionMenu(width = self.b_width)
        cmds.menuItem('Chest')
        cmds.menuItem('Plus')
        cmds.menuItem('Root')
        cmds.menuItem('Sphere')
        cmds.menuItem('Square')
        cmds.menuItem('Triangle_back')
        cmds.menuItem('Triangle_front')
        #cmds.text(label = self.sep_str, parent = self.curve_layout)

        # DISPLAY
        self.display_layout = cmds.frameLayout(label='Display', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        cmds.text(label = 'Color node', align='left', font = 'boldLabelFont', parent = self.display_layout)
        cmds.rowColumnLayout (numberOfColumns = 4, parent = self.display_layout)
        cmds.button(label='BLUE', w=self.b4_width, bgc=(0.26279, 0.61957, 0.99998))
        cmds.button(label='GOLD', w=self.b4_width, bgc=(1.0, 0.7461085915565491, 0.0))
        cmds.button(label='GREEN', w=self.b4_width, bgc=(0.0, 1.0, 0.0))
        cmds.button(label='MAGENTA', w=self.b4_width, bgc=(0.913, 0.441, 0.478))
        cmds.button(label='ORANGE', w=self.b4_width, bgc=(1.0, 0.476, 0.187))
        cmds.button(label='PINK', w=self.b4_width, bgc=(0.892, 0.589, 0.745))
        #cmds.button(label='RED', w=self.b4_width, bgc=(1.0, 0.4, 0.4))
        cmds.button(label='WHITE', w=self.b4_width, bgc=(1.0, 1.0, 1.0))
        cmds.button(label='YELLOW', w=self.b4_width, bgc=(0.9906, 0.99258, 0.38934))
        cmds.text(label = self.sep_str, parent = self.display_layout)

        # JOINT
        cmds.frameLayout(label='Joint', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)

        # MATRIX
        cmds.frameLayout(label='Matrix', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)

        # OFFSET
        self.offset_layout = cmds.frameLayout(label='Offset', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        # Offset parent matrix
        cmds.text(label = 'Offset Parent Matrix', align='left', font = 'boldLabelFont', parent = self.offset_layout)
        cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.offset_layout)
        cmds.button(label = 'Transforms -> OPMatrix', width = self.b_width, bgc=self.blue, command = self.bake_transforms_to_offset_parent_matrix)
        cmds.button(label = 'OPMatrix -> Transforms', width = self.b_width, bgc=self.blue, command = self.offset_parent_matrix_to_transforms)
        #cmds.text(label = self.sep_str, parent = self.offset_layout)

        # RIBBON
        self.ribbon_layout = cmds.frameLayout(label='Ribbon', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        cmds.text(label = 'Ribbon', align='left', font = 'boldLabelFont', parent = self.ribbon_layout)
        self.ribbon_lyt = cmds.rowColumnLayout (numberOfColumns = 2, rowSpacing = [2,3], columnSpacing = [2,3], parent = self.ribbon_layout)
        cmds.text(label='Name :', align='left')
        cmds.text(label='Subdivisions :', align='left')
        self.textfield_ribbon_name = cmds.textField(text='ribbon', width=self.b_width)
        self.intslider_ribbon_sub = cmds.intSliderGrp(field=True, minValue=3, maxValue=9, fieldMinValue=3, fieldMaxValue=9, value=5, width=self.b_width)
        cmds.radioCollection()
        self.radiobutton_ribbon_world = cmds.radioButton('World', select=True)
        self.radiobutton_ribbon_bone = cmds.radioButton('Bone')
        cmds.button(label='Create Ribbon', bgc=self.blue, parent=self.ribbon_layout, command=self.create_ribbon)

        # RIG
        cmds.frameLayout(label='Rig', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)

        # RIVET
        self.rivet_layout = cmds.frameLayout(label='Rivet', collapsable=True, width=self.size[0], bgc=self.layout_bgc, parent=self.main_layout)
        cmds.button(label = 'Create Rivet', width = self.width, bgc=self.blue, command = self.create_rivet)
        #cmds.text(label = self.sep_str, parent = self.rivet_layout)
        
        # Show
        cmds.dockControl (self.dock_ui, l = 'Maya tools', area = 'right', content = self.window, allowedArea = ['right', 'left'])
        cmds.refresh()
        cmds.dockControl (self.dock_ui, e = 1, r = 1, w = self.size[0]+20)


    def sep_cb(self, button: str, v: bool) -> None:
        attribute.sep_cb(cmds.ls(selection=True), value = v)

    def transform_attributes(self, button: str) -> None:
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

    
    def proxy_attribute(self, button: str) -> None:
        proxy_node: str = cmds.textField(self.textfield_proxy_node, query=True, text=True)
        at: str = cmds.textField(self.textfield_attribute, query=True, text=True)
        attribute.proxy_attribute(cmds.ls(selection=True), proxy_node, at)


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


    def create_ribbon(self, button: str) -> None:
        sub = int(cmds.intSliderGrp(self.intslider_ribbon_sub, query=True, value=True))
        name = cmds.textField(self.textfield_ribbon_name, query=True, text=True)

        if cmds.radioButton(self.radiobutton_ribbon_world, query=True, select=True):
            ribbon.ribbon(sub, name)

        else:
            ribbon.bone_ribbon(*cmds.ls(selection=True), sub=sub)


    def create_rivet(self, button: str) -> None:
        rivet.rivet_mesh_user()
#
#
MainWindow()
