# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

import django_excel as excel
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify

from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet, upgrade_excel_spreadsheet
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def download_spreadsheet(request, report_id, file_type) -> HttpResponse:
    account = get_account(request)

    filename, spreadsheet = create_spreadsheet(account=account, report_id=report_id)

    if file_type == "xlsx":
        # todo: requesting infinite files will flood the system as temp files are saved. Probably load file into
        #   memory and then remove the original file. With the current group of users the risk is minimal, so no bother

        # Upgrading happens with openpyxl which supports formulas. You cannot open those files with django_excel as
        # that does _not_ understand formulas and will simply delete them.
        file_type = "xlsx-openpyxl"
        spreadsheet = upgrade_excel_spreadsheet(spreadsheet)

    return create_spreadsheet_download(filename, spreadsheet, file_type)


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
        with open(spreadsheet_data.name, 'rb') as file_handle:
            output: HttpResponse = HttpResponse(file_handle.read())
        file_type = "xlsx"
    else:
        # Simple xls files and such
        output = excel.make_response(spreadsheet_data, file_type)

    output["Content-Disposition"] = f"attachment; filename={slugify(file_name)}.{file_type}"
    output["Content-type"] = content_types[file_type]

    return output
