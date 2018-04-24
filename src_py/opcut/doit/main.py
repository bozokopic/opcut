from doit.action import CmdAction

from opcut.doit import _common

import opcut.doit.pyopcut
import opcut.doit.jsopcut
from opcut.doit.pyopcut import *  # NOQA
from opcut.doit.jsopcut import *  # NOQA


__all__ = (['task_clean_all', 'task_gen_all', 'task_dist_build',
            'task_dist_clean'] +
           opcut.doit.pyopcut.__all__ +
           opcut.doit.jsopcut.__all__)


def task_clean_all():
    """Clean all"""

    return {'actions': [(_common.rm_rf, ['build', 'dist'])],
            'task_dep': ['pyopcut_clean',
                         'jsopcut_clean',
                         'dist_clean']}


def task_gen_all():
    """Generate all"""

    return {'actions': None,
            'task_dep': ['pyopcut_gen',
                         'jsopcut_gen']}


def task_check_all():
    """Check all"""

    return {'actions': None,
            'task_dep': ['pyopcut_check']}


def task_dist_clean():
    """Distribution - clean"""

    return {'actions': [(_common.rm_rf, ['dist'])]}


def task_dist_build():
    """Distribution - build (DEFAULT)"""

    def generate_setup_py():
        with open('requirements.txt', encoding='utf-8') as f:
            dependencies = [i.strip() for i in f.readlines() if i.strip()]
        with open('build/dist/setup.py', 'w', encoding='utf-8') as f:
            f.write(_setup_py.format(
                version='0.1.0',
                dependencies=repr(dependencies)))

    return {'actions': [
                (_common.rm_rf, ['dist', 'build/dist']),
                (_common.cp_r, ['build/pyopcut', 'build/dist']),
                (_common.cp_r, ['build/jsopcut', 'build/dist/opcut/web']),
                (_common.cp_r, ['README.rst', 'build/dist/README.rst']),
                generate_setup_py,
                CmdAction('python setup.py bdist_wheel --dist-dir ../../dist',
                          cwd='build/dist')],
            'task_dep': [
                'gen_all',
                'pyopcut_build',
                'jsopcut_build']}


_setup_py = r"""
from setuptools import setup
setup(
    name='opcut',
    version='{version}',
    description='Cutting stock problem optimizer',
    url='https://github.com/bozokopic/opcut',
    author='Bozo Kopic',
    author_email='bozo.kopic@gmail.com',
    license='GPLv3',
    python_requires='>=3.5',
    zip_safe=False,
    packages=['opcut'],
    package_data={{
        'opcut': ['web/*', 'web/fonts/*']
    }},
    install_requires={dependencies},
    entry_points={{
        'console_scripts': [
            'opcut = opcut.main:main'
        ]
    }}
)
"""
