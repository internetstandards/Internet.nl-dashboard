# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

import django_excel as excel
import orjson
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.text import slugify

from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__package__)
LOGIN_URL = "/account/login/"

"""
Todo: csrf via API calls...
    https://docs.djangoproject.com/en/dev/ref/csrf/#csrf-ajax
    Is handled and validated via middleware, so we don't need to concern ourselves with it here.
"""


def logout_view(request) -> HttpResponse:
    logout(request)
    return redirect("/")


def get_account(request) -> Account:
    # todo: what about the exceptions that happen when there is no account? Currently exceptions, it should not happen.
    # log.debug(request)
    # log.debug(request.user)
    return DashboardUser.objects.all().filter(user=request.user).get().account


def get_dashboarduser(request) -> DashboardUser:
    # todo: what about the exceptions that happen when there is no account? Currently exceptions, it should not happen.
    return DashboardUser.objects.all().filter(user=request.user).get()


def empty_response() -> JsonResponse:
    return JsonResponse({})


def error_response(message: str) -> JsonResponse:
    return JsonResponse({"status": "error", "message": message})


def get_json_body(request):

    try:
        user_input = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        user_input = {}

    return user_input


# pylint disable=http-response-with-content-type-json
def json_response(data: dict[Any, Any] | list[Any]) -> HttpResponse:
    return HttpResponse(orjson.dumps(data), content_type="application/json", status=200)


def create_spreadsheet_download(file_name: str, spreadsheet_data: Any, file_type: str = "xlsx") -> HttpResponse:

    if file_type not in ["xlsx", "ods", "csv", "xlsx-openpyxl"] or not spreadsheet_data or not file_name:
        return JsonResponse({})

    content_types = {
        "csv": "text/csv",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx-openpyxl": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    if file_type == "xlsx-openpyxl":
        with open(spreadsheet_data.name, "rb") as file_handle:
            output: HttpResponse = HttpResponse(file_handle.read())
        file_type = "xlsx"
    else:
        # Simple xls files and such
        output = excel.make_response(spreadsheet_data, file_type)

    output["Content-Disposition"] = f"attachment; filename={slugify(file_name)}.{file_type}"
    output["Content-type"] = content_types[file_type]

    return output
