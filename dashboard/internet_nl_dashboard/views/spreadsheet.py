# SPDX-License-Identifier: Apache-2.0
import logging

from constance import config
from celery import group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.spreadsheet import (import_step_2, get_upload_history, save_file,
                                                               upload_domain_spreadsheet_to_list, import_step_1)
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_dashboarduser

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def upload(request) -> HttpResponse:

    response: HttpResponse = render(request, 'internet_nl_dashboard/templates/internet_nl_dashboard/upload.html', {
        'menu_item_addressmanager': "current",
        'max_lists': int(config.DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET),
        'max_urls':  int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET)
    })

    return response


@login_required(login_url=LOGIN_URL)
def upload_spreadsheet(request) -> HttpResponse:
    # Instead of some json message, give a full page, so the classic uploader also functions pretty well.
    # todo: Or should this be a redirect, so the 'reload' page does not try to resend the form...
    response = upload(request)

    # The status code is needed for dropzone. So a redirect status code will not work properly.
    response.status_code = 400

    # happens when no file is sent
    if 'file' not in request.FILES:
        return response

    if request.method == 'POST' and request.FILES['file']:
        file = save_file(request.FILES['file'])
        status = import_step_1(user=get_dashboarduser(request), file=file)
        print(status)

        if status['error']:
            # The GUI wants the error to contain some text: As that text is sensitive to xss(?) (probably only
            # if you see the output directly, not via javascript or json).
            status['error'] = status['message']
            return response

        group([import_step_2.si(get_dashboarduser(request).id, file)]).apply_async()

        response.status_code = 200
        return response

    return response


@login_required(login_url=LOGIN_URL)
def upload_history(request) -> JsonResponse:
    account = get_account(request)

    # list of dicts: In order to allow non-dict objects to be serialized set the safe parameter to False.
    return JsonResponse(get_upload_history(account), encoder=JSEncoder, safe=False)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def upload_list_(request, list_id):
    # params = get_json_body(request)
    return JsonResponse(upload_domain_spreadsheet_to_list(
        get_account(request),
        get_dashboarduser(request),
        list_id,
        request.FILES.get('file', None)
    ))
