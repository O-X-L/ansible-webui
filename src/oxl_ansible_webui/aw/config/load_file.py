from os import environ
from pathlib import Path
from sys import exit as sys_exit

from yaml import safe_load as yaml_load
from yaml import YAMLError

from aw.config.main import config
from aw.utils.debug import log_warn, log, log_error
from aw.config.hardcoded import ENV_KEY_CONFIG, MIN_SECRET_LEN
from aw.config.environment import AW_ENV_VARS_REV


def load_config_file():
    # read config file and write settings into env-vars
    if ENV_KEY_CONFIG not in environ:
        return

    config_file = environ[ENV_KEY_CONFIG]

    if not Path(config_file).is_file():
        log_warn(
            f"The provided config-file was not found or unreadable: {config_file}",
            _stderr=True,
        )
        environ[ENV_KEY_CONFIG] = '0'
        return

    log(msg=f"Using config-file: {config_file}", level=4, _stderr=True)

    with open(config_file, 'r', encoding='utf-8') as _config:
        try:
            yaml_config = yaml_load(_config.read())
            if not isinstance(yaml_config, dict):
                raise ValueError('Content is not a dictionary')

            for setting, value in yaml_config.items():
                if setting.startswith('AW_'):
                    setting_env = setting

                else:
                    setting_env = f'AW_{setting.upper()}'

                if setting_env not in AW_ENV_VARS_REV:
                    log_warn(msg=f"Provided setting is invalid: {setting}", _stderr=True)
                    continue

                if isinstance(value, dict):
                    environ[setting_env] = setting

                elif isinstance(value, list):
                    environ[setting_env] = ','.join(value)

                else:
                    environ[setting_env] = str(value)

        except (YAMLError, ValueError) as err:
            log_warn(f"The provided config-file could not be loaded: {config_file} - {err}", _stderr=True)


def check_for_bad_config():
    if 'AW_SECRET' not in environ:
        log_warn(
            "The environmental variable 'AW_SECRET' was not supplied! "
            "Job-secrets like passwords might not be loadable after restart.",
            _stderr=True,
        )

    secret_len = len(config['secret'])
    if secret_len < MIN_SECRET_LEN:
        log_error(f"The provided secret key is too short! ({secret_len}<{MIN_SECRET_LEN} characters)")
        sys_exit(1)
