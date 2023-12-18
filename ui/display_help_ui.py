from ..utils.imports import *

class DisplayHelpUI:
    
    def __init__(self, func):
        
        self.func = func
        self._init_ui()
        
    def _init_ui(self):
        
        window = cmds.window(title="Doc", widthHeight=(1000, 600))
        cmds.columnLayout(adjustableColumn=True)
        output_field = cmds.scrollField(wordWrap=True, editable=False, height=600, font = "plainLabelFont", fontPointSize = 16)
        cmds.showWindow(window)
        
        cmds.scrollField(output_field, edit = True, text = "")
        doc = self.func.__doc__
        cmds.scrollField(output_field, edit = True, insertText = doc)
