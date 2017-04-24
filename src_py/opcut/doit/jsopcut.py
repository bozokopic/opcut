import json
import yaml
import subprocess
from pathlib import Path

from opcut.doit import _common


__all__ = ['task_jsopcut_clean', 'task_jsopcut_install_deps',
           'task_jsopcut_remove_deps', 'task_jsopcut_gen',
           'task_jsopcut_gen_validator', 'task_jsopcut_build',
           'task_jsopcut_watch']


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

    return {'actions': ['yarn install',
                        patch]}


def task_jsopcut_remove_deps():
    """JsOpcut - remove dependencies"""

    return {'actions': [(_common.rm_rf, ['node_modules', 'yarn.lock'])]}


def task_jsopcut_gen():
    """JsOpcut - generate additional JavaScript modules"""

    return {'actions': None,
            'task_dep': ['jsopcut_gen_validator']}


def task_jsopcut_gen_validator():
    """JsOpcut - generate json validator"""

    schema_files = list(Path('schemas_json').glob('**/*.yaml'))
    output_file = Path('src_js/opcut/validator.js')

    def parse_schemas():
        for schema_file in schema_files:
            with open(schema_file, encoding='utf-8') as f:
                yield yaml.safe_load(f)

    def generate_output():
        schemas_json = json.dumps(list(parse_schemas()), indent=4)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(
                'import tv4 from "tv4";\n\n\n' +
                schemas_json + '.forEach(i => tv4.addSchema(i.id, i));\n\n\n' +
                'export function validate(data, schemaId) {\n' +
                '    return tv4.validate(data, tv4.getSchema(schemaId));\n' +
                '}\n')

    return {'actions': [generate_output],
            'file_dep': schema_files,
            'targets': [output_file]}


def task_jsopcut_build():
    """JsOpcut - build"""

    return {'actions': ['yarn run build'],
            'task_dep': ['jsopcut_install_deps', 'jsopcut_gen']}


def task_jsopcut_watch():
    """JsOpcut - build on change"""

    return {'actions': ['yarn run watch'],
            'task_dep': ['jsopcut_install_deps', 'jsopcut_gen']}
