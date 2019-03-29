import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from dashboard.internet_nl_dashboard.scan_monitor import get_running_scans
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, get_account,
                                                   inject_default_language_cookie)
from websecmap.app.common import JSEncoder

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def scan_monitor(request) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/scan_monitor.html', {
        'menu_item_dashboard': "current",
    })

    return inject_default_language_cookie(request, response)


@login_required(login_url=LOGIN_URL)
def running_scans(request) -> JsonResponse:
    account = get_account(request)

    # list of dicts: In order to allow non-dict objects to be serialized set the safe parameter to False.
    return JsonResponse(get_running_scans(account), encoder=JSEncoder, safe=False)
