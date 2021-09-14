# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.report import (
    ad_hoc_tagged_report, get_previous_report, get_recent_reports, get_report,
    get_report_differences_compared_to_current_list, get_shared_report, get_urllist_timeline_graph,
    share, unshare, update_report_code, update_share_code)
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body


@login_required(login_url=LOGIN_URL)
def get_report_(request, report_id) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_report(get_account(request), report_id),
        content_type="application/json"
    )

    # return JsonResponse(get_report(get_account(request), report_id), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_report_differences_compared_to_current_list_(request, report_id):
    return JsonResponse(get_report_differences_compared_to_current_list(get_account(request), report_id),
                        encoder=JSEncoder, safe=True)


@login_required(login_url=LOGIN_URL)
def get_previous_report_(request, urllist_id, at_when):
    return JsonResponse(get_previous_report(get_account(request), urllist_id, at_when), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_ad_hoc_tagged_report_(request, report_id: int):
    data = get_json_body(request)

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        ad_hoc_tagged_report(get_account(request), report_id, data.get('tags', [])),
        content_type="application/json"
    )


@login_required(login_url=LOGIN_URL)
def get_recent_reports_(request) -> JsonResponse:
    return JsonResponse(get_recent_reports(get_account(request)), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_urllist_report_graph_data_(request, urllist_ids) -> JsonResponse:
    return JsonResponse(get_urllist_timeline_graph(get_account(request), urllist_ids), encoder=JSEncoder, safe=False)


# No login required: reports via this method are public
def get_shared_report_(request, report_code: str) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files

    data = get_json_body(request)

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_shared_report(report_code, data.get('share_code', '')),
        content_type="application/json"
    )


@login_required(login_url=LOGIN_URL)
def x_share(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(share(account, data.get('report_id', -1), data.get('public_share_code', '')), safe=False)


@login_required(login_url=LOGIN_URL)
def x_unshare(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(unshare(account, data.get('report_id', -1)), safe=False)


@login_required(login_url=LOGIN_URL)
def x_update_share_code(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(update_share_code(account, data.get('report_id', -1), data.get('public_share_code', '')),
                        safe=False)


@login_required(login_url=LOGIN_URL)
def x_update_report_code(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(update_report_code(account, data.get('report_id', -1)), safe=False)
