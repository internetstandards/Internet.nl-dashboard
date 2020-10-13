from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic.user import save_user_settings, get_user_settings
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_json_body, get_dashboarduser


@login_required(login_url=LOGIN_URL)
def save_user_settings_(request) -> JsonResponse:
    return JsonResponse(save_user_settings(get_dashboarduser(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def get_user_settings_(request) -> JsonResponse:
    return JsonResponse(get_user_settings(get_dashboarduser(request)))
