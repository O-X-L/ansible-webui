from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.views import logout_then_login
from django.shortcuts import HttpResponse
from django.urls import path, re_path

from aw.config.hardcoded import LOGIN_PATH
from aw.settings import LOGIN_REDIRECT_URL
from aw.utils.http import ui_endpoint_wrapper
from aw.utils.util import get_logo


@login_required
@ui_endpoint_wrapper
def not_implemented(request) -> HttpResponse:
    return render(request, status=404, template_name='fallback.html', context={'content': 'Not yet implemented'})


@ui_endpoint_wrapper
def catchall(request) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)

    return redirect(LOGIN_PATH)  # will be done by endpoint_wrapper


def not_found(request) -> HttpResponse:
    del request
    return HttpResponse(content=b'Not found', status=404)


def favicon(request) -> HttpResponse:
    del request
    return redirect(get_logo())


@login_required
@ui_endpoint_wrapper
def logout(request) -> HttpResponse:
    return logout_then_login(request)


@login_required
@ui_endpoint_wrapper
def home(request) -> HttpResponse:
    return render(request, status=200, template_name='home.html')


@login_required
@ui_endpoint_wrapper
def system(request) -> HttpResponse:
    return render(request, status=200, template_name='system.html')


urlpatterns_ui = [
    path('ui', home),
    path('ui/system', system),
    re_path(r'^ui/*', not_implemented),
]
