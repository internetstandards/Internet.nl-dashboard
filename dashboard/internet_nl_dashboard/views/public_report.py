# SPDX-License-Identifier: Apache-2.0
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import Router

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

router = Router(tags=["Public Reports"])

# No login required: reports via this method are public


@router.post("/shared/{report_code}", response={200: ReportSchema | SharedReportAuthRequiredSchema})
@csrf_exempt
def get_shared_report_api(request, report_code: str, data: SharedReportInputSchema) -> HttpResponse:
    # Explicitly NOT use jsonresponse as this loads the json data into an encoder which is extremely slow on large files
    return HttpResponse(  # pylint: disable=http-response-with-content-type-json
        get_shared_report(report_code, data.share_code), content_type="application/json"
    )


@router.get(
    "",
    response={200: list[PublicReportItemSchema]},
    summary="List of publicly available reports",
    description="List of public reports which are published on the front page of the dashboard. "
    "Public reports have to be explicitly configured in the admin interface.",
)
def get_public_reports_api(request):
    return get_public_reports()


@router.get("/account/{account_id}/lists/all", response={200: list[PubliclySharedListResponseSchema]})
def get_publicly_shared_lists_per_account_api(request, account_id: int):
    return get_publicly_shared_lists_per_account(account_id)


@router.get("/account/{account_id}/lists/{urllist_id}", response={200: list[PubliclySharedListResponseSchema]})
def get_publicly_shared_lists_per_account_and_list_id_api(request, account_id: int, urllist_id: int):
    return get_publicly_shared_lists_per_account_and_list_id(account_id, urllist_id)


@router.get("/lists/{urllist_id}/latest", response={200: LatestReportCodeSchema})
def get_latest_report_id_from_list_api(request, urllist_id: int):
    return get_latest_report_id_from_list_and_type(urllist_id, "")


@router.get("/lists/{urllist_id}/latest/{report_type}", response={200: LatestReportCodeSchema})
def get_latest_report_id_from_list_and_type_api(request, urllist_id: int, report_type: str):
    return get_latest_report_id_from_list_and_type(urllist_id, report_type)
