import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.views import get_json_body, get_account, get_dashboarduser

"""
Uses django sessions to keep users logged in, so no trickery with JWT is needed.
This of course will _only_ work on the same machine. So you cannot access a remote installation by design.

The login stuff will be as strong as django's stuff, which is acceptable. 
"""

log = logging.getLogger(__package__)


def session_login_(request):
    # taken from: https://stackoverflow.com/questions/11891322/setting-up-a-user-login-in-python-django-using-json-and-
    if request.method != 'POST':
        return operation_response(success=True, message=f"post_only")

    # get the json data:
    parameters = get_json_body(request)

    username = parameters.get('username', '').strip()
    password = parameters.get('password', '').strip()

    if not username or not password:
        return operation_response(error=True, message=f"no_credentials_supplied")

    user = authenticate(username=username, password=password)

    if user is None:
        return operation_response(error=True, message=f"invalid_credentials")

    if not user.is_active:
        return operation_response(error=True, message=f"user_not_active")

    # how will this work with second factor?

    login(request, user)
    return operation_response(success=True, message=f"logged_in")


def session_logout_(request):
    # If you don't include credentials in your get request, you'll get an AnonymousUser.
    # The preferred method of detecting anonymous users is to see if they are authenticated, according to:
    # https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
    if not request.user.is_authenticated:
        log.debug('User is not authenticated...')
        return operation_response(success=True, message=f"logged_out")
    else:
        logout(request)
        return operation_response(success=True, message=f"logged_out")


def session_status_(request):
    """
        Returns a dictionary of permissions the user has. We keep it simple and only distinct
        :param request:
        :return:
    """

    if not request.user.is_authenticated:
        return {
            'is_authenticated': False,
            'is_superuser': False,
        }

    return {
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser
    }


def session_login(request):
    return JsonResponse(session_login_(request))


def session_status(request):
    return JsonResponse(session_status_(request))


def session_logout(request):
    return JsonResponse(session_logout_(request))

