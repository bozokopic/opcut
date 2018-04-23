import os
import yaml
from pathlib import Path
from doit.action import CmdAction

from opcut.doit import _common


__all__ = ['task_pyopcut_clean', 'task_pyopcut_build', 'task_pyopcut_check',
           'task_pyopcut_gen', 'task_pyopcut_gen_json_validator']


def task_pyopcut_clean():
    """PyOpcut - clean"""

    return {'actions': [(_common.rm_rf, ['build/pyopcut',
                                         'src_py/opcut/json_validator.py'])]}


def task_pyopcut_build():
    """PyOpcut - build"""

    generated_files = {Path('src_py/opcut/json_validator.py')}

    def compile(src_path, dst_path):
        _common.mkdir_p(dst_path.parent)
        _common.cp_r(src_path, dst_path)

    def create_subtask(src_path):
        dst_path = Path('build/pyopcut') / src_path.relative_to('src_py')
        return {'name': str(src_path),
                'actions': [(compile, [src_path, dst_path])],
                'file_dep': [src_path],
                'targets': [dst_path]}

    for src_path in generated_files:
        yield create_subtask(src_path)

    for dirpath, dirnames, filenames in os.walk('src_py'):
        for i in ['__pycache__', 'doit']:
            if i in dirnames:
                dirnames.remove(i)
        for i in filenames:
            src_path = Path(dirpath) / i
            if src_path not in generated_files:
                yield create_subtask(src_path)


def task_pyopcut_check():
    """PyOpcut - run flake8"""

    return {'actions': [CmdAction('python -m flake8 .', cwd='src_py')]}


def task_pyopcut_gen():
    """PyOpcut - generate additional python modules"""

    return {'actions': None,
            'task_dep': ['pyopcut_gen_json_validator']}


def task_pyopcut_gen_json_validator():
    """PyOpcut - generate json validator"""

    schema_files = list(Path('schemas_json').glob('**/*.yaml'))
    output_file = Path('src_py/opcut/json_validator.py')

    def parse_schemas():
        schemas = {}
        for schema_file in schema_files:
            with open(schema_file, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data['id'] in schemas:
                    raise Exception("duplicate schema id " + data['id'])
                schemas[data['id']] = data
        return schemas

    def generate_output():
        schemas = parse_schemas()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(
                '# pylint: skip-file\n'
                'import jsonschema\n\n\n'
                '_schemas = {schemas}  # NOQA\n\n\n'
                'def validate(data, schema_id):\n'
                '    """ Validate data with JSON schema\n\n'
                '    Args:\n'
                '       data: validated data\n'
                '       schema_id (str): JSON schema identificator\n\n'
                '    Raises:\n'
                '       Exception: validation fails\n\n'
                '    """\n'
                '    base_uri = schema_id.split("#")[0] + "#"\n'
                '    resolver = jsonschema.RefResolver(\n'
                '        base_uri=base_uri,\n'
                '        referrer=_schemas[base_uri],\n'
                '        store=_schemas,\n'
                '        cache_remote=False)\n'
                '    jsonschema.validate(\n'
                '        instance=data,\n'
                '        schema=resolver.resolve(schema_id)[1],\n'
                '        resolver=resolver)\n'.format(schemas=schemas))

    return {'actions': [generate_output],
            'file_dep': schema_files,
            'targets': [output_file]}
