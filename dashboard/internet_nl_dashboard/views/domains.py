# SPDX-License-Identifier: Apache-2.0
from typing import List

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.domains import (alter_url_in_urllist, cancel_scan,
                                                           create_list, delete_list,
                                                           delete_url_from_urllist,
                                                           download_as_spreadsheet,
                                                           get_scan_status_of_list,
                                                           get_urllist_content,
                                                           get_urllists_from_account,
                                                           save_urllist_content,
                                                           save_urllist_content_by_name, scan_now,
                                                           update_list_settings)
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body


@login_required(login_url=LOGIN_URL)
def get_lists(request) -> JsonResponse:
    return JsonResponse(get_urllists_from_account(account=get_account(request)), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_urllist_content_(request, urllist_id: int) -> JsonResponse:
    return JsonResponse(get_urllist_content(account=get_account(request), urllist_id=urllist_id), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def get_scan_status_of_list_(request, urllist_id: int) -> JsonResponse:
    return JsonResponse(get_scan_status_of_list(account=get_account(request), list_id=urllist_id), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def save_list_content(request, urllist_name: str, urls: List[str]) -> JsonResponse:
    return JsonResponse(save_urllist_content_by_name(get_account(request), urllist_name, urls), encoder=JSEncoder)


@login_required(login_url=LOGIN_URL)
def update_list_settings_(request):
    return JsonResponse(update_list_settings(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def create_list_(request):
    return JsonResponse(create_list(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def delete_list_(request):
    return JsonResponse(delete_list(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def alter_url_in_urllist_(request):
    return JsonResponse(alter_url_in_urllist(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def add_urls_to_urllist(request):
    return JsonResponse(save_urllist_content(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def delete_url_from_urllist_(request):
    account = get_account(request)
    request = get_json_body(request)
    item_deleted = delete_url_from_urllist(account, request.get('urllist_id', None), request.get('url_id', None))
    return JsonResponse({'items_deleted': None, 'success': item_deleted})


@login_required(login_url=LOGIN_URL)
def scan_now_(request):
    return JsonResponse(scan_now(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def cancel_scan_(request):
    account = get_account(request)
    request = get_json_body(request)
    response = cancel_scan(account, request.get('id'))
    return JsonResponse(response)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def download_list_(request):
    params = get_json_body(request)
    return download_as_spreadsheet(get_account(request), params.get('list-id', None), params.get('file-type', None))
