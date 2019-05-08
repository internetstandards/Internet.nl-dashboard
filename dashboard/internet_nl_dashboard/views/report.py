
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.report import (get_previous_report, get_recent_reports,
                                                          get_report, get_urllist_report_graph_data)
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, get_account,
                                                   inject_default_language_cookie)


@login_required(login_url=LOGIN_URL)
def dashboard(request, report_id=0) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/report.html', {
        'menu_item_dashboard': "current",
        'debug': settings.DEBUG
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def get_report_(request, report_id) -> JsonResponse:
    return JsonResponse(get_report(get_account(request), report_id), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_previous_report_(request, urllist_id, at_when):
    return JsonResponse(get_previous_report(get_account(request), urllist_id, at_when), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_recent_reports_(request) -> JsonResponse:
    return JsonResponse(get_recent_reports(get_account(request)), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_urllist_report_graph_data_(request, urllist_id) -> JsonResponse:
    return JsonResponse(get_urllist_report_graph_data(get_account(request), urllist_id), encoder=JSEncoder, safe=False)
