import ast
from maya import cmds

def string_to_list(string: str) -> list:
    """
    """
    return ast.literal_eval(string)

def get_selection():
    selection = cmds.ls(selection = True)
    if len(selection) == 0:
        return ""
    else:
        return selection