# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.views.decorators.http import require_http_methods
from ninja import Router
from websecmap.organizations.models import Url
from websecmap.scanners_internetnl_dns_endpoints.tasks import has_a_or_aaaa, has_soa

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema
from dashboard.internet_nl_dashboard.logic.domains import (
    CreateListResponseSchema,
    CreateUrlListInputSchema,
    DeleteUrlListInputSchema,
    UrlListContentResponseSchema,
    UrlListScanStatusResponseSchema,
    UrlListsResponseSchema,
    add_domains_from_raw_user_data,
    alter_url_in_urllist,
    cancel_scan,
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
from dashboard.internet_nl_dashboard.views import LOGIN_URL, get_account, get_json_body, json_response

router = Router(tags=["urllists"])


@login_required(login_url=LOGIN_URL)
def suggest_subdomains_(request) -> JsonResponse:
    domain = request.GET.get("domain", "")
    period = request.GET.get("period", 370)
    account = get_account(request)
    urllist_id = request.GET.get("urllist_id", None)

    suggestions = suggest_subdomains(domain, period)
    # already add the domain, so the frontend doesn't have to.
    if suggestions:
        suggestions = [domain] + [f"{sug}.{domain}" for sug in suggestions]

    # remove domains already in this list, this is very fast and even with a list of 10k domains a user won't notice it.
    if account and urllist_id:
        existing_urls = (
            Url.objects.all()
            .filter(urls_in_dashboard_list_2__account=account, urls_in_dashboard_list_2__id=urllist_id)
            .values_list("url", flat=True)
        )
        suggestions = sorted(list(set(suggestions) - set(existing_urls)))

    # if the domain is still suggested, add it in FRONT of the list:
    if domain in suggestions:
        suggestions.remove(domain)
        suggestions.insert(0, domain)

    # perform some AAAA/MX record lookups, so a user can select some things.
    # but take into account that too many lookups take time and thus over 20 will result in an "unknown"
    # perhaps this should be scanned from ctlssa?
    # this will increase loading time a lot, but creates better suggestions for smaller domains.
    # perhaps using a different dns server or lower timeouts will help performance.
    domains_with_dns_status = []
    if len(suggestions) < 30:
        for domain in suggestions:
            has_website = has_a_or_aaaa(domain)
            has_email = has_soa(domain)
            domains_with_dns_status.append(
                {
                    "domain": domain,
                    "has_website": has_website,
                    "has_email": has_email,
                }
            )
    else:
        domains_with_dns_status.extend(
            {
                "domain": domain,
                "has_website": "unknown",
                "has_email": "unknown",
            }
            for domain in suggestions
        )

    try:
        result = json_response(domains_with_dns_status)
    except ValueError:
        result = HttpResponseBadRequest("Invalid input")
    except Exception:  # pylint: disable=broad-exception-caught
        result = HttpResponseServerError("Error occured while getting subdomain suggestions")

    return result


@router.get("/get", response={200: UrlListsResponseSchema})
@login_required(login_url=LOGIN_URL)
def get_lists(request):
    return get_urllists_from_account(account=get_account(request))


@router.post("/create", response={200: CreateListResponseSchema})
@login_required(login_url=LOGIN_URL)
def create_list_api(request, data: CreateUrlListInputSchema):
    return create_list(get_account(request), data)


@router.get("/get_content/{urllist_id}", response={200: UrlListContentResponseSchema})
@login_required(login_url=LOGIN_URL)
def get_urllist_content_(request, urllist_id: int):
    return get_urllist_content(account=get_account(request), urllist_id=urllist_id)


@router.get("/scan_status/{urllist_id}", response={200: UrlListScanStatusResponseSchema})
@login_required(login_url=LOGIN_URL)
def get_scan_status_of_list_(request, urllist_id: int):
    return get_scan_status_of_list(account=get_account(request), list_id=urllist_id)


# unused
# @login_required(login_url=LOGIN_URL)
# def save_list_content(request, urllist_name: str, urls: List[str]) -> HttpResponse:
#     return json_response(save_urllist_content_by_name(get_account(request), urllist_name, urls))


@login_required(login_url=LOGIN_URL)
def update_list_settings_(request):
    return json_response(update_list_settings(get_account(request), get_json_body(request)))


# @login_required(login_url=LOGIN_URL)
# def create_list_(request):
#     body = get_json_body(request)
#     data = CreateUrlListInputSchema(**body) if isinstance(body, dict) else CreateUrlListInputSchema(**{})
#     result = create_list(get_account(request), data)
#     return json_response(result.dict())


@router.post("/delete", response={200: OperationResponseSchema})
@login_required(login_url=LOGIN_URL)
def delete_list_api(request, data: DeleteUrlListInputSchema):
    return delete_list(get_account(request), data)


# @login_required(login_url=LOGIN_URL)
# def delete_list_(request):
#     result = delete_list(get_account(request), DeleteUrlListInputSchema(id=get_json_body(request).get("id", -1)))
#     return json_response(result.dict())


@login_required(login_url=LOGIN_URL)
def alter_url_in_urllist_(request):
    return json_response(alter_url_in_urllist(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def add_urls_to_urllist(request):
    return json_response(add_domains_from_raw_user_data(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def delete_url_from_urllist_(request):
    account = get_account(request)
    request = get_json_body(request)
    item_deleted = delete_url_from_urllist(account, request.get("urllist_id", None), request.get("url_id", None))
    return json_response({"items_deleted": None, "success": item_deleted})


@login_required(login_url=LOGIN_URL)
def scan_now_(request):
    return json_response(scan_now(get_account(request), get_json_body(request)))


@login_required(login_url=LOGIN_URL)
def cancel_scan_(request):
    account = get_account(request)
    request = get_json_body(request)
    response = cancel_scan(account, request.get("id"))
    return json_response(response)


@login_required(login_url=LOGIN_URL)
@require_http_methods(["POST"])
def download_list_(request):
    params = get_json_body(request)
    return download_as_spreadsheet(get_account(request), params.get("list-id", None), params.get("file-type", None))
