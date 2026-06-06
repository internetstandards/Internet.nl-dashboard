# SPDX-License-Identifier: Apache-2.0
from django.conf import settings


def template_settings_processor(request):
    """
    Making the debug and LANGUAGE variables available to all templates:
    https://stackoverflow.com/questions/17901341/django-how-to-make-a-variable-available-to-all-templates

    This allows these variables to be used consistently in templates.

    :param request:
    :return:
    """

    return {"LANGUAGES": settings.LANGUAGES, "debug": settings.DEBUG}
