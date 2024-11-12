# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.tags import add_tag, remove_tag, tags_in_urllist
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body


@login_required(login_url=LOGIN_URL)
def add_tag_(request):
    data = get_json_body(request)
    add_tag(
        account=get_account(request),
        urllist_id=data.get("urllist_id", []),
        url_ids=data.get("url_ids", []),
        tag=data.get("tag", ""),
    )
    return JsonResponse(operation_response(success=True), safe=False)


@login_required(login_url=LOGIN_URL)
def remove_tag_(request):
    data = get_json_body(request)
    remove_tag(
        account=get_account(request),
        urllist_id=data.get("urllist_id", []),
        url_ids=data.get("url_ids", []),
        tag=data.get("tag", ""),
    )
    return JsonResponse(operation_response(success=True), safe=False)


@login_required(login_url=LOGIN_URL)
def tags_in_urllist_(request, urllist_id):
    return JsonResponse(tags_in_urllist(account=get_account(request), urllist_id=urllist_id), safe=False)
