from aw.config.main import config

ES = {
    # base
    'btn.add': 'Añadir',
    'btn.save': 'Guardar',
    'btn.discard': 'Descartar',
    'btn.edit': 'Editar',
    'btn.clone': 'Clonar',
    'btn.close': 'Cerrar',
    'btn.execute': 'Ejecutar',
    'btn.delete': 'Eliminar',
    'btn.stop': 'Detener',
    'btn.logs': 'Registros',
    'btn.pause': 'Pausar',
    'btn.download': 'Descargar',
    'btn.update': 'Actualizar',
    'btn.scroll_down': 'Desplazar hacia abajo',
    'btn.encrypt': 'Encriptado con Ansible-Vault',
    'nav.home': 'Inicio',
    'nav.system': 'Sistema',
    'nav.lang': 'Lenguaje',
    'nav.darkLight': 'Interruptor modo oscuro/claro',
    'nav.docs': 'Documentación',
    'nav.repo': 'Repositorio de código abierto',
    'nav.bugs': 'Reportar un error',
    'nav.user_settings': 'Configuración de usuario',
    'nav.logout': 'Cerrar sesión',
    'footer.user': 'Usuario',
    'footer.oss': 'Uso de código abierto',
    'footer.oss.frontend': 'Interfaz de usuario',
    'footer.oss.backend': 'Servidor',
    'footer.oss.license': 'Licencia',

    # common phrases
    'common.name': 'Nombre',
    'common.choices': 'Opciones',
    'common.required': 'Requerido',
    'common.status': 'Estado',
    'common.error': 'Error',
    'common.success': 'Acción exitosa',
    'common.actions': 'Acciones',
    'common.search': 'Buscar',
    'common.updated_at': 'Actualizado en',
    'common.created_at': 'Creado en',
    'common.click_to_copy': 'Presiona para copiar',
    'common.comment': 'Comentario',
    'common.invalid_value': 'El campo tiene un valor válido',  # '<msg>: "<field>"'
    'common.invalid_form': 'Valores inválidos detectados',  # not field-specific..
    'common.version': 'Versión',
    'common.path': 'Ruta',
    'common.setting': 'Configuración',
    'common.value': 'Valor',
    'common.kind': 'Tipo',

    # auth
    'login.user': 'Nombre de usuario',
    'login.pwd': 'Contraseña',
    'login.saveUser': 'Guardar nombre de usuario',
    'login.btn': 'Iniciar sesión',
    'login.sso': 'SSO',
    'login.localUser': 'Usuario local',
    # home
    'home.dashboard': 'Pizarra',
    'home.jobs': 'Trabajos',
    'home.logs': 'Registros',
    'home.repos': 'Repositorios',
    'home.alerts': 'Alertas',
    'home.creds': 'Credenciales',

    # dashboard
    'db.stats': 'Estadísticas',
    'db.chart.exec_over_time': 'Ejecuciones a lo largo del tiempo',
    'db.chart.exec_by_user': 'Ejecuciones por Usuario',
    'db.chart.exec_results_by_job': 'Resultados de Ejecución por Trabajo',
    'db.chart.exec_results_by_host': 'Resultados de Ejecución por Host',
    'db.runs': 'Ejecuciones',
    'db.time.select': 'Período de tiempo',
    'db.time.minutes': 'Minutos',
    'db.time.hours': 'Horas',
    'db.time.days': 'Días',
    'db.time.weeks': 'Semanas',
    'db.time.months': 'Meses',

    # jobs
    'jobs.new': 'Nuevo Trabajo',
    'jobs.edit': 'Editar Trabajo',
    'jobs.execute': 'Ejecutar Trabajo',
    'jobs.job': 'Trabajo',
    'jobs.info': 'Información del Trabajo',
    'jobs.info.execution': 'Información de Ejecución',
    'jobs.info.next_run': 'Siguiente Ejecución',
    'jobs.info.last_run': 'Última Ejecución',
    'jobs.info.duration': 'Duración',
    'jobs.info.running': 'En ejecución',
    'jobs.info.failed': 'Fallido',
    'jobs.info.succeeded': 'Realizado con éxito',
    'jobs.info.scheduled': 'Programado',
    'jobs.info.unreachable': 'Inalcanzable',
    'jobs.info.changed': 'Cambiado',
    'jobs.execute.tmp_credentials': 'Proporcionar Credenciales',
    'jobs.execute.required_limit': 'Un límite es requerido',
    'jobs.execute.required_var': 'Falta variable requerida',
    'jobs.execute.required_credentials': 'Credenciales requeridas',
    'jobs.execute.regex_mismatch': 'La entrada no cumple con el patrón requerido',
    'jobs.execute.regex_mismatch': 'Input does not satisfy the required pattern',

    ## form fields
    'jobs.action.start': 'Trabajo en cola',
    'jobs.action.stop': 'Iniciada detención de trabajo',
    'jobs.action.delete': 'Trabajo eliminado',
    'jobs.action.create': 'Trabajo creado',
    'jobs.action.update': 'Trabajo actualizado',
    'jobs.action.exec_delete': 'Ejecución eliminada',
    'jobs.form.repository': 'Repositorio',
    'jobs.form.playbook_file': 'Archivo de estrategia (Playbook)',
    'jobs.form.inventory_file': 'Archivo de inventario',
    'jobs.form.file_browse.empty': 'Vacío',
    'jobs.form.schedule': 'Calendario',
    'jobs.form.cron': 'Programación Cron',
    'jobs.form.enabled': 'Programación habilitada',
    'jobs.form.limit': 'Límite',
    'jobs.form.tags': 'Etiquetas',
    'jobs.form.tags_skip': 'Omitir Etiquetas',
    'jobs.form.mode_diff': 'Modo Diferencia',
    'jobs.form.mode_check': 'Modo de comprobación (ejecución de prueba)',
    'jobs.form.environment_vars': 'Variables de entorno',
    'jobs.form.cmd_args': 'Argumentos de línea de comandos',
    'jobs.form.credentials_needed': 'Credenciales requeridas',
    'jobs.form.credentials_default': 'Credenciales de trabajo predeterminadas',
    'jobs.form.credentials_category': 'Categoría de credenciales',
    'jobs.form.execution_prompts': 'Indicaciones de ejecución',
    'jobs.form.execution_prompts_enforce': 'Forzar indicaciones de ejecución',
    'jobs.form.verbosity': 'Verbosidad',
    'jobs.form.credentials': 'Credenciales',
    'jobs.form.prompt_limit_req': 'Límite requerido',
    'jobs.form.prompt_credentials_req': 'Credenciales requeridas',
    'jobs.form.prompt_credentials_tmp': 'Credenciales temporales',
    'jobs.form.prompt_fields': 'Campos de indicación',
    'jobs.form.prompt_vars': 'Variables de indicación',
    'jobs.form.prompt_name': 'Nombre a mostrar',
    'jobs.form.prompt_varname': 'Nombre de variable',
    'jobs.form.prompt_regex': 'Validación de expresión regular (Regex)',
    'jobs.form.prompt_choice_text': 'Texto',
    ## form help
    'jobs.form.help.playbook_file': 'Estrategia (Playbook) a ejecutar',
    'jobs.form.help.inventory_file': 'Uno o varios archivos/directorios de inventario que se deben incluir para la ejecución. '
                                     'Lista separada por comas. Para más detalles, consulte: '
                                     '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/'
                                     'intro_inventory.html">Documentación de Ansible - Inventory</a>',
    'jobs.form.help.repository': 'Se utiliza para definir la fuente estática o dinámica de la estructura de directorios de su Estrategia (Playbook). '
                                 f"El valor predeterminado es '{config['path_play']}'",
    'jobs.form.help.limit': 'Hosts o grupos del inventario de Ansible a los que limitar la ejecución.'
                            'Para más detalles, consulte: '
                            '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html">'
                            'Documentación de Ansible - Limit</a>',
    'jobs.form.help.schedule': 'Programación para ejecutar el trabajo automáticamente. Para el formato, consulte: '
                                '<a href="https://crontab.guru/">crontab.guru</a>',
    'jobs.form.help.environment_vars': 'Environmental variables to be passed to the Ansible execution. '
                                       'Lista separada por comas de pares clave-valor. (VAR1=TEST1,VAR2=0)',
    'jobs.form.help.cmd_args': "Argumentos adicionales de la línea de comandos que se deben pasar a 'ansible-playbook'. "
                               "Se puede utilizar para pasar variables adicionales",
    'jobs.form.help.tags': 'Para más detalles, véase: '
                           '<a href="https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html">'
                           'Documentación de Ansible - Tags</a>',
    'jobs.form.help.mode_check': 'Para más detalles, véase: '
                                 '<a href="https://docs.ansible.com/ansible/2.8/user_guide/playbooks_checkmode.html">'
                                 'Documentación de Ansible - Check Mode</a>',
    'jobs.form.help.credentials_needed': 'Si el trabajo requiere especificar credenciales '
                                         '(ya sea por defecto o en el momento de la ejecución; '
                                         'las credenciales de usuario del usuario que ejecuta el programa son las de reserva)',
    'jobs.form.help.credentials_default': 'Especifique las credenciales predeterminadas a nivel de trabajo que se utilizarán (requeridas para la ejecución programada)',
    'jobs.form.help.credentials_category': 'La categoría de credenciales se puede utilizar para la coincidencia dinámica de '
                                           'credenciales de usuario en el momento de la ejecución',
    'jobs.form.help.enabled': 'Activar o desactivar la programación. Se puede ignorar si no se ha establecido ninguna programación',
    'jobs.form.help.execution_prompts_required': 'Atributos y/o variables del trabajo necesarios para solicitar en la ejecución personalizada. '
                                                 'Lista separada por comas de pares clave-valor.<br>'
                                                 "Las variables se pueden proporcionar de la siguiente manera: 'var={VAR-NAME}#{DISPLAY-NAME}'<br>"
                                                 "Ejemplo: 'límite,comprobación,var=add_user #Usuario que añadir' ",
    'jobs.form.help.prompt_choices': 'Lista de opciones separadas por comas.',
    'jobs.form.help.prompt_regex': 'Puede usar <a href="https://regex101.com/">Regex101.com</a> para comprobar la validación de sus entradas. '
                                   'Asegúrate de seleccionar el "ECMAScript (Javascript)" sabor.',

    # credentials
    'creds.user': 'Personal',
    'creds.shared': 'Compartido',
    'creds.new': 'Nueva Credencial',
    'creds.info': 'Información de Credencial',
    'creds.vault_encrypt': 'Encriptado con Ansible-Vault',
    'creds.action.create': 'Credencial creada',
    'creds.action.update': 'Credencial actualizada',
    'creds.action.delete': 'Credencial eliminada',
    'creds.action.vault_encrypt': 'Texto encriptado',

    ## form fields
    'creds.form.category': 'Categoría',
    'creds.form.accounts': 'Cuentas',
    'creds.form.secrets': 'Secretos',
    'creds.form.connect_user': 'Usuario de Conexión',
    'creds.form.connect_pwd': 'Contraseña de Conexión',
    'creds.form.ssh_key': 'Llave SSH',
    'creds.form.become_user': 'Convertirse en Usuario',
    'creds.form.become_pwd': 'Contraseña de Conversión',
    'creds.form.vault': 'Boveda',
    'creds.form.vault_pwd': 'Contraseña de Boveda',
    'creds.form.vault_file': 'Archivo de Boveda',
    'creds.form.vault_id': 'ID de Boveda',
    'creds.form.vault_encrypt': 'Texto a encriptar',

    ## form help
    'creds.form.help.vault_file': 'Ruta al archivo que contiene su contraseña de bóveda',
    'creds.form.help.vault_id': 'Para más detalles, véase: '
                                '<a href="https://docs.ansible.com/ansible/latest/vault_guide/'
                                'vault_managing_passwords.html">'
                                'Documentación de Ansible - Managing Passwords</a>',
    'creds.form.help.ssh_key': 'Provide an unencrypted SSH private key',
    'creds.form.help.category': 'La categoría de credenciales de usuario. Se utiliza para la coincidencia dinámica en el momento de la ejecución.',
    'creds.form.help.vault_encrypt': 'Texto para cifrar mediante Bóveda (Ansible-Vault). Para más detalles, consulte '
                                     '<a href="https://docs.ansible.com/ansible/latest/vault_guide/index.html">'
                                     'Documentación de Ansible - Guía de la bóveda</a>',

    # repositories
    'repos.static': 'Estático / Local',
    'repos.git': 'Git',
    'repos.static.src': 'Ruta',
    'repos.git.src': 'Origen',
    'repos.info': 'Información del Repositorio',
    'repos.new': 'Nuevo Repositorio',
    'repos.edit': 'Editar Repositorio',
    'repos.action.create': 'Repositorio creado',
    'repos.action.update': 'Repositorio actualizado',
    'repos.action.delete': 'Repositorio eliminado',
    'repos.action.download': 'Descarga del repositorio iniciada',

    ## form fields
    'repos.form.git_origin': 'Origen',
    'repos.form.git_branch': 'Rama',
    'repos.form.git_credentials': 'Credenciales',
    'repos.form.git_limit_depth': 'Límite de Profundidad',
    'repos.form.git_lfs': 'LFS',
    'repos.form.git_playbook_base': 'Directorio base de la Estrategia (Playbook)',
    'repos.form.git_isolate': 'Directorio de aislamientos',
    'repos.form.git_hook_pre': 'Gancho Previo (Pre-Hook)',
    'repos.form.git_hook_post': 'Gancho Posterior (Post-Hook)',
    'repos.form.git_hook_cleanup': 'Gancho de limpieza (Cleanup-Hook)',
    'repos.form.git_override_initialize': 'Sobrescribir comando de inicialización',
    'repos.form.git_override_update': 'Sobrescribir comando de actualización',
    'repos.form.git_hooks': 'Ganchos (Hooks)',
    'repos.form.git_options': 'Opciones',

    ## form help
    'repos.form.help.static_path': 'Ruta al repositorio estático local/directorio base de Estrategia (playbook)',
    'repos.form.help.git_origin': "URL completa del repositorio remoto. "
                                  "Por ejemplo: '<a href=\"https://github.com/O-X-L/ansible-webui.git\">"
                                  "https://github.com/O-X-L/ansible-webui.git'</a>'",
    'repos.form.help.git_credentials': "Credenciales para conectarse al origen. "
                                       "'Conectar usuario', 'Contraseña de conexión' y 'Llave Privada SSH' se utilizan",
    'repos.form.help.git_playbook_base': 'Ruta relativa al directorio base de Estrategia (Playbook) desde la raíz del repositorio',
    'repos.form.help.git_lfs': 'Habilitar o deshabilitar la comprobación de archivos Git-LFS',
    'repos.form.help.git_isolate': 'Habilitar o deshabilitar si se debe utilizar un clon del repositorio Git para todos los trabajos. '
                                   'Si está habilitado, el repositorio se clonará/descargará cada vez que se ejecute un trabajo. '
                                   'Esto tendrá un impacto negativo en el rendimiento',
    'repos.form.help.git_hook_pre': 'Comandos que se deben ejecutar antes de inicializar/actualizar el repositorio. '
                                    'Lista separada por comas de comandos de shell',
    'repos.form.help.git_hook_post': 'Comandos que se deben ejecutar después de inicializar/actualizar el repositorio. '
                                     'Lista separada por comas de comandos de shell',
    'repos.form.help.git_override_initialize': 'Uso avanzado. Anule por completo el comando utilizado para inicializar '
                                               '(clone) the repository',
    'repos.form.help.git_override_update': 'Advanced usage! Completely override the command used to update '
                                           '(clonar) el repositorio',

    # logs
    'logs.all_jobs': 'Todos los trabajos',
    'logs.exec_count': 'Numero de ejecuciones',
    'logs.job_logs': 'Registros de trabajo',
    'logs.time': 'Tiempo',
    'logs.time_start': 'Tiempo de inicio',
    'logs.time_start_short': 'Inicio',
    'logs.time_fin_short': 'Fin',
    'logs.command': 'Comando',
    'logs.executed_by': 'Ejecutado por',
    'logs.exec_log_file': 'Archivo de registro de ejecución',
    'logs.exec_error_log_file': 'Archivo de registro de errores de ejecución',
    'logs.repo_log_file': 'Archivo de registro del repositorio',
    'logs.repo_error_log_file': 'Archivo de registro de errores del repositorio',
    'logs.exec_finished': 'Ejecución terminada!',
    'logs.exec_failed': 'Ejecución fallida!',
    'logs.error_short': 'Resumen',
    'logs.error_medium': 'Error',

    # system
    'system.settings': 'Settings',
    'system.permission': 'Permissions',
    'system.environment': 'Environment',
    'system.api_keys': 'API Keys',
    'system.admin': 'Admin',
    'system.api_docs': 'API Docs',

    # api-keys
    'api_keys.token': 'Token',
    'api_keys.key': 'Llave',
    'api_keys.new': 'Nuevo par de claves de API',
    'api_keys.action.create': 'Lave API creada',
    'api_keys.action.delete': 'Lave API eliminada',

    # config
    'config.paths': 'Rutas',
    'config.mailing': 'Envío de correos',
    'config.execution': 'Ejecución',
    'config.internal': 'Interno',
    'config.action.update': 'Configuración actualizada',
    'config.is_read_only': 'Esta configuración es de solo lectura porque se proporcionó como variable de entorno!',

    ## form fields
    'config.form.path_run': 'Directorio de tiempo de ejecución',
    'config.form.path_play': 'Directorio base de Estrategias (playbook)',
    'config.form.path_log': 'Directorio para registros de ejecución',
    'config.form.path_template': 'Directorio de plantillas',
    'config.form.run_timeout': 'Tiempo de espera para la ejecución de Estrategias (playbook)',
    'config.form.session_timeout': 'Tiempo de espera para inicio de sesión en la interfaz de usuario web',
    'config.form.path_ansible_config': 'Archivo de configuración de Ansible',
    'config.form.path_ssh_known_hosts': 'Archivo SSH Known-Hosts',
    'config.form.debug': 'Modo de depuración',
    # 'config.form.audit_log': 'Audit Logging',

    ### env-vars
    'config.form.timezone': 'Zona horaria',
    'config.form.db': 'Base de datos',
    'config.form.hostnames': 'Nombres de host',
    'config.form.proxy': 'Utilizar Proxy',
    'config.form.db_migrate': 'Automigración de base de datos',
    'config.form.serve_static': 'Servir archivos estáticos',
    'config.form.deployment': 'Implementación',
    'config.form.version': 'Ansible-WebUI Versión',
    'config.form.logo_url': 'URL del logotipo que se va a utilizar',
    'config.form.ara_server': 'URL del servidor de análisis de ejecución de Ansible (ARA)',
    'config.form.global_environment_vars': 'Variables de entorno globales',
    'config.form.auth_mode': 'Modo de autenticación',
    'config.form.saml_config': 'Archivos de configuración SAML',
    'config.form.address': 'Dirección de escucha',
    'config.form.port': 'Puerto de escucha',
    'config.form.ssl_file_crt': 'Certificado SSL',
    'config.form.ssl_file_key': 'Lave Privada SSL',
    'config.form.mail_server': 'Servidor de correo',
    'config.form.mail_transport': 'Transporte de correo',
    'config.form.mail_ssl_verify': 'Verificación de correo SS',
    'config.form.mail_sender': 'Dirección de correo electrónico de envío',
    'config.form.mail_user': 'Nombre de usuario de correo',
    'config.form.mail_pass': 'Contraseña de correo',
    ## form help
    'config.form.help.path_run': 'Base directory for <a href="https://ansible.readthedocs.io/projects/runner/en/latest/intro/">'
                                 'Ansible-Runner archivos de tiempo de ejecución</a>',
    'config.form.help.path_play': 'Camino hacia el <a href="https://docs.ansible.com/ansible/2.8/user_guide/'
                                  'playbooks_best_practices.html#directory-layout">Directorio base/Estrategia (playbook) de Ansible</a>',
    'config.form.help.path_log': 'Defina la ruta donde se guardan los registros completos de los trabajos',
    'config.form.help.path_template': 'Defina la ruta donde se colocan las plantillas personalizadas',
    'config.form.help.path_ansible_config': 'Ruta a <a href="https://docs.ansible.com/ansible/latest/installation_guide'
                                            '/intro_configuration.html#configuration-file">Archivo de configuración de Ansible</a> utilizar',
    'config.form.help.path_ssh_known_hosts': 'Ruta a  <a href="https://en.wikibooks.org/wiki/OpenSSH/'
                                             'Client_Configuration_Files#~/.ssh/known_hosts">Archivos known_hosts SSH</a> utilizar',
    'config.form.help.debug': 'Habilitar el modo de depuración. ¡No lo habilite de forma permanente en sistemas de producción! '
                              'Es posible que abra vectores de ataque. '
                              'Es posible que tengas que reiniciar la aplicación para aplicar esta configuración',
    # 'config.form.help.audit_log': 'Enable Audit-Logging. All create/update/delete actions are logged to the database '
    #                               'and can be viewed in the Admin-UI at '
    #                               '<a href="/ui/system#admin">System - Admin - Administration - Log entries</a>',
    'config.form.help.logo_url': 'Ejemplo: '
                                 '<a href="https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo'
                                 '/vscode-ansible.svg">'
                                 'https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo/vscode-ansible.svg'
                                 '</a>',
    'config.form.help.ara_server': 'Proporcione la URL de su servidor ARA (análisis de ejecución de Ansible). Se puede utilizar para recopilar estadísticas de trabajo. Véase: '
                                   '<a href="https://ansible-webui.OXL.app/usage/integrations.html">'
                                   'Documentación - Integraciones</a>',
    'config.form.help.global_environment_vars': 'Establecer variables de entorno que se añadirán a cada ejecución de trabajo. '
                                                'Lista separada por comas de pares clave-valor. (VAR1=TEST1,VAR2=0)',
    'config.form.help.mail_server': 'Servidor de correo que se utilizará para los correos de alerta. Combinación de servidor y puerto (default 25)',
    'config.form.help.mail_ssl_verify': 'Habilitar o deshabilitar la verificación del certificado SSL. '
                                        'Si está habilitado, el SAN del certificado debe contener el FQDN del servidor de correo '
                                        'y debe ser emitido por una CA de confianza',
    'config.form.help.mail_sender': 'Dirección del remitente del correo electrónico que se utilizará para los correos electrónicos de alerta. La opción alternativa es mail-user',
    'config.form.help.mail_transport': 'La asignación de puertos predeterminada es: 25 = Sin cifrar, 465 = SSL, 587 = StartTLS',

    # user settings
    'user_settings.action.pwd_change': 'Contraseña actualizada',
    'user_settings.btn.change_pwd': 'Cambiar contraseña',

    ## form fields
    'user_settings.form.pwd': 'Nueva contraseña',

    ## form help
    'user_settings.form.help.pwd': 'Requisitos mínimos: 10 caracteres, letras, dígitos y caracteres especiales.',

    # system-environment
    'env.main': 'Principal',
    'env.component': 'Componente',
    'env.ansible.config': 'Configuración Ansible',
    'env.ansible.collections': 'Colecciones de Ansible',
    'env.python_modules': 'Módulos Python',

    # alerts
    'alerts.user': 'Personal',
    'alerts.group': 'Grupo',
    'alerts.global': 'Global',
    'alerts.plugin': 'Complemento (Plugin)',
    'alerts.info': 'Información de alerta',
    'alerts.action.create': 'Alerta creada',
    'alerts.action.update': 'Alerta actualizada',
    'alerts.action.delete': 'Alerta eliminada',
    'alerts.new': 'Nueva alerta',
    'alerts.edit': 'Editar alerta',
    'alerts.plugin.new': 'Nuevo complemento (plugin)',
    'alerts.plugin.edit': 'Editar complemento (plugin)',
    'alerts.plugin.action.create': 'Complemento (plugin) creado',
    'alerts.plugin.action.update': 'Complemento (plugin) actualizado',
    'alerts.plugin.action.delete': 'Complemento (plugin) eliminado',

    'alerts.type.email': 'Correo electrónico',
    'alerts.condition.failure': 'Fallo',
    'alerts.condition.success': 'Éxito',
    'alerts.condition.always': 'Siempre',

    ## form
    'alerts.form.jobs_all': 'Todos los trabajos',
    'alerts.form.condition': 'Condición',
    'alerts.form.plugin.executable': 'Ejecutable',

    ## form help
    'alerts.form.help.plugin.executable': 'Ruta al script del complemento (plugin) que se va a ejecutar. Para más detalles, consulte: '
                                          '<a href="https://ansible-webui.oxl.app/usage/alerts.html#plugins">'
                                          'Documentación</a>',

    # permissions
    'permission.new': 'Nuevo permiso',
    'permission.edit': 'Editar permiso',
    'permission.action.create': 'Permiso creado',
    'permission.action.update': 'Permiso actualizado',
    'permission.action.delete': 'Permiso eliminado',
    'permission.members': 'Miembros',
    'permission.permitted': 'Permitido',
    'permission.users': 'Usuarios',
    'permission.groups': 'Grupos',
    'permission.level': 'Nivel',
    'permission.jobs_all': 'Todos los trabajos',
    'permission.credentials_all': 'Todas las credenciales',
    'permission.repositories_all': 'Todos los repositorios',
}
