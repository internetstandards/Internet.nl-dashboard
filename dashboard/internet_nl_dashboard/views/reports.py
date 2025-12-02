# SPDX-License-Identifier: Apache-2.0
from django.http import HttpResponse
from ninja import Router
from ninja.security import django_auth

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.mail import ImprovementRegressionSummarySchema, values_from_previous_report
from dashboard.internet_nl_dashboard.logic.report import (
    RecentReportItemSchema,
    ReportSchema,
    ReportVsListDifferenceSchema,
    SaveAdHocTaggedReportInputSchema,
    ShareCodeSchema,
    ad_hoc_tagged_report,
    get_recent_reports,
    get_report,
    get_report_differences_compared_to_current_list,
    parse_ad_hoc_input,
    save_ad_hoc_tagged_report,
    share,
    unshare,
    update_report_code,
    update_share_code,
)
from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet, upgrade_excel_spreadsheet
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.views import create_spreadsheet_download, get_account

router = Router(tags=["Reports"], auth=django_auth)


@router.get("", response={200: list[RecentReportItemSchema]})
def get_recent_reports_operation(request):
    return get_recent_reports(get_account(request))


@router.get("/{report_id}", response={200: list[ReportSchema]})
def get_report_operation(request, report_id: int) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_report(get_account(request), report_id), content_type="application/json"
    )


@router.get(
    "/{report_id}/differences",
    response={200: ReportVsListDifferenceSchema},
)
def get_report_differences_compared_to_current_list_operation(request, report_id: int):
    return get_report_differences_compared_to_current_list(get_account(request), report_id)


@router.get("/{report_id}/improvements-and-regressions", response={200: ImprovementRegressionSummarySchema})
def improvement_regressions_compared_to_previous_report_operation(request, report_id: int):
    account = get_account(request)
    report = UrlListReport.objects.all().filter(id=report_id, urllist__account=account).first()
    if report:
        return values_from_previous_report(
            report.id,
            report.get_previous_report_from_this_list(),
        )
    # Return an empty structured response when no report is found
    return values_from_previous_report(0, None)


@router.get("/{report_id}/spreadsheets/{file_type}")
def download_spreadsheet(request, report_id: int, file_type: str) -> HttpResponse:
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


@router.post("/{report_id}/share", response={200: OperationResponseSchema})
def share_operation(request, report_id: int, data: ShareCodeSchema):
    return share(get_account(request), report_id, data.public_share_code)


@router.put("/{report_id}/share/report-code", response={200: OperationResponseSchema})
def update_report_code_operation(request, report_id: int):
    return update_report_code(get_account(request), report_id)


@router.delete("/{report_id}/share", response={200: OperationResponseSchema})
def unshare_operation(request, report_id: int):
    return unshare(get_account(request), report_id)


@router.put("/{report_id}/share/share-code", response={200: OperationResponseSchema})
def update_share_code_operation(request, report_id: int, data: ShareCodeSchema):
    return update_share_code(get_account(request), report_id, data.public_share_code)


@router.get("/{report_id}/ad-hoc", response={200: list[ReportSchema]})
def get_ad_hoc_tagged_report_operation(request, report_id: int, data: SaveAdHocTaggedReportInputSchema):
    tags, at_when = parse_ad_hoc_input(data)

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        ad_hoc_tagged_report(get_account(request), report_id, tags, at_when), content_type="application/json"
    )


@router.post("/{report_id}/ad-hoc", response={200: OperationResponseSchema})
def save_ad_hoc_tagged_report_operation(request, report_id: int, data: SaveAdHocTaggedReportInputSchema):
    tags, at_when = parse_ad_hoc_input(data)
    return save_ad_hoc_tagged_report(get_account(request), report_id, tags, at_when)


# # todo: route seems not to be used anymore.
# @router.get("/{urllist_id}/get_previous//{str:at_when}", response={200: list[ReportSchema]})
# def get_previous_report_operation(request, urllist_id: int, at_when):
#     return HttpResponse(  # pylint: disable=http-response-with-content-type-json
#         get_previous_report(get_account(request), urllist_id, at_when), content_type="application/json"
#     )
