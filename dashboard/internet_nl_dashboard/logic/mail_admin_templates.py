from typing import Any

from constance import config
from django_mail_admin.models import EmailTemplate


def xget_template(template_name: str = "scan_finished", preferred_language: str = 'en') -> EmailTemplate:
    """

    :param template_name:
    :param preferred_language: Countryfield value.
    :return:
    """

    # tries to retrieve the preferred language for emails. If that template is not available,
    # the fallback language (EN) is used.

    template = EmailTemplate.objects.filter(name=f'{template_name}_{preferred_language}').first()
    if template:
        return template

    template = EmailTemplate.objects.filter(name=f'{template_name}_{config.EMAIL_FALLBACK_LANGUAGE}').first()
    if template:
        return template

    raise LookupError(f"Could not find e-mail template {template_name}, neither for language {preferred_language} nor"
                      f"the fallback language {config.EMAIL_FALLBACK_LANGUAGE}.")


def xget_template_as_string(template_name: str = "scan_finished", preferred_language: Any = None) -> str:
    template = xget_template(template_name, preferred_language)
    return template.email_html_text


def store_template(template_name, template_content):
    e = EmailTemplate()
    e.name = template_name
    e.email_html_text = template_content
    e.save()
