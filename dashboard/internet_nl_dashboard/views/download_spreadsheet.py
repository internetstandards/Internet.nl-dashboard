import logging

import django_excel as excel
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify
from websecmap.app.common import JSEncoder

from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet
from dashboard.internet_nl_dashboard.views.__init__ import LOGIN_URL, get_account

log = logging.getLogger(__package__)


@login_required(login_url=LOGIN_URL)
def download_spreadsheet(request, report_id, file_type) -> HttpResponse:
    account = get_account(request)

    filename, spreadsheet = create_spreadsheet(account=account, report_id=report_id)

    if not spreadsheet:
        return JsonResponse({}, encoder=JSEncoder)

    if file_type == "xlsx":
        http_response = excel.make_response(spreadsheet, file_type)
        http_response["Content-Disposition"] = "attachment; filename=%s.xlsx" % slugify(filename)
        http_response["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return http_response

    if file_type == "ods":
        output = excel.make_response(spreadsheet, file_type)
        output["Content-Disposition"] = "attachment; filename=%s.ods" % slugify(filename)
        output["Content-type"] = "application/vnd.oasis.opendocument.spreadsheet"
        return output

    if file_type == "csv":
        output = excel.make_response(spreadsheet, file_type)
        output["Content-Disposition"] = "attachment; filename=%s.csv" % slugify(filename)
        output["Content-type"] = "text/csv"
        return output

    # anything that is not valid at all.
    return JsonResponse({}, encoder=JSEncoder)
