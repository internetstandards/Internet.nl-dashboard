
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.dashboard import get_recent_reports, get_report
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, get_account,
                                                   inject_default_language_cookie)


@login_required(login_url=LOGIN_URL)
def dashboard(request) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/dashboard.html', {
        'menu_item_dashboard': "current",
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def get_report_(request, report_id) -> JsonResponse:
    account = get_account(request)
    response = get_report(account, report_id)
    return JsonResponse(response, encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def get_recent_reports_(request) -> JsonResponse:
    account = get_account(request)
    response = get_recent_reports(account)
    return JsonResponse(response, encoder=JSEncoder, safe=False)
