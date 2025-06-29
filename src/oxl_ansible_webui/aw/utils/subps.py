from pathlib import Path
from os import environ
from functools import cache

from oxl_utils.ps import process as oxl_utils_process

from aw.utils.debug import log
from aw.settings import BASE_DIR
from aw.config.environment import AW_ENV_VARS_SECRET, AW_ENV_VARS


# pylint: disable=R0914
def process(
        cmd: (str, list), timeout_sec: int = None, shell: bool = False,
        cwd: Path = BASE_DIR, env: dict = None, pass_env_secrets: bool = False, stdin: str = None,
) -> dict:
    cmd_str = cmd
    if isinstance(cmd, list):
        cmd_str = ' '.join(cmd)

    log(msg=f"Executing command: '{cmd_str}'", level=6)

    # merge provided env with current env and hide secrets
    env_full = environ.copy()
    if env is not None:
        env_full = {**env_full, **env}

    if not pass_env_secrets:
        for secret_var in AW_ENV_VARS_SECRET:
            for secret_env_var in AW_ENV_VARS[secret_var]:
                if secret_env_var in env_full:
                    env_full.pop(secret_env_var)

    return oxl_utils_process(
        cmd=cmd, timeout_sec=timeout_sec, shell=shell, cwd=cwd, env=env_full, stdin=stdin,
        env_inherit=False, empty_none=False, timeout_shell=False,
    )


@cache
def process_cache(
        cmd: str, timeout_sec: int = None, shell: bool = False,
        cwd: Path = BASE_DIR, env: dict = None,
) -> dict:
    # read-only commands which results can be cached
    return process(cmd=cmd.split(' '), timeout_sec=timeout_sec, shell=shell, cwd=cwd, env=env)
