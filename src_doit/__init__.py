from pathlib import Path
import subprocess
import sys
import tempfile

from hat import json
from hat.doit import common
from hat.doit.py import (build_wheel,
                         run_pytest,
                         run_flake8)
from hat.doit.js import run_eslint

from .c import *  # NOQA
from .dist import *  # NOQA
from . import c
from . import dist


__all__ = ['task_clean_all',
           'task_wheel',
           'task_check',
           'task_test',
           'task_ui',
           'task_deps',
           'task_format',
           'task_json_schema_repo',
           *c.__all__,
           *dist.__all__]


build_dir = Path('build')
src_py_dir = Path('src_py')
src_js_dir = Path('src_js')
src_static_dir = Path('src_static')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')
schemas_dir = Path('schemas')
node_modules_dir = Path('node_modules')

build_py_dir = build_dir / 'py'
ui_dir = src_py_dir / 'opcut/ui'
json_schema_repo_path = src_py_dir / 'opcut/json_schema_repo.json'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir,
                                        ui_dir,
                                        json_schema_repo_path,
                                        src_py_dir / 'opcut/bin'])]}


def task_wheel():
    """Build wheel"""

    def build():
        build_wheel(
            src_dir=src_py_dir,
            dst_dir=build_py_dir,
            name='opcut',
            description='Cutting stock problem optimizer',
            url='https://github.com/bozokopic/opcut',
            license=common.License.GPL3,
            packages=['opcut'],
            console_scripts=['opcut = opcut.main:main'])

    return {'actions': [build],
            'task_dep': ['ui',
                         'json_schema_repo',
                         'c']}


def task_check():
    """Check"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir]),
                        (run_eslint, [src_js_dir])],
            'task_dep': ['deps']}


def task_test():
    """Test"""
    return {'actions': [(common.mkdir_p, [ui_dir]),
                        lambda args: run_pytest(pytest_dir, *(args or []))],
            'pos_arg': 'args',
            'task_dep': ['json_schema_repo']}


def task_ui():
    """Build UI"""

    def build(args):
        args = args or []
        common.rm_rf(ui_dir)
        common.cp_r(src_static_dir, ui_dir)
        common.cp_r(schemas_dir, ui_dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_path = tmpdir / 'webpack.config.js'
            config_path.write_text(_webpack_conf.format(
                src_path=(src_js_dir / 'main.js').resolve(),
                dst_dir=ui_dir.resolve()))
            subprocess.run([str(node_modules_dir / '.bin/webpack'),
                            '--config', str(config_path),
                            *args],
                           check=True)

    return {'actions': [build],
            'pos_arg': 'args',
            'task_dep': ['deps']}


def task_deps():
    """Install dependencies"""
    return {'actions': ['yarn install --silent',
                        f'{sys.executable} -m peru sync']}


def task_format():
    """Format"""
    files = [*Path('src_c').rglob('*.c'),
             *Path('src_c').rglob('*.h')]
    for f in files:
        yield {'name': str(f),
               'actions': [f'clang-format -style=file -i {f}'],
               'file_dep': [f]}


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
                test: /\.scss$/,
                use: [
                    "style-loader",
                    {{
                        loader: "css-loader",
                        options: {{url: false}}
                    }},
                    {{
                        loader: "sass-loader",
                        options: {{sourceMap: true}}
                    }}
                ]
            }}
        ]
    }},
    watchOptions: {{
        ignored: /node_modules/
    }},
    devtool: 'source-map',
    stats: 'errors-only'
}};
"""
