# SPDX-License-Identifier: Apache-2.0
"""
Purposes of this file / pattern:
- Factor out "request" and the derived "account" from the views, as working with requests is janky/ugly in tests.
- Order the operations on url lists in the documentation and move operations around without moving large chunks of code.

Url Lists: lists with urls that should be tested for standard compliance. It can contain domains and subdomains.
"""

import logging
from typing import Annotated

from ninja import File, Query, Router, Schema, Status
from ninja.files import UploadedFile
from ninja.security import django_auth
from pydantic import StringConstraints

from dashboard.internet_nl_dashboard.logic.domains import (
    AlterUrlResponseSchema,
    CreateListResponseSchema,
    CreateUrlListInputSchema,
    SuggestedDomainSchema,
    SuggestedSubdomainsInputSchema,
    UpdateListSettingsInputSchema,
    UrlListContentResponseSchema,
    UrlListScanStatusResponseSchema,
    UrlListsResponseSchema,
    alter_url_in_urllist,
    create_list,
    delete_list,
    delete_url_from_urllist,
    download_as_spreadsheet,
    get_scan_status_of_list,
    get_urllist_content,
    get_urllists_from_account,
    scan_now,
    suggest_subdomains_for_list,
    update_list_settings,
)
from dashboard.internet_nl_dashboard.logic.report import UrlListTimelineSeriesSchema, get_urllist_timeline_graph
from dashboard.internet_nl_dashboard.logic.domain_batches import (
    BatchConfirmSchema,
    BatchInputSchema,
    BatchItemSchema,
    BatchSchema,
    CorrectionsSchema,
    batch_summary,
    cancel_batch,
    confirm_batch,
    correct_batch,
    owned_batch,
    retry_batch,
    start_batch,
)
from dashboard.internet_nl_dashboard.logic.spreadsheets import (
    UploadHistoryItemSchema,
    start_spreadsheet_upload,
    upload_history_for_account,
)
from dashboard.internet_nl_dashboard.logic.tags import add_tag, remove_tag, tags_in_urllist
from dashboard.internet_nl_dashboard.models import TAG_MAX_LENGTH, DomainBatch, UrlList
from dashboard.internet_nl_dashboard.problems import ApiError, ProblemSchema, ProblemType, problem_responses
from dashboard.internet_nl_dashboard.scanners.subdomains import scan_status
from dashboard.internet_nl_dashboard.views import get_account, get_dashboarduser

log = logging.getLogger(__package__)


class TagInputSchema(Schema):
    tag: Annotated[str, StringConstraints(max_length=TAG_MAX_LENGTH)]


class AddTagsInputSchema(TagInputSchema):
    url_ids: list[int]


class UpdateUrlInputSchema(Schema):
    new_url_string: Annotated[str, StringConstraints(max_length=255)]


# django_auth replaces @login_required on every call
router = Router(tags=["Url Lists"], auth=django_auth)


@router.get("", response={200: UrlListsResponseSchema})
def get_lists_operation(request):
    return get_urllists_from_account(account=get_account(request))


@router.post("", response={201: CreateListResponseSchema})
def create_list_operation(request, data: CreateUrlListInputSchema):
    return create_list(get_account(request), data)


@router.get("/import-spreadsheets", response={200: list[UploadHistoryItemSchema]})
def upload_history(request):
    account = get_account(request)
    return upload_history_for_account(account)


@router.post(
    "/import-spreadsheets",
    response={202: BatchSchema},
    openapi_extra=problem_responses(start_spreadsheet_upload),
)
def upload_spreadsheet(request, file: UploadedFile = File(...)) -> Status[dict]:
    user = get_dashboarduser(request)
    return Status(202, start_spreadsheet_upload(user, file))


@router.get("/domain-batches", response={200: list[BatchSchema]})
def domain_batches_operation(
    request,
    urllist_id: int | None = Query(None, alias="urllistId"),
    pending_only: bool = Query(False, alias="pendingOnly"),
):
    batches = DomainBatch.objects.filter(account=get_account(request)).select_related("account", "urllist")
    if urllist_id is not None:
        batches = batches.filter(urllist__id=urllist_id)
    if pending_only:
        batches = batches.exclude(status__in=("completed", "cancelled"))
    return [batch_summary(batch) for batch in batches.order_by("-id")[:30]]


@router.get("/domain-batches/{batch_id}", response={200: BatchSchema, 404: ProblemSchema})
def domain_batch_operation(request, batch_id: int):
    return batch_summary(owned_batch(get_account(request), batch_id))


