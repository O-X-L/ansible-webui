.. _administration_service:

.. include:: ../_include/head.rst


==============
Run as Service
==============

If you want to use this Ansible-WebUI as persistent service - you will have to set-up a web-proxy and database.

----

Proxy
#####

You can find a nginx config example here: `Nginx config example <https://github.com/O-X-L/ansible-webui/blob/latest/examples/nginx.conf>`_

----

Databases
#########

.. _administration_service_install_db:

MariaDB / MySQL
***************

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
**********

* Install dependencies:

  .. code-block:: bash

      pip install oxl-ansible-webui[psql]

* Setup DB & User:

  .. code-block:: psql

      CREATE USER aw WITH PASSWORD '<PASSWORD>';
      CREATE DATABASE aw;
      GRANT ALL PRIVILEGES ON aw TO aw;

Migrate Data
************

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

----

Service
#######

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

Ansible Role
############

You can find an Ansible Role to install the app on Debian here: `O-X-L/ansible-role-AW <https://github.com/O-X-L/ansible-role-AW>`_
