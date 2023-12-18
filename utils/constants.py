import os

def find_package_path(package_name: str):
    """
    """
    
    current_path = os.path.abspath(__file__)
    
    while current_path:
        current_dir, dirname = os.path.split(current_path)
        if dirname == package_name:
            return current_path
        
        current_path = current_dir
 

PACKAGE_NAME = "sun"    
PACKAGE_PATH = find_package_path(PACKAGE_NAME)
USERNAME = f'{os.getenv("USERNAME")}'
LOG_PATH = os.path.join(PACKAGE_PATH, "logs")
ICON_PATH = os.path.join(PACKAGE_PATH, "icons")
STYLE_PATH = os.path.join(PACKAGE_PATH, "ui", "styles")