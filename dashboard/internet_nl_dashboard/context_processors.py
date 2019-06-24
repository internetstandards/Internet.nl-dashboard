from django.conf import settings


def template_settings_processor(request):
    """
    Making the debug and LANGUAGE variables available to all templates:
    https://stackoverflow.com/questions/17901341/django-how-to-make-a-variable-available-to-all-templates

    This allows you to use these variables also in the two_factor template without hassle.

    :param request:
    :return:
    """

    return {'LANGUAGES': settings.LANGUAGES, 'debug': settings.DEBUG}
