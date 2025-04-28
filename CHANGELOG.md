# Changelog

## Version 1

tbd

----

## Version 0

### 0.8.6

Features:

* Reimplemented `System - Permissions` page
* Permission-audit logging 

Fixes:

* Better handling for execution-errors in logs-view
* MariaDB/MySQL connection-timeout fixes [#27](https://github.com/O-X-L/ansible-webui/issues/27)

----

### 0.8.5

Fixes:

* Migrate long VARCHAR fields to TEXT

----

### 0.8.4

Features:

* Bumped [AWS-SSM to version 1.2.707.0](https://github.com/aws/session-manager-plugin/releases/tag/1.2.707.0) (*Docker image oxlorg-ansible-webui-aws*)
* Security: Added job-queue validation

  This lowers the danger of an attack-vector that would utilize DB-write-access to execute jobs.

* Reimplemented `System - Environment` page
* Reimplemented `Alerts` page
* Frontend optimizations for mobile devices/small screens
* Improved logs-view
* Quick-save by pressing `Alt + S`

Fixes:

* Security: Hide DB-Password from System-Config view
* Issue when switching between Jobs in logs-list
* Multiple MariaDB/MySQL/PSQL fixes [#27](https://github.com/O-X-L/ansible-webui/issues/27)
* Frontend Cache-Invalidation on Version-Change

----

### 0.8.3

Fixes:

* Corrected Execution Failed-state
* Scrolling on mobile/small screens [#21](https://github.com/O-X-L/ansible-webui/issues/21)
* Show Execution errors on logs-view
* Credentials update-issues
* Load config-file before 'manage' actions
* Startup-Errors when using MariaDB/PSQL [#27](https://github.com/O-X-L/ansible-webui/issues/27)
* Regex-validation for Execution-prompts

Features:

* Ability to change Dashboard Stats-Time-Period

----

### 0.8.2

Fixes:

* Quote value of prompted extra vars [#23](https://github.com/O-X-L/ansible-webui/issues/23)
* SAML Authentication fixes [#4](https://github.com/O-X-L/ansible-webui/issues/4)
* Execution-issues from cli [#25](https://github.com/O-X-L/ansible-webui/issues/25)

Features:

* Ability to supply one-off credentials at execution [#18](https://github.com/O-X-L/ansible-webui/issues/18)
* MariaDB, MySQL and PostgreSQL Support [#24](https://github.com/O-X-L/ansible-webui/issues/24)
* Passing AW username & email as env-vars to Ansible [#5](https://github.com/O-X-L/ansible-webui/issues/5)

Chore:

* Cleaned-up Credentials-API

----

### 0.8.1

* Completely refactored frontend (SvelteJS & TailwindCSS)
* Permission checks for scheduled jobs (job-owners) [c40f049c](https://github.com/O-X-L/ansible-webui/commit/c40f049c6a248ec682bbb03bf25dff4632381d91)
* Fix for job-form file-browsing when using isolated git-repo [#19](https://github.com/O-X-L/ansible-webui/issues/19)
* Updated some API endpoints
* Implemented new Stats-Endpoint
* Some basic charts on the WebUI dashboard 
* Logging of user logon/logoff/failed-logon

**BREAKING CHANGES**:

* Existing **Execution Prompts** are NOT compatible!
  You will have to manually re-configure them.
* Existing **Permissions** are NOT compatible!
  In this version the permission-system is only configurable using the Django-Admin interface.
  It will be refactored in the next releases [#15](https://github.com/O-X-L/ansible-webui/issues/15)

----

### 0.0.25

* Handle edge-case error of schedule
* Handle jobs without credentials
* Cleanup execution status if thread stopped
* Fix editing of credentials (*ssk-key invalid*)

----

### 0.0.24-3

* Disable data-refresh if in background
* Allow to save current form by using SHIFT+S
* Add missing become- and connect-user

----

### 0.0.24-2

* Cleanup job-stati on startup
* Fix Log-view expand-on-waiting behavior
* Fix known_hosts cli-argument

----

### 0.0.24

* Fix for Nginx config-example
* Fix for Log-Directory creation
* Enable SSH host-key checking by default (*ansible-runner seem to disable it by default*) 
* Enhanced Buttons of Log Live-View
* Git-Repository Cleanup-Hook (Post Job-Run)
* Refactored runtime secret-handling ([ansible-runner](https://ansible.readthedocs.io/projects/runner/en/latest/intro))
* Disabling quick-execution button if custom-execution form is open

----

### 0.0.23

* Fix for possible XSS
* Implemented [Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) to protect against XSS and injections
* Migrated vendor CSS/JS to be included in the package
* Option to enforce execution prompts
* Fix use of GitHub private repositories

----

### 0.0.22

* Improved [custom execution prompts](https://webui.ansibleguy.net/usage/jobs.html#execute)

----

### 0.0.21

* Added [validation against XSS](https://github.com/ansibleguy/webui/issues/44)
* Execution prompts/forms to provide job overrides

----

### 0.0.20

* Fixes for Alert Mails

----

### 0.0.19

* Enhanced graceful stop
* Alerting
  * E-Mail
  * Plugin System
* Credential categories
* Fix for SSH-RSA key usage (*error in libcrypto*)
* Fix for [Log-View API usage](https://github.com/ansibleguy/webui/issues/36)

----

### 0.0.18

* Support for Config-File
  * Moved SAML config to general Config-File
* Added Execution-Duration to UI
* Allow to save Username at Login-Form
* Multiple fixes for UI
* Increased maximum execution-command length

----

### 0.0.17

* [Integration for SAML-SSO Identity Providers](https://webui.ansibleguy.net/usage/authentication.html)

----

### 0.0.16

* Job-Form Selection
  * Auto-Completion via Tab-Key
  * Select using Up/Down/Enter Keys
* Ability to clone existing jobs
* Ability to sort jobs and repositories
* Split-up Repository Forms
* Fix for Git-Clone Depth

----

### 0.0.14 / 0.0.15

* SQLite connection optimizations
* Database version-upgrade enhancements
* Allow to change listen address
* Fixed DB-migrations for PIP-based installation

----

### 0.0.13

* Multiple UI improvements
  * Job Form
  * Logs UI
  * Added timezone to datetime
  * Style non-existent log-files
* HTTPS support
* [ARA config integration](https://webui.ansibleguy.net/usage/integrations.html)
* Global Environmental-Variables for Jobs

----

### 0.0.12

* Better [Trademark compliance](https://github.com/ansible/logos/blob/main/TRADEMARKS.md#53-unpermitted-uses-we-consider-infringing)
* Support for custom Logo
* Minor fixes

----

### 0.0.10 / 0.0.11

**Features:**

* Git Repository support - `Jobs - Repositories` UI
* Form-Validation enhancements
  * Checking if provided file/directory exists
  * Enhanced job-file file-browsing
* Privilege System - Manager Groups
* Password-Change UI
* Docker
  * Support to [run as unprivileged user](https://webui.ansibleguy.net/usage/docker.html#unprivileged)
  * [Image with AWS-CLI support](https://webui.ansibleguy.net/usage/docker.html#aws-cli-support)
* Enhanced handling of [SQLite Write-Locks](https://github.com/ansibleguy/webui/issues/6)


### 0.0.9

**Features:**

* `System - Config` UI
* Support for SSH `known_hosts` file

**Fixes:**

* Dark-Mode fixes
* Multiple fixes for SSH connections

----

### 0.0.8

* Credentials
  * Global/Shared credentials
  * User-specific credentials
  * Credential permissions
* Basic Integration Tests
* Support for dockerized deployments
* Support to run behind Proxy (Nginx tested)
* Dynamic pulling of UI data using JS

----

### 0.0.7

* Job Permissions
* Job Output UI
* Refactored UI to use Ajax for dynamic Updates
* System - Environment UI

----

### 0.0.6

* Job Logs
  * Realtime following of Output
* Ability to stop running jobs
* Fixes for secret handling

----

### 0.0.5

* [Ansible-Runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/) integration
  * Ability to execute simple playbooks successfully
* Scheduled jobs working
* Manual job execution using UI and API working
* Job-Management UI with basic result stats
* Job-Secrets are saved encrypted

----

### 0.0.4

* Very basic job management
* Scheduler to run jobs by cron-based expressions
* Queue to process manually triggered jobs
