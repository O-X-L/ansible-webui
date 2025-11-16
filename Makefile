install:
	bash scripts/install_dev.sh

run-dev-local-init:
	bash scripts/run_dev.sh

run-dev-local:
	bash scripts/run_dev.sh q

run-dev:
	bash scripts/docker_dev.sh

run-dev-fe:
	bash scripts/docker_dev_fe.sh

run-dev-be:
	bash scripts/docker_dev_be.sh

run-dev-be-noinit:
	bash scripts/docker_dev_be.sh 0

run-staging-local:
	bash scripts/run_staging.sh

lint-be:
	bash scripts/lint.sh

lint-fe:
	bash scripts/frontend/lint.sh

lint:
	bash scripts/lint.sh
	bash scripts/frontend/lint.sh

test:
	bash scripts/test.sh

test-unit:
	bash scripts/test_unit.sh

test-webui:
	bash scripts/frontend/build.sh
	bash scripts/test_webui.sh

test-api:
	bash scripts/test_api.sh

test-job-exec:
	bash scripts/test_job_exec.sh

test-db:
	bash scripts/test_db_sqlite.sh
	bash scripts/test_db_mariadb.sh
	bash scripts/test_db_psql.sh

test-auth:
	bash scripts/test_auth_saml.sh

build-fe-local:
	bash scripts/frontend/build.sh

build-fe-local-auto:
	bash scripts/frontend/run_updater.sh


#build.sh           kill_ps.sh     run_pip_build.sh  test_api.sh        test_db_mariadb.sh  test_webui.sh
#docker_build.sh    lint.sh        run_shared.sh     test_auth_saml.sh  test_db_psql.sh     update_version.sh
#docker_release.sh  migrate_db.sh  run_staging.sh    test_base.sh       test_db_sqlite.sh
#frontend           run_dev.sh     test.sh           test_db_base.sh    test_job_exec.sh
