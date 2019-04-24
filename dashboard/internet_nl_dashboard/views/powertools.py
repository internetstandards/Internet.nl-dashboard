from typing import Tuple

from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.internet_nl_dashboard.forms import InstantAccountAddForm
from dashboard.internet_nl_dashboard.models import Account, DashboardUser
from dashboard.internet_nl_dashboard.views import (LOGIN_URL, dashboard, get_account,
                                                   inject_default_language_cookie)


# Create your views here.
@login_required(login_url=LOGIN_URL)
def powertools(request) -> HttpResponse:

    # only for the true superusers :)
    if not request.user.is_staff and request.user.is_active and request.user.is_superuser:
        return dashboard.dashboard(request)

    # account switching.=
    if request.POST.get('change_account', None):
        dashboard_user = DashboardUser.objects.all().filter(user=request.user).first()
        # very new users don't have the dashboarduser fields filled in, and are thus not connected to an account.
        if not dashboard_user:
            dashboard_user = DashboardUser(**{'account': Account.objects.all().first(), 'user': request.user})

        dashboard_user.account = Account.objects.get(id=request.POST.get('change_account'))
        dashboard_user.save()

    selected_account_id: int = 0
    account = get_account(request)
    if account:
        selected_account_id = account.pk
    # end account switching

    # Fast account creation. Of the most basic kind.
    state, add_account_and_user_form = default_form_logic(InstantAccountAddForm, request)

    response = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/powertools.html', {
        'add_account_and_user_form': add_account_and_user_form,
        'add_account_and_user_form_state': state,
        'menu_item_powertools': "current",
        'selected_account': selected_account_id,
        'accounts': list(Account.objects.all().values('id', 'name'))
    })

    return inject_default_language_cookie(request, response)


def default_form_logic(form, request) -> Tuple[str, forms.Form]:

    if not request.POST:
        return "initial", form()

    form = form(request.POST)

    if not form.is_valid():
        return "invalid", form

    form.save()
    return "success", form
