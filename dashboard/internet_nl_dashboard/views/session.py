# SPDX-License-Identifier: Apache-2.0
import logging
from time import sleep

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django_otp.plugins.otp_totp.models import TOTPDevice
from ninja import Router, Schema

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
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

    # logging in via javascript is not possible, because the CSRF is tied to the session cookie.
    # The session cookie cannot be requested by javascript, and we're not going to use JWT because
    # the second factor part is also django only, and not implemented as REST methods.
    # So there is currently no way to move to rest based auth _including_ second factor authentication.
    # of course except OAUTH, but there is no knowledge for that yet.

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
    # got a unique constraint when creating a user in another account. A user may be in one account only.
    dashboarduser, _ = DashboardUser.objects.get_or_create(user=request.user, defaults={"account": account})

    return {
        "is_authenticated": request.user.is_authenticated,
        "is_superuser": request.user.is_superuser,
        "account_name": dashboarduser.account.name,
        "account_id": dashboarduser.account.id,
    }


def session_status(request):
    return JsonResponse(session_status_(request))
    # try:
    #     return JsonResponse(session_status_(request))
    # except Exception as e:
    #     log.error("Error in session_status: %s", str(e))
    #     return JsonResponse({"error": f"Forbidden: {str(e)}"}, status=403)


def session_logout(request):
    resp = session_logout_(request)
    return JsonResponse(resp.dict() if hasattr(resp, "dict") else resp)


def session_login(request):
    resp = session_login_(request)
    return JsonResponse(resp.dict() if hasattr(resp, "dict") else resp)


# Ninja router for session management (excluding login)
router = Router(tags=["Session Management"])


class SessionStatusSchema(Schema):
    is_authenticated: bool
    is_superuser: bool
    second_factor_enabled: bool | None = False
    account_name: str
    account_id: int | None = None


@router.get("/status", response={200: SessionStatusSchema})
def session_status_api(request) -> SessionStatusSchema:
    data = session_status_(request)
    # Ensure it fits the schema
    return SessionStatusSchema(
        is_authenticated=bool(data.get("is_authenticated", False)),
        is_superuser=bool(data.get("is_superuser", False)),
        second_factor_enabled=(
            bool(data.get("second_factor_enabled", False)) if "second_factor_enabled" in data else False
        ),
        account_name=str(data.get("account_name", "")),
        account_id=data.get("account_id"),
    )


@router.get("/logout", response={200: OperationResponseSchema})
def session_logout_api(request) -> OperationResponseSchema:
    # Reuse existing logic function
    resp = session_logout_(request)
    return resp
