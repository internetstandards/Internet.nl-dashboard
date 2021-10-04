# SPDX-License-Identifier: Apache-2.0
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.scanners.subdomains import request_scan, scan_status
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def request_subdomain_discovery_scan_(request, urllist_id) -> JsonResponse:
    return JsonResponse(request_scan(get_account(request), urllist_id), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
def subdomain_discovery_scan_status_(request, urllist_id) -> JsonResponse:
    return JsonResponse(scan_status(get_account(request), urllist_id), encoder=JSEncoder, safe=False)
