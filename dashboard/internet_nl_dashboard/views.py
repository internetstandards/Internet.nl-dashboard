from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dashboard import __version__

LOGIN_URL = '/account/login/'


# Create your views here.
def index(request):

    return render(request, 'internet_nl_dashboard/index.html', {
        'version': __version__,
        'debug': settings.DEBUG,
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'menu_item_login': "current",
    })


@login_required(login_url=LOGIN_URL)
def dashboard(request):

    return render(request, 'internet_nl_dashboard/dashboard.html', {
        'menu_item_dashboard': "current",
    })


@login_required(login_url=LOGIN_URL)
def addressmanager(request):

    return render(request, 'internet_nl_dashboard/addressmanager.html', {
        'menu_item_addressmanager': "current",
    })


@login_required(login_url=LOGIN_URL)
def logout_view(request):
    logout(request)
    return index(request)
