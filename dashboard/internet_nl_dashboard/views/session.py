# SPDX-License-Identifier: Apache-2.0
import logging

from django.contrib.auth import logout
from django.http import JsonResponse
from ninja import Router, Schema

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.models import Account, DashboardUser

"""
Uses django sessions to keep users logged in, so no trickery with JWT is needed.
This of course will _only_ work on the same machine. So you cannot access a remote installation by design.
The login stuff will be as strong as django's stuff, which is acceptable.
"""

log = logging.getLogger(__package__)


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
            "account_name": "",
        }

    # This is for users that are able to log in but are not associated with an account. To prevent
    # application crashes and unexpected behavior, the user is assigned to a fallback account.
    # This fallback account is not able to perform scans. The existence of the fallback account in production
    # means there was a problem when creating or setting up a user. For example, the createsuperuser
    # command was issued, but the new user was not assigned an account yet.
    account, _ = Account.objects.get_or_create(name="Fallback account for incomplete new users")
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


# Ninja router for session management. Login is handled by django-allauth.
router = Router(tags=["Session Management"])


class SessionStatusSchema(Schema):
    is_authenticated: bool
    is_superuser: bool
    account_name: str
    account_id: int | None = None


@router.get("/status", response={200: SessionStatusSchema})
def session_status_api(request) -> SessionStatusSchema:
    data = session_status_(request)
    # Ensure it fits the schema
    return SessionStatusSchema(
        is_authenticated=bool(data.get("is_authenticated", False)),
        is_superuser=bool(data.get("is_superuser", False)),
        account_name=str(data.get("account_name", "")),
        account_id=data.get("account_id"),
    )


@router.get("/logout", response={200: OperationResponseSchema})
def session_logout_api(request) -> OperationResponseSchema:
    # Reuse existing logic function
    resp = session_logout_(request)
    return resp
