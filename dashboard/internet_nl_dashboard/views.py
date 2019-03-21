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
from dashboard.internet_nl_dashboard.spreadsheet import complete_import, get_upload_history
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

    response = render(request, 'internet_nl_dashboard/index.html', {
        'version': __version__,
        'debug': settings.DEBUG,
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'menu_item_login': "current",
        'selected_account': selected_account_id,
        'accounts': accounts
    })

    return inject_default_language_cookie(request, response)


def inject_default_language_cookie(request, response):
    # If you visit any of the main pages, this is set to the desired language your browser emits.
    # This synchronizes the language between javascript (OS language) and browser (Accept Language).
    if 'dashboard_language' not in request.COOKIES:
        # Get the accept language,
        # Add the cookie to render.
        accept_language = request.LANGUAGE_CODE
        response.set_cookie(key='dashboard_language', value=accept_language)

    return response


@login_required(login_url=LOGIN_URL)
def upload(request):

    response = render(request, 'internet_nl_dashboard/upload.html', {
        'menu_item_addressmanager': "current",
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def dashboard(request):

    response = render(request, 'internet_nl_dashboard/dashboard.html', {
        'menu_item_dashboard': "current",
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def addressmanager(request):

    response = render(request, 'internet_nl_dashboard/addressmanager.html', {
        'menu_item_addressmanager': "current",
    })

    return inject_default_language_cookie(request, response)


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
    account = get_account(request)
    if not account:
        return empty_response()

    # Instead of some json message, give a full page, so the classic uploader also functions pretty well.
    response = upload(request)
    response.status_code = 400

    # happens when no file is sent
    if 'file' not in request.FILES:
        return response

    if request.method == 'POST' and request.FILES['file']:
        file = save_file(request.FILES['file'])
        status = complete_import(user=get_dashboarduser(request), file=file)

        if status['error']:
            # The GUI wants the error to contain some text: As that text is sensitive to xss(?) (probably only
            # if you see the output directly, not via javascript or json).
            status['error'] = status['message']
            return response

        response.status_code = 200
        return response

    return response


def save_file(myfile) -> str:
    # todo: filesystem might be full.
    # todo: docs
    # https://docs.djangoproject.com/en/2.1/ref/files/storage/
    fs = FileSystemStorage(location=settings.UPLOAD_ROOT)
    filename = fs.save(myfile.name, myfile)
    file = settings.UPLOAD_ROOT + '/' + filename
    return file


@login_required(login_url=LOGIN_URL)
def upload_history(request):
    account = get_account(request)
    if not account:
        return empty_response()

    # list of dicts: In order to allow non-dict objects to be serialized set the safe parameter to False.
    return JsonResponse(get_upload_history(account), encoder=JSEncoder, safe=False)
