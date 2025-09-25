.. _dev_intro:

.. include:: ../_include/head.rst

=========
DEV Intro
=========

Feel free to contribute to this project using `pull-requests <https://github.com/O-X-L/ansible-webui/pulls>`_, `issues <https://github.com/O-X-L/ansible-webui/issues>`_ and `discussions <https://github.com/O-X-L/ansible-webui/discussions>`_!

Testers are also very welcome! Please `give feedback <https://github.com/O-X-L/ansible-webui/discussions>`_

For further details - see: `Contribute <https://github.com/O-X-L/ansible-webui/blob/latest/CONTRIBUTE.md>`_

Read into the :ref:`Troubleshooting Guide <administration_troubleshooting>` to get some insight on how the stack works.

----

Development-Environment
#######################

Admin user for testing:

* User: :code:`ansible`
* Pwd: :code:`automateMe`

Containerized
*************

We recommend to use the containerized/dockerized development environment.

For details see: `${REPO}/docker/README.md <https://github.com/O-X-L/ansible-webui/blob/latest/docker/README.md>`_

----

Local
*****

Requirements
============

* Create a Python3-VENV (>=3.10) and install all requirements in :code:`${REPO}/requirements*.txt`

    .. code-block:: bash

       # setup dev-env
       make install

* You need to have Node.js installed

  See: `NodeJS download <https://nodejs.org/en/download>`_

  Or use the quick-install script: :code:`bash ./scripts/frontend/nodejs_install.sh`

Run
===

Frontend
--------

To build the frontend bundles - you can either run:

* :code:`make run-dev` or :code:`bash ./scripts/run_dev.sh` for the full app
* :code:`make build-fe-auto` or :code:`bash ./scripts/frontend/run_updater.sh` for automatic update whenever code changes
* :code:`make build-fe` or :code:`bash ./scripts/frontend/build.sh` to build it once

The bundles are generated into :code:`src/oxl_ansible_webui/aw/static_dev` - django will use this statics-directory in dev-mode.

DO NOT copy & commit bundles to/in :code:`src/oxl_ansible_webui/aw/static` - they are only generated/updated on release.

This is also necessary if a sub-component is used in multiple others. You will see a 404 error if the js-files are missing from the script. (*as they are not copied to django's static-dir*)

When adding additional svelte-apps - they should be added to :code:`script/frontend/validate_prod_build.sh`.

Backend
-------

You can run the service in its development mode:

.. code-block:: bash

    # first run (performs db-migrations on startup)
    make run-dev-init

    # after db-init
    make run-dev

    # or
    bash ${REPO}/scripts/run_dev.sh

Run in staging mode: (*close to production behavior*)

.. code-block:: bash

    make run-staging

    # or
    bash ${REPO}/scripts/run_staging.sh

----

Know How
########

* Do not commit `database migrations <https://docs.djangoproject.com/en/5.0/topics/migrations/#module-django.db.migrations>`_ - they are created on release.

* As we mainly use SQLite as database we should keep the DB writes to a minimum, so we do not run into locking issues (:code:`OperationalError: database is locked`)

* For MySQL/MariaDB we are required to run this function before every DB-write

  .. code-block:: python3

      from aw.utils.db_handler import close_old_mysql_connections
      close_old_mysql_connections()

* Important fixes and features should be added to the CHANGELOG.md file

* This project is API-first - the API should be built for clean external usage.

* Add new views, APIs and job-execution-features to the integration tests (:code:`test/integration/`)

----

Testing
#######

Test to build the app using PIP:

.. code-block:: bash

    bash ${REPO}/scripts/run_pip_build.sh

Run tests and lint:

.. code-block:: bash

    # setup dev-env
    make install

    make lint
    make test

    # or run single tests:
    make test-api
    make test-job-exec

    make test-webui  # NOTE: you can enable screenshots via env-var 'AW_DEBUG=1'
    make test-auth

    make test-db

----

API
###

Many-to-Many relations
**********************

DRF serializing is a little harder for many-to-many relations.

To make it work:

1. Initialize the choices for correct validation - example:

    .. code-block:: python3

        class BaseAlertWriteRequest(serializers.ModelSerializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields['jobs'] = serializers.MultipleChoiceField(choices=[job.id for job in Job.objects.all()])

            jobs = serializers.MultipleChoiceField(allow_blank=True, choices=[])

2. The update of the FK has to be done manually - example:

    .. code-block:: python3

        def update_jobs(alert: BaseAlert, job_ids: list):
            jobs = []
            for job_id in job_ids:
                try:
                    jobs.append(Job.objects.get(id=job_id))

                except ObjectDoesNotExist:
                    continue

            alert.jobs.set(jobs)

         update_jobs(alert=alert, job_ids=serializer.validated_data.pop('jobs'))
         AlertGlobal.objects.filter(id=alert.id).update(**serializer.validated_data)

Unique constraints
******************

DRF has some issues with validating UC's set at model level.

To work around this - we can disable this validation:

.. code-block:: python3

    class RepositoryWriteRequest(serializers.ModelSerializer):
        class Meta:
            model = Repository
            fields = Repository.api_fields_write

        name = serializers.CharField(validators=[])  # uc on update
