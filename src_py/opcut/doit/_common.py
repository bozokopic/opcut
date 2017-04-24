import os
import shutil
from pathlib import Path


def mkdir_p(*paths):
    for path in paths:
        os.makedirs(str(Path(path)), exist_ok=True)


def rm_rf(*paths):
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        if p.is_dir():
            shutil.rmtree(str(p), ignore_errors=True)
        else:
            p.unlink()


def cp_r(src, dest):
    src = Path(src)
    dest = Path(dest)
    if src.is_dir():
        shutil.copytree(str(src), str(dest))
    else:
        shutil.copy2(str(src), str(dest))
