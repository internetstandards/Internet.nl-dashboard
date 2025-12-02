# SPDX-License-Identifier: Apache-2.0
from ninja import Router
from ninja.security import django_auth

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.account import get_report_settings, save_report_settings
from dashboard.internet_nl_dashboard.logic.user import (
    SaveUserSettingsInputSchema,
    UserSettingsSchema,
    get_user_settings,
    save_user_settings,
)
from dashboard.internet_nl_dashboard.views import get_account, get_dashboarduser, get_json_body

router = Router(tags=["Settings"], auth=django_auth)  # Mounted under the urllist router


@router.get("/user", response={200: UserSettingsSchema})
def get_user_settings_api(request):
    return get_user_settings(get_dashboarduser(request))


@router.post("/user", response={200: OperationResponseSchema})
def save_user_settings_api(request, data: SaveUserSettingsInputSchema):
    return save_user_settings(get_dashboarduser(request), data)


@router.get("/account/report", response={200: OperationResponseSchema})
def get_report_settings_api(request):
    return get_report_settings(get_account(request))


@router.post("/account/report", response={200: OperationResponseSchema})
def save_report_settings_api(request):
    return save_report_settings(get_account(request), get_json_body(request))
