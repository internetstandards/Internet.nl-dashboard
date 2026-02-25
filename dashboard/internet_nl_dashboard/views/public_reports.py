# SPDX-License-Identifier: Apache-2.0
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.logic.report import (
    PublicReportItemSchema,
    ReportSchema,
    SharedReportAuthRequiredSchema,
    SharedReportInputSchema,
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
        200: list[ReportSchema],
        201: SharedReportAuthRequiredSchema,
        404: OperationResponseSchema,
    },
)
def get_shared_report_api(request, report_code: str) -> HttpResponse:
    # no code :)
    log.debug(report_code)
    payload = get_shared_report(report_code, "")
    if payload == []:
        return HttpResponse(
            operation_response(error=True, message="report_not_found").json(),
            content_type="application/json",
            status=404,
        )
    if isinstance(payload, str) and '"authentication_required": true' in payload:
        return HttpResponse(payload, content_type="application/json", status=201)
    return HttpResponse(payload, content_type="application/json")


@router.post(
    "/{report_code}",
    response={
        200: ReportSchema | SharedReportAuthRequiredSchema,
        201: SharedReportAuthRequiredSchema,
        404: OperationResponseSchema,
    },
)
@csrf_exempt
def get_shared_report_api_with_code(request, report_code: str, data: SharedReportInputSchema) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    payload = get_shared_report(report_code, data.share_code)
    if payload == []:
        return HttpResponse(
            operation_response(error=True, message="report_not_found").json(),
            content_type="application/json",
            status=404,
        )
    if isinstance(payload, str) and '"authentication_required": true' in payload:
        return HttpResponse(payload, content_type="application/json", status=201)
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
