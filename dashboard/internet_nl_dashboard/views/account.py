# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.decorators import login_required
from ninja import Router

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.account import get_report_settings, save_report_settings
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body

router = Router(tags=["account"])  # Mounted in urls.py at /data/account


@router.get("/report_settings/get", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def get_report_settings_api(request):
    return get_report_settings(get_account(request))


@router.post("/report_settings/save", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def save_report_settings_api(request):
    return save_report_settings(get_account(request), get_json_body(request))
