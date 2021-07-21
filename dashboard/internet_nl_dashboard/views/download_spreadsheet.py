import logging

import django_excel as excel
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import (create_spreadsheet,
                                                                         upgrade_excel_spreadsheet)
from dashboard.internet_nl_dashboard.views.__init__ import LOGIN_URL, get_account

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def download_spreadsheet(request, report_id, file_type) -> HttpResponse:
    account = get_account(request)

    filename, spreadsheet = create_spreadsheet(account=account, report_id=report_id)

    if not spreadsheet:
        return JsonResponse({}, encoder=JSEncoder)

    if file_type == "xlsx":
        # todo: requesting infinite files will flood the system as temp files are saved. Probably load file into
        #   memory and then remove the original file. With the current group of users the risk is minimal, so no bother
        tmp_file_handle = upgrade_excel_spreadsheet(spreadsheet)
        with open(tmp_file_handle.name, 'rb') as file_handle:
            response = HttpResponse(file_handle.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f"attachment; filename={slugify(filename)}.xlsx"
        return response

    if file_type == "ods":
        output = excel.make_response(spreadsheet, file_type)
        output["Content-Disposition"] = f"attachment; filename={slugify(filename)}.ods"
        output["Content-type"] = "application/vnd.oasis.opendocument.spreadsheet"
        return output

    if file_type == "csv":
        output = excel.make_response(spreadsheet, file_type)
        output["Content-Disposition"] = f"attachment; filename={slugify(filename)}.csv"
        output["Content-type"] = "text/csv"
        return output

    # anything that is not valid at all.
    return JsonResponse({}, encoder=JSEncoder)
