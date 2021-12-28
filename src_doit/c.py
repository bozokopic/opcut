from pathlib import Path

from hat.doit.c import (local_platform,
                        get_exe_suffix,
                        Platform,
                        CBuild)


__all__ = ['task_c',
           'task_c_obj',
           'task_c_dep']


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

build_c_dir = build_dir / 'c'

platforms = [local_platform]
if local_platform == Platform.LINUX:
    platforms.append(Platform.WINDOWS)

builds = [CBuild(src_paths=[*src_c_dir.rglob('*.c'),
                            *(deps_dir / 'argparse').rglob('*.c')],
                 build_dir=build_c_dir / platform.name.lower(),
                 platform=platform,
                 cc_flags=['-fPIC', '-O2',
                           f'-I{deps_dir / "jsmn"}',
                           f'-I{deps_dir / "argparse"}'],
                 task_dep=['deps'])
          for platform in platforms]

exe_paths = [src_py_dir / (f'opcut/{platform.name.lower()}-'
                           f'opcut-calculate'
                           f'{get_exe_suffix(platform)}')
             for platform in platforms]


def task_c():
    """Build native app"""
    for build, exe_path in zip(builds, exe_paths):
        yield from build.get_task_exe(exe_path)


def task_c_obj():
    """Build .o files"""
    for build in builds:
        yield from build.get_task_objs()


def task_c_dep():
    """Build .d files"""
    for build in builds:
        yield from build.get_task_deps()
