# SPDX-License-Identifier: Apache-2.0
from typing import Annotated

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from ninja import Query, Router, Schema
from ninja.security import django_auth_superuser
from pydantic import StringConstraints

from dashboard.internet_nl_dashboard.logic.usage import (
    ActionStatisticsSchema,
    UsageMetricsSchema,
    UserStatisticsInputSchema,
    UserStatisticsSchema,
    usage_action_metrics,
    usage_metrics,
    user_statistics,
)
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, DashboardUser, UrlList
from dashboard.internet_nl_dashboard.problems import ApiError, ProblemSchema, ProblemType
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


@router.post(
    "/accounts/{account_id}/impersonation",
    response={200: dict, 404: ProblemSchema},
    openapi_extra={"responses": {404: {"description": "The account to switch to does not exist."}}},
)
def set_account(request, account_id: int) -> HttpResponse:

    dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()

    # very new users don't have the dashboarduser fields filled in, and are thus not connected to an account.
    if not dashboard_user:
        dashboard_user = DashboardUser(**{"account": Account.objects.all().first(), "user": request.user})

    account = Account.objects.filter(id=account_id).first()
    if not account:
        raise ApiError(404, "Account not found.", ProblemType.ACCOUNT_NOT_FOUND)
    dashboard_user.account = account
    dashboard_user.save()

    return JsonResponse({"account_name": dashboard_user.account.name})


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
                data.new_account_internet_nl_api_username,
                data.new_account_internet_nl_api_password,
            ),
        }
    )


class InstantAccountAndUserCreationSchema(Schema):
    new_username: str = ""
    new_email_address: Annotated[str, StringConstraints(min_length=1, max_length=254)]
    new_password: str = ""
    use_existing_account_id: int | None = None
    new_account_name: str = ""
    new_account_internet_nl_api_username: str = ""
    new_account_internet_nl_api_password: str = ""


# TODO: split account and user creation into separate resources; keep combined for backward compatibility.
@router.post(
    "/accounts",
    response={201: dict, 400: ProblemSchema, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra={
        "responses": {
            400: {
                "description": (
                    "Required account/user details are missing, the email address is invalid, or the "
                    "password is too short."
                )
            },
            404: {"description": "The selected existing account does not exist."},
            409: {"description": "The username or new account name is already in use."},
        }
    },
)
def save_instant_account_and_user(request, data: InstantAccountAndUserCreationSchema) -> HttpResponse:
    """
    More elaborate version of save_instant_account, where an admin can create an account and a user separately.
    It becomes more common that multiple users share the same account.
    """

    if not data.new_username:
        raise ApiError(400, "No username supplied.", ProblemType.USERNAME_REQUIRED, field="new_username")

    if User.objects.all().filter(username=data.new_username).exists():
        raise ApiError(409, "Username already exists.", ProblemType.USERNAME_ALREADY_EXISTS, field="new_username")

    try:
        validate_email(data.new_email_address)
    except ValidationError:
        raise ApiError(400, "Invalid email address.", ProblemType.INVALID_EMAIL_ADDRESS, field="new_email_address")

    if Account.objects.all().filter(name=data.new_account_name).exists():
        raise ApiError(
            409, "Account name already exists.", ProblemType.ACCOUNT_NAME_ALREADY_EXISTS, field="new_account_name"
        )

    # Extremely arbitrary password requirements. Just to make sure a password has been filled in.
    if len(data.new_password) < 12:
        raise ApiError(400, "Password too short.", ProblemType.PASSWORD_TOO_SHORT, field="new_password")

    if data.use_existing_account_id:
        account = Account.objects.filter(id=data.use_existing_account_id).first()
        if not account:
            raise ApiError(404, "Account not found.", ProblemType.ACCOUNT_NOT_FOUND, field="use_existing_account_id")
    else:

        if not data.new_account_name:
            raise ApiError(
                400, "No account name supplied.", ProblemType.ACCOUNT_NAME_REQUIRED, field="new_account_name"
            )

        account = Account(
            **{
                "name": data.new_account_name,
                "internet_nl_api_username": data.new_account_internet_nl_api_username,
                "internet_nl_api_password": Account.encrypt_password(data.new_account_internet_nl_api_password),
                "can_connect_to_internet_nl_api": Account.connect_to_internet_nl_api(
                    data.new_account_internet_nl_api_username,
                    data.new_account_internet_nl_api_password,
                ),
            }
        )
        account.save()

    # all seems fine, let's add the user
    user = User(**{"username": data.new_username, "email": data.new_email_address})
    user.set_password(data.new_password)
    user.is_active = True
    user.save()

    dashboarduser = DashboardUser(**{"user": user, "account": account})
    dashboarduser.save()

    return JsonResponse({"user_id": user.id, "account_id": account.id}, status=201)


@router.get("/usage-statistics", response={200: UsageMetricsSchema})
def usage_api(request) -> UsageMetricsSchema:
    return usage_metrics()


@router.get("/action-statistics", response={200: ActionStatisticsSchema})
def usage_action_api(request) -> ActionStatisticsSchema:
    return usage_action_metrics()


@router.get("/user-statistics", response={200: UserStatisticsSchema})
def usage_user_api(request, data: Query[UserStatisticsInputSchema]) -> UserStatisticsSchema:
    return user_statistics(
        start_date=data.start_date,
        end_date=data.end_date,
        max_records=data.max_records,
    )
