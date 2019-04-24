from typing import List

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.domains import (create_list, get_urllist_content,
                                                           get_urllists_from_account,
                                                           save_urllist_content)
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, get_account,
                                                   inject_default_language_cookie)


@login_required(login_url=LOGIN_URL)
def index(request) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/domains.html', {
        'menu_item_addressmanager': "current",
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def get_lists(request) -> JsonResponse:
    account = get_account(request)

    # todo: make sure the output is safe, or converted to safe.
    response = get_urllists_from_account(account=account)

    return JsonResponse(response, encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def create_list_(request, list_name: str) -> JsonResponse:
    account = get_account(request)
    result = create_list(account=account, name=list_name)
    return JsonResponse({'name': result.name}, encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def get_urllist_content_(request, urllist_id: int) -> JsonResponse:
    account = get_account(request)
    return JsonResponse(get_urllist_content(account=account, urllist_id=urllist_id), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def save_list_content(request, urllist_name: str, urls: List[str]) -> JsonResponse:
    account = get_account(request)
    return JsonResponse(save_urllist_content(account, urllist_name, urls), encoder=JSEncoder)
