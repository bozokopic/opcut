from hat.doit import common

DOIT_CONFIG = common.init(python_paths=['src_py'],
                          default_tasks=['build'])

from src_doit import *  # NOQA
