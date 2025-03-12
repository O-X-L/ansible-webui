import ssl
from pathlib import Path
from smtplib import SMTP, SMTP_SSL, SMTPResponseException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.template.loader import get_template
from premailer import transform as html_transform_styles

from aw.base import USERS
from aw.utils.util import valid_email, is_set
from aw.utils.debug import log
from aw.config.main import config
from aw.model.job import JobExecution
from aw.settings import get_main_web_address
from aw.model.system import MAIL_TRANSPORT_TYPE_SSL, MAIL_TRANSPORT_TYPE_STARTTLS


def _email_send(server: SMTP, user: USERS, stats: dict, execution: JobExecution, error_msgs: dict):
    if is_set(config['mail_pass']):
        server.login(user=config['mail_user'], password=config['mail_pass'])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Ansible WebUI - Job '{execution.job.name}' - {execution.status_name}"
    msg['From'] = config['mail_sender'] if is_set(config['mail_sender']) else config['mail_user']
    msg['To'] = user.email

    tmpl_html, tmpl_text = 'email/alert.html', 'email/alert.txt'
    if is_set(config['path_template']):  # custom templates
        _tmpl_base = Path(config['path_template'])
        _tmpl_html = _tmpl_base / 'alert.html'
        _tmpl_text = _tmpl_base / 'alert.txt'
        if _tmpl_html.is_file():
            tmpl_html = str(_tmpl_html)

        if _tmpl_text.is_file():
            tmpl_text = str(_tmpl_text)

    tmpl_ctx = {'execution': execution, 'stats': stats, 'url': get_main_web_address(), 'error_msgs': error_msgs}
    text_content = get_template(tmpl_text).render(tmpl_ctx)
    html_content = get_template(tmpl_html).render(tmpl_ctx)
    html_content = html_transform_styles(html=html_content, pretty_print=True, allow_network=False)

    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    server.sendmail(
        from_addr=config['mail_sender'],
        to_addrs=user.email,
        msg=msg.as_string()
    )


def alert_plugin_email(user: USERS, stats: dict, execution: JobExecution, error_msgs: dict):
    if user.email.endswith('@localhost') or not valid_email(user.email):
        log(msg=f"User has an invalid email address configured: {user.username} ({user.email})", level=3)
        return

    try:
        server, port = config['mail_server'].split(':', 1)

    except ValueError:
        server = config['mail_server']
        port = 25

    try:
        ssl_context = ssl.create_default_context()
        if config['mail_ssl_verify']:
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED

        else:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        if config['mail_transport'] == MAIL_TRANSPORT_TYPE_SSL:
            with SMTP_SSL(server, port, context=ssl_context) as server:
                _email_send(server=server, user=user, stats=stats, execution=execution, error_msgs=error_msgs)

        else:
            with SMTP(server, port) as server:
                if config['mail_transport'] == MAIL_TRANSPORT_TYPE_STARTTLS:
                    server.starttls(context=ssl_context)

                _email_send(server=server, user=user, stats=stats, execution=execution, error_msgs=error_msgs)

        log(msg=f"Sent alert email to: {user.username} ({user.email})", level=6)

    except (SMTPResponseException, OSError) as e:
        log(msg=f"Got error sending alert mail: {e}", level=2)
