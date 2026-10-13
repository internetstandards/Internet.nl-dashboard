# SPDX-License-Identifier: Apache-2.0
import logging

from ninja import Router, Status
from ninja.security import django_auth

from dashboard.internet_nl_dashboard.logic.scan_monitor import ScanMonitorItemSchema, cancel_scan, get_scan_monitor_data
from dashboard.internet_nl_dashboard.problems import problem_responses
from dashboard.internet_nl_dashboard.views import get_account

log = logging.getLogger(__package__)

router = Router(tags=["Scans"], auth=django_auth)


@router.get("", response={200: list[ScanMonitorItemSchema]})
def running_scans(request):
    account = get_account(request)
    return get_scan_monitor_data(account)


@router.delete(
    "/{scan_id}",
    response={204: None},
    openapi_extra=problem_responses(
        cancel_scan,
        descriptions={
            204: "The scan was cancelled, or was already cancelled. No response body.",
            400: "Invalid scan_id; the scan ID must be an integer.",
        },
    ),
)
def cancel_scan_api(request, scan_id: int):
    account = get_account(request)
    return Status(204, cancel_scan(account, scan_id))
