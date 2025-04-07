#!/usr/bin/env python3

from os import environ
from os import path as os_path
from sys import argv as sys_argv
from sys import exit as sys_exit
from sys import path as sys_path


def entrypoint():
    # pylint: disable=C0415,E0401
    try:
        from main import main

    except ModuleNotFoundError:
        sys_path.append(os_path.dirname(os_path.abspath(__file__)))
        from main import main

    if len(sys_argv) > 1:
        if sys_argv[1] in ['--version', '-v']:
            from cli_init import init_cli
            from cli import _print_version
            init_cli()
            _print_version()
            sys_exit(0)

        elif sys_argv[1] in ['--config', '-c']:
            from aw.config.hardcoded import ENV_KEY_CONFIG
            environ[ENV_KEY_CONFIG] = sys_argv[2]

    from aw.config.main import VERSION
    print(f'Ansible-WebUI Version {VERSION}')
    main()


if __name__ == '__main__':
    entrypoint()
