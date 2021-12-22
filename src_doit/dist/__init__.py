from pathlib import Path
import subprocess
import zipfile

from hat.doit import common


__all__ = ['task_dist',
           'task_dist_windows',
           'task_dist_container']


package_path = Path(__file__).parent

build_dir = Path('build')
cache_dir = Path('cache')

wheel_dir = build_dir / 'py/dist'
dist_dir = build_dir / 'dist'
dist_windows_dir = dist_dir / f'opcut-{common.get_version()}-windows'
dist_container_dir = dist_dir / f'opcut-{common.get_version()}-container'

win_python_url = 'https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip'  # NOQA
cache_win_python_path = cache_dir / win_python_url.split('/')[-1]


def task_dist():
    """Build distribution"""

    return {'actions': None,
            'task_dep': ['dist_windows',
                         'dist_container']}


def task_dist_windows():
    """Build windows distribution"""

    def build():
        common.rm_rf(dist_windows_dir)
        common.mkdir_p(dist_windows_dir.parent)
        common.cp_r(package_path / 'windows', dist_windows_dir)

        common.mkdir_p(cache_dir)
        if not cache_win_python_path.exists():
            subprocess.run(['curl', '-s',
                            '-o', str(cache_win_python_path),
                            '-L', win_python_url],
                           check=True)

        python_dir = dist_windows_dir / 'python'
        common.mkdir_p(python_dir)
        with zipfile.ZipFile(str(cache_win_python_path)) as f:
            f.extractall(str(python_dir))

        python_lib_path = python_dir / 'python39.zip'
        python_lib_dir = python_dir / 'lib'
        common.mkdir_p(dist_windows_dir / 'python/lib')
        with zipfile.ZipFile(str(python_lib_path)) as f:
            f.extractall(str(python_lib_dir))
        common.rm_rf(python_lib_path)

        (python_dir / 'python39._pth').write_text(
            '..\\packages\n'
            'lib\n'
            '.\n'
            'import site\n'
        )

        packages_dir = dist_windows_dir / 'packages'
        common.mkdir_p(packages_dir)

        packages = [*(str(i) for i in wheel_dir.glob('*.whl'))]
        subprocess.run(['pip', 'install', '-q',
                        '-t', str(packages_dir),
                        '--only-binary=:all:',
                        '--platform', 'win_amd64',
                        *packages],
                       check=True)

        zip_path = dist_dir / f'{dist_windows_dir.name}.zip'
        common.rm_rf(zip_path)
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as f:
            for i in dist_windows_dir.rglob('*'):
                if i.is_dir():
                    continue
                f.write(str(i), str(i.relative_to(dist_windows_dir)))

    return {'actions': [build],
            'task_dep': ['wheel']}


def task_dist_container():
    """Build container distribution"""

    def build():
        common.rm_rf(dist_container_dir)
        common.mkdir_p(dist_container_dir.parent)
        common.cp_r(package_path / 'container', dist_container_dir)

        for i in wheel_dir.glob('*.whl'):
            common.cp_r(i, dist_container_dir / i.name)

        name = f'opcut:{common.get_version()}'
        img_path = dist_dir / f'{dist_container_dir.name}.tar'

        subprocess.run(['podman', 'build', '-q', '-t', name, '.'],
                       cwd=str(dist_container_dir),
                       check=True)

        subprocess.run(['podman', 'save', '-q', '-o', str(img_path), name],
                       check=True)

    return {'actions': [build],
            'task_dep': ['wheel']}
