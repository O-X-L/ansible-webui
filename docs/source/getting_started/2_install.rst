.. _start_install:

.. include:: ../_include/head.rst

.. include:: ../_include/head_getting_started.rst

================
2 - Installation
================

Ansible
#######

See `the documentation <https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#pip-install>`_ on how to install Ansible.

**Make sure to read** the official documentation: `Getting-Started Guide <https://docs.ansible.com/ansible/latest/getting_started/index.html>`_, `Directory Layout <https://docs.ansible.com/ansible/latest/tips_tricks/sample_setup.html#sample-directory-layout>`_ and `Playbooks <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks.html>`_!

----

Install
#######

Requires Python >=3.11

.. code-block:: bash

    python3 -m pip install oxl-ansible-webui

**Using docker**:

.. code-block:: bash

    docker image pull oxlorg/ansible-webui:latest


For more information see: :ref:`Administration - Docker <administration_docker>`

----

Start
#####

**TLDR**:

.. code-block:: bash

    cd $PLAYBOOK_DIR
    oxl-ansible-webui



**Using docker**:

.. code-block:: bash

    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 oxlorg/ansible-webui:latest


**Details**:

See: :ref:`Getting Started - Run <start_run>`


Now you can open the Ansible-WebUI in your browser: `http://localhost:8000 <http://localhost:8000>`_

----

Multi-User Setup as Service
###########################

See: :ref:`Administration - Run as Service <administration_service>`
