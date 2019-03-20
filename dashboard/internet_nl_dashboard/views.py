import logging
from datetime import datetime
from typing import List

import pytz
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard import __version__
from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.spreadsheet import (get_data, get_upload_history,
                                                         log_spreadsheet_upload, save_data)
from dashboard.internet_nl_dashboard.urllist_management import (create_list, get_urllist_content,
                                                                get_urllists_from_account,
                                                                save_urllist_content)

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
    selected_account_id = 0

    accounts = []
    if request.user.is_staff:
        accounts = list(Account.objects.all().values('id', 'name'))

        if request.POST.get('change_account', None):
            dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()
            dashboard_user.account = Account.objects.get(id=request.POST.get('change_account'))
            dashboard_user.save()

        account = get_account(request)
        if account:
            selected_account_id = account.id

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

    # todo: make sure the output is safe, or converted to safe.
    response = get_urllists_from_account(account=account)

    return JsonResponse(response, encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def create_list_(request, list_name):
    account = get_account(request)
    if not account:
        return empty_response()

    result = create_list(account=account, name=list_name)

    return JsonResponse({'name': result.name}, encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def get_urllist_content_(request, urllist_name: str) -> {}:
    account = get_account(request)
    if not account:
        return empty_response()

    return JsonResponse(get_urllist_content(account=account, urllist_name=urllist_name), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def save_list_content(request, urllist_name: str, urls: List[str]) -> {}:
    account = get_account(request)
    if not account:
        return empty_response()

    return JsonResponse(save_urllist_content(account, urllist_name, urls), encoder=JSEncoder)


def get_account(request) -> Account:
    try:
        return DashboardUser.objects.all().filter(user=request.user).first().account
    except AttributeError:
        log.debug("Not a valid account.")
        return None


def get_dashboarduser(request) -> Account:
    try:
        return DashboardUser.objects.all().filter(user=request.user).first()
    except AttributeError:
        log.debug("Not a valid dashboarduser.")
        return None


def empty_response():
    return JsonResponse({})


def error_response(message: str):
    return JsonResponse({'status': 'error', 'message': message})


@login_required(login_url=LOGIN_URL)
def upload_spreadsheet(request):
    from dashboard.internet_nl_dashboard.spreadsheet import validate

    account = get_account(request)
    if not account:
        return empty_response()

    user = get_dashboarduser(request)

    # todo: filesystem might be full.
    # then try to import it...
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage(location=settings.UPLOAD_ROOT)
        filename = fs.save(myfile.name, myfile)
        file = settings.UPLOAD_ROOT + '/' + filename

        if not validate(file):
            log_spreadsheet_upload(user=user, file=file, message="File incorrect: is it a spreadsheet?")
            return JsonResponse({'error': True}, encoder=JSEncoder, status=400)

        data = get_data(file)
        if not data:
            # probably not intended to upload an empty file, or something happened that caused a crash.
            log_spreadsheet_upload(user=user, file=file, message="No data in file detected.")
            return JsonResponse({'error': True}, encoder=JSEncoder, status=400)

        details = save_data(account, data)

        log_spreadsheet_upload(user=user, file=file, message="Success!")
        return JsonResponse({'success': True, 'details': details}, encoder=JSEncoder, status=200)

    return JsonResponse({'error': True}, encoder=JSEncoder, status=400)


@login_required(login_url=LOGIN_URL)
def upload_history(request):
    account = get_account(request)
    if not account:
        return empty_response()

    # list of dicts: In order to allow non-dict objects to be serialized set the safe parameter to False.
    return JsonResponse(get_upload_history(account), encoder=JSEncoder, safe=False)
