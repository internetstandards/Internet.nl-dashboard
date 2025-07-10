# SPDX-License-Identifier: Apache-2.0
import logging
from time import sleep

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django_otp.plugins.otp_totp.models import TOTPDevice

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.views import get_json_body

"""
Uses django sessions to keep users logged in, so no trickery with JWT is needed.
This of course will _only_ work on the same machine. So you cannot access a remote installation by design.
The login stuff will be as strong as django's stuff, which is acceptable.
"""

log = logging.getLogger(__package__)


def session_login_(request):
    """
    Note that login is not possible, as the session cookie must be set correctly. The CSRF is tied to the session
    cookie, so you cannot retrieve that in a different fashion. There are frameworks that allow you to login
    such as djoser, but they DO NOT do second factor authentication and there is nothing equivalent to
    django_second_factor_auth. So all logins and session management must be done, until we drop second factor auth
    or when there is a json api available for the latter.

    :param request:
    :return:
    """
    # taken from: https://stackoverflow.com/questions/11891322/setting-up-a-user-login-in-python-django-using-json-and-
    if request.method != "POST":
        sleep(2)
        return operation_response(error=True, message="post_only")

    # get the json data:
    parameters = get_json_body(request)

    username = parameters.get("username", "").strip()
    password = parameters.get("password", "").strip()

    if not username or not password:
        sleep(2)
        return operation_response(error=True, message="no_credentials_supplied")

    user = authenticate(username=username, password=password)

    if user is None:
        sleep(2)
        return operation_response(error=True, message="invalid_credentials")

    if not user.is_active:
        sleep(2)
        return operation_response(error=True, message="user_not_active")

    # todo: implement generate_challenge and verify_token, so we can do login from new site.
    devices = TOTPDevice.objects.all().filter(user=user, confirmed=True)
    if devices:
        sleep(2)
        return operation_response(error=True, message="second_factor_login_required")

    login(request, user)
    return operation_response(success=True, message="logged_in")


def session_logout_(request):
    # If you don't include credentials in your get request, you'll get an AnonymousUser.
    # The preferred method of detecting anonymous users is to see if they are authenticated, according to:
    # https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
    if not request.user.is_authenticated:
        log.debug("User is not authenticated...")
        return operation_response(success=True, message="logged_out")

    logout(request)
    return operation_response(success=True, message="logged_out")


def session_status_(request):
    """
    Returns a dictionary of permissions the user has. We keep it simple and only distinct
    :param request:
    :return:
    """

    if not request.user.is_authenticated:
        return {
            "is_authenticated": False,
            "is_superuser": False,
            "second_factor_enabled": False,
            "account_name": "",
        }

    account, _ = Account.objects.get_or_create(name="users")
    dashboarduser, _ = DashboardUser.objects.get_or_create(user=request.user, account=account)

    return {
        "is_authenticated": request.user.is_authenticated,
        "is_superuser": request.user.is_superuser,
        "account_name": dashboarduser.account.name,
        "account_id": dashboarduser.account.id,
    }


def session_status(request):
    try:
        return JsonResponse(session_status_(request))
    except Exception as e:
        log.error("Error in session_status: %s", str(e))
        return JsonResponse({"error": f"Forbidden: {str(e)}"}, status=403)


def session_logout(request):
    return JsonResponse(session_logout_(request))


def session_login(request):
    return JsonResponse(session_login_(request))
