.. _administration_docker:

.. include:: ../_include/head.rst

======
Docker
======

You can find the dockerfiles and scripts used to build the images `in the Repository <https://github.com/O-X-L/ansible-webui/tree/latest/docker>`_

Images
******

* `ansible-webui <https://hub.docker.com/r/oxlorg/ansible-webui>`_
* `ansible-webui-unprivileged <https://hub.docker.com/r/oxlorg/ansible-webui-unprivileged>`_ (*runs as non-root*)
* `ansible-webui-mysql <https://hub.docker.com/r/oxlorg/ansible-webui-mysql>`_ (*support for MariaDB/MySQL DB, non-root*)
* `ansible-webui-psql <https://hub.docker.com/r/oxlorg/ansible-webui-psql>`_ (*support for postgres DB, non-root*)
* `ansible-webui-aws <https://hub.docker.com/r/oxlorg/ansible-webui-aws>`_ (*support for aws-ssm-client, non-root*)

We recommend to use the :code:`latest` tag.

The images use the `official Python3 containers <https://hub.docker.com/_/python>`_ (:code:`alpine` and :code:`debian`) as a base.

----

Ansible Requirements
********************

Our `docker image oxlorg/ansible-webui <https://hub.docker.com/r/oxlorg/ansible-webui>`_ enables you to install Ansible dependencies on container startup.

Files inside the container:

* Python3 Modules: :code:`/play/requirements.txt`
* `Ansible Roles & Collections <https://docs.ansible.com/ansible/latest/collections_guide/collections_installing.html#install-multiple-collections-with-a-requirements-file>`_: :code:`/play/requirements.yml`

    * Only Ansible Roles: :code:`/play/requirements_roles.yml` or :code:`/play/roles/requirements.yml`
    * Only Ansible Collections: :code:`/play/requirements_collections.yml` or :code:`/play/collections/requirements.yml`

----

Unprivileged
************

There are images for running Ansible-WebUI as unprivileged user :code:`aw` with UID/GID :code:`8785` inside the container:

* Latest: :code:`oxlorg/ansible-webui-unprivileged:latest`

* Unstable: :code:`oxlorg/ansible-webui-unprivileged:unstable`

----

Persistent Data
***************

It might make sense for you to mount these paths in the container:

* :code:`/data` (:code:`AW_DB` & :code:`AW_PATH_LOG` env-vars) - for database & execution-logs
* :code:`/play` (:code:`AW_PATH_PLAY` env-var) - for static Ansible playbook base-directory

If you are running an :code:`unprivileged` image - you will have to allow the service-user to write to the directories. The UID needs to match!

Basic example:

.. code-block:: bash

    # add matching service-user on the host system
    sudo useradd ansible-webui --shell /usr/sbin/nologin --uid 8785 --user-group
    chown ansible-webui:ansible-webui ${YOUR_DATA_DIR}

----

AWS CLI Support
***************

There is also an image that has `AWS-CLI support <https://github.com/aws/session-manager-plugin>`_ pre-enabled: :code:`oxlorg/ansible-webui-aws:latest` (needed for :code:`community.aws.*` modules)

Its base-image is :code:`oxlorg/ansible-webui-unprivileged:latest`

----

Custom build
************

If you want to build a custom docker image - make sure to set those environmental variables:

:code:`AW_VERSION=X.X.X AW_DOCKER=1 PYTHONUNBUFFERED=1`
