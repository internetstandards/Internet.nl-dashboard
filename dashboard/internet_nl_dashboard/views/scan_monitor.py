# SPDX-License-Identifier: Apache-2.0
import logging

from django.contrib.auth.decorators import login_required
from ninja import Router

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.scan_monitor import (
    CancelScanInputSchema,
    ScanMonitorItemSchema,
    cancel_scan,
    get_scan_monitor_data,
)
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account

log = logging.getLogger(__package__)

router = Router(tags=["scan"])


@router.get("/monitor", response={200: list[ScanMonitorItemSchema]})
@login_required(login_url=LOGIN_URL)
def running_scans(request):
    account = get_account(request)
    return get_scan_monitor_data(account)


@router.post("/cancel", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def cancel_scan_api(request, data: CancelScanInputSchema):
    account = get_account(request)
    return cancel_scan(account, data.id)
