import json
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.domains import (alter_url_in_urllist, create_list,
                                                           delete_list, get_urllist_content,
                                                           get_urllists_from_account,
                                                           save_urllist_content,
                                                           update_list_settings)
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, get_account,
                                                   inject_default_language_cookie)


@login_required(login_url=LOGIN_URL)
def index(request) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/domains.html', {
        'menu_item_addressmanager': "current",
        'debug': settings.DEBUG
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def get_lists(request) -> JsonResponse:
    account = get_account(request)

    response = get_urllists_from_account(account=account)

    return JsonResponse(response, encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_urllist_content_(request, urllist_id: int) -> JsonResponse:
    account = get_account(request)
    return JsonResponse(get_urllist_content(account=account, urllist_id=urllist_id), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def save_list_content(request, urllist_name: str, urls: List[str]) -> JsonResponse:
    account = get_account(request)
    return JsonResponse(save_urllist_content(account, urllist_name, urls), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def update_list_settings_(request):
    account = get_account(request)
    # json loads will probably error when wrong data is given. Is that a problem? And how?
    try:
        user_input = json.loads(request.body)
    except json.JSONDecodeError:
        user_input = {}

    return JsonResponse(update_list_settings(account, user_input))


@login_required(login_url=LOGIN_URL)
def create_list_(request):
    account = get_account(request)
    # json loads will probably error when wrong data is given. Is that a problem? And how?
    try:
        user_input = json.loads(request.body)
    except json.JSONDecodeError:
        user_input = {}

    return JsonResponse(create_list(account, user_input))


@login_required(login_url=LOGIN_URL)
def delete_list_(request):

    try:
        user_input = json.loads(request.body)['id']
    except json.JSONDecodeError:
        user_input = 0

    account = get_account(request)
    return JsonResponse(delete_list(account, user_input))


@login_required
def alter_url_in_urllist_(request):
    account = get_account(request)

    try:
        user_input = json.loads(request.body)
    except json.JSONDecodeError:
        user_input = {}

    return JsonResponse(alter_url_in_urllist(account, user_input))
