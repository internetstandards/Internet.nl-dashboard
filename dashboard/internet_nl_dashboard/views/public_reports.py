# SPDX-License-Identifier: Apache-2.0
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from dashboard.internet_nl_dashboard.logic.report import (
    PublicReportItemSchema,
    ReportSchema,
    SharedReportAccessDenied,
    SharedReportAccessProblemSchema,
    SharedReportInputSchema,
    SharedReportNotFound,
    get_public_reports,
    get_shared_report,
)
from dashboard.internet_nl_dashboard.logic.shared_report_lists import (
    LatestReportCodeSchema,
    PubliclySharedListResponseSchema,
    get_latest_report_id_from_list_and_type,
    get_publicly_shared_lists_per_account,
    get_publicly_shared_lists_per_account_and_list_id,
)
from dashboard.internet_nl_dashboard.problems import ProblemSchema, problem_responses

log = logging.getLogger(__package__)

# No login required: reports via this method are public
router = Router(tags=["Public Reports"])


@router.get(
    "",
    response={200: list[PublicReportItemSchema]},
    summary="List of publicly available reports",
    description="List of public reports which are published on the front page of the dashboard. "
    "Public reports have to be explicitly configured in the admin interface.",
)
def get_public_reports_operation(request):
    return get_public_reports()


@router.get(
    "/{report_code}",
    response={
        200: ReportSchema,
        SharedReportAccessDenied.status: SharedReportAccessProblemSchema,
        SharedReportNotFound.status: ProblemSchema,
    },
    openapi_extra=problem_responses(get_shared_report),
)
def get_shared_report_api(request, report_code: str) -> HttpResponse:
    payload = get_shared_report(report_code, "")
    return HttpResponse(payload, content_type="application/json")


@router.post(
    "/{report_code}",
    response={
        200: ReportSchema,
        SharedReportAccessDenied.status: SharedReportAccessProblemSchema,
        SharedReportNotFound.status: ProblemSchema,
    },
    openapi_extra=problem_responses(get_shared_report),
)
@csrf_exempt
def get_shared_report_api_with_code(request, report_code: str, data: SharedReportInputSchema) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    payload = get_shared_report(report_code, data.share_code)
    return HttpResponse(payload, content_type="application/json")


@router.get("/accounts/{account_id}", response={200: list[PubliclySharedListResponseSchema]})
def get_publicly_shared_lists_per_account_operation(request, account_id: int):
    return get_publicly_shared_lists_per_account(account_id)


@router.get(
    "/accounts/{account_id}/urllists/{urllist_id}",
    response={200: list[PubliclySharedListResponseSchema]},
)
def get_publicly_shared_lists_per_account_and_list_id_operation(request, account_id: int, urllist_id: int):
    return get_publicly_shared_lists_per_account_and_list_id(account_id, urllist_id)


@router.get("/urllists/{urllist_id}/latest", response={200: LatestReportCodeSchema})
def get_latest_report_id_from_list_operation(request, urllist_id: int):
    return get_latest_report_id_from_list_and_type(urllist_id, "")


@router.get(
    "/urllists/{urllist_id}/latest/{report_type}",
    response={200: LatestReportCodeSchema},
)
def get_latest_report_id_from_list_and_type_operation(request, urllist_id: int, report_type: str):
    return get_latest_report_id_from_list_and_type(urllist_id, report_type)
