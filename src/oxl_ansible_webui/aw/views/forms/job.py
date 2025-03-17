from django import forms
from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from aw.config.main import config
from aw.utils.http import ui_endpoint_wrapper_kwargs
from aw.model.repository import Repository, CHOICES_REPOSITORY
from aw.utils.util import get_choice_key_by_value
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.views.base import choices_global_credentials


class RepositoryGitForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = Repository.form_fields_git
        field_order = Repository.form_fields_git
        labels = FORM_LABEL['jobs']['repository']
        help_texts = FORM_HELP['jobs']['repository']

    git_credentials = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=choices_global_credentials,
        label=Meta.labels['git_credentials'],
    )


class RepositoryStaticForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = Repository.form_fields_static
        field_order = Repository.form_fields_static
        labels = FORM_LABEL['jobs']['repository']
        help_texts = FORM_HELP['jobs']['repository']

    static_path = forms.CharField(max_length=500, initial=config['path_play'], required=False)


REPOSITORY_EDIT_FORMS = {
    'Git': RepositoryGitForm,
    'Static': RepositoryStaticForm,
}


def _job_repository_edit(request, rtype_name: str, repo_id: int = None) -> HttpResponse:
    form_method = 'post'
    form_api = 'repository'
    repository_type = get_choice_key_by_value(choices=CHOICES_REPOSITORY, find=rtype_name)
    repository = {}

    if repo_id is not None and repo_id != 0:
        # pylint: disable=R0801
        try:
            repository = Repository.objects.get(id=repo_id)

        except ObjectDoesNotExist:
            repository = None

        if repository is None:
            return redirect(f"/ui/jobs/repository?error=Repository with ID {repo_id} do not exist")

        if repository.rtype != repository_type:
            return redirect(f"/ui/jobs/repository?error=Repository with ID {repo_id} is not of type '{rtype_name}'")

        repository = repository.__dict__
        form_method = 'put'
        form_api += f'/{repo_id}'

    repository_form = REPOSITORY_EDIT_FORMS[rtype_name]()
    repository_form_html = repository_form.render(
        template_name='forms/snippet.html',
        context={'form': repository_form, 'existing': repository},
    )
    return render(
        request, status=200, template_name='jobs/repository_edit.html',
        context={
            'form': repository_form_html, 'form_api': form_api, 'form_method': form_method,
            'repository_type': repository_type,
        }
    )


@login_required
@ui_endpoint_wrapper_kwargs
def job_repository_git_edit(request, repo_id: int = None) -> HttpResponse:
    return _job_repository_edit(request=request, rtype_name='Git', repo_id=repo_id)


@login_required
@ui_endpoint_wrapper_kwargs
def job_repository_static_edit(request, repo_id: int = None) -> HttpResponse:
    return _job_repository_edit(request=request, rtype_name='Static', repo_id=repo_id)
