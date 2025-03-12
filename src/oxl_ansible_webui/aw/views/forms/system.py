from pytz import all_timezones
from django import forms
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from aw.config.main import config
from aw.config.defaults import CONFIG_DEFAULTS
from aw.utils.http import ui_endpoint_wrapper
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.config.environment import AW_ENV_VARS, AW_ENV_VARS_SECRET
from aw.model.system import SystemConfig, get_config_from_db
from aw.utils.deployment import deployment_dev
from aw.model.base import CHOICES_BOOL


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = SystemConfig.form_fields
        field_order = SystemConfig.form_fields
        labels = FORM_LABEL['system']['config']
        help_texts = FORM_HELP['system']['config']

    path_run = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_run'], required=True,
        label=Meta.labels['path_run'],
    )
    path_play = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_play'], required=True,
        label=Meta.labels['path_play'],
    )
    path_log = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_log'], required=True,
        label=Meta.labels['path_log'],
    )
    path_ansible_config = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_ansible_config'], required=False,
        label=Meta.labels['path_ansible_config'],
    )
    path_ssh_known_hosts = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_ssh_known_hosts'], required=False,
        label=Meta.labels['path_ssh_known_hosts'],
    )
    timezone = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=[(tz, tz) for tz in sorted(all_timezones)],
        label=Meta.labels['timezone'],
    )
    debug = forms.ChoiceField(
        initial=CONFIG_DEFAULTS['debug'] or deployment_dev(), choices=CHOICES_BOOL,
    )
    mail_pass = forms.CharField(
        max_length=100, required=False, label=Meta.labels['mail_pass'],
    )


@login_required
@ui_endpoint_wrapper
def system_config(request) -> HttpResponse:
    config_form = SystemConfigForm()
    form_method = 'put'
    form_api = 'config'

    existing = {key: config[key] for key in SystemConfig.form_fields}
    existing['_enc_mail_pass'] = get_config_from_db()._enc_mail_pass
    config_form_html = config_form.render(
        template_name='forms/snippet.html',
        context={'form': config_form, 'existing': existing},
    )
    return render(
        request, status=200, template_name='system/config.html',
        context={
            'form': config_form_html, 'form_api': form_api, 'form_method': form_method,
            'env_vars': AW_ENV_VARS, 'env_labels': FORM_LABEL['system']['config'],
            'env_vars_secret': AW_ENV_VARS_SECRET,
            'env_vars_config': {key: config[key] for key in AW_ENV_VARS},
        }
    )
