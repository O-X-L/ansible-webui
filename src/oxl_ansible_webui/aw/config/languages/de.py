from aw.config.main import config

DE = {
    # base
    'btn.add': 'Neu',
    'btn.save': 'Speichern',
    'btn.discard': 'Verwerfen',
    'btn.edit': 'Bearbeiten',
    'btn.clone': 'Kopieren',
    'btn.close': 'Schließen',
    'btn.execute': 'Ausführen',
    'btn.delete': 'Löschen',
    'btn.stop': 'Stoppen',
    'btn.logs': 'Logs',
    'btn.pause': 'Pausieren',
    'btn.download': 'Downloaden',
    'btn.update': 'Aktualisieren',
    'btn.scroll_down': 'Runter scrollen',
    'btn.encrypt': 'Ansible-Vault Verschlüsseln',
    'nav.home': 'Home',
    'nav.system': 'System',
    'nav.lang': 'Sprache',
    'nav.darkLight': 'Dunkel/Hell Modus umschalten',
    'nav.docs': 'Dokumentation',
    'nav.repo': 'Open Source Repository',
    'nav.bugs': 'Fehler melden',
    'nav.donate': 'Projekt unterstützen',
    'nav.user_settings': 'Benutzer Einstellungen',
    'nav.logout': 'Abmelden',
    'footer.user': 'Nutzer',
    'footer.oss': 'Open Source Nutzung',
    'footer.oss.frontend': 'Frontend',
    'footer.oss.backend': 'Backend',
    'footer.oss.license': 'Lizenz',

    # common phrases
    'common.name': 'Name',
    'common.choices': 'Optionen',
    'common.required': 'Erforderlich',
    'common.status': 'Status',
    'common.error': 'Fehler',
    'common.success': 'Aktion erfolgreich',
    'common.actions': 'Aktionen',
    'common.search': 'Suche',
    'common.updated_at': 'Aktualisiert um',
    'common.created_at': 'Erstellt um',
    'common.click_to_copy': 'zum Kopieren klicken',
    'common.comment': 'Kommentar',
    'common.invalid_value': 'Feld hat ungültigen Wert',  # '<msg>: "<field>"'
    'common.invalid_form': 'Ungültige Eingaben erkannt',  # not field-specific..
    'common.version': 'Version',
    'common.path': 'Pfad',
    'common.setting': 'Einstellung',
    'common.value': 'Wert',
    'common.kind': 'Art',
    'common.id': 'ID',

    # auth
    'login.user': 'Benutzer',
    'login.pwd': 'Passwort',
    'login.saveUser': 'Benutzername speichern',
    'login.btn': 'Anmelden',
    'login.sso': 'SSO',
    'login.localUser': 'Lokaler Benutzer',
    # home
    'home.dashboard': 'Dashboard',
    'home.jobs': 'Jobs',
    'home.logs': 'Logs',
    'home.repos': 'Repositories',
    'home.alerts': 'Alarme',
    'home.creds': 'Zugangsdaten',

    # dashboard
    'db.stats': 'Statistiken',
    'db.chart.exec_over_time': 'Ausführungen über Zeit',
    'db.chart.exec_by_user': 'Ausführungen bei Nutzer',
    'db.chart.exec_results_by_job': 'Resultate nach Job',
    'db.chart.exec_results_by_host': 'Resultate nach Host',
    'db.runs': 'Ausführungen',
    'db.time.select': 'Zeitraum',
    'db.time.minutes': 'Minuten',
    'db.time.hours': 'Stunden',
    'db.time.days': 'Tage',
    'db.time.weeks': 'Wochen',
    'db.time.months': 'Monate',

    # jobs
    'jobs.new': 'Neuer Job',
    'jobs.edit': 'Job bearbeiten',
    'jobs.execute': 'Job ausführen',
    'jobs.job': 'Job',
    'jobs.info': 'Job Information',
    'jobs.info.execution': 'Information zur Ausführung',
    'jobs.info.next_run': 'Nächste Ausführung',
    'jobs.info.last_run': 'Letzte Ausführung',
    'jobs.info.duration': 'Laufzeit',
    'jobs.info.running': 'Aktiv',
    'jobs.info.failed': 'Fehlgeschlagen',
    'jobs.info.succeeded': 'Erfolgreich',
    'jobs.info.skipped': 'Übersprungen',
    'jobs.info.scheduled': 'Geplant',
    'jobs.info.unreachable': 'Nicht erreichbar',
    'jobs.info.changed': 'Geändert',
    'jobs.execute.tmp_credentials': 'Zugangsdaten angeben',
    'jobs.execute.required_limit': 'Eine Limit ist erforderlich',
    'jobs.execute.required_var': 'Erforderliche Variable fehlt',  # '<msg>: "<varname>"'
    'jobs.execute.required_credentials': 'Zugangsdaten sind erforderlich',
    'jobs.execute.regex_mismatch': 'Eingabe entspricht nicht dem erforderlichen Format',
    ## form fields
    'jobs.action.start': 'Job in Warteschlange',
    'jobs.action.stop': 'Job-Stop initiiert',
    'jobs.action.delete': 'Job gelöscht',
    'jobs.action.create': 'Job erstellt',
    'jobs.action.update': 'Job aktualisiert',
    'jobs.action.exec_delete': 'Ausführung gelöscht',
    'jobs.form.repository': 'Repository',
    'jobs.form.playbook_file': 'Playbook Datei',
    'jobs.form.inventory_file': 'Inventory Datei',
    'jobs.form.file_browse.empty': 'Leer',
    'jobs.form.schedule': 'Geplante Ausführung',
    'jobs.form.cron': 'Zeitplan Cron',
    'jobs.form.enabled': 'Zeitplan aktiviert',
    'jobs.form.limit': 'Limit',
    'jobs.form.tags': 'Tags',
    'jobs.form.tags_skip': 'Tags zu Überspringen',
    'jobs.form.mode_diff': 'Diff-Modus',
    'jobs.form.mode_check': 'Check-Modus (Try Run)',
    'jobs.form.environment_vars': 'Umgebungsvariablen',
    'jobs.form.cmd_args': 'Kommandozeilen-Argumente',
    'jobs.form.credentials_needed': 'Zugangsdaten erforderlich',
    'jobs.form.credentials_default': 'Standard-Zugangsdaten',
    'jobs.form.credentials_category': 'Zugangsdaten-Kategorie',
    'jobs.form.execution_prompts': 'Ausführungs-Abfragen',
    'jobs.form.execution_prompts_enforce': 'Abfragen erzwingen',
    'jobs.form.verbosity': 'Verbosity',
    'jobs.form.credentials': 'Zugangsdaten',
    'jobs.form.prompt_limit_req': 'Limit erzwingen',
    'jobs.form.prompt_credentials_req': 'Zugangsdaten erforderlich',
    'jobs.form.prompt_credentials_tmp': 'Temporäre Zugangsdaten',
    'jobs.form.prompt_fields': 'Abzufragende Felder',
    'jobs.form.prompt_vars': 'Abzufragende Variablen',
    'jobs.form.prompt_name': 'Anzeigename',
    'jobs.form.prompt_varname': 'Variablen-Name',
    'jobs.form.prompt_regex': 'Validierungs-Regex',
    'jobs.form.prompt_choice_text': 'Text',
    ## form help
    'jobs.form.help.playbook_file': 'Auszuführendes Playbook',
    'jobs.form.help.inventory_file': 'Eine oder mehrere Inventardateien/-verzeichnisse, die für die Ausführung genutzt werden sollen. '
                                     'Durch Kommas getrennte Liste. Weitere Informationen: '
                                     '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/'
                                     'intro_inventory.html">Ansible Docs - Inventory</a>',
    'jobs.form.help.repository': 'Wird verwendet, um die statische oder dynamische Quelle der Playbook-Verzeichnisstruktur zu definieren. '
                                 f"Der Standardwert lautet: '{config['path_play']}'",
    'jobs.form.help.limit': 'Ansible-Inventar-Hosts oder -Gruppen, auf die die Ausführung beschränkt werden soll. '
                            'Weitere Informationen: '
                            '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html">'
                            'Ansible Docs - Limit</a>',
    'jobs.form.help.schedule': 'Zeitplan für die automatische Ausführung des Auftrags. Für das Format siehe:'
                               '<a href="https://crontab.guru/">crontab.guru</a>',
    'jobs.form.help.environment_vars': 'Umgebungsvariablen die an Ansible übergeben werden sollen. '
                                       'Durch Kommas getrennte Liste von Schlüssel-Wert-Paaren. (VAR1=TEST1,VAR2=0)',
    'jobs.form.help.cmd_args': "Zusätzliche Befehlszeilenargumente, die an 'ansible-playbook' übergeben werden sollen. "
                               "Kann zum Übergeben von zusätzlichen Variablen (extra-vars) verwendet werden.",
    'jobs.form.help.tags': 'Weitere Informationen: '
                           '<a href="https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html">'
                           'Ansible Docs - Tags</a>',
    'jobs.form.help.mode_check': 'Weitere Informationen: '
                                 '<a href="https://docs.ansible.com/ansible/2.8/user_guide/playbooks_checkmode.html">'
                                 'Ansible Docs - Check Mode</a>',
    'jobs.form.help.credentials_needed': 'Ob Zugangsdaten angegeben werden müssen '
                                         '(entweder als Standard oder zum Zeitpunkt der Ausführung; '
                                         'als Fallback dienen die Zugangsdaten des ausführenden Benutzers)',
    'jobs.form.help.credentials_default': 'Standard-Zugangsdaten für diesen Job (erforderlich für die geplante Ausführung).',
    'jobs.form.help.credentials_category': 'Die Zugangsdaten-Kategorie kann zur dynamischen Zuordnung von '
                                           'Benutzeranmeldeinformationen zur Ausführungszeit verwendet werden.',
    'jobs.form.help.enabled': 'Die geplante Ausführung aktivieren oder deaktivieren. '
                              'Kann ignoriert werden, wenn kein Zeitplan festgelegt wurde.',
    'jobs.form.help.prompt_choices': 'Komma-separierte Liste von Optionen.',
    'jobs.form.help.prompt_regex': '<a href="https://regex101.com/">Regex101.com</a> kann dazu genutzt werden, um die '
                                   'Eingabevalidierung zu testen. '
                                   "Die Variante 'ECMAScript (Javascript)' muss ausgewählt werden.",

    # credentials
    'creds.edit': 'Zugangsdaten bearbeiten',
    'creds.user': 'Persönliche',
    'creds.shared': 'Geteilte',
    'creds.new': 'Neuer Job',
    'creds.info': 'Informationen zu Zugangsdaten',
    'creds.vault_encrypt': 'Ansible-Vault verschlüsseln',
    'creds.action.create': 'Zugangsdaten erstellt',
    'creds.action.update': 'Zugangsdaten aktualisiert',
    'creds.action.delete': 'Zugangsdaten gelöscht',
    'creds.action.vault_encrypt': 'Text verschlüsselt',
    ## form fields
    'creds.form.category': 'Kategorie',
    'creds.form.accounts': 'Konten',
    'creds.form.secrets': 'Geheimnisse',
    'creds.form.connect_user': 'Verbindungs-Benutzer',
    'creds.form.connect_pwd': 'Verbindungs-Passwort',
    'creds.form.ssh_key': 'SSH Key',
    'creds.form.become_user': 'Admin-Benutzer',
    'creds.form.become_pwd': 'Admin-Passwort',
    'creds.form.vault': 'Vault',
    'creds.form.vault_pwd': 'Vault Passwort',
    'creds.form.vault_file': 'Vault File',
    'creds.form.vault_id': 'Vault ID',
    'creds.form.vault_encrypt': 'Text zu verschlüsseln',
    ## form help
    'creds.form.help.vault_file': 'Pfad zur Datei, die das Ansible-Vault Passwort beinhaltet',
    'creds.form.help.vault_id': 'Weitere Informationen: '
                                '<a href="https://docs.ansible.com/ansible/latest/vault_guide/'
                                'vault_managing_passwords.html">'
                                'Ansible Docs - Managing Passwords</a>',
    'creds.form.help.ssh_key': 'Ein unverschlüsselter, privater SSH-Schlüssel',
    'creds.form.help.category': 'Die Kategorie der Zugangsdaten des Benutzers. '
                                'Wird für die dynamische Zuordnung zur Ausführungszeit verwendet.',
    'creds.form.help.vault_encrypt': 'Text, der via Ansible-Vault verschlüsselt werden soll. '
                                     'Weitere Informationen: '
                                     '<a href="https://docs.ansible.com/ansible/latest/vault_guide/index.html">'
                                     'Ansible Docs - Vault Guide</a>',

    # repositories
    'repos.static': 'Statisch / Lokal',
    'repos.git': 'Git',
    'repos.static.src': 'Pfad',  # common.path
    'repos.git.src': 'Origin',
    'repos.info': 'Repository Information',
    'repos.new': 'Neues Repository',
    'repos.edit': 'Repository bearbeiten',
    'repos.action.create': 'Repository erstellt',
    'repos.action.update': 'Repository aktualisiert',
    'repos.action.delete': 'Repository gelöscht',
    'repos.action.download': 'Repository-Download initiiert',

    ## form fields
    'repos.form.git_origin': 'Origin',
    'repos.form.git_branch': 'Branch',
    'repos.form.git_credentials': 'Zugangsdaten',
    'repos.form.git_limit_depth': 'Tiefe limitieren',
    'repos.form.git_lfs': 'LFS',
    'repos.form.git_playbook_base': 'Playbook Basis-Verzeichnis',
    'repos.form.git_isolate': 'Verzeichnis isolieren',
    'repos.form.git_timeout': 'Maximale Laufzeit von Kommandos',
    'repos.form.git_hook_pre': 'Pre-Hook',
    'repos.form.git_hook_post': 'Post-Hook',
    'repos.form.git_hook_cleanup': 'Cleanup-Hook',
    'repos.form.git_override_initialize': 'Initialisierungsbefehl überschreiben',
    'repos.form.git_override_update': 'Update-Befehl überschreiben',
    'repos.form.git_hooks': 'Hooks',
    'repos.form.git_options': 'Optionen',

    ## form help
    'repos.form.help.static_path': 'Pfad zum lokalen statischen Repository/Playbook-Basisverzeichnis',
    'repos.form.help.git_origin': "Vollständige URL zum Remote-Repository. "
                                  "Beispiel: '<a href=\"https://github.com/O-X-L/ansible-webui.git\">"
                                  "https://github.com/O-X-L/ansible-webui.git'</a>'",
    'repos.form.help.git_credentials': "Zugangsdaten für die Verbindung zum Git-Server. "
                                       "'Verbindungs-Benutzer', 'Verbindungs-Passwort' und 'Privater SSH-Key' "
                                       "werden verwendet.",
    'repos.form.help.git_playbook_base': 'Relativer Pfad zum Basis-Playbook-Verzeichnis, '
                                         'relativ zum Basisverzeichnis des Repositorys',
    'repos.form.help.git_lfs': 'De-/Aktiviert das Herunterladen von Git-LFS-Dateien.',
    'repos.form.help.git_isolate': 'De-/Aktiviert die Nutzung eines einzelne Repository-Klons für alle Job-Ausführungen. '
                                   'Wenn aktiviert, wird das Repository bei jeder Jobausführung geklont/abgerufen. '
                                   'Dies führt zu einer Verzögerung des Start von Jobs (abhängig von der Größe des Repositorys).',
    'repos.form.help.git_hook_pre': 'Befehle, die vor der Initialisierung/Aktualisierung des Repositorys ausgeführt werden müssen. '
                                    'Komma-Separierte Liste von Shell-Kommandos',
    'repos.form.help.git_hook_post': 'Befehle, die nach der Initialisierung/Aktualisierung des Repositorys ausgeführt werden sollen. '
                                     'Komma-Separierte Liste von Shell-Kommandos',
    'repos.form.help.git_override_initialize': 'Fortgeschrittene Nutzung! '
                                               'Überschreibt den Befehl zum Initialisieren (Klonen) des Repositorys vollständig.',
    'repos.form.help.git_override_update': 'Fortgeschrittene Nutzung! '
                                           'Überschreibt den Befehl zum Aktualisieren (Pull) des Repositorys vollständig.',

    # logs
    'logs.all_jobs': 'Alle Jobs',
    'logs.exec_count': 'Anzahl der Ausführungen',
    'logs.job_logs': 'Logs des Jobs',
    'logs.time': 'Zeit',
    'logs.time_start': 'Startzeit',
    'logs.time_start_short': 'Start',
    'logs.time_fin_short': 'Ende',
    'logs.command': 'Kommando',
    'logs.executed_by': 'Gestartet durch',
    'logs.exec_log_file': 'Ausführung Log-Datei',
    'logs.exec_error_log_file': 'Ausführung Fehler-Log-Datei',
    'logs.repo_log_file': 'Repository Log-Datei',
    'logs.repo_error_log_file': 'Repository Fehler-Log-Datei',
    'logs.exec_finished': 'Ausführung abgeschlossen!',
    'logs.exec_failed': 'Ausführung fehlgeschlagen!',
    'logs.error_short': 'Zusammenfassung',
    'logs.error_medium': 'Fehler',

    # system
    'system.settings': 'Einstellungen',
    'system.permission': 'Berechtigungen',
    'system.environment': 'Umgebung',
    'system.api_keys': 'API Keys',
    'system.admin': 'Admin',
    'system.api_docs': 'API Docs',
    'system.ssh_hostkey': 'SSH Hostkeys',

    # api-keys
    'api_keys.token': 'Token',
    'api_keys.key': 'Schlüssel',
    'api_keys.new': 'Neues API-Schlüsselpaar',
    'api_keys.action.create': 'API-Schlüssel erstellt',
    'api_keys.action.delete': 'API-Schlüssel gelöscht',

    # config
    'config.paths': 'Pfade',
    'config.mailing': 'E-Mail',
    'config.execution': 'Ausführung',
    'config.internal': 'Intern',
    'config.action.update': 'Einstellungen aktualisiert',
    'config.is_read_only': 'Diese Einstellung ist schreibgeschützt, da sie als Umgebungsvariable gesetzt wurde!',

    ## form fields
    'config.form.path_run': 'Laufzeitverzeichnis',
    'config.form.path_play': 'Playbook-Basisverzeichnis',
    'config.form.path_log': 'Verzeichnis für Ausführungs-Logs',
    'config.form.path_template': 'Verzeichnis für Vorlagen (Templates)',
    'config.form.run_timeout': 'Maximale Laufzeit für Ausführungen',
    'config.form.session_timeout': 'Zeitlimit für WebUI-Sitzungen',
    'config.form.path_ansible_config': 'Ansible-Konfigurationsdatei',
    'config.form.path_ssh_known_hosts': 'SSH Known-Hosts Datei',
    'config.form.debug': 'Debug-Modus',
    'config.form.audit_log': 'Audit-Protokollierung',
    ### env-vars
    'config.form.timezone': 'Zeitzone',
    'config.form.db': 'Datenbank',
    'config.form.hostnames': 'Hostnamen',
    'config.form.proxy': 'Proxy in Nutzung',
    'config.form.db_migrate': 'automatische Datenbank-Aktualisierung',
    'config.form.serve_static': 'Bereitstellung statischer Dateien',
    'config.form.deployment': 'Umgebung',
    'config.form.version': 'Ansible-WebUI Version',
    'config.form.logo_url': 'URL zu einem zu verwendenden Logo',
    'config.form.ara_server': 'ARA Server URL',
    'config.form.global_environment_vars': 'Globale Umgebungsvariablen',
    'config.form.auth_mode': 'Authentifizierungsmodus',
    'config.form.saml_config': 'SAML Konfigurationsdatei',
    'config.form.address': 'Listen Address',
    'config.form.port': 'Listen Port',
    'config.form.ssl_file_crt': 'SSL Zertifikat',
    'config.form.ssl_file_key': 'SSL Privater Schlüssel',
    'config.form.mail_server': 'E-Mail Server',
    'config.form.mail_transport': 'E-Mail Transport',
    'config.form.mail_ssl_verify': 'E-Mail SSL Verifizierung',
    'config.form.mail_sender': 'E-Mail Absenderadresse',
    'config.form.mail_user': 'E-Mail Login Benutzer',
    'config.form.mail_pass': 'E-Mail Login Passwort',
    ## form help
    'config.form.help.path_run': 'Basisverzeichnis für <a href="https://ansible.readthedocs.io/projects/runner/en/latest/intro/">'
                                 'Ansible-Runner Laufzeitdateien</a>',
    'config.form.help.path_play': 'Pfad zum <a href="https://docs.ansible.com/ansible/2.8/user_guide/'
                                  'playbooks_best_practices.html#directory-layout">Ansible-Basis-/Playbook-Verzeichnis</a>',
    'config.form.help.path_log': 'Pfad unter dem die vollständigen Job-Logs gespeichert werden',
    'config.form.help.path_template': 'Pfad unter dem individuelle Vorlagen (Templates) gespeichert sind',
    'config.form.help.path_ansible_config': 'Pfad zu einer <a href="https://docs.ansible.com/ansible/latest/installation_guide'
                                            '/intro_configuration.html#configuration-file">Ansible Konfigurationsdatei</a>',
    'config.form.help.path_ssh_known_hosts': 'Pfad zu einer <a href="https://en.wikibooks.org/wiki/OpenSSH/'
                                             'Client_Configuration_Files#~/.ssh/known_hosts">SSH known_hosts Datei</a>',
    'config.form.help.debug': 'Debug-Modus aktivieren. Nicht dauerhaft auf produktiven Systemen aktivieren! '
                              'Dies kann mögliche Angriffsvektoren öffnen. '
                              'Der Dienst muss möglicherweise neu gestartet werden, um die Änderung zu übernehmen.',
    'config.form.help.audit_log': 'Audit-Protokollierung aktivieren. Alle Erstellungs-/Aktualisierungs-/Löschvorgänge '
                                  'werden in der Datenbank protokolliert und können in der Admin-Benutzeroberfläche unter '
                                  '<a href="/ui/system#admin">System - Admin - Administration - Log entries</a>',
    'config.form.help.logo_url': 'Beispiel: '
                                 '<a href="https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo'
                                 '/vscode-ansible.svg">'
                                 'https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo/vscode-ansible.svg'
                                 '</a>',
    'config.form.help.ara_server': 'URL eines ARA Servers.Provide the URL to your ARA server. '
                                   'Kann zum Erfassen von Jobstatistiken verwendet werden. '
                                   'Weitere Informationen: '
                                   '<a href="https://ansible-webui.OXL.app/admin/integrations.html">'
                                   'Dokumentation - Integrationen</a>',
    'config.form.help.global_environment_vars': 'Umgebungsvariablen definieren, die bei jeder Job-Ausführung gesetzt werden. '
                                                'Komma-Separierte Liste von Schlüssel-Wert-Paaren. (VAR1=TEST1,VAR2=0)',
    'config.form.help.mail_server': 'Für Benachrichtigungs-E-Mails zu verwendender Mailserver. '
                                    'Kombination aus Server und Port (Standard: 25)',
    'config.form.help.mail_ssl_verify': 'SSL-Zertifikat-Verifizierung de-/aktivieren. '
                                        'Wenn aktiviert, muss das Zertifikat SAN den FQDN des Mail-Servers enthalten '
                                        'und von einer vertrauenswürdigen Zertifizierungsstelle ausgestellt sein.',
    'config.form.help.mail_sender': 'E-Mail-Absenderadresse, die für Benachrichtigungs-E-Mails verwendet werden soll. '
                                    'Als Fallback wird der E-Mail Login-Benutzer genutzt',
    'config.form.help.mail_transport': 'Die Standard-Portzuordnung ist: 25 = Unencrypted, 465 = SSL, 587 = StartTLS',

    # user settings
    'user_settings.action.pwd_change': 'Passwort geändert',
    'user_settings.btn.change_pwd': 'Password ändern',

    ## form fields
    'user_settings.form.pwd': 'Neues Passwort',

    ## form help
    'user_settings.form.help.pwd': 'Mindestanforderungen: 10 Zeichen, Buchstaben, Ziffern und Sonderzeichen',

    # system-environment
    'env.main': 'Haupt',
    'env.component': 'Komponente',
    'env.ansible.config': 'Ansible-Konfiguration',
    'env.ansible.collections': 'Ansible-Kollektionen',
    'env.python_modules': 'Python Module',

    # alerts
    'alerts.user': 'Persönlich',
    'alerts.group': 'Gruppe',
    'alerts.global': 'Global',
    'alerts.plugin': 'Plugin',
    'alerts.info': 'Alarm Informationen',
    'alerts.action.create': 'Alarm erstellt',
    'alerts.action.update': 'Alarm aktualisiert',
    'alerts.action.delete': 'Alarm gelöscht',
    'alerts.new': 'Neuer Alarm',
    'alerts.edit': 'Alarm bearbeiten',
    'alerts.plugin.new': 'Neues Plugin',
    'alerts.plugin.edit': 'Plugin bearbeiten',
    'alerts.plugin.action.create': 'Plugin erstellt',
    'alerts.plugin.action.update': 'Plugin aktualisiert',
    'alerts.plugin.action.delete': 'Plugin gelöscht',

    'alerts.type.email': 'E-Mail',
    'alerts.condition.failure': 'Fehlschlag',
    'alerts.condition.success': 'Erfolg',
    'alerts.condition.always': 'Immer',

    ## form
    'alerts.form.jobs_all': 'Alle Jobs',
    'alerts.form.condition': 'Bedingung',
    'alerts.form.plugin.executable': 'Ausführbare Datei',

    ## form help
    'alerts.form.help.plugin.executable': 'Pfad zum auszuführenden Plugin-Skript. '
                                          'Weitere Informationen: '
                                          '<a href="https://ansible-webui.oxl.app/usage/alerts.html#plugins">'
                                          'Dokumentation</a>',

    # permissions
    'permission.new': 'Neue Berechtigung',
    'permission.edit': 'Berechtigung bearbeiten',
    'permission.action.create': 'Berechtigung erstellt',
    'permission.action.update': 'Berechtigung aktualisiert',
    'permission.action.delete': 'Berechtigung gelöscht',
    'permission.members': 'Mitglieder',
    'permission.permitted': 'Erlaubt',
    'permission.users': 'Benutzer',
    'permission.groups': 'Gruppen',
    'permission.level': 'Stufe',
    'permission.jobs_all': 'Alle Jobs',
    'permission.credentials_all': 'Alle Zugangsdaten',
    'permission.repositories_all': 'All Repositories',

    # ssh hostkeys
    'ssh_hostkey.action.scan': 'Ziel(e) auf SSH-Hostkeys gescannt',
    'ssh_hostkey.action.delete': 'Ziel SSH-Hostkeys gelöscht',
    'ssh_hostkey.scan': 'Ziel(e) nach SSH-Hostkeys scannen',
    'ssh_hostkey.target': 'Ziel(e) scannen',

    ## form help
    'ssh_hostkey.form.help.target': 'Ziel-Domäne, IP oder Netzwerk im CIDR-Format',
    'ssh_hostkey.form.help.file': 'Der Name der Datei, in welche die SSH-Hostkeys geschrieben werden sollen. '
                                  'Dies kann nützlich sein, um Hostschlüssel zwischen Umgebungen zu trennen. '
                                  '(z.B. intern and prod)',
}
