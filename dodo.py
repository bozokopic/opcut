import sys
import os

sys.path += ['src_py']

os.environ['PYTHONPATH'] = os.pathsep.join(map(
    os.path.abspath, ['src_py']))

DOIT_CONFIG = {
    'backend': 'sqlite3',
    'default_tasks': ['dist_build'],
    'verbosity': 2}

from opcut.doit.main import *  # NOQA
