from pathlib import Path
import os

from hat.doit import common
from hat.doit.c import (get_lib_suffix,
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
if common.local_platform == common.Platform.LINUX_GNU_X86_64:
    if 'SKIP_CROSS_COMPILE' not in os.environ:
        platforms.append(common.Platform.WINDOWS_AMD64)

cc_flags = ['-fPIC', '-O2']
# cc_flags = ['-fPIC', '-O0', '-ggdb']

builds = [CBuild(src_paths=[*src_c_dir.rglob('*.c')],
                 build_dir=build_c_dir / platform.name.lower(),
                 platform=platform,
                 cc_flags=cc_flags)
          for platform in platforms]

lib_paths = [src_py_dir / (f'opcut/_libopcut{get_lib_suffix(platform)}')
             for platform in platforms]


def task_c():
    """Build native libs"""
    for build, lib_path in zip(builds, lib_paths):
        yield from build.get_task_lib(lib_path)


def task_c_obj():
    """Build .o files"""
    for build in builds:
        yield from build.get_task_objs()


def task_c_dep():
    """Build .d files"""
    for build in builds:
        yield from build.get_task_deps()