@router.delete(
    "/domain-batches/{batch_id}",
    response={204: None, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra={
        "responses": {
            404: {"description": "The domain batch does not exist in the current account."},
            409: {"description": "Completed domain batches cannot be cancelled."},
        }
    },
)
def domain_batch_cancel_operation(request, batch_id: int):
    cancel_batch(get_account(request), batch_id)
    return Status(204, None)


@router.get("/domain-batches/{batch_id}/rejections", response={200: list[BatchItemSchema], 404: ProblemSchema})
def domain_batch_rejections_operation(request, batch_id: int):
    batch = owned_batch(get_account(request), batch_id)
    return batch.items.filter(status__in=("invalid", "unresolvable", "limit")).order_by("position")


@router.post(
    "/domain-batches/{batch_id}/confirm",
    response={202: BatchSchema, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def domain_batch_confirm_operation(request, batch_id: int, data: BatchConfirmSchema | None = None):
    options = data or BatchConfirmSchema()
    return Status(202, confirm_batch(get_account(request), batch_id, options.overwrite, options.confirmation))


@router.post(
    "/domain-batches/{batch_id}/corrections",
    response={202: BatchSchema, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def domain_batch_correct_operation(request, batch_id: int, data: CorrectionsSchema):
    return Status(202, correct_batch(get_account(request), batch_id, data.corrections))


@router.post(
    "/domain-batches/{batch_id}/retry",
    response={202: BatchSchema, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def domain_batch_retry_operation(request, batch_id: int):
    return Status(202, retry_batch(get_account(request), batch_id))


@router.delete(
    "/{urllist_id}",
    response={204: None, 404: ProblemSchema},
    openapi_extra={
        "responses": {
            404: {"description": "The list does not exist in the current account or has already been deleted."}
        }
    },
)
def delete_list_operation(request, urllist_id: int):
    return Status(204, delete_list(get_account(request), urllist_id))


@router.put(
    "/{urllist_id}",
    response={200: CreateListResponseSchema, 404: ProblemSchema},
    openapi_extra={
        "responses": {404: {"description": "The list does not exist in the current account or has been deleted."}}
    },
)
def update_list_settings_operation(request, urllist_id: int, data: UpdateListSettingsInputSchema):
    # enforce path id to avoid body tampering
    data.id = urllist_id
    return update_list_settings(get_account(request), data)


@router.get("/{urllist_id}/scans", response={200: UrlListScanStatusResponseSchema})
def get_scan_status_of_list_operation(request, urllist_id: int):
    return get_scan_status_of_list(account=get_account(request), list_id=urllist_id)


@router.post(
    "/{urllist_id}/scans",
    response={202: None, 400: ProblemSchema, 404: ProblemSchema, 409: ProblemSchema},
    openapi_extra={
        "responses": {
            400: {
                "description": (
                    "Invalid list ID, the list exceeds the domain limit, or the configured "
                    "Internet.nl API credentials are invalid."
                )
            },
            404: {"description": "The list does not exist in the current account or has been deleted."},
            409: {"description": "The list does not currently meet the conditions for starting a scan."},
        }
    },
)
def create_scan_operation(request, urllist_id: int) -> Status[None]:
    return Status(202, scan_now(get_account(request), urllist_id))


@router.get(
    "/{urllist_id}/url-suggestions",
    response={200: list[SuggestedDomainSchema]},
    openapi_extra=problem_responses(suggest_subdomains_for_list),
)
def suggest_subdomains_operation(request, urllist_id: int, data: Query[SuggestedSubdomainsInputSchema]):
    return suggest_subdomains_for_list(get_account(request), urllist_id, data.domain, data.period)


@router.post(
    "/{urllist_id}/www-subdomain-discovery",
    response={202: BatchSchema, 404: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def request_subdomain_discovery_scan_api(request, urllist_id: int):
    urllist = UrlList.objects.filter(account=get_account(request), id=urllist_id, is_deleted=False).first()
    if not urllist:
        raise ApiError(404, "List does not exist.", ProblemType.LIST_NOT_FOUND)
    domains = "\n".join(
        f"www.{domain}"
        for domain in urllist.urls.filter(computed_subdomain="").values_list("url", flat=True).iterator()
    )
    if not domains:
        raise ApiError(400, "There are no top-level domains to discover in this list.")
    return Status(202, start_batch(get_dashboarduser(request), urllist_id=urllist_id, raw_urls=domains))


@router.get(
    "/{urllist_id}/www-subdomain-discovery",
    response={200: dict, 404: ProblemSchema},
    openapi_extra={
        "responses": {
            404: {
                "description": (
                    "The list does not exist in the current account, has been deleted, or has no discovery scan yet."
                )
            }
        }
    },
)
def subdomain_discovery_scan_status_api(request, urllist_id: int):
    return scan_status(get_account(request), urllist_id)


@router.post("/{urllist_id}/spreadsheets/{file_type}", response={200: UploadedFile})
def download_list_operation(request, urllist_id: int, file_type: str):
    # django ninja does not support file downloads in the schema, which is odd
    return download_as_spreadsheet(get_account(request), urllist_id, file_type)


@router.post(
    "/{urllist_id}/spreadsheets",
    response={202: BatchSchema, 404: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def upload_list_operation(request, urllist_id: int, file: UploadedFile = File(...)):
    return Status(202, start_batch(get_dashboarduser(request), urllist_id=urllist_id, file=file))


@router.get("/{urllist_id}/tags", response={200: list[str]})
def tags_in_urllist_operation(request, urllist_id: int):
    return tags_in_urllist(account=get_account(request), urllist_id=urllist_id)


@router.get("/{urllist_id}/urls", response={200: UrlListContentResponseSchema})
def get_urllist_content_operation(request, urllist_id: int):
    return get_urllist_content(account=get_account(request), urllist_id=urllist_id)


@router.post(
    "/{urllist_id}/urls",
    response={202: BatchSchema, 404: ProblemSchema},
    openapi_extra=problem_responses(start_batch, descriptions={404: "The list does not exist in the current account."}),
)
def add_urls_to_urllist_operation(request, urllist_id: int, data: BatchInputSchema):
    return Status(202, start_batch(get_dashboarduser(request), urllist_id=urllist_id, raw_urls=data.raw_urls))


@router.post("/{urllist_id}/urls/tags", response={204: None})
def add_tags_operation(request, urllist_id: int, data: AddTagsInputSchema):
    add_tag(
        account=get_account(request),
        urllist_id=urllist_id,
        url_ids=data.url_ids,
        tag=data.tag,
    )
    return None


@router.put(
    "/{urllist_id}/urls/{url_id}",
    response={200: AlterUrlResponseSchema, 400: ProblemSchema, 404: ProblemSchema},
    openapi_extra={
        "responses": {
            400: {"description": "Invalid request data or the new URL has an invalid format."},
            404: {
                "description": (
                    "The list does not exist in the current account, has been deleted, or does not contain the URL."
                )
            },
        }
    },
)
def alter_url_in_urllist_operation(request, urllist_id: int, url_id: int, data: UpdateUrlInputSchema):
    return alter_url_in_urllist(get_account(request), urllist_id, url_id, data.new_url_string)


@router.post("/{urllist_id}/urls/{url_id}/tags", response={204: None})
def add_tag_operation(request, urllist_id: int, url_id: int, data: TagInputSchema):
    add_tag(
        account=get_account(request),
        urllist_id=urllist_id,
        url_ids=[url_id],
        tag=data.tag,
    )
    return None


@router.delete("/{urllist_id}/urls/{url_id}/tags/{tag}", response={204: None})
def remove_tag_operation(request, urllist_id: int, url_id: int, tag: str):
    remove_tag(
        account=get_account(request),
        urllist_id=urllist_id,
        url_ids=[url_id],
        tag=tag,
    )
    return None


@router.delete(
    "/{urllist_id}/urls/{url_id}",
    response={204: None, 404: ProblemSchema},
    openapi_extra={
        "responses": {
            404: {"description": "The URL does not exist in the requested list belonging to the current account."}
        }
    },
)
def delete_url_from_urllist_operation(request, urllist_id: int, url_id: int):
    account = get_account(request)
    item_deleted = delete_url_from_urllist(account, urllist_id, url_id)
    if not item_deleted:
        raise ApiError(404, "URL not found in this list.")
    return Status(204, None)


@router.get(
    "/{urllist_ids_csv}/timeline-graph/{report_type}",
    response={200: list[UrlListTimelineSeriesSchema]},
)
def get_urllist_timeline_graph_operation(request, urllist_ids_csv: str, report_type: str):
    return get_urllist_timeline_graph(get_account(request), urllist_ids_csv, report_type)
