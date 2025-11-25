# SPDX-License-Identifier: Apache-2.0
import logging

from constance import config
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.internet_nl_dashboard.views import LOGIN_URL

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def upload(request) -> HttpResponse:
    """This classic page is needed for old school upload scenarios. Those seemed to be required by some browsers."""
    response: HttpResponse = render(
        request,
        "internet_nl_dashboard/templates/internet_nl_dashboard/upload.html",
        {
            "menu_item_addressmanager": "current",
            "max_lists": int(config.DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET),
            "max_urls": int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET),
        },
    )

    return response
