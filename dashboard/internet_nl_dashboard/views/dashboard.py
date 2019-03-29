
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.internet_nl_dashboard.views import LOGIN_URL, inject_default_language_cookie


@login_required(login_url=LOGIN_URL)
def dashboard(request) -> HttpResponse:

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/dashboard.html', {
        'menu_item_dashboard': "current",
    })

    return inject_default_language_cookie(request, response)
