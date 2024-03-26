from maya import cmds
import os

def get_sound_node() -> str:
    audio_nodes = cmds.ls(type = 'audio')
    if audio_nodes:
        return audio_nodes[0]
    
def list_existing_files(directory: str, file_basename: str) -> list:
    files = os.listdir(directory)
    existing_files = []
    for file in files:
        if file_basename in file:
            existing_files.append(file)

    existing_files.sort()
    return existing_files

def playblast():

    file_path: str = cmds.file(query = True, sceneName = True)

    anim_directory: str = os.path.dirname(os.path.dirname(file_path))
    movies_directory: str = os.path.join(anim_directory, 'movies')
    if not os.path.exists(movies_directory):
        os.mkdir(movies_directory)

    file_basename: str = os.path.basename(file_path).split('E')[0] + 'E'

    existing_files = list_existing_files(movies_directory, file_basename)
    print(existing_files, 'EXISTING FILES')

    increment: int = 1
    if existing_files:
        increment = len(existing_files) + 1

    movie_file_name: str = f'{file_basename}_{increment:03}.mov'
    movie_file_path: str = os.path.join(movies_directory, movie_file_name)
    movie_file_path = movie_file_path.replace('\\', '/')

    sound_node: str = get_sound_node()
    if sound_node:
        print(f"cmds.playblast(format = 'qt', sound = {sound_node}, filename = {movie_file_path}, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])")
        cmds.playblast(format = 'qt', sound = sound_node, filename = movie_file_path, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])

    else:
        print(f"cmds.playblast(format = 'qt', filename = {movie_file_path}, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])")
        cmds.playblast(format = 'qt', filename = movie_file_path, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])

playblast()
