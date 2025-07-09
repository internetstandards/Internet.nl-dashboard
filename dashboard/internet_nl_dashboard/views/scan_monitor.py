# SPDX-License-Identifier: Apache-2.0
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from dashboard.internet_nl_dashboard.logic.scan_monitor import get_scan_monitor_data
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, json_response

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def running_scans(request) -> HttpResponse:
    account = get_account(request)

    # list of dicts: In order to allow non-dict objects to be serialized set the safe parameter to False.
    return json_response(get_scan_monitor_data(account))
