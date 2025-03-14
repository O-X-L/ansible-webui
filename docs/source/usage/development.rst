.. _usage_development:

.. include:: ../_include/head.rst

===========
Development
===========

Feel free to contribute to this project using `pull-requests <https://github.com/O-X-L/ansible-webui/pulls>`_, `issues <https://github.com/O-X-L/ansible-webui/issues>`_ and `discussions <https://github.com/O-X-L/ansible-webui/discussions>`_!

Testers are also very welcome! Please `give feedback <https://github.com/O-X-L/ansible-webui/discussions>`_

For further details - see: `Contribute <https://github.com/O-X-L/ansible-webui/blob/latest/CONTRIBUTE.md>`_

Read into the :ref:`Troubleshooting Guide <usage_troubleshooting>` to get some insight on how the stack works.


----

Install Unstable Version
************************

**WARNING**: If you run non-release versions you will have to save your :code:`src/oxl_ansible_webui/aw/migrations/*` else your database upgrades might fail. Can be ignored if you do not care about losing the Ansible-WebUI config.

.. code-block:: bash

    # download
    git clone https://github.com/O-X-L/ansible-webui

    # install dependencies (venv recommended)
    cd webui
    python3 -m pip install --upgrade requirements.txt
    bash scripts/update_version.sh

    # run
    python3 src/oxl_ansible_webui/


**Using docker**:

.. code-block:: bash

    docker image pull oxlorg/ansible-webui:unstable
    docker run -it --name ansible-webui-dev --publish 127.0.0.1:8000:8000 --volume /tmp/awdata:/data oxlorg/ansible-webui:unstable
    # to safe db-migrations use:
    # --volume /var/local/ansible-webui/migrations/:/usr/local/lib/python3.11/site-packages/oxl_ansible_webui/aw/migrations
