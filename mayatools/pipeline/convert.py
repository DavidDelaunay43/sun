from maya import cmds, mel
from maya.api import OpenMaya as om
import os

# FUNCTIONS


def get_time_slider_range() -> tuple:

    start_frame: float = cmds.playbackOptions(query=True, minTime=True)
    end_frame: float = cmds.playbackOptions(query=True, maxTime=True)

    return start_frame, end_frame


def convert_abc_to_gpu_cache(alembic_file_path: str, output_directory: str) -> None:

    alembic_file: str = os.path.basename(alembic_file_path)
    cmds.AbcImport(alembic_file_path, mode="import", fitTimeRange=True)
    om.MGlobal.displayInfo(f"Import alembic file : {alembic_file_path}")
    mesh: str = cmds.rename("simu", alembic_file.split(".")[0])
    om.MGlobal.displayInfo(f"Mesh name : {mesh}")

    if "moving" in mesh:
        start_frame, end_frame = get_time_slider_range()

    else:  # static
        start_frame, end_frame = 0, 0

    gpu_cache_cmd: str = (
        f'gpuCache -startTime {start_frame} -endTime {end_frame} -optimize -optimizationThreshold 40000 -dataFormat ogawa -useBaseTessellation -directory "{output_directory}" -fileName "{mesh}" {mesh};'
    )
    mel.eval(gpu_cache_cmd)
    om.MGlobal.displayInfo(f"Export {mesh} to GPU Cache")

    cmds.delete(mesh)
    om.MGlobal.displayInfo(f"Delete mesh : {mesh}")


# CODE

sim_directory: str = (
    r"//gandalf/3d4_23_24/COUPDESOLEIL/06_shot/seq030/sh080/fx/sand/sim"
)
alembic_files: tuple = (
    "static_grains_02.abc",
    "static_grains_03.abc",
    "static_grains_04.abc",
)

for i, alembic_file in enumerate(alembic_files):

    alembic_file_path: str = os.path.join(sim_directory, alembic_file)
    output_directory: str = (
        r"//gandalf/3d4_23_24/COUPDESOLEIL/06_shot/seq030/sh080/fx/sand/gpucache"
    )

    convert_abc_to_gpu_cache(alembic_file_path, output_directory)

    om.MGlobal.displayInfo(f"{i+1} / {len(alembic_files)}")
