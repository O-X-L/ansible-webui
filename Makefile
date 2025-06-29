install:
	bash scripts/install_dev.sh

run-dev-init:
	bash scripts/run_dev.sh

run-dev:
	bash scripts/run_dev.sh q

run-staging:
	bash scripts/run_staging.sh

lint:
	bash scripts/lint.sh

test:
	bash scripts/test.sh

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

build-fe:
	bash scripts/frontend/build.sh

build-fe-auto:
	bash scripts/frontend/run_updater.sh


#build.sh           kill_ps.sh     run_pip_build.sh  test_api.sh        test_db_mariadb.sh  test_webui.sh
#docker_build.sh    lint.sh        run_shared.sh     test_auth_saml.sh  test_db_psql.sh     update_version.sh
#docker_release.sh  migrate_db.sh  run_staging.sh    test_base.sh       test_db_sqlite.sh
#frontend           run_dev.sh     test.sh           test_db_base.sh    test_job_exec.sh
