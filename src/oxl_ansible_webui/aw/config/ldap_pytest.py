from os import environ

# pylint: disable=C0415
from aw.config.ldap import map_ldap_config, LDAP_DEFAULT_FILTER_USER, LDAP_GROUP_TYPES

BASE_CONFIG = {
    'SERVER_URI': 'ldap://ldap.example.com:389',
    'BIND_DN': 'cn=svc-search,dc=example,dc=com',
    'BIND_PASSWORD': 'secret',
    'USER_SEARCH_BASE': 'ou=people,dc=example,dc=com',
}


def _get_auth_ldap(config: dict) -> dict:
    auth_ldap, error = map_ldap_config(config)
    assert error is None
    return auth_ldap


def _get_error(config: dict) -> str:
    auth_ldap, error = map_ldap_config(config)
    assert auth_ldap is None
    return error


def test_ldap_valid_minimal():
    auth_ldap = _get_auth_ldap(dict(BASE_CONFIG))
    assert auth_ldap['AUTH_LDAP_SERVER_URI'] == BASE_CONFIG['SERVER_URI']
    assert auth_ldap['AUTH_LDAP_BIND_DN'] == BASE_CONFIG['BIND_DN']
    assert auth_ldap['AUTH_LDAP_BIND_PASSWORD'] == BASE_CONFIG['BIND_PASSWORD']
    assert auth_ldap['AUTH_LDAP_START_TLS'] is False
    assert auth_ldap['AUTH_LDAP_USER_SEARCH'].base_dn == BASE_CONFIG['USER_SEARCH_BASE']
    assert auth_ldap['AUTH_LDAP_USER_SEARCH'].filterstr == LDAP_DEFAULT_FILTER_USER


def test_ldap_valid_full():
    config = dict(BASE_CONFIG)
    config.update({
        'START_TLS': True,
        'CA_CERT_FILE': '/etc/ssl/certs/example.pem',
        'USER_FILTER': '(sAMAccountName=%(user)s)',
        'USER_ATTR_MAP': {'email': 'mail', 'first_name': 'givenName', 'last_name': 'sn'},
        'ALWAYS_UPDATE_USER': False,
        'GROUP_SEARCH_BASE': 'ou=groups,dc=example,dc=com',
        'GROUP_TYPE': 'ad',
        'REQUIRE_GROUP': 'cn=awui-users,ou=groups,dc=example,dc=com',
        'GROUP_MAPPING': {'cn=awui-managers,ou=groups,dc=example,dc=com': 'AW Managers'},
        'USER_FLAGS_BY_GROUP': {
            'is_staff': 'cn=awui-admins,ou=groups,dc=example,dc=com',
        },
    })

    auth_ldap = _get_auth_ldap(config)
    assert auth_ldap['AUTH_LDAP_START_TLS'] is True
    assert auth_ldap['AUTH_LDAP_CA_CERT_FILE'] == config['CA_CERT_FILE']
    assert auth_ldap['AUTH_LDAP_ALWAYS_UPDATE_USER'] is False
    assert auth_ldap['AUTH_LDAP_USER_ATTR_MAP'] == config['USER_ATTR_MAP']
    assert auth_ldap['AUTH_LDAP_REQUIRE_GROUP'] == config['REQUIRE_GROUP']
    assert auth_ldap['AUTH_LDAP_MIRROR_GROUPS'] is True
    group_type = auth_ldap['AUTH_LDAP_GROUP_TYPE']
    assert group_type.group_name_from_info(
        ('CN=awui-managers,OU=groups,DC=example,DC=com', {'cn': ['awui-managers']})
    ) == 'AW Managers'
    assert group_type.group_name_from_info(
        ('CN=unmapped-group,OU=groups,DC=example,DC=com', {'cn': ['unmapped-group']})
    ) is None
    assert auth_ldap['AUTH_LDAP_USER_FLAGS_BY_GROUP'] == config['USER_FLAGS_BY_GROUP']
    assert auth_ldap['AUTH_LDAP_USER_SEARCH'].filterstr == '(sAMAccountName=%(user)s)'
    assert auth_ldap['AUTH_LDAP_GROUP_SEARCH'].base_dn == config['GROUP_SEARCH_BASE']


def test_ldap_dn_template():
    config = dict(BASE_CONFIG)
    del config['USER_SEARCH_BASE']
    config['USER_DN_TEMPLATE'] = 'uid=%(user)s,ou=people,dc=example,dc=com'

    auth_ldap = _get_auth_ldap(config)
    assert auth_ldap['AUTH_LDAP_USER_DN_TEMPLATE'] == config['USER_DN_TEMPLATE']
    assert 'AUTH_LDAP_USER_SEARCH' not in auth_ldap


def test_ldap_search_bases():
    config = dict(BASE_CONFIG)
    del config['USER_SEARCH_BASE']
    config['USER_SEARCH_BASES'] = ['ou=people,dc=example,dc=com', 'ou=other,dc=example,dc=com']

    auth_ldap = _get_auth_ldap(config)
    assert 'AUTH_LDAP_USER_SEARCH' in auth_ldap
    assert 'LDAPSearchUnion' in str(auth_ldap['AUTH_LDAP_USER_SEARCH'])


def test_ldap_missing_server_uri():
    config = dict(BASE_CONFIG)
    del config['SERVER_URI']
    assert 'SERVER_URI' in _get_error(config)


def test_ldap_missing_user_lookup():
    config = dict(BASE_CONFIG)
    del config['USER_SEARCH_BASE']
    assert 'USER_SEARCH_BASE' in _get_error(config)


def test_ldap_missing_group_search_base():
    config = dict(BASE_CONFIG)
    config['GROUP_MAPPING'] = {'cn=awui-managers,ou=groups,dc=example,dc=com': 'AW Managers'}
    assert 'GROUP_SEARCH_BASE' in _get_error(config)


def test_ldap_invalid_group_type():
    config = dict(BASE_CONFIG)
    config['GROUP_SEARCH_BASE'] = 'ou=groups,dc=example,dc=com'
    config['GROUP_TYPE'] = 'invalid'
    assert 'GROUP_TYPE' in _get_error(config)


def test_ldap_group_type_choices():
    config = dict(BASE_CONFIG)
    config['GROUP_SEARCH_BASE'] = 'ou=groups,dc=example,dc=com'

    for group_type in LDAP_GROUP_TYPES:
        config['GROUP_TYPE'] = group_type
        auth_ldap = _get_auth_ldap(dict(config))
        assert 'AUTH_LDAP_GROUP_TYPE' in auth_ldap


def test_ldap_auth_mode(monkeypatch):
    # pylint: disable=C0415
    from aw.config.environment import auth_mode_ldap, get_aw_env_var_or_default
    monkeypatch.setenv('AW_AUTH', 'ldap')
    monkeypatch.setenv('AW_LDAP', 'LDAP')
    monkeypatch.setenv('AW_CONFIG', '/etc/ansible-webui/config.yml')
    get_aw_env_var_or_default.cache_clear()
    assert auth_mode_ldap() is True

    monkeypatch.setenv('AW_AUTH', 'local')
    get_aw_env_var_or_default.cache_clear()
    assert auth_mode_ldap() is False
    get_aw_env_var_or_default.cache_clear()
