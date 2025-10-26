from pathlib import Path
from os import open as open_file
from os import remove as remove_file

from aw.utils.subps import process
from aw.utils.util import get_random_str


def _open_file_0600(path: (str, Path), flags):
    return open_file(path, flags, 0o600)


def write_file_0600(file: (str, Path), content: str):
    file = Path(file)
    if not file.parent.is_dir():
        file.parent.mkdir(mode=0o750, parents=True, exist_ok=True)

    mode = 'w'
    if file.is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0600) as _file:
        _file.write(content)


def _open_file_0640(path: (str, Path), flags):
    return open_file(path, flags, 0o640)


def write_file_0640(file: (str, Path), content: str):
    file = Path(file)
    if not file.parent.is_dir():
        file.parent.mkdir(mode=0o750, parents=True, exist_ok=True)

    mode = 'w'
    if file.is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0640) as _file:
        _file.write(content)


def overwrite_and_delete_file(file: (str, Path)):
    if not isinstance(file, Path):
        file = Path(file)

    if not file.is_file():
        return

    for _ in range(3):
        write_file_0600(
            file=file,
            content=get_random_str(),
        )

    remove_file(file)


def rm_dir(path: (str, Path)) -> int:
    return process(f'rm -rf {path}')['rc']
