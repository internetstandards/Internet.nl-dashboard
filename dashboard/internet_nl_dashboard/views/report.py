# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Optional

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
    ShareInputSchema,
    UnshareInputSchema,
    UpdateReportCodeInputSchema,
    UpdateShareCodeInputSchema,
    UrlListTimelineSeriesSchema,
    ad_hoc_tagged_report,
    get_previous_report,
    get_recent_reports,
    get_report,
    get_report_differences_compared_to_current_list,
    get_urllist_timeline_graph,
    save_ad_hoc_tagged_report,
    share,
    unshare,
    update_report_code,
    update_share_code,
)
from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet, upgrade_excel_spreadsheet
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.views import create_spreadsheet_download, get_account, get_json_body

router = Router(tags=["Reports"], auth=django_auth)


@router.get("/get/{report_id}", response={200: list[ReportSchema]})
def get_report_api(request, report_id: int) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_report(get_account(request), report_id), content_type="application/json"
    )


@router.get("/differences_compared_to_current_list/{report_id}", response={200: ReportVsListDifferenceSchema})
def get_report_differences_compared_to_current_list_api(request, report_id: int):
    return get_report_differences_compared_to_current_list(get_account(request), report_id)


# todo: route seems not to be used anymore.
@router.get("/get_previous/{int:urllist_id}/{str:at_when}", response={200: list[ReportSchema]})
def get_previous_report_api(request, urllist_id, at_when):
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_previous_report(get_account(request), urllist_id, at_when), content_type="application/json"
    )


@router.get("/ad_hoc/{report_id}", response={200: list[ReportSchema]})
def get_ad_hoc_tagged_report_(request, report_id: int):
    data = get_json_body(request)
    tags = data.get("tags", [])

    try:
        at_when: Optional[datetime] = datetime.fromisoformat(f"{data.get('custom_date')} {data.get('custom_time')}")
    except ValueError:
        at_when = None

    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        ad_hoc_tagged_report(get_account(request), report_id, tags, at_when), content_type="application/json"
    )


@router.post("/ad_hoc_save/{report_id}", response={200: OperationResponseSchema})
def save_ad_hoc_tagged_report_api(request, report_id: int, data: SaveAdHocTaggedReportInputSchema):
    tags = data.tags or []
    try:
        at_when: Optional[datetime] = (
            datetime.fromisoformat(f"{data.custom_date} {data.custom_time}")
            if data.custom_date and data.custom_time
            else None
        )
    except ValueError:
        at_when = None
    return save_ad_hoc_tagged_report(get_account(request), report_id, tags, at_when)


@router.get("/list", response={200: list[RecentReportItemSchema]})
def get_recent_reports_api(request):
    return get_recent_reports(get_account(request))


@router.get("/urllist_timeline_graph/{urllist_ids}/{report_type}", response={200: list[UrlListTimelineSeriesSchema]})
def get_urllist_timeline_graph_api(request, urllist_ids: str, report_type: str):
    return get_urllist_timeline_graph(get_account(request), urllist_ids, report_type)


@router.post("/share/share", response={200: OperationResponseSchema})
def share_api(request, data: ShareInputSchema):
    account = get_account(request)
    return share(account, data.report_id, data.public_share_code)


@router.post("/share/unshare", response={200: OperationResponseSchema})
def unshare_api(request, data: UnshareInputSchema):
    account = get_account(request)
    return unshare(account, data.report_id)


@router.post("/share/update_share_code", response={200: OperationResponseSchema})
def update_share_code_api(request, data: UpdateShareCodeInputSchema):
    account = get_account(request)
    return update_share_code(account, data.report_id, data.public_share_code)


@router.post("/share/update_report_code", response={200: OperationResponseSchema})
def update_report_code_api(request, data: UpdateReportCodeInputSchema):
    account = get_account(request)
    return update_report_code(account, data.report_id)


@router.get("/get_improvements_and_regressions/{report_id}", response={200: ImprovementRegressionSummarySchema})
def improvement_regressions_compared_to_previous_report_api(request, report_id: int):
    account = get_account(request)
    report = UrlListReport.objects.all().filter(id=report_id, urllist__account=account).first()
    if report:
        return values_from_previous_report(
            report.id,
            report.get_previous_report_from_this_list(),
        )
    # Return an empty structured response when no report is found
    return values_from_previous_report(0, None)


@router.get("/spreadsheet/{report_id}/{file_type}")
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
