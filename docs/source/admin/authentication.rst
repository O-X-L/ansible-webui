.. _administration_auth:

.. include:: ../_include/head.rst

==============
Authentication
==============

In case your primary authentication method is not working for some reason - you can enter the application with a local user at: :code:`/a/login/fallback`

.. _administration_auth_saml:

SAML SSO
########

**Tested config examples**: `Google Workspace <https://github.com/O-X-L/ansible-webui/blob/latest/examples/saml_google_workspace.yml>`_

This app is integrating the `django-saml2-auth-community <https://github.com/mostafa/django-saml2-auth>`_ (indirect `pysaml2 <https://github.com/IdentityPython/pysaml2>`_).

If you have troubles with getting SAML to work - check out :ref:`Administration - Troubleshooting - SAML <administration_troubleshooting_saml>`

----

Setup
*****

1. Add the :code:`SAML` config-block to your config-file. See: :ref:`Getting Started - Config - File <start_config_file>`

  For options see: `Module settings <https://github.com/mostafa/django-saml2-auth?tab=readme-ov-file#module-settings>`_

  Example:

  .. code-block:: yaml

      HOSTNAMES: '<YOUR-DOMAIN>'
      AUTH: 'saml'
      SAML:
          METADATA_AUTO_CONF_URL: 'https://<YOUR-IDP>/metadata'
          # METADATA_LOCAL_FILE_PATH: '/etc/ansible-webui/saml-metadata.txt'

          # replace with your scheme, domain and port!
          ASSERTION_URL: 'http://localhost:8000'
          ENTITY_ID: 'http://localhost:8000/a/saml/acs/'
          DEFAULT_NEXT_URL: 'http://localhost:8000/'

          CREATE_USER: true
          NEW_USER_PROFILE:
              USER_GROUPS: []  # The default group name when a new user logs in
              ACTIVE_STATUS: true
              STAFF_STATUS: true  # allow user to view 'System - Admin' page
              SUPERUSER_STATUS: false  # full system admin privileges

          ATTRIBUTES_MAP:  # email or username and token are required!
              # mapping: django => IDP
              email: 'email'
              username: 'email'
              token: 'id'
              # optional:
              first_name: 'firstName'
              last_name: 'lastName'
              groups: 'Groups'  # Optional

          DEBUG: false  # DO NOT PERMANENTLY ENABLE!

          GROUPS_MAP:  # map IDP groups to django groups
              'IDP GROUP': 'AW Job Managers'

          # NAME_ID_FORMAT: 'user.email'
          # KEY_FILE: '/etc/ansible-webui/saml.key'
          # CERT_FILE: '/etc/ansible-webui/saml.crt'

2. SSO identity provider settings:

  **ACS URL**: :code:`http://localhost:8000/a/saml/acs/`

  **Entity ID/Audience URL**: :code:`http://localhost:8000/a/saml/acs/`

  Note: Replace *http://localhost:8000* with your scheme, domain and port


3. For non-Docker setups: Install the :code:`xmlsec` package that is used internally (see: `details <https://github.com/IdentityPython/pysaml2?tab=readme-ov-file#external-dependencies>`_)


You should now be able to see :code:`[INFO] [main] Using Auth-Mode: saml` logged on startup.

----

Docker
******

Example:

.. code-block:: bash

    # save all needed SAML files to /etc/ansible-webui/ on your host system
    sudo docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --env AW_CONFIG=/etc/aw/config.yml --volume /etc/ansible-webui/:/etc/aw/ oxlorg/ansible-webui:latest

.. _administration_auth_ldap:

LDAP
####

**Tested config examples**: `Active Directory / Samba-AD <https://github.com/O-X-L/ansible-webui/blob/latest/examples/ldap_active_directory.yml>`_, `OpenLDAP <https://github.com/O-X-L/ansible-webui/blob/latest/examples/ldap_openldap.yml>`_

