import subprocess

from opcut.doit import _common


__all__ = ['task_jsopcut_clean', 'task_jsopcut_install_deps',
           'task_jsopcut_remove_deps', 'task_jsopcut_build',
           'task_jsopcut_watch', 'task_jsopcut_check']


def task_jsopcut_clean():
    """JsOpcut - clean"""

    return {'actions': [(_common.rm_rf, ['build/jsopcut',
                                         'src_js/opcut/validator.js'])]}


def task_jsopcut_install_deps():
    """JsOpcut - install dependencies"""

    def patch():
        subprocess.Popen(['patch', '-r', '/dev/null', '--forward', '-p0',
                          '-i', 'node_modules.patch'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL).wait()

    return {'actions': ['yarn install --silent',
                        patch]}


def task_jsopcut_remove_deps():
    """JsOpcut - remove dependencies"""

    return {'actions': [(_common.rm_rf, ['node_modules'])]}


def task_jsopcut_build():
    """JsOpcut - build"""

    return {'actions': ['yarn run build'],
            'task_dep': ['jsopcut_install_deps']}


def task_jsopcut_watch():
    """JsOpcut - build on change"""

    return {'actions': ['yarn run watch'],
            'task_dep': ['jsopcut_install_deps']}


def task_jsopcut_check():
    """JsOpcut - check"""

    return {'actions': ['yarn run check'],
            'task_dep': ['jsopcut_install_deps']}
