# Contribute

Contributions are very welcome!

We're also open to allow co-maintainers.

## What to contribute?

* [Find and report issues/bugs](https://github.com/O-X-L/ansible-webui/issues/new)
* [Translations](https://github.com/O-X-L/ansible-webui/blob/latest/CONTRIBUTE.md#translations) for your language(s)
* Add [Integration-Tests](https://github.com/O-X-L/ansible-webui/tree/latest/test/integration) for Web-UI, API and Job-Execution
* Add Unit-Tests (*pytest*)
* [Start Discussions about Implementations/Optimizations](https://github.com/O-X-L/ansible-webui/discussions/new/choose)

Read into the [Troubleshooting Guide](https://ansible-webui.OXL.app/usage/troubleshooting.html) to get some insight on how the stack works.

----

## Know How

* Do not commit [database migrations](https://docs.djangoproject.com/en/5.0/topics/migrations/#module-django.db.migrations) - they will be created on release.
* As we mainly use SQLite as database we should keep the DB writes to a minimum, so we do not run into locking issues (`OperationalError: database is locked`)
* Important fixes and features should be added to the CHANGELOG.md file
* This project is API-first - the API should be built for clean external usage.
* Add new views, APIs and job-execution-features to the integration tests (`test/integration/`)

----

## Install

```bash
# setup dev-env
make install
```

#### Frontend

You need to have Node.js installed.

See: [NodeJS download](https://nodejs.org/en/download)

Or use the quick-install script: `bash ./scripts/frontend/nodejs_install.sh`

----

### Using Docker

todo..

----

## Development

You can run the service in its development mode:

```bash
# first run (performs db-migrations on startup)
make run-dev-init

# after db-init
make run-dev

# or
bash ${REPO}/scripts/run_dev.sh
```

Run in staging mode: (*close to production behavior*)

```bash
make run-staging

# or
bash ${REPO}/scripts/run_staging.sh
```

Admin user for testing:

* User: `ansible`
* Pwd: `automateMe`

### Frontend

To build the frontend bundles - you can either run:

* `make run-dev  # OR: bash ./scripts/run_dev.sh` for the full app
* `make build-fe-auto  # OR: bash ./scripts/frontend/run_updater.sh` for automatic update whenever code changes
* `make build-fe  # OR: bash ./scripts/frontend/build.sh` to build it once

The bundles are generated into `src/oxl_ansible_webui/aw/static_dev` - django will use this statics-directory in dev-mode.

DO NOT copy & commit bundles to/in `src/oxl_ansible_webui/aw/static` - they are only generated/updated on release.

This is also necessary if a sub-component is used in multiple others. You will see a 404 error if the js-files are missing from the script. (*as they are not copied to django's static-dir*)

When adding additional svelte-apps - they should be added to `script/frontend/validate_prod_build.sh`.

----

### Translations

* Translations are added in `src/oxl_ansible_webui/aw/config/language.py`.

* If you add features that introduce new language-codes - either auto-translate them with a tool like [deepl](https://deepl.com/) or create a follow-up issue/ticket.

* New languages also have to be added:
  * to the frontend in `frontend/src/base/Nav.svelte`
  * the country's flag needs to be added to `src/oxl_ansible_webui/aw/static/img/`
  * the translations-file needs to be referenced in `src/oxl_ansible_webui/aw/config/language.py` for them to be picked-up by the API at `src/oxl_ansible_webui/aw/api_endpoints/frontend.py` (`APIBackendTranslations`)

----

## Testing

Test to build the app using PIP:
```bash
bash ${REPO}/scripts/run_pip_build.sh
```

Run tests and lint:

```bash
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
```

----

## API

### Many-to-Many relations

DRF serializing is a little harder for many-to-many relations.

To make it work:

1. Initialize the choices for correct validation - example:

  ```python3
  class BaseAlertWriteRequest(serializers.ModelSerializer):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields['jobs'] = serializers.MultipleChoiceField(choices=[job.id for job in Job.objects.all()])
  
      jobs = serializers.MultipleChoiceField(allow_blank=True, choices=[])
   ```

2. The update of the FK has to be done manually - example:

  ```python3
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
   ```

----

### Unique constraints

DRF has some issues with validating UC's set at model level.

To work around this - we can disable this validation:

```python3
class RepositoryWriteRequest(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = Repository.api_fields_write

    name = serializers.CharField(validators=[])  # uc on update
```
