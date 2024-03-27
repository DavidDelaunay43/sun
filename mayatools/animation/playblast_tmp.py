from maya import cmds
import os
from subprocess import Popen


def get_sound_node() -> str:
    audio_nodes = cmds.ls(type="audio")
    if audio_nodes:
        return audio_nodes[0]


def list_existing_files(directory: str, file_basename: str) -> list:
    """
    List existing files in the specified directory that contain the given file basename.

    Parameters
    ----------
    directory : str
        The directory in which to search for existing files.
    file_basename : str
        The base name of the files to search for.

    Returns
    -------
    list
        A list of existing files in the directory that contain the specified file basename,
        sorted in lexicographical order.

    Examples
    --------
    >>> list_existing_files("/path/to/directory", "example")
    ['example_file1.txt', 'example_file2.txt', 'example_file3.txt']
    """

    files = os.listdir(directory)
    existing_files = []
    for file in files:
        if file_basename in file:
            existing_files.append(file)

    existing_files.sort()
    return existing_files


def open_movie_file(movie_file_path: str) -> None:
    """
    Open a video file using the Keyframe Pro application.

    Parameters
    ----------
    movie_file_path : str
        The path to the video file to open.

    Returns
    -------
    None

    Notes
    -----
    This function utilizes the Keyframe Pro application to open a video file.
    Make sure Keyframe Pro is installed on your system.

    Examples
    --------
    >>> open_movie_file("path/to/my_video_file.mp4")
    """

    APP_DIR: str = r"C:\Program Files\Keyframe Pro\bin\KeyframePro.exe"
    command = [APP_DIR, movie_file_path]
    Popen(command)


def playblast():

    file_path: str = cmds.file(query=True, sceneName=True)

    anim_directory: str = os.path.dirname(os.path.dirname(file_path))
    movies_directory: str = os.path.join(anim_directory, "movies")
    if not os.path.exists(movies_directory):
        os.mkdir(movies_directory)

    file_basename: str = os.path.basename(file_path).split("E")[0] + "E"

    existing_files = list_existing_files(movies_directory, file_basename)
    print(existing_files, "EXISTING FILES")

    increment: int = 1
    if existing_files:
        increment = len(existing_files) + 1

    movie_file_name: str = f"{file_basename}_{increment:03}.mov"
    movie_file_path: str = os.path.join(movies_directory, movie_file_name)
    movie_file_path = movie_file_path.replace("\\", "/")

    sound_node: str = get_sound_node()
    if sound_node:
        print(
            f"cmds.playblast(format = 'qt', sound = {sound_node}, filename = {movie_file_path}, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])"
        )
        cmds.playblast(
            format="qt",
            sound=sound_node,
            filename=movie_file_path,
            sequenceTime=False,
            clearCache=True,
            viewer=True,
            showOrnaments=False,
            offScreen=True,
            framePadding=4,
            percent=100,
            compression="H.264",
            quality=100,
            widthHeight=[1998, 1080],
        )

    else:
        print(
            f"cmds.playblast(format = 'qt', filename = {movie_file_path}, sequenceTime = False, clearCache = True, viewer = True, showOrnaments = False, offScreen = True, framePadding = 4, percent = 100, compression = 'H.264', quality = 100, widthHeight = [1998, 1080])"
        )
        cmds.playblast(
            format="qt",
            filename=movie_file_path,
            sequenceTime=False,
            clearCache=True,
            viewer=True,
            showOrnaments=False,
            offScreen=True,
            framePadding=4,
            percent=100,
            compression="H.264",
            quality=100,
            widthHeight=[1998, 1080],
        )

    open_movie_file(movie_file_path)


playblast()
