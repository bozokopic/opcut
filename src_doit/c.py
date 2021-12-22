from pathlib import Path

from hat.doit.c import (exe_suffix,
                        CBuild)


__all__ = ['task_c',
           'task_c_obj',
           'task_c_dep']


build_dir = Path('build')
src_c_dir = Path('src_c')
deps_dir = Path('deps')

build_c_dir = build_dir / 'c'
exe_path = build_c_dir / f'opcut-calculate{exe_suffix}'


def task_c():
    """Build native app"""
    return _build.get_task_exe(exe_path)


def task_c_obj():
    """Build .o files"""
    yield from _build.get_task_objs()


def task_c_dep():
    """Build .d files"""
    yield from _build.get_task_deps()


_build = CBuild(
    src_paths=[*src_c_dir.rglob('*.c')],
    src_dir=src_c_dir,
    build_dir=build_c_dir,
    cc_flags=['-fPIC', '-O2', f'-I{deps_dir / "jsmn"}'],
    task_dep=['deps'])
