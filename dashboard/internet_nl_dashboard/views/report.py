# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.mail import ImprovementRegressionSummarySchema, values_from_previous_report
from dashboard.internet_nl_dashboard.logic.report import (
    PublicReportItemSchema,
    RecentReportItemSchema,
    ReportSchema,
    ReportVsListDifferenceSchema,
    SaveAdHocTaggedReportInputSchema,
    SharedReportAuthRequiredSchema,
    SharedReportInputSchema,
    ShareInputSchema,
    UnshareInputSchema,
    UpdateReportCodeInputSchema,
    UpdateShareCodeInputSchema,
    UrlListTimelineSeriesSchema,
    ad_hoc_tagged_report,
    get_previous_report,
    get_public_reports,
    get_recent_reports,
    get_report,
    get_report_differences_compared_to_current_list,
    get_shared_report,
    get_urllist_timeline_graph,
    save_ad_hoc_tagged_report,
    share,
    unshare,
    update_report_code,
    update_share_code,
)
from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet, upgrade_excel_spreadsheet
from dashboard.internet_nl_dashboard.logic.shared_report_lists import (
    LatestReportCodeSchema,
    PubliclySharedListResponseSchema,
    get_latest_report_id_from_list_and_type,
    get_publicly_shared_lists_per_account,
    get_publicly_shared_lists_per_account_and_list_id,
)
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.views import LOGIN_URL, create_spreadsheet_download, get_account, get_json_body

# Ninja router for report endpoints
router = Router(tags=["report"])


@router.get("/get/{report_id}", response={200: list[ReportSchema]})
@router.post("/get/{report_id}", response={200: list[ReportSchema]})
@login_required(login_url=LOGIN_URL)
def get_report_api(request, report_id: int) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_report(get_account(request), report_id), content_type="application/json"
    )


@router.get("/differences_compared_to_current_list/{report_id}", response={200: ReportVsListDifferenceSchema})
@login_required(login_url=LOGIN_URL)
def get_report_differences_compared_to_current_list_api(request, report_id: int):
    return get_report_differences_compared_to_current_list(get_account(request), report_id)


# todo: route seems not to be used anymore.
@router.get("/get_previous/{int:urllist_id}/{str:at_when}", response={200: list[ReportSchema]})
@login_required(login_url=LOGIN_URL)
def get_previous_report_api(request, urllist_id, at_when):
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_previous_report(get_account(request), urllist_id, at_when), content_type="application/json"
    )


@router.post("/ad_hoc/{report_id}", response={200: list[ReportSchema]})
@login_required(login_url=LOGIN_URL)
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
@login_required(login_url=LOGIN_URL)
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
@login_required(login_url=LOGIN_URL)
def get_recent_reports_api(request):
    return get_recent_reports(get_account(request))


@router.get("/urllist_timeline_graph/{urllist_ids}/{report_type}", response={200: list[UrlListTimelineSeriesSchema]})
@login_required(login_url=LOGIN_URL)
def get_urllist_timeline_graph_api(request, urllist_ids: str, report_type: str):
    return get_urllist_timeline_graph(get_account(request), urllist_ids, report_type)


# No login required: reports via this method are public
@router.post("/shared/{report_code}", response={200: ReportSchema | SharedReportAuthRequiredSchema})
@csrf_exempt
def get_shared_report_api(request, report_code: str, data: SharedReportInputSchema) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_shared_report(report_code, data.share_code), content_type="application/json"
    )


@router.get(
    "/public",
    response={200: list[PublicReportItemSchema]},
    summary="List of publicly available reports",
    description="List of public reports which are published on the front page of the dashboard. "
    "Public reports have to be explicitly configured in the admin interface.",
)
@csrf_exempt
def get_public_reports_api(request):
    return get_public_reports()


@router.post("/share/share", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def share_api(request, data: ShareInputSchema):
    account = get_account(request)
    return share(account, data.report_id, data.public_share_code)


@router.post("/share/unshare", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def unshare_api(request, data: UnshareInputSchema):
    account = get_account(request)
    return unshare(account, data.report_id)


@router.post("/share/update_share_code", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def update_share_code_api(request, data: UpdateShareCodeInputSchema):
    account = get_account(request)
    return update_share_code(account, data.report_id, data.public_share_code)


@router.post("/share/update_report_code", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def update_report_code_api(request, data: UpdateReportCodeInputSchema):
    account = get_account(request)
    return update_report_code(account, data.report_id)


@router.get("/public/account/{account_id}/lists/all", response={200: list[PubliclySharedListResponseSchema]})
def get_publicly_shared_lists_per_account_api(request, account_id: int):
    return get_publicly_shared_lists_per_account(account_id)


@router.get("/public/account/{account_id}/lists/{urllist_id}", response={200: list[PubliclySharedListResponseSchema]})
def get_publicly_shared_lists_per_account_and_list_id_api(request, account_id: int, urllist_id: int):
    return get_publicly_shared_lists_per_account_and_list_id(account_id, urllist_id)


@router.get("/public/lists/{urllist_id}/latest", response={200: LatestReportCodeSchema})
def get_latest_report_id_from_list_api(request, urllist_id: int):
    return get_latest_report_id_from_list_and_type(urllist_id, "")


@router.get("/public/lists/{urllist_id}/latest/{report_type}", response={200: LatestReportCodeSchema})
def get_latest_report_id_from_list_and_type_api(request, urllist_id: int, report_type: str):
    return get_latest_report_id_from_list_and_type(urllist_id, report_type)


@router.get("/get_improvements_and_regressions/{report_id}", response={200: ImprovementRegressionSummarySchema})
@login_required(login_url=LOGIN_URL)
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
@login_required(login_url=LOGIN_URL)
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
