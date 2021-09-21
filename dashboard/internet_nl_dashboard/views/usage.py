# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic.usage import usage_metrics
from dashboard.internet_nl_dashboard.views import LOGIN_URL
from dashboard.internet_nl_dashboard.views.powertools import is_powertool_user


@user_passes_test(is_powertool_user, login_url=LOGIN_URL)
def usage_(request) -> JsonResponse:
    return JsonResponse(usage_metrics())
