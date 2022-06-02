from pathlib import Path

from hat.doit import common
from hat.doit.c import (get_exe_suffix,
                        CBuild)


__all__ = ['task_c',
           'task_c_obj',
           'task_c_dep']


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

build_c_dir = build_dir / 'c'

platforms = [common.local_platform]
if common.local_platform == common.Platform.LINUX_X86_64:
    platforms.append(common.Platform.WINDOWS_AMD64)

builds = [CBuild(src_paths=[*src_c_dir.rglob('*.c'),
                            deps_dir / 'argparse/argparse.c',
                            deps_dir / 'hat-util/src_c/hat/libc_allocator.c'],
                 build_dir=build_c_dir / platform.name.lower(),
                 platform=platform,
                 cc_flags=['-fPIC', '-O2',
                           f'-I{deps_dir / "jsmn"}',
                           f'-I{deps_dir / "argparse"}',
                           f'-I{deps_dir / "hat-util/src_c"}'],
                 task_dep=['deps'])
          for platform in platforms]

exe_paths = [src_py_dir / (f'opcut/bin/{platform.name.lower()}-'
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
