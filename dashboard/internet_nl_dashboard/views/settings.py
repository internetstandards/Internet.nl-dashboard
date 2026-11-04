# SPDX-License-Identifier: Apache-2.0
from ninja import Body, Router, Status
from ninja.security import django_auth

from dashboard.internet_nl_dashboard.logic.account import get_report_settings, save_report_settings
from dashboard.internet_nl_dashboard.logic.user import (
    SaveUserSettingsInputSchema,
    UserSettingsSchema,
    get_user_settings,
    save_user_settings,
)
from dashboard.internet_nl_dashboard.problems import ProblemSchema
from dashboard.internet_nl_dashboard.views import get_account, get_dashboarduser

router = Router(tags=["Settings"], auth=django_auth)  # Mounted under the urllist router


@router.get("/user", response={200: UserSettingsSchema})
def get_user_settings_api(request):
    return get_user_settings(get_dashboarduser(request))


@router.post(
    "/user",
    response={204: None, 400: ProblemSchema, 404: ProblemSchema},
    openapi_extra={
        "responses": {
            400: {
                "description": (
                    "Required settings are missing, the selected language is unsupported, or the "
                    "email address is invalid."
                )
            },
            404: {"description": "User settings could not be found for the current user."},
        }
    },
)
def save_user_settings_api(request, data: SaveUserSettingsInputSchema):
    return Status(204, save_user_settings(get_dashboarduser(request), data))


@router.get("/account/report", response={200: dict})
def get_report_settings_api(request):
    return get_report_settings(get_account(request))


@router.post("/account/report", response={204: None})
def save_report_settings_api(request, data: dict = Body(...)):
    return save_report_settings(get_account(request), data)
