from pathlib import Path

from hat.doit import common
from hat.doit.c import (get_lib_suffix,
                        CBuild)


__all__ = ['task_libopcut',
           'task_libopcut_obj',
           'task_libopcut_dep',
           'task_libopcut_cleanup']


build_dir = Path('build')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

libopcut_path = src_py_dir / f'opcut/_libopcut{get_lib_suffix()}'

c_flags = ['-fPIC', '-O2']
# cc_flags = ['-fPIC', '-O0', '-ggdb']

build = CBuild(src_paths=[*src_c_dir.rglob('*.c')],
               build_dir=(build_dir / 'libopcut' /
                          common.target_platform.name.lower()),
               c_flags=c_flags,
               task_dep=['libopcut_cleanup'])


def task_libopcut():
    """Build libopcut"""
    return build.get_task_lib(libopcut_path)


def task_libopcut_obj():
    """Build libopcut .o files"""
    return build.get_task_objs()


def task_libopcut_dep():
    """Build libopcut .d files"""
    return build.get_task_deps()


def task_libopcut_cleanup():
    """Cleanup libopcut"""

    def cleanup():
        for path in libopcut_path.parent.glob('_libopcut.*'):
            if path == libopcut_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}
