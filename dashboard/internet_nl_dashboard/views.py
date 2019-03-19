import logging
from datetime import datetime
from typing import List

import pytz
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard import __version__
from dashboard.internet_nl_dashboard.listmanagement import (create_list, get_urllist_content,
                                                            get_urllists_from_account,
                                                            save_urllist_content)
from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__package__)
LOGIN_URL = '/account/login/'

"""
Todo: csrf via API calls...
    https://docs.djangoproject.com/en/dev/ref/csrf/#csrf-ajax
    Is handled and validated via middleware, so we don't need to concern ourselves with it here.
"""


# Create your views here.
@login_required(login_url=LOGIN_URL)
def index(request):

    # account switching.
    account = get_account(request)
    if account:
        selected_account_id = account.id
    else:
        selected_account_id = 0

    accounts = []
    if request.user.is_staff:
        accounts = list(Account.objects.all().values('id', 'name'))

        if request.POST.get('change_account', None):
            dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()
            dashboard_user.account = Account.objects.get(id=request.POST.get('change_account'))
            dashboard_user.save()

    return render(request, 'internet_nl_dashboard/index.html', {
        'version': __version__,
        'debug': settings.DEBUG,
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'menu_item_login': "current",
        'selected_account': selected_account_id,
        'accounts': accounts
    })


@login_required(login_url=LOGIN_URL)
def dashboard(request):

    return render(request, 'internet_nl_dashboard/dashboard.html', {
        'menu_item_dashboard': "current",
    })


@login_required(login_url=LOGIN_URL)
def addressmanager(request):

    return render(request, 'internet_nl_dashboard/addressmanager.html', {
        'menu_item_addressmanager': "current",
    })


@login_required(login_url=LOGIN_URL)
def logout_view(request):
    logout(request)
    return index(request)


@login_required(login_url=LOGIN_URL)
def get_lists(request):
    """
    :param request:
    :return:
    """
    account = get_account(request)
    if not account:
        return empty_response()

    response = get_urllists_from_account(account=account)

    JsonResponse(response, encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def create_list_(request, list_name):
    account = get_account(request)
    if not account:
        return empty_response()

    result = create_list(account=account, name=list_name)

    return JsonResponse({'name': result.name}, encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def get_list_content(request, urllist_name: int) -> {}:
    """

    :param request:
    :param urllist_name:
    :return:
    """

    account = get_account(request)
    if not account:
        return empty_response()

    response = get_urllist_content(account=account, urllist_name=urllist_name)

    return JsonResponse(response, encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def save_list_content(request, urllist_name: str, urls: List[str]) -> {}:
    account = get_account(request)
    if not account:
        return empty_response()

    result = save_urllist_content(account, urllist_name, urls)

    return JsonResponse(result, encoder=JSEncoder)


def get_account(request):
    try:
        return DashboardUser.objects.all().filter(user=request.user).first().account
    except AttributeError:
        log.debug("Not a valid account.")
        return None


def empty_response():
    return JsonResponse({})


def error_response(message: str):
    return JsonResponse({'status': 'error', 'message': message})
