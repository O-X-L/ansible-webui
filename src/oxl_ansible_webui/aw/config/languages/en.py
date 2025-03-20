from aw.config.main import config

# pylint: disable=C0301

# todo: api-endpoint responses (add lang-code to api responses)

EN = {
    # base
    'btn.add': 'Add',
    'btn.save': 'Save',
    'btn.discard': 'Discard',
    'btn.edit': 'Edit',
    'btn.clone': 'Clone',
    'btn.execute': 'Execute',
    'btn.delete': 'Delete',
    'btn.stop': 'Stop',
    'btn.logs': 'Logs',
    'btn.download': 'Download',
    'nav.lang': 'Language',
    'nav.darkLight': 'Dark/Light Mode Switch',
    'nav.docs': 'Documentation',
    'nav.repo': 'Open Source Repository',
    'nav.bugs': 'Report Bugs',
    'nav.logout': 'Log out',
    'footer.user': 'User',
    'footer.version': 'Version',
    'footer.oss': 'Open Source Usage',

    # common phrases
    'common.name': 'Name',
    'common.choices': 'Choices',
    'common.required': 'Required',
    'common.status': 'Status',
    'common.error': 'Error',
    'common.success': 'Action succeeded',
    'common.actions': 'Actions',
    'common.search': 'Search',
    'common.updated_at': 'Updated at',

    # auth
    'login.user': 'Username',
    'login.pwd': 'Password',
    'login.saveUser': 'Save Username',
    'login.btn': 'Login',
    'login.sso': 'SSO',
    'login.localUser': 'Local User',
    # home
    'home.dashboard': 'Dashboard',
    'home.jobs': 'Jobs',
    'home.logs': 'Logs',
    'home.repos': 'Repositories',
    'home.alerts': 'Alerts',
    'home.creds': 'Credentials',
    'alerts.user': 'Personal',
    'alerts.group': 'Group',
    'alerts.global': 'Global',
    'alerts.plugin': 'Plugin',

    # jobs
    'jobs.new': 'New Job',
    'jobs.edit': 'Edit Job',
    'jobs.execute': 'Execute Job',
    'jobs.job': 'Job',
    'jobs.info': 'Job Information',
    'jobs.info.execution': 'Execution Information',
    'jobs.info.next_run': 'Next Run',
    'jobs.info.last_run': 'Last Run',
    'jobs.info.duration': 'Duration',
    'jobs.info.failed': 'Failed',
    'jobs.execute.required_limit': 'A limit is required',
    'jobs.execute.required_var': 'Required variable missing',  # '<msg>: "<varname>"'
    'jobs.execute.required_credentials': 'Credentials are required',
    ## form fields
    'jobs.action.start': 'Job queued',
    'jobs.action.stop': 'Job stop initiated',
    'jobs.action.delete': 'Job deleted',
    'jobs.action.create': 'Job created',
    'jobs.action.update': 'Job updated',
    'jobs.form.name': 'Name',
    'jobs.form.repository': 'Repository',
    'jobs.form.playbook_file': 'Playbook File',
    'jobs.form.inventory_file': 'Inventory File',
    'jobs.form.comment': 'Comment',
    'jobs.form.schedule': 'Schedule',
    'jobs.form.cron': 'Schedule Cron',
    'jobs.form.enabled': 'Schedule Enabled',
    'jobs.form.limit': 'Limit',
    'jobs.form.tags': 'Tags',
    'jobs.form.tags_skip': 'Skip Tags',
    'jobs.form.mode_diff': 'Diff Mode',
    'jobs.form.mode_check': 'Check Mode (Try Run)',
    'jobs.form.environment_vars': 'Environmental Variables',
    'jobs.form.cmd_args': 'Commandline Arguments',
    'jobs.form.credentials_needed': 'Needs Credentials',
    'jobs.form.credentials_default': 'Default Job Credentials',
    'jobs.form.credentials_category': 'Credentials Category',
    'jobs.form.execution_prompts': 'Execution Prompts',
    'jobs.form.execution_prompts_enforce': 'Enforce Prompts',
    'jobs.form.verbosity': 'Verbosity',
    'jobs.form.credentials': 'Credentials',
    'jobs.form.prompt_limit_req': 'Require Limit',
    'jobs.form.prompt_credentials_req': 'Require Credentials',
    'jobs.form.prompt_fields': 'Fields to prompt',
    'jobs.form.prompt_vars': 'Variables to prompt',
    'jobs.form.prompt_name': 'Display Name',
    'jobs.form.prompt_varname': 'Variable Name',
    'jobs.form.prompt_kind': 'Kind',
    'jobs.form.prompt_regex': 'Validation Regex',
    'jobs.form.prompt_choice_text': 'Text',
    ## form help
    'jobs.form.help.playbook_file': 'Playbook to execute',
    'jobs.form.help.inventory_file': 'One or multiple inventory files/directories to include for the execution. '
                                     'Comma-separated list. For details see: '
                                     '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/'
                                     'intro_inventory.html">Ansible Docs - Inventory</a>',
    'jobs.form.help.repository': 'Used to define the static or dynamic source of your playbook directory structure. '
                                 f"Default is '{config['path_play']}'",
    'jobs.form.help.limit': 'Ansible inventory hosts or groups to limit the execution to.'
                            'For details see: '
                            '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html">'
                            'Ansible Docs - Limit</a>',
    'jobs.form.help.schedule': 'Schedule for running the job automatically. For format see: '
                                '<a href="https://crontab.guru/">crontab.guru</a>',
    'jobs.form.help.environment_vars': 'Environmental variables to be passed to the Ansible execution. '
                                       'Comma-separated list of key-value pairs. (VAR1=TEST1,VAR2=0)',
    'jobs.form.help.cmd_args': "Additional commandline arguments to pass to 'ansible-playbook'. "
                               "Can be used to pass extra-vars",
    'jobs.form.help.tags': 'For details see: '
                           '<a href="https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html">'
                           'Ansible Docs - Tags</a>',
    'jobs.form.help.mode_check': 'For details see: '
                                 '<a href="https://docs.ansible.com/ansible/2.8/user_guide/playbooks_checkmode.html">'
                                 'Ansible Docs - Check Mode</a>',
    'jobs.form.help.credentials_needed': 'If the job requires credentials to be specified '
                                         '(either as default or at execution-time; '
                                         'fallback are the user-credentials of the executing user)',
    'jobs.form.help.credentials_default': 'Specify job-level default credentials to use (required for scheduled execution)',
    'jobs.form.help.credentials_category': 'The credential category can be used for dynamic matching of '
                                           'user credentials at execution time',
    'jobs.form.help.enabled': 'En- or disable the schedule. Can be ignored if no schedule was set',
    'jobs.form.help.execution_prompts_required': 'Required job attributes and/or variables to prompt at custom execution. '
                                                 'Comma-separated list of key-value pairs.<br>'
                                                 "Variables can be supplied like so: 'var={VAR-NAME}#{DISPLAY-NAME}'<br>"
                                                 "Example: 'limit,check,var=add_user#User to add' ",
    'jobs.form.help.prompt_choices': 'Comma-separated list of choices.',
    'jobs.form.help.prompt_regex': 'You can use <a href="https://regex101.com/">Regex101.com</a> to test your input-validation. '
                                   'Make sure to select the "ECMAScript (Javascript)" flavor.',

    # credentials
    'creds.user': 'Personal',
    'creds.shared': 'Shared',
    'creds.new': 'New Credentials',
    'creds.info': 'Credentials Information',
    'creds.action.create': 'Credentials created',
    'creds.action.update': 'Credentials updated',
    'creds.action.delete': 'Credentials deleted',
    ## form fields
    'creds.form.category': 'Category',
    'creds.form.accounts': 'Accounts',
    'creds.form.secrets': 'Secrets',
    'creds.form.connect_user': 'Connect User',
    'creds.form.connect_pwd': 'Connect Password',
    'creds.form.ssh_key': 'SSH Key',
    'creds.form.become_user': 'Become User',
    'creds.form.become_pwd': 'Become Password',
    'creds.form.vault': 'Vault',
    'creds.form.vault_pwd': 'Vault Password',
    'creds.form.vault_file': 'Vault File',
    'creds.form.vault_id': 'Vault ID',
    ## form help
    'creds.form.help.vault_file': 'Path to the file containing your vault-password',
    'creds.form.help.vault_id': 'For details see: '
                                '<a href="https://docs.ansible.com/ansible/latest/vault_guide/'
                                'vault_managing_passwords.html">'
                                'Ansible Docs - Managing Passwords</a>',
    'creds.form.help.ssh_key': 'Provide an unencrypted SSH private key',
    'creds.form.help.category': 'The category of user credentials. Used for dynamic matching at execution time',

    # repositories
    'repos.static': 'Static / Local',
    'repos.git': 'Git',
    'repos.static.src': 'Path',
    'repos.git.src': 'Origin',
    'repos.info': 'Repository Information',
    'repos.new': 'New Repository',
    'repos.edit': 'Edit Repository',
    'repos.action.create': 'Repository created',
    'repos.action.update': 'Repository updated',
    'repos.action.delete': 'Repository deleted',
    'repos.action.download': 'Repository download initiated',

    ## form fields
    'repos.form.static_path': 'Path',
    'repos.form.git_origin': 'Origin',
    'repos.form.git_branch': 'Branch',
    'repos.form.git_credentials': 'Credentials',
    'repos.form.git_limit_depth': 'Limit Depth',
    'repos.form.git_lfs': 'LFS',
    'repos.form.git_playbook_base': 'Playbook Base-Directory',
    'repos.form.git_isolate': 'Isolate Directory',
    'repos.form.git_hook_pre': 'Pre-Hook',
    'repos.form.git_hook_post': 'Post-Hook',
    'repos.form.git_hook_cleanup': 'Cleanup-Hook',
    'repos.form.git_override_initialize': 'Override Initialize-Command',
    'repos.form.git_override_update': 'Override Update-Command',
    'repos.form.git_hooks': 'Hooks',
    'repos.form.git_options': 'Options',

    ## form help
    'repos.form.help.static_path': 'Path to the local static repository/playbook-base-directory',
    'repos.form.help.git_origin': "Full URL to the remote repository. "
                                  "Per example: '<a href=\"https://github.com/O-X-L/ansible-webui.git\">"
                                  "https://github.com/O-X-L/ansible-webui.git'</a>'",
    'repos.form.help.git_credentials': "Credentials for connecting to the origin. "
                                       "'Connect User', 'Connect Password' and 'SSH Private Key' are used",
    'repos.form.help.git_playbook_base': 'Relative path to the Playbook base-directory relative from the repository root',
    'repos.form.help.git_lfs': 'En- or disable checkout of Git-LFS files',
    'repos.form.help.git_isolate': 'En- or disable if one clone of the Git-repository should be used for all jobs. '
                                   'If enabled - the repository will be cloned/fetched on every job execution. '
                                   'This will have a negative impact on performance',
    'repos.form.help.git_hook_pre': 'Commands to execute before initializing/updating the repository. '
                                    'Comma-separated list of shell-commands',
    'repos.form.help.git_hook_post': 'Commands to execute after initializing/updating the repository. '
                                     'Comma-separated list of shell-commands',
    'repos.form.help.git_override_initialize': 'Advanced usage! Completely override the command used to initialize '
                                               '(clone) the repository',
    'repos.form.help.git_override_update': 'Advanced usage! Completely override the command used to update '
                                           '(pull) the repository',

    # logs
    'logs.job_logs': 'Logs of job',
    'logs.time': 'Time',
    'logs.time_start': 'Start time',
    'logs.time_start_short': 'Start',
    'logs.time_fin_short': 'End',
    'logs.command': 'Command',
    'logs.executed_by': 'Executed by',
    'logs.exec_log_file': 'Execution log file',
    'logs.exec_error_log_file': 'Execution error-log file',
    'logs.repo_log_file': 'Repository log file',
    'logs.repo_error_log_file': 'Repository error-log file',
    'logs.exec_finished': 'Execution finished!',
}
