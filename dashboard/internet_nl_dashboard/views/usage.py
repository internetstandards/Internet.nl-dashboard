from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dashboard.internet_nl_dashboard.logic.usage import usage_metrics
from dashboard.internet_nl_dashboard.views import LOGIN_URL


@login_required(login_url=LOGIN_URL)
def usage_(request) -> JsonResponse:
    return JsonResponse(usage_metrics())
