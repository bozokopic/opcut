from .dist import *  # NOQA
from .libopcut import *  # NOQA

from pathlib import Path
import subprocess

from hat.doit import common
from hat.doit.js import (ESLintConf,
                         run_eslint)
from hat.doit.py import (get_task_build_wheel,
                         get_task_create_pip_requirements,
                         run_flake8)
from hat.doit.c import get_task_clang_format

from . import dist
from . import libopcut


__all__ = ['task_clean_all',
           'task_wheel',
           'task_check',
           'task_ts',
           'task_static',
           'task_node_modules',
           'task_format',
           'task_json_schema_repo',
           'task_version',
           'task_pip_requirements',
           *libopcut.__all__,
           *dist.__all__]


build_dir = Path('build')
man_dir = Path('man')
node_modules_dir = Path('node_modules')
node_modules_patch_path = Path('node_modules.patch')
schemas_dir = Path('schemas')
src_js_dir = Path('src_js')
src_py_dir = Path('src_py')
src_scss_dir = Path('src_scss')
src_static_dir = Path('src_static')

build_py_dir = build_dir / 'py'
ui_dir = src_py_dir / 'opcut/ui'
json_schema_repo_path = src_py_dir / 'opcut/json_schema_repo.json'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [
        build_dir,
        ui_dir,
        json_schema_repo_path,
        *src_py_dir.glob('opcut/_libopcut.*')])]}


def task_wheel():
    """Build wheel"""
    return get_task_build_wheel(
        src_dir=src_py_dir,
        build_dir=build_py_dir,
        platform=common.target_platform,
        data_paths=[(man_dir / 'opcut.1', Path('share/man/man1/opcut.1'))],
        task_dep=['json_schema_repo',
                  'static',
                  'ts',
                  'libopcut'])


def task_check():
    """Check"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_eslint, [src_js_dir, ESLintConf.TS])],
            'task_dep': ['node_modules']}


def task_ts():
    """Build TypeScript"""

    def build(args):
        args = args or []
        subprocess.run(['npx', 'tsc', *args],
                       check=True)

    return {'actions': [build],
            'pos_arg': 'args',
            'task_dep': ['node_modules',
                         'version']}


def task_static():
    """Copy static files"""
    return common.get_task_copy(
        [(src_static_dir, ui_dir),
         (schemas_dir, ui_dir),
         (node_modules_dir / '@hat-open/renderer',
          ui_dir / 'script/@hat-open/renderer'),
         (node_modules_dir / '@hat-open/util',
          ui_dir / 'script/@hat-open/util'),
         (node_modules_dir / 'snabbdom',
          ui_dir / 'script/snabbdom'),
         (node_modules_dir / 'papaparse/LICENSE',
          ui_dir / 'script/papaparse/LICENSE'),
         (node_modules_dir / 'papaparse/README.md',
          ui_dir / 'script/papaparse/README.md'),
         (node_modules_dir / 'papaparse/package.json',
          ui_dir / 'script/papaparse/package.json'),
         (node_modules_dir / 'papaparse/papaparse.js',
          ui_dir / 'script/papaparse/papaparse.js')],
        task_dep=['node_modules'])


def task_node_modules():
    """Install node modules"""

    def patch():
        subprocess.run(['patch', '-u', '-p', '1', '-N',
                        '-i', str(node_modules_patch_path)],
                       stdout=subprocess.DEVNULL)

    return {'actions': ['npm install --silent --progress false',
                        patch]}


def task_format():
    """Format"""
    yield from get_task_clang_format([*Path('src_c').rglob('*.c'),
                                      *Path('src_c').rglob('*.h')])


def task_json_schema_repo():
    """Generate JSON Schema Repository"""
    return common.get_task_json_schema_repo([schemas_dir / 'opcut.yaml'],
                                            json_schema_repo_path)


def task_version():
    """Generate version files"""
    version = common.get_version()
    pyproject_path = Path('pyproject.toml')

    def generate(path, template):
        path.write_text(template.format(version=version))

    for dst_path, template in [(src_js_dir / 'version.ts', _version_ts)]:
        yield {'name': str(dst_path),
               'actions': [(generate, [dst_path, template])],
               'file_dep': [pyproject_path],
               'targets': [dst_path]}


def task_pip_requirements():
    """Create pip requirements"""
    return get_task_create_pip_requirements()


_version_ts = "export default '{version}';\n"
