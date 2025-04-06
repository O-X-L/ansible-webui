from urllib.parse import urljoin

from django.dispatch import receiver
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

try:
    from django_saml2_auth.user import create_jwt_token

except (ImportError, ModuleNotFoundError):
    pass

from aw.utils.http import ui_endpoint_wrapper_auth
from aw.settings import SAML2_AUTH, LOGIN_PATH, LOGIN_REDIRECT_URL
from aw.utils.debug import log, log_error
from aw.utils.util import get_client_ip
from aw.dependencies import saml_installed, log_dependency_error


# SP-initiated SAML SSO; see: https://github.com/grafana/django-saml2-auth/issues/105
@ui_endpoint_wrapper_auth
def saml_sp_initiated_login(request) -> HttpResponse:
    if not saml_installed():
        log_dependency_error('SAML', 'saml')
        return HttpResponse(status=500, content=b'Dependency error')

    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)

    return render(request, status=200, template_name='registration/login.html')


@ui_endpoint_wrapper_auth
def saml_sp_initiated_login_init(request) -> HttpResponse:
    if not saml_installed():
        log_dependency_error('SAML', 'saml')
        return HttpResponse(status=500, content=b'Dependency error')

    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)

    if request.method != 'POST' or 'username' not in request.POST:
        return redirect(f"{LOGIN_PATH}?error=Required 'username' was not provided!")

    token = create_jwt_token(request.POST['username'])
    assertion_url = SAML2_AUTH['ASSERTION_URL']
    sso_init_url = urljoin(assertion_url, f'a/saml/sp/?token={token}')
    return redirect(sso_init_url)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    del sender
    log(f"Login successful: User '{user}' from IP {get_client_ip(request)}")


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    del sender
    log(f"Logout successful: User '{user}' from IP {get_client_ip(request)}")


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    del sender
    log_error(f"Login failed: User '{credentials['username']}'")
