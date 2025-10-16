# SPDX-License-Identifier: Apache-2.0
from ninja import Query, Router
from ninja.security import django_auth
from websecmap.organizations.models import Url
from websecmap.scanners_internet_nl_dns_endpoints.tasks import get_nameservers, has_a_or_aaaa, has_soa

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.logic.domains import (
    AlterUrlResponseSchema,
    CreateListResponseSchema,
    CreateUrlListInputSchema,
    DeleteUrlFromListInputSchema,
    DeleteUrlListInputSchema,
    DownloadSpreadsheetInputSchema,
    SuggestedDomainSchema,
    SuggestedSubdomainsInputSchema,
    UrlListContentResponseSchema,
    UrlListScanStatusResponseSchema,
    UrlListsResponseSchema,
    add_domains_from_raw_user_data,
    alter_url_in_urllist,
    create_list,
    delete_list,
    delete_url_from_urllist,
    download_as_spreadsheet,
    get_scan_status_of_list,
    get_urllist_content,
    get_urllists_from_account,
    scan_now,
    update_list_settings,
)
from dashboard.internet_nl_dashboard.logic.suggestions import suggest_subdomains
from dashboard.internet_nl_dashboard.views import get_account, get_json_body
from dashboard.internet_nl_dashboard.views import subdomains as subdomains_views
from dashboard.internet_nl_dashboard.views import tags as tags_views

# django_auth replaces @login_required on every call
router = Router(tags=["Url Lists"], auth=django_auth)
# Mount tag operations under the urllist router, so paths become /data/urllist/tag/...
router.add_router("/tag", tags_views.router)
# Mount subdomain discovery operations under the urllist router, so paths become /data/urllist/discover-subdomains/...
router.add_router("/discover-subdomains", subdomains_views.router)


@router.get("/suggest-subdomains", response={200: list[SuggestedDomainSchema]})
def suggest_subdomains_api(request, data: Query[SuggestedSubdomainsInputSchema]):
    account = get_account(request)

    suggestions = suggest_subdomains(data.domain, data.period)
    # already add the domain, so the frontend doesn't have to.
    if suggestions:
        suggestions = [data.domain] + [f"{sug}.{data.domain}" for sug in suggestions]

    # remove domains already in this list, this is very fast and even with a list of 10k domains a user won't notice it.
    if account and data.urllist_id:
        existing_urls = (
            Url.objects.all()
            .filter(urls_in_dashboard_list_2__account=account, urls_in_dashboard_list_2__id=data.urllist_id)
            .values_list("url", flat=True)
        )
        suggestions = sorted(list(set(suggestions) - set(existing_urls)))

    # if the domain is still suggested, add it in FRONT of the list:
    if data.domain in suggestions:
        suggestions.remove(data.domain)
        suggestions.insert(0, data.domain)

    # perform some AAAA/MX record lookups, so a user can select some things.
    # but take into account that too many lookups take time and thus over 20 will result in an "unknown"
    # perhaps this should be scanned from ctlssa?
    # this will increase loading time a lot, but creates better suggestions for smaller domains.
    # perhaps using a different dns server or lower timeouts will help performance.
    domains_with_dns_status: list[dict] = []
    nameservers = get_nameservers()
    if len(suggestions) < 30:
        for d in suggestions:
            has_website = has_a_or_aaaa(d, nameservers)
            has_email = has_soa(d, nameservers)
            domains_with_dns_status.append(
                {
                    "domain": d,
                    "has_website": has_website,
                    "has_email": has_email,
                }
            )
    else:
        domains_with_dns_status.extend(
            {
                "domain": d,
                "has_website": "unknown",
                "has_email": "unknown",
            }
            for d in suggestions
        )

    return domains_with_dns_status


@router.get("/get", response={200: UrlListsResponseSchema})
def get_lists(request):
    return get_urllists_from_account(account=get_account(request))


@router.post("/create", response={200: CreateListResponseSchema})
def create_list_api(request, data: CreateUrlListInputSchema):
    return create_list(get_account(request), data)


@router.get("/get_content/{urllist_id}", response={200: UrlListContentResponseSchema})
def get_urllist_content_(request, urllist_id: int):
    return get_urllist_content(account=get_account(request), urllist_id=urllist_id)


@router.get("/scan_status/{urllist_id}", response={200: UrlListScanStatusResponseSchema})
def get_scan_status_of_list_(request, urllist_id: int):
    return get_scan_status_of_list(account=get_account(request), list_id=urllist_id)


# unused
# @login_required(login_url=LOGIN_URL)
# def save_list_content(request, urllist_name: str, urls: List[str]) -> HttpResponse:
#     return json_response(save_urllist_content_by_name(get_account(request), urllist_name, urls))


@router.post("/update_list_settings", response={200: CreateListResponseSchema | OperationResponseSchema})
def update_list_settings_(request):
    return update_list_settings(get_account(request), get_json_body(request))


# def create_list_(request):
#     body = get_json_body(request)
#     data = CreateUrlListInputSchema(**body) if isinstance(body, dict) else CreateUrlListInputSchema(**{})
#     result = create_list(get_account(request), data)
#     return json_response(result.dict())


@router.post("/delete", response={200: OperationResponseSchema})
def delete_list_api(request, data: DeleteUrlListInputSchema):
    return delete_list(get_account(request), data)


# def delete_list_(request):
#     result = delete_list(get_account(request), DeleteUrlListInputSchema(id=get_json_body(request).get("id", -1)))
#     return json_response(result.dict())


@router.post("/url/update", response={200: AlterUrlResponseSchema})
def alter_url_in_urllist_(request):
    return alter_url_in_urllist(get_account(request), get_json_body(request))


@router.post("/url/add", response={200: OperationResponseSchema})
def add_urls_to_urllist(request):
    # todo: the response data is not well defined, so you'll be missing statistics... define this in the Schema...
    #  or doesn't this contain statistics?
    return add_domains_from_raw_user_data(get_account(request), get_json_body(request))


@router.delete("/url/delete", response={200: OperationResponseSchema})
def delete_url_from_urllist_(request, data: DeleteUrlFromListInputSchema):
    account = get_account(request)
    item_deleted = delete_url_from_urllist(account, data.urllist_id, data.url_id)
    return operation_response(success=bool(item_deleted), message="url_deleted" if item_deleted else "url_not_deleted")


@router.post("/scan-now", response={200: OperationResponseSchema})
def scan_now_(request) -> OperationResponseSchema:
    return scan_now(get_account(request), get_json_body(request))


# todo: django ninja does not support file downloads in the schema, which is odd
@router.post("/download")
def download_list_api(request, data: DownloadSpreadsheetInputSchema):
    return download_as_spreadsheet(get_account(request), data.urllist_id, data.file_type)
