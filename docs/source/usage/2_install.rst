.. _usage_install:

.. include:: ../_include/head.rst

================
2 - Installation
================

Ansible
*******

See `the documentation <https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pip-install>`_ on how to install Ansible.

**Make sure to read** the `Ansible best-practices <https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout>`_ on how to use Ansible!

----

Demo
****

Check out the demo at: `demo.ansible-webui.OXL.app <https://demo.ansible-webui.OXL.app>`_

Login: User :code:`demo`, Password :code:`Ansible1337`

----

Install
*******

Requires Python >=3.11

.. code-block:: bash

    python3 -m pip install oxl-ansible-webui

**Using docker**:

.. code-block:: bash

    docker image pull oxlorg/ansible-webui:latest


For more information see: :ref:`Usage - Docker <usage_docker>`


Start
*****

**TLDR**:

.. code-block:: bash

    cd $PLAYBOOK_DIR
    oxl-ansible-webui



**Using docker**:

.. code-block:: bash

    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 oxlorg/ansible-webui:latest


**Details**:

See: :ref:`Usage - Run <usage_run>`


Now you can open the Ansible-WebUI in your browser: `http://localhost:8000 <http://localhost:8000>`_

----

Proxy
*****

You can find a nginx config example here: `Nginx config example <https://github.com/O-X-L/ansible-webui/blob/latest/examples/nginx.conf>`_

----

Databases
*********

.. _usage_install_db:

Migrate Data
============

You can migrate data between database-types.

Make sure to use the same AW-version on dump and load!

.. code-block:: bash

    export AW_DB=$HOME/.config/ansible-webui/aw.db
    # OR
    export AW_CONFIG=$HOME/.config/ansible-webui/config.yml

    # dump to file
    oxl-ansible-webui-manage dumpdata --indent=2 --natural-foreign --natural-primary --verbosity=1 > aw-dump.json

    # change db config

    # test db connection
    oxl-ansible-webui-manage showmigrations

    # create db schema
    oxl-ansible-webui-manage migrate

    # load from file
    oxl-ansible-webui-manage loaddata aw-dump.json

    # if you encounter issues while importing data into mysql/mariadb - try to set 'AW_DEBUG' beforehand
    AW_DEBUG=1 oxl-ansible-webui-manage loaddata aw-dump.json


MariaDB / MySQL
===============

* Install dependencies:

    .. code-block:: bash

        # debian-based
        apt install default-libmysqlclient-dev pkg-config
        pip install oxl-ansible-webui[mysql]

        # alpine
        apk add py3-mysqlclient

* Setup DB & User:

    .. code-block:: mysql

        CREATE USER 'aw'@'%' IDENTIFIED BY '<PASSWORD>';
        CREATE DATABASE aw CHARACTER SET utf8;
        GRANT ALL PRIVILEGES ON aw.* TO 'aw'@'%';
        FLUSH PRIVILEGES;

PostgreSQL
==========

* Install dependencies:

    .. code-block:: bash

        pip install oxl-ansible-webui[psql]

* Setup DB & User:

    .. code-block:: psql

        CREATE USER aw WITH PASSWORD '<PASSWORD>';
        CREATE DATABASE aw;
        GRANT ALL PRIVILEGES ON aw TO aw;

----

Ansible Role
************

You can find an Ansible Role to install the app on Debian here: `ansibleguy.sw_ansible_webui <https://github.com/ansibleguy/sw_ansible_webui>`_

----

Service
*******

You might want to create a service-user:

.. code-block:: bash

    sudo useradd ansible-webui --shell /usr/sbin/nologin --create-home --home-dir /home/ansible-webui


You can find a service config example here: `Systemd config example <https://github.com/O-X-L/ansible-webui/blob/latest/examples/systemd_service.conf>`_

Enabling & starting the service:

.. code-block:: bash

    systemctl enable ansible-webui.service
    systemctl start ansible-webui.service

For production usage you should use a proxy like nginx in from of the Ansible-WebUI webservice!

----

Migration from ansibleguy-webui
*******************************

* If running => stop the service
* Make a backup-copy of your database-file:

  .. code-block:: bash

      cp ${HOME}/.config/ansible-webui/aw.db ${HOME}/.config/ansible-webui/aw.db.upgrade.bak

* Uninstall

  .. code-block:: bash

      pip uninstall ansibleguy-webui

* Install

  .. code-block:: bash

      pip install oxl-ansible-webui

* Try to run

  .. code-block:: bash

      oxl-ansible-webui
