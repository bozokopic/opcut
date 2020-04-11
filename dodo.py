from pathlib import Path
import datetime
import os
import shutil
import subprocess
import sys

import packaging.version


DOIT_CONFIG = {'backend': 'sqlite3',
               'default_tasks': ['dist'],
               'verbosity': 2}


pythonpath = os.environ.get('PYTHONPATH')
src_py_path = str(Path('src_py').resolve())

sys.path += [src_py_path]
if pythonpath:
    os.environ['PYTHONPATH'] = f'{src_py_path}{os.pathsep}{pythonpath}'
else:
    os.environ['PYTHONPATH'] = src_py_path


build_dir = Path('build')
dist_dir = Path('dist')
py_build_dir = build_dir / 'py'
js_build_dir = build_dir / 'js'


def task_clean_all():
    """Clean all"""
    return {'actions': [f'rm -rf {build_dir}',
                        f'rm -rf {dist_dir}']}


def task_check():
    """Run linters"""
    def flake8():
        subprocess.run(['python', '-m', 'flake8', '.'],
                       cwd='src_py',
                       check=True)

    return {'actions': [flake8,
                        'yarn run --silent check_js',
                        'yarn run --silent check_sass'],
            'task_dep': ['js_deps']}


def task_js_deps():
    """Install js dependencies"""
    return {'actions': ['yarn install --silent']}


def task_js_build():
    """Build js"""
    return {'actions': ['yarn run --silent build'],
            'task_dep': ['js_deps']}


def task_js_watch():
    """Build js on change"""

    return {'actions': ['yarn run --silent watch'],
            'task_dep': ['js_deps']}


def task_py_build():
    """Build py"""
    def mappings():
        src_py_dir = Path('src_py')
        for i in (src_py_dir / 'opcut').rglob('*.py'):
            yield i, dst_dir / i.relative_to(src_py_dir)

        src_json_dir = Path('schemas_json')
        for i in src_json_dir.rglob('*.yaml'):
            yield i, (dst_dir / 'opcut/schemas_json'
                              / i.relative_to(src_json_dir))

        for i in js_build_dir.rglob('*'):
            if i.is_dir():
                continue
            yield i, (dst_dir / 'opcut/ui'
                              / i.relative_to(js_build_dir))

    dst_dir = py_build_dir
    setup_path = dst_dir / 'setup.py'
    manifest_path = dst_dir / 'MANIFEST.in'
    src_paths = list(src_path for src_path, _ in mappings())
    dst_paths = [setup_path, *(dst_path for _, dst_path in mappings())]
    return {'actions': [(_copy_files, [mappings]),
                        (_create_manifest, [manifest_path, mappings]),
                        (_create_setup_py, [setup_path])],
            'file_dep': src_paths,
            'targets': dst_paths,
            'task_dep': ['js_build']}


def task_dist():
    """Create distribution"""
    def dist():
        dist_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['python', 'setup.py', '-q', 'bdist_wheel',
                        '--dist-dir', str(dist_dir.resolve())],
                       cwd=str(py_build_dir),
                       check=True)

    return {'actions': [dist],
            'task_dep': ['py_build']}


def _create_setup_py(path):
    version = _get_version()
    readme = _get_readme()
    dependencies = ['aiohttp',
                    'pycairo',
                    'hat-util']
    entry_points = {'console_scripts': ['opcut = opcut.main:main']}
    options = {'bdist_wheel': {'python_tag': 'cp38',
                               'py_limited_api': 'cp38',
                               'plat_name': 'any'}}
    classifiers = ['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: GPLv3 License']
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"from setuptools import setup\n\n\n"
                f"readme = r\"\"\"\n{readme}\n\"\"\"\n\n"
                f"setup(name='opcut',\n"
                f"      version={repr(version)},\n"
                f"      description='Cutting stock problem optimizer',\n"
                f"      long_description=readme,\n"
                f"      long_description_content_type='text/x-rst',\n"
                f"      url='https://github.com/bozokopic/opcut',\n"
                f"      author='Bozo Kopic',\n"
                f"      author_email='bozo.kopic@gmail.com',\n"
                f"      license='GPLv3',\n"
                f"      packages=['opcut'],\n"
                f"      include_package_data=True,\n"
                f"      install_requires={repr(dependencies)},\n"
                f"      python_requires='>=3.8',\n"
                f"      zip_safe=False,\n"
                f"      classifiers={repr(classifiers)},\n"
                f"      options={repr(options)},\n"
                f"      entry_points={repr(entry_points)})\n")


def _copy_files(mappings):
    for src_path, dst_path in mappings():
        if not dst_path.parent.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(src_path), str(dst_path))


def _create_manifest(path, mappings):
    with open(path, 'w', encoding='utf-8') as f:
        for _, i in mappings():
            f.write(f"include {i.relative_to(path.parent)}\n")


def _get_version():
    with open('VERSION', encoding='utf-8') as f:
        version_str = f.read().strip()
    if version_str.endswith('dev'):
        version_str += datetime.datetime.now().strftime("%Y%m%d")
    version = packaging.version.Version(version_str)
    return version.public


def _get_readme():
    with open('README.rst', encoding='utf-8') as f:
        return f.read().strip()
