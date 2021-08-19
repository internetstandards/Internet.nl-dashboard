
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


def xget_template_as_string(template_name: str = "scan_finished", preferred_language: str = 'en') -> str:
    template = xget_template(template_name, preferred_language)
    # django_mail_admin does not use types, so everything is any
    return template.email_html_text  # type: ignore


def store_template(template_name, template_content):
    email_template = EmailTemplate()
    email_template.name = template_name
    email_template.email_html_text = template_content
    email_template.save()
