from ..utils.imports import *

class ScaleControlUi:

    def __init__(self):

        self.title = "Scale Controls"
        if cmds.workspaceControl(self.title, exists = True):
            cmds.workspaceControl(self.title, e=1, floating = True) 
            cmds.deleteUI(self.title, window = True)

        self.wspace = cmds.workspaceControl(self.title, retain = False, floating = False, mh = 100, mw = 400)

        #UI LAYOUT 
        self.root = cmds.formLayout()
        cmds.columnLayout()
        cmds.separator(h=10, st="in")
        self.value = cmds.floatSliderGrp(l = "Scale value", f=1, v=1, fmn=0.1, fmx=2, min=0.1, max=2, cc= self.scale_control)

        self.nodes = cmds.ls(sl=1)
        om.MGlobal.displayInfo(f"{self.nodes}")

    def scale_control(self, value: float):

        value = cmds.floatSliderGrp(self.value, q = 1, v = 1)
        om.MGlobal.displayInfo(f"{value}")

        for ctrl in self.nodes:

            om.MGlobal.displayInfo(f"Scale {ctrl}")
            cvs = cmds.getAttr(f"{ctrl}.spans")
            om.MGlobal.displayInfo(f"{cvs}")
            cmds.select(f"{ctrl}.cv[0:{cvs-1}]")
            cmds.scale(value, value, value, ws=1)

        cmds.select(cl=1)
        cmds.floatSliderGrp(self.value, e=1, v=1)