# SPDX-License-Identifier: Apache-2.0
from collections import defaultdict
from datetime import datetime
from typing import Annotated, Any, Literal

from django.http import HttpResponse
from ninja import Field, Router, Schema
from ninja.security import django_auth
from pydantic import StringConstraints
from websecmap.reporting.severity import get_severity
from websecmap.scanners.impact import get_impact
from websecmap.scanners.models import EndpointGenericScan

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
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


class LiveLatestMetricsInputSchema(Schema):
    urls: list[Annotated[str, StringConstraints(max_length=255)]] = Field(default=["internet.nl"])
    metrics: list[Annotated[str, StringConstraints(max_length=60)]] = Field(
        default=["internet_nl_mail_overall_score", "internet_nl_web_overall_score"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "urls": ["internet.nl"],
                "metrics": ["internet_nl_mail_overall_score", "internet_nl_web_overall_score"],
            }
        }
    }


class LiveLatestMetricSchema(Schema):
    type: str
    explanation: str
    evidence: str
    meaning: Any | None = None
    since: datetime
    last_scan: datetime
    high: int
    medium: int
    low: int
    ok: int
    not_testable: int | bool
    not_applicable: int | bool
    error_in_test: int | bool
    translation: str = ""
    technical_details: str = ""
    test_result: str = ""
    is_explained: bool
    scan: int
    scan_type: str
    highlight: dict[str, Any]
    impact: Literal["high", "medium", "low", "good"]


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


@router.get(
    "/{report_id}/improvements-and-regressions",
    response={200: ImprovementRegressionSummarySchema},
)
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
        ad_hoc_tagged_report(get_account(request), report_id, tags, at_when),
        content_type="application/json",
    )


@router.post("/{report_id}/ad-hoc", response={200: OperationResponseSchema})
def save_ad_hoc_tagged_report_operation(request, report_id: int, data: SaveAdHocTaggedReportInputSchema):
    tags, at_when = parse_ad_hoc_input(data)
    return save_ad_hoc_tagged_report(get_account(request), report_id, tags, at_when)


@router.post(
    "/metrics/now/",
    response={200: dict[str, dict[str, LiveLatestMetricSchema]], 403: OperationResponseSchema},
)
def get_ad_hoc_live_latest_metrics(request, data: LiveLatestMetricsInputSchema):
    """
    Return the live status on a series of metrics on a series of urls.

    The impact of this method scales linearly with the number of urls and metrics.

    Requires staff account. Make sure the is_staff flag is set for the user in the admin interface.
    """
    if not request.user.is_staff:
        return 403, operation_response(error=True, message="staff_account_required")

    scans = EndpointGenericScan.objects.filter(
        endpoint__url__url__in=data.urls,
        is_the_latest_scan=True,
        type__in=data.metrics,
    ).select_related("endpoint__url")

    ad_hoc_live_report = defaultdict(dict)

    for scan in scans:
        severity = get_severity(scan)
        severity["impact"] = get_impact(severity)

        # prevent confusion with useless fields
        del severity["comply_or_explain_explained_by"]
        del severity["comply_or_explain_explanation"]
        del severity["comply_or_explain_explanation_valid_until"]
        del severity["comply_or_explain_valid_at_time_of_report"]
        del severity["comply_or_explain_explained_on"]

        ad_hoc_live_report[scan.endpoint.url.url][severity["type"]] = severity

    return ad_hoc_live_report


# # todo: route seems not to be used anymore.
# @router.get("/{urllist_id}/get_previous//{str:at_when}", response={200: list[ReportSchema]})
# def get_previous_report_operation(request, urllist_id: int, at_when):
#     return HttpResponse(  # pylint: disable=http-response-with-content-type-json
#         get_previous_report(get_account(request), urllist_id, at_when), content_type="application/json"
#     )
