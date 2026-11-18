from django_auth_ldap.config import (
    LDAPSearch,
    LDAPSearchUnion,
    PosixGroupType,
    MemberDNGroupType,
    NestedMemberDNGroupType,
    ActiveDirectoryGroupType,
    NestedActiveDirectoryGroupType,
)

# defaults & choices for the config-file "LDAP"-block
LDAP_DEFAULT_FILTER_USER = '(uid=%(user)s)'
LDAP_DEFAULT_FILTER_GROUP = '(objectClass=*)'
class _MappedGroupTypeMixin:
    # maps LDAP-group DNs/names to django-group names; unmapped groups are ignored
    _group_mapping: dict = None

    def group_name_from_info(self, group_info):
        name = super().group_name_from_info(group_info)
        if self._group_mapping is None:
            return name

        dn = group_info[0].lower()
        return self._group_mapping.get(dn, self._group_mapping.get(name, None))


def _mapped_group_type(base_type: type, mapping: dict) -> type:
    mapping = {key.lower(): value for key, value in mapping.items()}
    return type(
        'MappedGroupType',
        (_MappedGroupTypeMixin, base_type),
        {'_group_mapping': mapping},
    )


def _group_type_group_of_names():
    return MemberDNGroupType(member_attr='member')


def _group_type_group_of_names_nested():
    return NestedMemberDNGroupType(member_attr='member')


LDAP_GROUP_TYPES = {
    'posix': PosixGroupType,
    'group-of-names': _group_type_group_of_names,
    'group-of-names-nested': _group_type_group_of_names_nested,
    'ad': ActiveDirectoryGroupType,
    'ad-nested': NestedActiveDirectoryGroupType,
}
LDAP_DEFAULT_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}


def _scope_subtree():
    # pylint: disable=C0415, E1101
    import ldap
    return ldap.SCOPE_SUBTREE


def _validate_ldap_config(ldap_cnf: dict) -> (str, None):
    try:
        _ = ldap_cnf['SERVER_URI']

        if 'USER_SEARCH_BASE' not in ldap_cnf and 'USER_SEARCH_BASES' not in ldap_cnf and \
                'USER_DN_TEMPLATE' not in ldap_cnf:
            raise KeyError('USER_SEARCH_BASE, USER_SEARCH_BASES or USER_DN_TEMPLATE')

        group_cnf = ('GROUP_SEARCH_BASE', 'REQUIRE_GROUP', 'GROUP_MAPPING', 'USER_FLAGS_BY_GROUP')
        if any(key in ldap_cnf for key in group_cnf) and 'GROUP_SEARCH_BASE' not in ldap_cnf:
            raise KeyError('GROUP_SEARCH_BASE')

        group_type = ldap_cnf.get('GROUP_TYPE', 'group-of-names')
        if group_type not in LDAP_GROUP_TYPES:
            raise KeyError(f"GROUP_TYPE '{group_type}' is not one of: {', '.join(LDAP_GROUP_TYPES)}")

    except KeyError as err:
        return f"Missing or invalid LDAP-setting: '{err}'"

    return None


def map_ldap_config(ldap_cnf: dict) -> (dict, tuple):
    """
    Validates the config-file "LDAP"-block and maps it into django-auth-ldap settings.
    Returns a tuple: (settings, error). 'settings' is 'None' if the configuration is invalid.
    """
    error = _validate_ldap_config(ldap_cnf)
    if error is not None:
        return None, error

    auth_ldap = {
        'AUTH_LDAP_SERVER_URI': ldap_cnf['SERVER_URI'],
        'AUTH_LDAP_BIND_DN': ldap_cnf.get('BIND_DN', ''),
        'AUTH_LDAP_BIND_PASSWORD': ldap_cnf.get('BIND_PASSWORD', ''),
        'AUTH_LDAP_START_TLS': ldap_cnf.get('START_TLS', False),
        'AUTH_LDAP_ALWAYS_UPDATE_USER': ldap_cnf.get('ALWAYS_UPDATE_USER', True),
        'AUTH_LDAP_USER_ATTR_MAP': ldap_cnf.get('USER_ATTR_MAP', LDAP_DEFAULT_ATTR_MAP),
        'AUTH_LDAP_USER_DN_TEMPLATE': ldap_cnf.get('USER_DN_TEMPLATE', None),
        'AUTH_LDAP_CONNECTION_OPTIONS': ldap_cnf.get('CONNECTION_OPTIONS', {}),
    }

    if ldap_cnf.get('CA_CERT_FILE', None) is not None:
        auth_ldap['AUTH_LDAP_CA_CERT_FILE'] = ldap_cnf['CA_CERT_FILE']

    user_filter = ldap_cnf.get('USER_FILTER', LDAP_DEFAULT_FILTER_USER)

    if auth_ldap['AUTH_LDAP_USER_DN_TEMPLATE'] is not None:
        pass  # direct DN-template is used instead of a search

    elif 'USER_SEARCH_BASES' in ldap_cnf:  # multiple search-bases
        auth_ldap['AUTH_LDAP_USER_SEARCH'] = LDAPSearchUnion(*[
            LDAPSearch(base, _scope_subtree(), user_filter)
            for base in ldap_cnf['USER_SEARCH_BASES']
        ])

    else:
        auth_ldap['AUTH_LDAP_USER_SEARCH'] = LDAPSearch(
            ldap_cnf['USER_SEARCH_BASE'], _scope_subtree(), user_filter,
        )

    if 'GROUP_SEARCH_BASE' in ldap_cnf:
        auth_ldap['AUTH_LDAP_GROUP_SEARCH'] = LDAPSearch(
            ldap_cnf['GROUP_SEARCH_BASE'],
            _scope_subtree(),
            ldap_cnf.get('GROUP_FILTER', LDAP_DEFAULT_FILTER_GROUP),
        )
        auth_ldap['AUTH_LDAP_GROUP_TYPE'] = LDAP_GROUP_TYPES[ldap_cnf.get('GROUP_TYPE', 'group-of-names')]()

        if ldap_cnf.get('REQUIRE_GROUP', None) is not None:
            auth_ldap['AUTH_LDAP_REQUIRE_GROUP'] = ldap_cnf['REQUIRE_GROUP']

        if ldap_cnf.get('GROUP_MAPPING', None) is not None:
            # NOTE: django-auth-ldap has no native group-name-mapping -
            #  this makes user-group-membership mirror the configured django-groups
            auth_ldap['AUTH_LDAP_GROUP_TYPE'] = _mapped_group_type(
                auth_ldap['AUTH_LDAP_GROUP_TYPE'].__class__,
                ldap_cnf['GROUP_MAPPING'],
            )()
            auth_ldap['AUTH_LDAP_MIRROR_GROUPS'] = True

        if ldap_cnf.get('USER_FLAGS_BY_GROUP', None) is not None:
            auth_ldap['AUTH_LDAP_USER_FLAGS_BY_GROUP'] = ldap_cnf['USER_FLAGS_BY_GROUP']

    return auth_ldap, None
