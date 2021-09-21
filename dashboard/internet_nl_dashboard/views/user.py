# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic.user import get_user_settings, save_user_settings
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_dashboarduser, get_json_body


@login_required(login_url=LOGIN_URL)
def save_user_settings_(request) -> JsonResponse:
    return JsonResponse(save_user_settings(get_dashboarduser(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def get_user_settings_(request) -> JsonResponse:
    return JsonResponse(get_user_settings(get_dashboarduser(request)))
