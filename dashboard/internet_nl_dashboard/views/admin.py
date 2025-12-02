# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from ninja import Router, Schema
from ninja.security import django_auth_superuser

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.logic.usage import UsageMetricsSchema, usage_metrics
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, DashboardUser, UrlList
from dashboard.internet_nl_dashboard.views import get_account

router = Router(tags=["Administration"], auth=django_auth_superuser)


@router.get("/accounts")
def get_accounts(request) -> HttpResponse:
    myaccount = get_account(request)
    scans = AccountInternetNLScan.objects.all().filter(account=myaccount.id).count()
    lists = UrlList.objects.all().filter(account=myaccount.id).count()
    users = list(User.objects.all().filter(dashboarduser__account=myaccount.id).values_list("username", flat=True))
    current_account = {
        "id": myaccount.id,
        "name": myaccount.name,
        "scans": scans,
        "lists": lists,
        "users": users,
        "label": f"{myaccount.id}: {myaccount.name} (Lists: {lists}, Scans: {scans}, Users: {len(users)})",
    }

    accounts = Account.objects.all().values_list("id", "name").order_by("id")

    account_data = []
    # add some metadata to the accounts, so it's more clear where you are switching to:
    for account in accounts:
        scans = AccountInternetNLScan.objects.all().filter(account=account[0]).count()
        lists = UrlList.objects.all().filter(account=account[0]).count()
        users = list(User.objects.all().filter(dashboarduser__account=account[0]).values_list("username", flat=True))
        account_information = {
            "id": account[0],
            "name": account[1],
            "scans": scans,
            "lists": lists,
            "users": users,
            "label": f"{account[0]}: {account[1]} (Lists: {lists}, Scans: {scans}, Users: {len(users)})",
        }

        account_data.append(account_information)

    return JsonResponse({"current_account": current_account, "accounts": account_data})


@router.post("/accounts/{account_id}/impersonation", response={200: OperationResponseSchema})
def set_account(request, account_id: int) -> HttpResponse:

    dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()

    # very new users don't have the dashboarduser fields filled in, and are thus not connected to an account.
    if not dashboard_user:
        dashboard_user = DashboardUser(**{"account": Account.objects.all().first(), "user": request.user})

    dashboard_user.account = Account.objects.get(id=account_id)
    dashboard_user.save()

    return JsonResponse(
        operation_response(
            success=True, message="switched_account", data={"account_name": dashboard_user.account.name}
        ).dict()
    )


class CredentialCheckSchema(Schema):
    new_account_internet_nl_api_username: str = ""
    new_account_internet_nl_api_password: str = ""


class CredentialCheckResponseSchema(Schema):
    can_connect_to_internet_nl_api: bool = False


@router.post("/accounts/api-credential-check", response={200: CredentialCheckResponseSchema})
def check_api_credentials(request, data: CredentialCheckSchema) -> HttpResponse:
    return JsonResponse(
        {
            "can_connect_to_internet_nl_api": Account.connect_to_internet_nl_api(
                data.new_account_internet_nl_api_username, data.new_account_internet_nl_api_password
            ),
        }
    )


class InstantAccountAndUserCreationSchema(Schema):
    new_username: str = ""
    new_password: str = ""
    use_existing_account_id: int | None = None
    new_account_name: str = ""
    new_account_internet_nl_api_username: str = ""
    new_account_internet_nl_api_password: str = ""


# TODO: split account and user creation into separate resources; keep combined for backward compatibility.
@router.post(
    "/accounts",
    response={
        201: OperationResponseSchema,
        400: OperationResponseSchema,
        404: OperationResponseSchema,
        409: OperationResponseSchema,
    },
)
def save_instant_account_and_user(request, data: InstantAccountAndUserCreationSchema) -> HttpResponse:
    """
    More elaborate version of save_instant_account, where an admin can create an account and a user separately.
    It becomes more common that multiple users share the same account.
    """

    if not data.new_username:
        return JsonResponse(operation_response(error=True, message="error_no_username_supplied").dict(), status=400)

    if User.objects.all().filter(username=data.new_username).exists():
        return JsonResponse(operation_response(error=True, message="error_username_already_exists").dict(), status=409)

    if Account.objects.all().filter(name=data.new_username).exists():
        return JsonResponse(
            operation_response(error=True, message="error_account_name_already_exists").dict(), status=409
        )

    # Extremely arbitrary password requirements. Just to make sure a password has been filled in.
    if len(data.new_password) < 12:
        return JsonResponse(operation_response(error=True, message="error_password_too_short").dict(), status=400)

    if data.use_existing_account_id:
        account = Account.objects.filter(id=data.use_existing_account_id).first()
        if not account:
            return JsonResponse(operation_response(error=True, message="error_account_not_found").dict(), status=404)
    else:

        if not data.new_account_name:
            return JsonResponse(
                operation_response(error=True, message="error_no_account_name_supplied").dict(), status=400
            )

        account = Account(
            **{
                "name": data.new_account_name,
                "internet_nl_api_username": data.new_account_internet_nl_api_username,
                "internet_nl_api_password": Account.encrypt_password(data.new_account_internet_nl_api_password),
                "can_connect_to_internet_nl_api": Account.connect_to_internet_nl_api(
                    data.new_account_internet_nl_api_username, data.new_account_internet_nl_api_password
                ),
            }
        )
        account.save()

    # all seems fine, let's add the user
    user = User(**{"username": data.new_username})
    user.set_password(data.new_password)
    user.is_active = True
    user.save()

    dashboarduser = DashboardUser(**{"user": user, "account": account})
    dashboarduser.save()

    return JsonResponse(
        operation_response(
            success=True,
            message=f"User {data.new_username} created and added to account {account.name}.",
            data={"user_id": user.id, "account_id": account.id},
        ).dict(),
        status=201,
    )


@router.get("/usage-statistics", response={200: UsageMetricsSchema})
def usage_api(request) -> UsageMetricsSchema:
    return usage_metrics()
