# Docker Build Notes

## Images

### Development

* `Dockerfile_dev_frontend` => build the frontend JS-files from your local sources

  ```bash
  # build image
  docker build -f Dockerfile_dev_frontend -t aw-dev-fe --network=host --no-cache .
  # run whenever you want to re-build the JS-bundle
  docker run -it --rm --network=host --volume "$(pwd)/..:/repo" aw-dev-fe
  ```

* `Dockerfile_dev_backend` => initialize and run the Gunicorn/Django web service

  ```bash
  # build image
  docker build -f Dockerfile_dev_backend -t aw-dev-be --network=host --no-cache .
  # start web-service
  docker run -it --rm --network=host --volume "$(pwd)/..:/repo" aw-dev-be
  ```

### End-Users

* `Dockerfile_builder_frontend` => build the frontend JS-files from Svelte-src via npm

* `Dockerfile_production_alpine` => Base image on alpine (running as root)

* `Dockerfile_production_debian` => Base image on debian (running as root)

* `Dockerfile_production_unprivileged_*` => Base image but running as unprivileged service-user

* `Dockerfile_production_mysql_*` => Image with MySQL/MariaDB-client support

* `Dockerfile_production_psql_*` => Image with postgreSQL-client support

* `Dockerfile_production_aws_*` => Image with AWS-CLI support

Build Script: `${REPO}/scripts/docker_build.sh`

----

## Testing

Before pushing/publishing the images.

* Run

  ```bash
  docker run --rm --network=host -d --name aw-test oxlorg/ansible-webui-unprivileged && docker logs -f aw-test
  ```

* Check WebUI

  * Login
  * Create git-repo
  * Create job
  * Run job
  * Job Logs
  * Check new Features

* Cleanup
  ```bash
  docker stop aw-test && docker rm aw-test
  ```

----

## Troubleshooting

Remove all existing images: `docker rmi -f $(docker images -aq)`

### Build manually

```bash
docker build -f Dockerfile_production -t aw-test --build-arg "AW_VERSION=<VERSION>" --progress=plain --no-cache .
```

### Interactive

Execute a container in interactive mode:

**Debian**:

```bash
docker run --rm -it --entrypoint /bin/bash oxlorg/ansible-webui-mysql:0.9.0-debian
```

**Alpine**:

```bash
docker run --rm -it --entrypoint /bin/sh oxlorg/ansible-webui-mysql:0.9.0-alpine
```

### MySQL/MariaDB

* Start Test-DB

  ```bash
  docker run --detach --name test-mariadb --env MARIADB_ROOT_PASSWORD=test -p 3306 mariadb:latest
  ```

* Check port

  ```bash
  docker ps -a | grep test
  ```
  
* Enter container (*see above*)

* Connect to DB

  ```python3
  import MySQLdb
  db = MySQLdb.connect(host="<docker-host>",port=<port>,user="root",password="test")
  c = db.cursor()
  c.execute("select user,host from mysql.user")
  # 6
  c.fetchall()
  # (('root', '%'), ('healthcheck', '127.0.0.1'), ('healthcheck', '::1'), ('healthcheck', 'localhost'), ('mariadb.sys', 'localhost'), ('root', 'localhost'))
  ```
