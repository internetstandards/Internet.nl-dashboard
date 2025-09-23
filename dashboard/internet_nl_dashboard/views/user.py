# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.decorators import login_required
from ninja import Router

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.user import (
    SaveUserSettingsInputSchema,
    UserSettingsSchema,
    get_user_settings,
    save_user_settings,
)
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_dashboarduser

router = Router(tags=["user"])  # Mounted under the urllist router


@router.get("/settings", response={200: UserSettingsSchema})
@login_required(login_url=LOGIN_URL)
def get_user_settings_api(request):
    return get_user_settings(get_dashboarduser(request))


@router.post("/settings/save", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def save_user_settings_api(request, data: SaveUserSettingsInputSchema):
    return save_user_settings(get_dashboarduser(request), data)
