from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan, DashboardUser,
                                                    UrlList)
from dashboard.internet_nl_dashboard.views import (get_account, get_json_body,
                                                   inject_default_language_cookie, report)
from dashboard.settings import LOGIN_URL


def is_powertool_user(user):
    """
    A user_passes_test method that requires a login, active and either admin or staff permissions.

    :param user:
    :return:
    """

    if not user:
        return False

    if not isinstance(user, User):
        return False

    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    if user.is_superuser:
        return True

    if user.is_staff:
        return True

    return False


@user_passes_test(is_powertool_user, login_url=LOGIN_URL)
def set_account(request) -> HttpResponse:

    if not request.user.is_staff and request.user.is_active and request.user.is_superuser:
        return report.dashboard(request)

    request_data = get_json_body(request)
    selected_account_id: int = request_data['id']

    if selected_account_id:

        dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()

        # very new users don't have the dashboarduser fields filled in, and are thus not connected to an account.
        if not dashboard_user:
            dashboard_user = DashboardUser(**{'account': Account.objects.all().first(), 'user': request.user})

        dashboard_user.account = Account.objects.get(id=selected_account_id)
        dashboard_user.save()

        return JsonResponse(operation_response(success=True, message=f"Switched account."))


@user_passes_test(is_powertool_user, login_url=LOGIN_URL)
def get_accounts(request) -> HttpResponse:
    account = get_account(request)

    if not request.user.is_staff and request.user.is_active and request.user.is_superuser:
        return report.dashboard(request)

    accounts = Account.objects.all().values_list('id', 'name')

    account_data = []
    # add some metadata to the accounts, so it's more clear where you are switching to:
    for account in accounts:
        account_information = {}
        account_information['id'], account_information['name'] = account
        account_information['scans'] = AccountInternetNLScan.objects.all().filter(
            account=account_information['id']).count()
        account_information['lists'] = UrlList.objects.all().filter(account=account_information['id']).count()
        account_information['users'] = list(User.objects.all().filter(
            dashboarduser__account=account_information['id']).values_list('username', flat=True))

        account_data.append(account_information)

    return JsonResponse({'current_account': account, 'accounts': account_data})


@user_passes_test(is_powertool_user, login_url=LOGIN_URL)
def save_instant_account(request) -> HttpResponse:

    request = get_json_body(request)
    username = request['username']
    password = request['password']

    if User.objects.all().filter(username=username).exists():
        return JsonResponse(operation_response(error=True, message=f"User with username '{username}' already exists."))

    if Account.objects.all().filter(name=username).exists():
        return JsonResponse(operation_response(error=True,
                                               message=f"Account with username {username}' already exists."))

    # Extremely arbitrary password requirements. Just to make sure a password has been filled in.
    if len(password) < 5:
        return JsonResponse(operation_response(error=True, message=f"Password not filled in or not long enough."))

    # all seems fine, let's add the user
    user = User(**{'username': username})
    user.set_password(password)
    user.is_active = True
    user.save()

    account = Account(**{
        'name': username,
        'internet_nl_api_username': username,
        'internet_nl_api_password': Account.encrypt_password(password),
        'can_connect_to_internet_nl_api': Account.connect_to_internet_nl_api(username, password)
    })
    account.save()

    dashboarduser = DashboardUser(**{'user': user, 'account': account})
    dashboarduser.save()

    return JsonResponse(operation_response(success=True, message=f"Account and user with name '{username}' created!"))


@login_required(login_url=LOGIN_URL)
def spa(request) -> HttpResponse:
    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/spa.html')
    return inject_default_language_cookie(request, response)