This app is integrating `django-auth-ldap <https://github.com/django-auth-ldap/django-auth-ldap>`_ (indirect `python-ldap <https://github.com/python-ldap/python-ldap>`_).

If you have troubles with getting LDAP to work - check out: :ref:`Administration - Troubleshooting - LDAP <administration_troubleshooting_ldap>`

----

Setup
*****

1. Add the :code:`LDAP` config-block to your config-file. See: :ref:`Getting Started - Config - File <start_config_file>`

  Example (OpenLDAP):

  .. code-block:: yaml

      HOSTNAMES: '<YOUR-DOMAIN>'
      AUTH: 'ldap'

      LDAP:
          SERVER_URI: 'ldap://ldap.example.com:389'
          START_TLS: true  # or use 'ldaps://ldap.example.com:636'

          BIND_DN: 'cn=svc-ansible-webui,ou=services,dc=example,dc=com'
          BIND_PASSWORD: '<PASSWORD>'

          USER_SEARCH_BASE: 'ou=people,dc=example,dc=com'
          # USER_FILTER: '(uid=%(user)s)'  # default

          # optional: map LDAP-groups to app-privileges
          GROUP_SEARCH_BASE: 'ou=groups,dc=example,dc=com'
          GROUP_TYPE: 'posix'  # posix | group-of-names | ad | ad-nested | posix-nested | group-of-names-nested
          GROUP_MAPPING:
              'cn=ansible-webui-managers,ou=groups,dc=example,dc=com': 'AW Managers'
              'cn=ansible-webui-executors,ou=groups,dc=example,dc=com': 'AW Job Executors'
          USER_FLAGS_BY_GROUP:
              'is_superuser': 'cn=ansible-webui-admins,ou=groups,dc=example,dc=com'
              'is_staff': 'cn=ansible-webui-admins,ou=groups,dc=example,dc=com'

  Settings:

  * :code:`SERVER_URI` - LDAP-server URI (:code:`ldap://` or :code:`ldaps://`)
  * :code:`START_TLS` - upgrade :code:`ldap://` connections with StartTLS (default: :code:`false`)
  * :code:`CA_CERT_FILE` - custom CA-certificate file (default: system CAs)
  * :code:`BIND_DN` / :code:`BIND_PASSWORD` - optional service-account used for the user-search
  * :code:`USER_SEARCH_BASE` - where to search for users (alternatively: :code:`USER_SEARCH_BASES` for multiple bases or :code:`USER_DN_TEMPLATE` for direct DN lookups)
  * :code:`USER_FILTER` - user search-filter (default: :code:`(uid=%(user)s)`, for AD: :code:`(sAMAccountName=%(user)s)`)
  * :code:`USER_ATTR_MAP` - user-attribute mapping (default: first-name, last-name, email)
  * :code:`GROUP_SEARCH_BASE` / :code:`GROUP_FILTER` / :code:`GROUP_TYPE` - optional group-search
  * :code:`REQUIRE_GROUP` - optional: only members of this group may login
  * :code:`GROUP_MAPPING` - optional: map LDAP-groups to app-privilege groups (e.g: :code:`AW Managers`)
  * :code:`USER_FLAGS_BY_GROUP` - optional: map LDAP-groups to user-flags (:code:`is_superuser`, :code:`is_staff`)
  * :code:`ALWAYS_UPDATE_USER` - update local user on every login (default: :code:`true`)

2. For non-Docker setups: Install the LDAP dependency: :code:`pip install oxl-ansible-webui[ldap]`

  .. note::

    The :code:`python-ldap` dependency requires some system-libraries to be installed:
    :code:`libldap2` / :code:`libsasl2` (Debian) or :code:`openldap` (Alpine). The provided Docker-images are Debian-based and already include them.

3. Local users can still login at the regular login-page - so you do not lock yourself out (e.g: the fallback admin)


You should now be able to see :code:`[INFO] [main] Using Auth-Mode: ldap` logged on startup.

