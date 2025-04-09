#!/usr/bin/env python3

from sys import argv as sys_argv
from sys import path as sys_path
from os import path as os_path

# pylint: disable=C0415


def main():
    try:
        from cli_init import init_cli

    except ModuleNotFoundError:
        sys_path.append(os_path.dirname(os_path.abspath(__file__)))
        from cli_init import init_cli

    init_cli()
    from db import get_db_string
    from aw.utils.debug import log
    log(msg=f"Using DB: {get_db_string()}", level=4, _stderr=True)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys_argv)


if __name__ == '__main__':
    main()
