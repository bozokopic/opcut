
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


def task_dist_clean():
    """Distribution - clean"""

    return {'actions': [(_common.rm_rf, ['dist'])]}


def task_dist_build():
    """Distribution - build (DEFAULT)"""

    return {'actions': [(_common.mkdir_p, ['dist'])],
            'task_dep': [
                'gen_all',
                'pyopcut_build',
                'jsopcut_build']}
