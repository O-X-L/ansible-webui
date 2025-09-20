import pytest

@pytest.mark.parametrize(
    'key, out, result',
    (
        (
                '-----BEGIN RSA PRIVATE KEY-----\n<key>\n-----END RSA PRIVATE KEY-----',
                '-----BEGIN RSA PRIVATE KEY-----\n<key>\n-----END RSA PRIVATE KEY-----\n',
                True,
        ),
        (
                '-----BEGIN OPENSSH PRIVATE KEY-----\n<key>\n-----END OPENSSH PRIVATE KEY-----',
                '-----BEGIN OPENSSH PRIVATE KEY-----\n<key>\n-----END OPENSSH PRIVATE KEY-----\n',
                True,
        ),
        (
                '   -----BEGIN RSA PRIVATE KEY-----\n<key>\n-----END RSA PRIVATE KEY-----    ',
                '-----BEGIN RSA PRIVATE KEY-----\n<key>\n-----END RSA PRIVATE KEY-----\n',
                True,
        ),
    )
)
def test_validate_and_fix_ssh_key(key, out, result):
    from aw.api_endpoints.credentials import _validate_and_fix_ssh_key, \
        REGEX_SSH_KEY_PREFIX, REGEX_SSH_KEY_APPENDIX, REGEX_NL_REPLACE

    if result:
        key_no_nl = key.replace('\n', REGEX_NL_REPLACE)
        assert REGEX_SSH_KEY_PREFIX.match(key_no_nl) is not None
        assert REGEX_SSH_KEY_APPENDIX.match(key_no_nl) is not None
        assert _validate_and_fix_ssh_key(key) == out

    else:
        assert REGEX_SSH_KEY_PREFIX.match(key) is None or REGEX_SSH_KEY_APPENDIX.match(key) is None
        assert _validate_and_fix_ssh_key(key) is None
