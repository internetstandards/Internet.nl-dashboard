import logging
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect

from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__package__)
LOGIN_URL = '/account/login/'

"""
Todo: csrf via API calls...
    https://docs.djangoproject.com/en/dev/ref/csrf/#csrf-ajax
    Is handled and validated via middleware, so we don't need to concern ourselves with it here.
"""


def inject_default_language_cookie(request, response):
    # If you visit any of the main pages, this is set to the desired language your browser emits.
    # This synchronizes the language between javascript (OS language) and browser (Accept Language).
    if 'dashboard_language' not in request.COOKIES:
        # Get the accept language,
        # Add the cookie to render.
        accept_language = request.LANGUAGE_CODE
        response.set_cookie(key='dashboard_language', value=accept_language)

    return response


def logout_view(request):
    logout(request)
    return redirect('/')


def get_account(request) -> Account:
    # todo: what about the exceptions that happen when there is no account?
    return DashboardUser.objects.all().filter(user=request.user).first().account


def get_dashboarduser(request) -> Account:
    # todo: what about the exceptions that happen when there is no account?
    return DashboardUser.objects.all().filter(user=request.user).first()


def empty_response():
    return JsonResponse({})


def error_response(message: str):
    return JsonResponse({'status': 'error', 'message': message})
