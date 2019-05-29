from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic.account import get_report_settings, save_report_settings
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body


@login_required(login_url=LOGIN_URL)
def get_report_settings_(request) -> JsonResponse:
    return JsonResponse(get_report_settings(get_account(request)))


@login_required(login_url=LOGIN_URL)
def save_report_settings_(request) -> JsonResponse:
    return JsonResponse(save_report_settings(get_account(request), get_json_body(request)))
