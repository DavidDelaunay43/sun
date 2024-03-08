from maya import cmds, mel
import os

# FUNCTIONS

def get_time_slider_range() -> tuple:

    start_frame: float = cmds.playbackOptions(query = True, minTime = True)
    end_frame: float = cmds.playbackOptions(query = True, maxTime = True)

    return start_frame, end_frame

def convert_abc_to_gpu_cache(alembic_file: str, output_directory: str) -> None:

    cmds.AbcImport(alembic_file, mode = 'import', fitTimeRange = True)
    mesh: str = cmds.rename('simu', alembic_file.split('.')[0])

    if 'moving' in mesh:
        start_frame, end_frame = get_time_slider_range()

    else: # static
        start_frame, end_frame = 0, 0

    gpu_cache_cmd: str = f'gpuCache -startTime {start_frame} -endTime {end_frame} -optimize -optimizationThreshold 40000 -dataFormat ogawa -useBaseTessellation -directory "{output_directory}" -fileName "{mesh}" moving_grains_01;'
    mel.eval(gpu_cache_cmd)

    cmds.delete(mesh)

# CODE

sim_directory: str = r'Z:\06_shot\seq030\sh080\fx\sand\sim'
alembic_files: tuple = (
    'moving_grains_01.abc',
    'moving_grains_02.abc',
    'moving_grains_03.abc',
    'moving_grains_04.abc',
    'moving_grains_05.abc',

    'static_grains_01.abc',
    'static_grains_02.abc',
    'static_grains_03.abc',
    'static_grains_04.abc',
    'static_grains_05.abc'
)

for alembic_file in alembic_files:

    alembic_file_path: str = os.path.join(sim_directory, alembic_file)
    output_directory: str = r'//gandalf/3d4_23_24/COUPDESOLEIL/06_shot/seq030/sh080/fx/sand/gpucache'

    convert_abc_to_gpu_cache(alembic_file, output_directory)
