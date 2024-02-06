from .dist import *  # NOQA
from .libopcut import *  # NOQA

from pathlib import Path
import subprocess
import tempfile

from hat import json
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
           'task_ui',
           'task_scss',
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
                  'ui',
                  'libopcut'])


def task_check():
    """Check"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_eslint, [src_js_dir, ESLintConf.TS])],
            'task_dep': ['node_modules']}


def task_ui():
    """Build UI"""

    def build(args):
        args = args or []

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_path = tmpdir / 'webpack.config.js'
            config_path.write_text(_webpack_conf.format(
                src_path=(src_js_dir / 'main.ts').resolve(),
                dst_dir=ui_dir.resolve()))
            subprocess.run([str(node_modules_dir / '.bin/webpack'),
                            '--config', str(config_path),
                            *args],
                           check=True)

    return {'actions': [build],
            'pos_arg': 'args',
            'task_dep': ['node_modules',
                         'version',
                         'static',
                         'scss']}


def task_scss():
    """Build SCSS"""

    def build(args):
        args = args or []
        subprocess.run([str(node_modules_dir / '.bin/sass'),
                        '--no-source-map',
                        *args,
                        f'{src_scss_dir}:{ui_dir}'],
                       check=True)

    return {'actions': [build],
            'pos_arg': 'args',
            'task_dep': ['node_modules']}


def task_static():
    """Copy static files"""
    for src_dir, dst_dir in [(src_static_dir, ui_dir),
                             (schemas_dir, ui_dir)]:
        for src_path in src_dir.rglob('*'):
            if not src_path.is_file():
                continue

            dst_path = dst_dir / src_path.relative_to(src_dir)

            yield {'name': str(dst_path),
                   'actions': [(common.mkdir_p, [dst_path.parent]),
                               (common.cp_r, [src_path, dst_path])],
                   'file_dep': [src_path],
                   'targets': [dst_path]}


def task_node_modules():
    """Install node modules"""

    def patch():
        subprocess.run(
            ['sed', '-i',
             r's/^import { h } from ".\/h"\;$/import { h } from ".\/h.js"\;/',
             str(node_modules_dir / 'snabbdom/build/jsx.js')],
            check=True)

    return {'actions': ['yarn install --silent',
                        patch]}


def task_format():
    """Format"""
    yield from get_task_clang_format([*Path('src_c').rglob('*.c'),
                                      *Path('src_c').rglob('*.h')])


def task_json_schema_repo():
    """Generate JSON Schema Repository"""
    src_paths = [schemas_dir / 'opcut.yaml']

    def generate():
        repo = json.SchemaRepository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, json_schema_repo_path, indent=None)

    return {'actions': [generate],
            'file_dep': src_paths,
            'targets': [json_schema_repo_path]}


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


_webpack_conf = r"""
module.exports = {{
    mode: 'none',
    entry: '{src_path}',
    output: {{
        filename: 'main.js',
        path: '{dst_dir}'
    }},
    module: {{
        rules: [
            {{
                test: /\.ts$/,
                use: [
                    {{
                        loader: 'ts-loader',
                        options: {{
                            compilerOptions: {{
                                sourceMap: true
                            }}
                        }}
                    }}
                ]
            }}
        ]
    }},
    resolve: {{
        extensions: ['.ts', '.js']
    }},
    watchOptions: {{
        ignored: /node_modules/
    }},
    devtool: 'source-map',
    stats: 'errors-only'
}};
"""
