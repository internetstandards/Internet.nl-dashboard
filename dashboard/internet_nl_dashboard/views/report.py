# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.internet_nl_dashboard.logic.mail import values_from_previous_report
from dashboard.internet_nl_dashboard.logic.report import (
    ad_hoc_tagged_report,
    get_previous_report,
    get_public_reports,
    get_recent_reports,
    get_report,
    get_report_differences_compared_to_current_list,
    get_shared_report,
    get_urllist_timeline_graph,
    save_ad_hoc_tagged_report,
    share,
    unshare,
    update_report_code,
    update_share_code,
)
from dashboard.internet_nl_dashboard.logic.shared_report_lists import (
    get_latest_report_id_from_list_and_type,
    get_publicly_shared_lists_per_account,
    get_publicly_shared_lists_per_account_and_list_id,
)
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body, json_response


@login_required(login_url=LOGIN_URL)
def get_report_(request, report_id) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_report(get_account(request), report_id), content_type="application/json"
    )

    # return JsonResponse(get_report(get_account(request), report_id), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_report_differences_compared_to_current_list_(request, report_id):
    return json_response(get_report_differences_compared_to_current_list(get_account(request), report_id))


@login_required(login_url=LOGIN_URL)
def get_previous_report_(request, urllist_id, at_when):
    return json_response(get_previous_report(get_account(request), urllist_id, at_when))


@login_required(login_url=LOGIN_URL)
def get_ad_hoc_tagged_report_(request, report_id: int):
    data = get_json_body(request)
    tags = data.get("tags", [])

    try:
        at_when: Optional[datetime] = datetime.fromisoformat(f"{data.get('custom_date')} {data.get('custom_time')}")
    except ValueError:
        at_when = None

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        ad_hoc_tagged_report(get_account(request), report_id, tags, at_when), content_type="application/json"
    )


@login_required(login_url=LOGIN_URL)
def save_ad_hoc_tagged_report_(request, report_id: int):
    data = get_json_body(request)
    tags = data.get("tags", [])
    try:
        at_when: Optional[datetime] = datetime.fromisoformat(f"{data.get('custom_date')} {data.get('custom_time')}")
    except ValueError:
        at_when = None
    return JsonResponse(save_ad_hoc_tagged_report(get_account(request), report_id, tags, at_when))


@login_required(login_url=LOGIN_URL)
def get_recent_reports_(request) -> JsonResponse:
    return json_response(get_recent_reports(get_account(request)))


@login_required(login_url=LOGIN_URL)
def get_urllist_report_graph_data_(request, urllist_ids, report_type: str = "web") -> JsonResponse:
    return json_response(get_urllist_timeline_graph(get_account(request), urllist_ids, report_type))


# No login required: reports via this method are public
@csrf_exempt
def get_shared_report_(request, report_code: str) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files

    data = get_json_body(request)

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_shared_report(report_code, data.get("share_code", "")), content_type="application/json"
    )


@csrf_exempt
def get_public_reports_(request) -> JsonResponse:
    return json_response(get_public_reports())


@login_required(login_url=LOGIN_URL)
def x_share(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(share(account, data.get("report_id", -1), data.get("public_share_code", "")), safe=False)


@login_required(login_url=LOGIN_URL)
def x_unshare(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(unshare(account, data.get("report_id", -1)), safe=False)


@login_required(login_url=LOGIN_URL)
def x_update_share_code(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(
        update_share_code(account, data.get("report_id", -1), data.get("public_share_code", "")), safe=False
    )


@login_required(login_url=LOGIN_URL)
def x_update_report_code(request):
    data = get_json_body(request)
    account = get_account(request)
    return JsonResponse(update_report_code(account, data.get("report_id", -1)), safe=False)


def get_publicly_shared_lists_per_account_(request, account_id) -> JsonResponse:
    return JsonResponse(get_publicly_shared_lists_per_account(account_id), safe=False)


def get_publicly_shared_lists_per_account_and_list_id_(request, account_id, urllist_id) -> JsonResponse:
    return JsonResponse(get_publicly_shared_lists_per_account_and_list_id(account_id, urllist_id), safe=False)


def get_latest_report_id_from_list(request, urllist_id) -> JsonResponse:
    return JsonResponse(get_latest_report_id_from_list_and_type(urllist_id, ""), safe=False)


def get_latest_report_id_from_list_and_type_(request, urllist_id, report_type) -> JsonResponse:
    return JsonResponse(get_latest_report_id_from_list_and_type(urllist_id, report_type), safe=False)


def improvement_regressions_compared_to_previous_report_(request, report_id):
    account = get_account(request)

    report = UrlListReport.objects.all().filter(id=report_id, urllist__account=account).first()
    return (
        JsonResponse(
            values_from_previous_report(
                report.id,
                report.get_previous_report_from_this_list(),
            ),
            safe=False,
        )
        if report
        else JsonResponse({}, safe=False)
    )
