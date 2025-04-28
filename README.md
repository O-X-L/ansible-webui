# Simple WebUI for using Ansible

[![Lint](https://github.com/O-X-L/ansible-webui/actions/workflows/lint.yml/badge.svg?branch=latest)](https://github.com/O-X-L/ansible-webui/actions/workflows/lint.yml)
[![Test Frontend](https://github.com/O-X-L/ansible-webui/actions/workflows/test_frontend.yml/badge.svg?branch=latest)](https://github.com/O-X-L/ansible-webui/actions/workflows/test_frontend.yml)
[![Test Backend](https://github.com/O-X-L/ansible-webui/actions/workflows/test_backend.yml/badge.svg?branch=latest)](https://github.com/O-X-L/ansible-webui/actions/workflows/test_backend.yml)
[![Test Job-Execution](https://github.com/O-X-L/ansible-webui/actions/workflows/test_job_execution.yml/badge.svg?branch=latest)](https://github.com/O-X-L/ansible-webui/actions/workflows/test_job_execution.yml)
[![Test Databases](https://github.com/O-X-L/ansible-webui/actions/workflows/test_dbs.yml/badge.svg?branch=latest)](https://github.com/O-X-L/ansible-webui/actions/workflows/test_dbs.yml)

**DISCLAIMER**: This is an **unofficial community project**! Do not confuse it with the vanilla [Ansible](https://ansible.com/) product!

The goal is to allow users to quickly install & run a WebUI for using Ansible locally.

Keep it simple.

[![Tech-Stack](https://skillicons.dev/icons?i=ansible,django,svelte,tailwind)](#)

<img src="https://raw.githubusercontent.com/O-X-L/ansible-webui/refs/heads/latest/docs/source/_static/img/intro.gif" alt="Intro GIF" width="70%"/>

----

## Setup

### Local - PIP

Requires Python >=3.10

```bash
# install
python3 -m pip install oxl-ansible-webui

# run
oxl-ansible-webui
```

### Docker

Images: [ansible-webui](https://hub.docker.com/r/oxlorg/ansible-webui), [ansible-webui-unprivileged](https://hub.docker.com/r/oxlorg/ansible-webui-unprivileged), [ansible-webui-mysql](https://hub.docker.com/r/oxlorg/ansible-webui-mysql), [ansible-webui-psql](https://hub.docker.com/r/oxlorg/ansible-webui-psql), [ansible-webui-aws](https://hub.docker.com/r/oxlorg/ansible-webui-aws)

```bash
docker image pull oxlorg/ansible-webui:latest
docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 oxlorg/ansible-webui:latest

# or with persistent data (volumes: /data = storage for logs & DB, /play = ansible playbook base-directory)
docker run -d --name ansible-webui --publish 127.0.0.1:8000:8000 --volume $(pwd)/ansible/data:/data --volume $(pwd)/ansible/play:/play oxlorg/ansible-webui:latest
```

### Optional Dependencies

```bash
pip install oxl-ansible-webui[mysql]
pip install oxl-ansible-webui[psql]
pip install oxl-ansible-webui[ara]
pip install oxl-ansible-webui[saml]
```

----

## Demo

Check out the demo at: [demo.ansible-webui.OXL.app](https://demo.ansible-webui.OXL.app)

Login: User `demo`, Password `Ansible1337`

----

## Usage

[Documentation](http://ansible-webui.OXL.app/)

[![Docs Uptime](https://status.oxl.at/api/v1/endpoints/1--oxl_ansible-webui-documentation/uptimes/7d/badge.svg)](https://status.oxl.at/endpoints/1--oxl_ansible-webui-documentation)

----

## Contribute

Feel free to contribute to this project using [pull-requests](https://github.com/O-X-L/ansible-webui/pulls), [issues](https://github.com/O-X-L/ansible-webui/issues) and [discussions](https://github.com/O-X-L/ansible-webui/discussions)!

What we need:

* Testers and [feedback](https://github.com/O-X-L/ansible-webui/discussions)
* More [Test-cases](https://github.com/O-X-L/ansible-webui/tree/latest/test/integration)
* [Translations](https://github.com/O-X-L/ansible-webui/blob/latest/CONTRIBUTE.md#translations) for your language(s)

See also: [Contributing](https://github.com/O-X-L/ansible-webui/blob/latest/CONTRIBUTE.md)

<img src="https://contrib.rocks/image?repo=O-X-L/ansible-webui&max=5" />

<img src="https://contrib.rocks/image?repo=ansibleguy/webui&max=5" />

----

## Roadmap

### V1.0

- [x] [Refactor WebUI => SvelteJS & TailwindCSS](https://github.com/O-X-L/ansible-webui/issues/4)
- [ ] [Data-update over Websockets](https://github.com/O-X-L/ansible-webui/issues/3)
- [x] Django 5.1

### Full

- [x] Ansible Config

  - [x] Static Playbook-Directory

  - [x] Git Repository support

- [ ] Users

  - [x] Management interface (Django built-in)

  - [x] Groups & Job Permissions

  - [ ] [LDAP integration](https://github.com/django-auth-ldap/django-auth-ldap)

  - [x] [SAML SSO integration](https://github.com/grafana/django-saml2-auth)

- [ ] Jobs

  - [x] Execute Ansible using [ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/)

    - [x] Scheduled execution (Cron-Format)

    - [x] Manual/immediate execution

    - [x] Custom Execution-Forms

    - [ ] Support for [ad-hoc commands](https://docs.ansible.com/ansible/latest/command_guide/intro_adhoc.html)

    - [ ] Support for [Process-Isolation](https://ansible.readthedocs.io/projects/runner/en/stable/standalone/#running-with-process-isolation)

  - [x] Job Logging

    - [x] Write job metadata to database

    - [x] Write full job-logs to Filesystem

  - [x] Secret handling (Connect, Become, Vault)

    - [x] User-specific job credentials

  - [x] Alerting on Failure

    - [x] E-Mail

    - [x] Support for external Plugins (*simple Interface for Scripts*)

- [ ] WebUI

  - [x] Job Dashboard

      Status, Execute, Time of last & next execution, Last run User, Links to Warnings/Errors

  - [x] Job Output

      Follow the jobs output in realtime

  - [ ] Job Errors

      UI that allows for easy error analysis. Access to logs and provide links to possible solutions

  - [x] Show Ansible Running-Config

  - [x] Show Ansible Collections

    - [ ] Check Collections for available updates (Galaxy + GitHub releases)

  - [x] Mobile Support

  - [x] Multi-Language Support

- [ ] API

  - [x] Manage and execute Jobs

- [x] Database

  - [x] Support for MySQL

- [ ] Testing

  - [ ] Unit Tests

  - [ ] Integration Tests

    - [x] WebUI checks

    - [x] API Endpoints

    - [x] Job Execution

    - [ ] Permission system

----

# License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)

For dependencies see: [attributions](https://github.com/O-X-L/ansible-webui/tree/latest/attributions) 
