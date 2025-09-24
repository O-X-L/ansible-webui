.. _start_run:

.. include:: ../_include/head.rst

.. include:: ../_include/head_getting_started.rst

=======
3 - Run
=======

Getting Started
###############

You may want to:

* Set the :code:`AW_SECRET` environmental variable with a length of at least 30 characters!
* Provide a Playbook base-directory - either:

  * Change into the target directory before executing :code:`oxl-ansible-webui`
  * Create :ref:`a Repository <usage_repositories>`
  * Set the :code:`AW_PATH_PLAY` to your Playbook base-directory (env-var or via WebUI)


See: :ref:`Getting Started - Config <start_config>` for more details

----

Run Locally (PIP)
#################

.. code-block:: bash

    # foreground
    oxl-ansible-webui

    # or background
    oxl-ansible-webui > /tmp/aw.log 2> /tmp/aw.err.log &

    # at the first startup you will see the auto-generated credentials:

    Ansible-WebUI Version 0.0.12
    [2024-02-25 20:59:47 +0100] [5302] [INFO] Using DB: <PATH-TO-DB>
    [2024-02-25 20:59:47 +0100] [5302] [WARN] Initializing database <PATH-TO-DB>..
    [2024-02-25 20:59:50 +0100] [5302] [WARN] No admin was found in the database!
    [2024-02-25 20:59:50 +0100] [5302] [WARN] Generated user: 'ansible'
    [2024-02-25 20:59:50 +0100] [5302] [WARN] Generated pwd: '<PASSWORD>'
    [2024-02-25 20:59:50 +0100] [5302] [WARN] Make sure to change the password!
    [2024-02-25 20:59:50 +0100] [5302] [INFO] Listening on http://127.0.0.1:8000
    [2024-02-25 20:59:50 +0100] [5302] [WARN] Starting..
    [2024-02-25 20:59:50 +0100] [5302] [INFO] Starting job-threads

----

Run Dockerized
##############

.. code-block:: bash

    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 oxlorg/ansible-webui:latest

    # or with persistent data (volumes: /data = storage for logs & DB, /play = ansible playbook base-directory)
    docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play oxlorg/ansible-webui:latest

    # find initial password
    docker logs ansible-webui
