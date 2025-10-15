# SPDX-License-Identifier: Apache-2.0
# pylint: disable=too-many-lines
import logging
import sys
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple, Union

import pyexcel as p
import requests
from actstream import action
from celery import group
from constance import config
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from ninja import Schema
from websecmap import tldextract
from websecmap.app.constance import constance_cached_value
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint
from websecmap.scanners_internetnl_dns_endpoints.tasks import compose_discover_task

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.models import (
    Account,
    AccountInternetNLScan,
    TaggedUrlInUrllist,
    UploadLog,
    UrlList,
    UrlListReport,
    determine_next_scan_moment,
)
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import initialize_scan
from dashboard.internet_nl_dashboard.views import create_spreadsheet_download


class UrlListSummarySchema(Schema):
    id: int
    name: str
    enable_scans: bool
    scan_type: str
    automated_scan_frequency: str
    scheduled_next_scan: datetime | None = None
    scan_now_available: bool
    enable_report_sharing_page: bool
    automatically_share_new_reports: bool
    default_public_share_code_for_new_reports: str = ""
    last_scan_id: int | None = None
    last_scan_state: str | None = None
    # Note: get_urllists_from_account returns ISO formatted strings for dates
    last_scan: str | None = None
    last_scan_finished: bool | None = None
    last_report_id: int | None = None
    last_report_date: str | None = None
    list_warnings: list[str] = []
    num_urls: int


class UrlListsResponseSchema(Schema):
    lists: list[UrlListSummarySchema]
    maximum_domains_per_list: int


class UrlItemSchema(Schema):
    id: int
    url: str
    subdomain: str
    domain: str
    suffix: str
    created_on: datetime
    resolves: bool
    has_mail_endpoint: bool
    has_web_endpoint: bool
    tags: list[str]


class UrlListContentResponseSchema(Schema):
    urllist_id: int
    urls: list[UrlItemSchema]


class UrlListScanStatusResponseSchema(Schema):
    last_scan_id: int | None = None
    last_scan_state: str | None = None
    last_scan_finished: bool | None = None
    last_report_id: int | None = None
    last_report_date: datetime | None = None
    scan_now_available: bool = False


# Specialized schemas for alter_url_in_urllist
class UrlChangeItemSchema(Schema):
    id: int
    url: str
    created_on: datetime
    has_mail_endpoint: bool | str
    has_web_endpoint: bool | str
    subdomain: str
    domain: str
    suffix: str


class AlterUrlDataSchema(Schema):
    created: UrlChangeItemSchema
    removed: UrlChangeItemSchema | None = None


class AlterUrlResponseSchema(OperationResponseSchema):
    data: AlterUrlDataSchema | None = None


class CreateListResponseSchema(OperationResponseSchema):
    data: UrlListSummarySchema | None = None


class CreateUrlListInputSchema(Schema):
    id: int
    name: str
    enable_scans: bool
    scan_type: str
    automated_scan_frequency: str
    scheduled_next_scan: datetime | None = None
    automatically_share_new_reports: bool
    default_public_share_code_for_new_reports: str = ""
    enable_report_sharing_page: bool


class DeleteUrlListInputSchema(Schema):
    id: int


class DeleteUrlFromListInputSchema(Schema):
    urllist_id: int
    url_id: int


class DownloadSpreadsheetInputSchema(Schema):
    urllist_id: int
    file_type: str = "xlsx"


class SuggestedSubdomainsInputSchema(Schema):
    domain: str = ""
    period: int = 370
    urllist_id: int | None = None


class SuggestedDomainSchema(Schema):
    domain: str
    has_website: bool | str
    has_email: bool | str


log = logging.getLogger(__package__)


class ServerError(BaseException):
    pass


def suggest_subdomains(domain: str, period: int = 370):
    extract = tldextract.extract(domain)

    # ip address or garbage
    if not extract.domain or not extract.suffix:
        raise ValueError("Invalid input")

    # call SUBDOMAIN_SUGGESTION_SERVER_ADDRESS
    try:
        response = requests.get(
            config.SUBDOMAIN_SUGGESTION_SERVER_ADDRESS,
            params={"domain": extract.domain, "suffix": extract.suffix, "period": period},
            timeout=10,
        )
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("Failed to retrieve subdomain suggestions from  %s.", config.SUBDOMAIN_SUGGESTION_SERVER_ADDRESS)
        raise

    if response.status_code == 404:
        return []

    if response.status_code != 200:
        log.error(
            "Failed to retrieve subdomain suggestions from: %s, status code: %s.",
            config.SUBDOMAIN_SUGGESTION_SERVER_ADDRESS,
            response.status_code,
        )
        raise ServerError("Failed to retrieve subdomain suggestions")

    return response.json()


# todo: write test
def alter_url_in_urllist(account, data) -> AlterUrlResponseSchema:
    # data = {'list_id': list.id, 'url_id': url.id, 'new_url_string': url.url}

    now = datetime.now(timezone.utc)

    expected_keys = ["list_id", "url_id", "new_url_string"]
    if not keys_are_present_in_object(expected_keys, data):
        return AlterUrlResponseSchema(error=True, message="Missing keys in data.", state="error", timestamp=now)

    # what was the old id we're changing?
    old_url = Url.objects.all().filter(pk=data["url_id"]).first()
    if not old_url:
        return AlterUrlResponseSchema(error=True, message="The old url does not exist.", state="error", timestamp=now)

    if old_url.url == data["new_url_string"]:
        # no changes, but return a created item for UI consistency
        created_item = UrlChangeItemSchema(
            id=old_url.id,
            url=old_url.url,
            created_on=old_url.created_on,
            has_mail_endpoint="unknown",
            has_web_endpoint="unknown",
            subdomain=old_url.computed_subdomain,
            domain=old_url.computed_domain,
            suffix=old_url.computed_suffix,
        )
        return AlterUrlResponseSchema(
            success=True,
            message="Saved.",
            state="success",
            data=AlterUrlDataSchema(created=created_item, removed=None),
            timestamp=now,
        )

    # is this really a list?
    urllist = UrlList.objects.all().filter(account=account, pk=data["list_id"]).first()
    if not urllist:
        return AlterUrlResponseSchema(error=True, message="List does not exist.", state="error", timestamp=now)

    # is the url valid?
    if not Url.is_valid_url(data["new_url_string"]):
        return AlterUrlResponseSchema(
            error=True, message="New url does not have the correct format.", state="error", timestamp=now
        )

    # fetch the url, or create it if it doesn't exist.
    new_url, created = get_url(data["new_url_string"])

    # don't throw away the url, only from the list. (don't call delete, as it will delete the record)
    urllist.urls.remove(old_url)
    # Save after deletion, in case the same url is added it will not cause a foreign key error.
    urllist.save()

    urllist.urls.add(new_url)
    urllist.save()

    # somewhat inefficient to do 4 queries, yet, good enough
    old_url_has_mail_endpoint = Endpoint.objects.all().filter(url=old_url, is_dead=False, protocol="dns_soa").exists()
    old_url_has_web_endpoint = Endpoint.objects.all().filter(url=old_url, is_dead=False, protocol="dns_a_aaa").exists()

    if not created:
        new_url_has_mail_endpoint = (
            Endpoint.objects.all().filter(url=new_url, is_dead=False, protocol="dns_soa").exists()
        )
        new_url_has_web_endpoint = (
            Endpoint.objects.all().filter(url=new_url, is_dead=False, protocol="dns_a_aaa").exists()
        )
    else:
        new_url_has_mail_endpoint = "unknown"
        new_url_has_web_endpoint = "unknown"

    new_fragments = tldextract.extract(new_url.url)
    old_fragments = tldextract.extract(old_url.url)

    created_item = UrlChangeItemSchema(
        id=new_url.id,
        url=new_url.url,
        created_on=new_url.created_on,
        has_mail_endpoint=new_url_has_mail_endpoint,
        has_web_endpoint=new_url_has_web_endpoint,
        subdomain=new_fragments.subdomain,
        domain=new_fragments.domain,
        suffix=new_fragments.suffix,
    )

    removed_item = UrlChangeItemSchema(
        id=old_url.id,
        url=old_url.url,
        created_on=old_url.created_on,
        has_mail_endpoint=old_url_has_mail_endpoint,
        has_web_endpoint=old_url_has_web_endpoint,
        subdomain=old_fragments.subdomain,
        domain=old_fragments.domain,
        suffix=old_fragments.suffix,
    )

    return AlterUrlResponseSchema(
        success=True,
        message="Saved.",
        state="success",
        data=AlterUrlDataSchema(created=created_item, removed=removed_item),
        timestamp=now,
    )


def scan_now(account, user_input) -> OperationResponseSchema:
    urllist = (
        UrlList.objects.all()
        .filter(account=account, id=user_input.get("id", -1), is_deleted=False)
        .annotate(num_urls=Count("urls"))
        .first()
    )

    if not urllist:
        return operation_response(error=True, message="List could not be found.")

    if not urllist.is_scan_now_available():
        return operation_response(error=True, message="Not all conditions for initiating a scan are met.")

    # make sure there are no errors on this list:
    max_urls = config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST
    if urllist.num_urls > max_urls:
        return operation_response(error=True, message=f"Cannot scan: Amount of urls exceeds the maximum of {max_urls}.")

    if not account.connect_to_internet_nl_api(account.internet_nl_api_username, account.decrypt_password()):
        return operation_response(error=True, message="Credentials for the internet.nl API are not valid.")

    # Make sure the fernet key is working fine, you are on the correct queue (-Q storage) and that the correct API
    # version is used.
    # Run this before updating the list, as this might go wrong for many reasons.
    initialize_scan(urllist.id, manual_or_scheduled="manual")

    # done: have to update the list info. On the other hand: there is no guarantee that this task already has started
    # ...to fix this issue, we'll use a 'last_manual_scan' field.
    urllist.last_manual_scan = datetime.now(timezone.utc)
    urllist.save()

    return operation_response(success=True, message="Scan started")


def scan_urllist_now_ignoring_business_rules(urllist: UrlList):
    my_urllist = UrlList.objects.all().filter(pk=urllist.id).first()

    if not my_urllist:
        return operation_response(error=True, message="List could not be found.")

    initialize_scan(my_urllist.id)

    my_urllist.last_manual_scan = datetime.now(timezone.utc)
    my_urllist.save()

    return operation_response(success=True, message="Scan started")


def get_url(new_url_string: str):
    # first check if one exists, if not, create it.
    url = Url.objects.all().filter(url=new_url_string).first()
    if url:
        return url, False

    url = Url.add(new_url_string)
    return url, True


def create_list(account: Account, data: CreateUrlListInputSchema) -> CreateListResponseSchema:
    frequency = validate_list_automated_scan_frequency(data.automated_scan_frequency)
    create_kwargs = {
        "account": account,
        "name": validate_list_name(data.name),
        "enable_scans": bool(data.enable_scans),
        "scan_type": validate_list_scan_type(data.scan_type),
        "automated_scan_frequency": frequency,
        # Always determine the next scan moment from frequency; ignore user provided value
        "scheduled_next_scan": determine_next_scan_moment(frequency),
        "enable_report_sharing_page": bool(getattr(data, "enable_report_sharing_page", False)),
        "automatically_share_new_reports": bool(getattr(data, "automatically_share_new_reports", False)),
        "default_public_share_code_for_new_reports": (data.default_public_share_code_for_new_reports or "")[:64],
    }

    urllist = UrlList(**create_kwargs)
    urllist.save()

    # Build a UrlListSummarySchema for the newly created list
    list_summary = UrlListSummarySchema(
        id=urllist.pk,
        name=urllist.name,
        enable_scans=urllist.enable_scans,
        scan_type=urllist.scan_type,
        automated_scan_frequency=urllist.automated_scan_frequency,
        scheduled_next_scan=urllist.scheduled_next_scan,
        scan_now_available=urllist.is_scan_now_available(),
        enable_report_sharing_page=urllist.enable_report_sharing_page,
        automatically_share_new_reports=urllist.automatically_share_new_reports,
        default_public_share_code_for_new_reports=urllist.default_public_share_code_for_new_reports,
        last_scan_id=None,
        last_scan_state=None,
        last_scan=None,
        last_scan_finished=None,
        last_report_id=None,
        last_report_date=None,
        list_warnings=[],
        num_urls=0,
    )

    # Sprinkling an activity stream action.
    action.send(account, verb="created list", target=urllist, public=False)

    # todo: abstract state and timestamp, just like in the old operation_response code.
    #  or... use rest status codes, like 200 and 400.
    return CreateListResponseSchema(
        success=True,
        error=False,
        message="List created.",
        state="success",
        data=list_summary,
        timestamp=datetime.now(timezone.utc),
    )


def delete_list(account: Account, data: DeleteUrlListInputSchema) -> OperationResponseSchema:
    """
    The first assumption was that a list is not precious or special, and that it can be quickly re-created with an
    import from excel or a csv paste in the web interface. Yet this assumption is wrong. It's valuable to keep the list
    also after it is deleted. This gives insight into what scans have happened in the past on what list.

    To do that, the is_deleted columns have been introduced.

    :param account:
    :param data: DeleteUrlListInputSchema containing the list id.
    :return: OperationResponseSchema
    """
    urllist = UrlList.objects.all().filter(account=account, id=data.id, is_deleted=False).first()
    if not urllist:
        return operation_response(error=True, message="List could not be deleted.")

    urllist.is_deleted = True
    urllist.enable_scans = False
    urllist.deleted_on = datetime.now(timezone.utc)
    urllist.save()

    # Sprinkling an activity stream action.
    action.send(account, verb="deleted list", target=urllist, public=False)

    return operation_response(success=True, message="List deleted.")


def get_scan_status_of_list(account: Account, list_id: int) -> UrlListScanStatusResponseSchema:
    """
    Gets the latest report and the scanning status of a list, this is meant as a small status monitor per list.
    This updates the "can scan" buttons and updates the link to the latest report. It does not propagate user changes.

    :param account:
    :param list_id:
    :return:
    """

    prefetch_last_scan = Prefetch(
        "accountinternetnlscan_set",
        queryset=AccountInternetNLScan.objects.order_by("-id")
        .select_related("scan")
        .only("scan_id", "id", "finished_on", "state", "urllist__id", "urllist"),
        to_attr="last_scan",
    )

    last_report_prefetch = Prefetch(
        "urllistreport_set",
        # filter(pk=UrlListReport.objects.latest('id').pk).
        queryset=UrlListReport.objects.order_by("-id").only("id", "at_when", "urllist__id", "urllist"),
        to_attr="last_report",
    )

    urllist = (
        UrlList.objects.all()
        .filter(account=account, id=list_id, is_deleted=False)
        .prefetch_related(prefetch_last_scan, last_report_prefetch)
        .first()
    )

    if not urllist:
        # Return an empty schema with defaults when the list is not found for this account
        return UrlListScanStatusResponseSchema()

    data = {
        "last_scan_id": None,
        "last_scan_state": None,
        "last_scan_finished": None,
        "last_report_id": None,
        "last_report_date": None,
        "scan_now_available": urllist.is_scan_now_available(),
    }

    if len(urllist.last_scan):  # type: ignore
        # Mypy does not understand to_attr. "UrlList" has no attribute "last_scan"
        data["last_scan_id"] = urllist.last_scan[0].scan.id  # type: ignore
        data["last_scan_state"] = urllist.last_scan[0].state  # type: ignore
        data["last_scan_finished"] = urllist.last_scan[0].state in ["finished", "cancelled"]  # type: ignore

    if len(urllist.last_report):  # type: ignore
        data["last_report_id"] = urllist.last_report[0].id  # type: ignore
        data["last_report_date"] = urllist.last_report[0].at_when  # type: ignore

    return UrlListScanStatusResponseSchema(**data)


# @pysnooper.snoop()
def update_list_settings(account: Account, user_input: Dict) -> CreateListResponseSchema | OperationResponseSchema:
    """

    This cannot update the urls, as that would increase complexity too much.

    :param account:
    :param user_input: {
        'id': int,
        'name': str,
        'enable_scans': bool,
        'scan_type': str,

        # todo: Who should set this? Should this be set by admins? How can we avoid permission hell?
        # Probably as long as the settings are not too detailed / too frequently.
        'automated_scan_frequency': str,
    }
    :return:
    """

    expected_keys = ["id", "name", "enable_scans", "scan_type", "automated_scan_frequency", "scheduled_next_scan"]
    if not keys_are_present_in_object(expected_keys, user_input):
        return operation_response(error=True, message="Missing settings.")

    prefetch_last_scan = Prefetch(
        "accountinternetnlscan_set",
        queryset=AccountInternetNLScan.objects.order_by("-id").select_related("scan"),
        to_attr="last_scan",
    )

    last_report_prefetch = Prefetch(
        "urllistreport_set",
        # filter(pk=UrlListReport.objects.latest('id').pk).
        queryset=UrlListReport.objects.order_by("-id").only("id", "at_when", "urllist__id"),
        to_attr="last_report",
    )

    urllist: UrlList = (
        UrlList.objects.all()
        .filter(account=account, id=user_input["id"], is_deleted=False)
        .annotate(num_urls=Count("urls"))
        .prefetch_related(prefetch_last_scan, last_report_prefetch)
        .first()
    )

    if not urllist:
        return operation_response(error=True, message="No list of urls found.")

    # Yes, you can try and set any value. Values that are not recognized do not result in errors / error messages,
    # instead they will be overwritten with the default. This means less interaction with users / less annoyance over
    # errors on such simple forms.
    frequency = validate_list_automated_scan_frequency(user_input["automated_scan_frequency"])
    data = {
        "id": urllist.id,
        "account": account,
        "name": validate_list_name(user_input["name"]),
        "enable_scans": bool(user_input["enable_scans"]),
        "scan_type": validate_list_scan_type(user_input["scan_type"]),
        "automated_scan_frequency": frequency,
        "scheduled_next_scan": determine_next_scan_moment(frequency),
        "enable_report_sharing_page": bool(user_input.get("enable_report_sharing_page", "")),
        "automatically_share_new_reports": bool(user_input.get("automatically_share_new_reports", "")),
        "default_public_share_code_for_new_reports": user_input.get("default_public_share_code_for_new_reports", "")[
            :64
        ],
    }

    updated_urllist = UrlList(**data)
    updated_urllist.save()

    # make sure the account is serializable, inject other data.
    data["account"] = account.id
    data["num_urls"] = urllist.num_urls
    data["last_scan_id"] = None
    data["last_scan_state"] = None
    data["last_scan"] = None
    data["last_scan_finished"] = None
    data["last_report_id"] = None
    data["last_report_date"] = None

    if urllist.last_scan:
        data["last_scan_id"] = urllist.last_scan[0].scan.id
        data["last_scan_state"] = urllist.last_scan[0].state
        data["last_scan"] = urllist.last_scan[0].started_on.isoformat()
        data["last_scan_finished"] = urllist.last_scan[0].state in ["finished", "cancelled"]

    if urllist.last_report:
        data["last_report_id"] = urllist.last_report[0].id
        data["last_report_date"] = urllist.last_report[0].at_when

    data["scan_now_available"] = updated_urllist.is_scan_now_available()

    # list warnings (might do: make more generic, only if another list warning ever could occur.)
    list_warnings = []
    if urllist.num_urls > config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST:
        list_warnings.append("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED")
    data["list_warnings"] = []

    # Sprinkling an activity stream action.
    action.send(account, verb="updated list", target=updated_urllist, public=False)

    return operation_response(success=True, message="Updated list settings", data=data)


def keys_are_present_in_object(expected_keys: List[str], any_object: Dict[str, Any]):
    # It's okay if more keys are present
    keys_in_object = any_object.keys()
    for key in expected_keys:
        if key not in keys_in_object:
            return False
    return True


def validate_list_name(list_name):
    return list_name[:120]


# todo: this can be a generic tuple check.
def validate_list_automated_scan_frequency(automated_scan_frequency):
    if (automated_scan_frequency, automated_scan_frequency) not in UrlList._meta.get_field(
        "automated_scan_frequency"
    ).choices:
        return UrlList._meta.get_field("automated_scan_frequency").default
    return automated_scan_frequency


def validate_list_scan_type(scan_type):
    # if the option doesn't exist, return the first option as the fallback / default.
    if (scan_type, scan_type) not in UrlList._meta.get_field("scan_type").choices:
        return UrlList._meta.get_field("scan_type").default
    return scan_type


def rename_list(account: Account, list_id: int, new_name: str) -> bool:
    # Existing list name: no problem.
    # List name too long? No problem, we'll truncate it.

    new_name = new_name[0:120]

    urllist = UrlList.objects.all().filter(account=account, id=list_id, is_deleted=False).first()
    if not urllist:
        return False

    urllist.name = new_name
    urllist.save()

    return True


def get_urllists_from_account(account: Account) -> UrlListsResponseSchema:
    """
    These are lists with some metadata. The metadata is used to give an indication how many urls etc (#52) are
    included. Note that this does not return the entire set of urls, given that URLS may be in the thousands.
    A few times a thousand urls will load slowly, which is detrimental to the user experience.

    Usually last_scan and last_report could be fetched with a prefetch, but slicing on prefetching is not possible,
    so the entire set of scans and reports is selected which is much slower than having a nested query per result.

    Prefetching could be limited with filters, but there is no filter that really limits the results down to a
    few results. For example: only prefetch the reports from the last year etc will result in a no data at one point.

    :param account:
    :return:
    """

    # Could that num_urls slows things down. Given that num_urls is overwritten when loading list data...
    urllists = (
        UrlList.objects.all()
        .filter(account=account, is_deleted=False)
        .annotate(num_urls=Count("urls"))
        .order_by("name")
        .only(
            "id",
            "name",
            "enable_scans",
            "scan_type",
            "automated_scan_frequency",
            "scheduled_next_scan",
            "enable_report_sharing_page",
            "default_public_share_code_for_new_reports",
            "automatically_share_new_reports",
        )
    )

    url_lists = []
    max_domains = config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST

    # Not needed to check the contest of the list. If it's empty, then there is just an empty list returned.
    for urllist in urllists:

        data = {
            "id": urllist.id,
            "name": urllist.name,
            "enable_scans": urllist.enable_scans,
            "scan_type": urllist.scan_type,
            "automated_scan_frequency": urllist.automated_scan_frequency,
            "scheduled_next_scan": urllist.scheduled_next_scan,
            "scan_now_available": urllist.is_scan_now_available(),
            "enable_report_sharing_page": urllist.enable_report_sharing_page,
            "automatically_share_new_reports": urllist.automatically_share_new_reports,
            "default_public_share_code_for_new_reports": urllist.default_public_share_code_for_new_reports,
            "last_scan_id": None,
            "last_scan_state": None,
            "last_scan": None,
            "last_scan_finished": None,
            "last_report_id": None,
            "last_report_date": None,
            "list_warnings": [],
            "num_urls": urllist.num_urls,
        }

        # this will create a warning if the number of domains in the list > max_domains
        # This is placed outside the loop to save a database query per time this is needed.
        if urllist.num_urls > max_domains:
            data["list_warnings"].append("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED")

        last_scan = (
            AccountInternetNLScan.objects.all()
            .filter(urllist=urllist)
            .select_related("scan")
            .only("scan__id", "state", "started_on")
            .last()
        )
        if last_scan and last_scan.scan and last_scan.started_on:
            data["last_scan_id"] = last_scan.scan.id
            data["last_scan_state"] = last_scan.state
            data["last_scan"] = last_scan.started_on.isoformat()
            data["last_scan_finished"] = last_scan.state in ["finished", "cancelled"]

        # Selecting the whole object is extremely slow as the reports are very large, therefore we use .only to limit
        # the number of fields returned. Then the prefetch is pretty fast again.
        last_report = UrlListReport.objects.all().filter(urllist=urllist).only("id", "at_when").last()
        if last_report:
            data["last_report_id"] = last_report.id
            data["last_report_date"] = last_report.at_when.isoformat()

        url_lists.append(data)

    # Sprinkling an activity stream action.
    action.send(account, verb="retrieved domain lists", public=False)

    return UrlListsResponseSchema(lists=url_lists, maximum_domains_per_list=max_domains)


def get_urllist_content(account: Account, urllist_id: int) -> UrlListContentResponseSchema:
    """
    Retrieve the contents of an urllist and return it as a Ninja schema.

    :param account: Account owning the list
    :param urllist_id: ID of the UrlList to retrieve
    :return: UrlListContentResponseSchema
    """
    # This prefetch changes a 1000 ms nested query into a 150 ms query.
    prefetch = Prefetch(
        "endpoint_set",
        queryset=Endpoint.objects.filter(protocol__in=["dns_soa", "dns_a_aaaa"], is_dead=False),
        to_attr="relevant_endpoints",
    )

    prefetch_tags = Prefetch(
        "taggedurlinurllist_set",
        queryset=TaggedUrlInUrllist.objects.all().filter(urllist=urllist_id).prefetch_related("tags"),
        to_attr="url_tags",
    )

    # This ordering makes sure all subdomains are near the domains with the right extension.
    urls = (
        Url.objects.all()
        .filter(urls_in_dashboard_list_2__account=account, urls_in_dashboard_list_2__id=urllist_id)
        .order_by("computed_domain", "computed_suffix", "computed_subdomain")
        .prefetch_related(prefetch, prefetch_tags)
        .all()
    )

    # It's very possible that the urllist_id is not matching with the account. The query will just return
    # nothing. Only if both match it will return something we can work with.
    url_items: list[UrlItemSchema] = []

    # This is just a simple iteration, all sorting and logic is placed in the vue as that is much more flexible.
    for url in urls:
        has_mail_endpoint = len([x for x in url.relevant_endpoints if x.protocol == "dns_soa"]) > 0
        has_web_endpoint = len([x for x in url.relevant_endpoints if x.protocol == "dns_a_aaaa"]) > 0

        # Prefetched tags collection building
        tags: list[str] = []
        for tag1 in [x.tags.values_list("name") for x in url.url_tags]:
            for tag2 in tag1:
                tags.extend(iter(tag2))

        url_items.append(
            UrlItemSchema(
                id=url.id,
                url=url.url,
                subdomain=url.computed_subdomain,
                domain=url.computed_domain,
                suffix=url.computed_suffix,
                created_on=url.created_on,
                resolves=not url.not_resolvable,
                has_mail_endpoint=has_mail_endpoint,
                has_web_endpoint=has_web_endpoint,
                tags=tags,
            )
        )

    return UrlListContentResponseSchema(urllist_id=urllist_id, urls=url_items)


def retrieve_possible_urls_from_unfiltered_input(unfiltered_input: str) -> Tuple[List[str], int]:
    # we do everything lowercase:
    unfiltered_input = unfiltered_input.lower()

    # Protocol is removed by tldextract
    # unfiltered_input = unfiltered_input.replace("http://", "")
    # unfiltered_input = unfiltered_input.replace("https://", "")

    # Allow CSV, newlines, tabs and space-split input
    unfiltered_input = unfiltered_input.replace(",", " ")
    unfiltered_input = unfiltered_input.replace("\n", " ")
    unfiltered_input = unfiltered_input.replace("\t", " ")

    # split email addresses from their domain
    # unfiltered_input = unfiltered_input.replace("@", " ")

    # https://github.com/internetstandards/Internet.nl-dashboard/issues/410
    # remove all invisible unicode characters and control characters such as ­
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    # Other characters will be translated to punycode when running. But saved as unicode for readability.
    unfiltered_input = "".join(ch for ch in unfiltered_input if unicodedata.category(ch)[0] != "C")

    # Split also removes double spaces etc
    unfiltered_input_list: Set[str] = set(unfiltered_input.split(" "))

    # this is done above
    # now remove _all_ whitespace characters
    # unfiltered_input_list = [re.sub(r"\s+", " ", u) for u in unfiltered_input_list]

    # this is done with tldextract
    # remove port numbers and paths
    # unfiltered_input_list = [re.sub(r":[^\s]*", "", u) for u in unfiltered_input_list]

    # this is done with tldextract
    # remove paths, directories etc
    # unfiltered_input_list = [re.sub(r"/[^\s]*", "", u) for u in unfiltered_input_list]

    # Remove empty values, only once because it's a set
    # The large number of spaces was the reason the function was very slow(!) It took 6 seconds for 25 domains.
    # But with using a set it's not even hitting 0.1 second for the same dataset
    if "" in unfiltered_input_list:
        unfiltered_input_list.remove("")

    # make list unique
    total_non_unique_items = len(unfiltered_input_list)
    # domains can still be wrong, such as "info" (or other tld like museum).
    # Check for all domains that it has a valid tld:
    has_tld = set()
    for domain in unfiltered_input_list:
        extract = tldextract.extract(domain)
        if extract.suffix and extract.domain:
            has_tld.add(extract.fqdn)

    duplicates_removed = total_non_unique_items - len(has_tld)

    # has_tld = [domain for domain in unfiltered_input_list
    #           if tldextract.extract(domain).suffix and tldextract.extract(domain).domain]

    # make sure the list is in alphabetical order, which is nice for testability.
    return sorted(has_tld), duplicates_removed


def add_domains_from_raw_user_data(account: Account, user_input: Dict[str, Any]) -> OperationResponseSchema:
    """
    This is the 'id' version of save_urllist. It is a bit stricter as in that it requires the list to exist.

    Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Used in the web / ajax frontend and uses operation responses.

    :param account:
    :param user_input:
    :return:
    """

    # how could we validate user_input a better way? Using a validator object?
    list_id: int = int(user_input.get("list_id", -1))
    unfiltered_urls: str = user_input.get("urls", [])

    # these are random unfiltered strings and the method expects keys...
    # in this case we'll run an extra retrieve_possible_urls_from_unfiltered_input so there is already some filtering.
    urls, _ = retrieve_possible_urls_from_unfiltered_input(unfiltered_urls)

    # does this remove tags of existing urls?
    result = save_urllist_content_by_id(account, list_id, {url: {"tags": []} for url in urls})
    if "error" in result:
        return OperationResponseSchema(**result)

    return operation_response(success=True, message="add_domains_valid_urls_added", data=result)


def save_urllist_content_by_name(
    account: Account,
    urllist_name: str,
    urls: Dict[str, Dict[str, list]],
    uploadlog_id: int = None,
    pending_message: str = None,
) -> dict:
    """
    This 'by name' variant is a best guess when a spreadsheet upload with list names is used.

    Stores urls in an urllist. If the url doesn't exist yet, it will be added to the database (so the urls
    can be shared with multiple accounts, and only requires one scan).

    Lists that don't exist will be created on the fly. The hope is to prevent data loss.

    Do not attempt to create a list if there are no valid urls for it, that would be a waste.

    Urls are just strings, which is enough to determine if it should be added.

    uploadlog_id and pending_message are used for user feedback, otherwise very long lists will never have interaction
    """

    urllist = get_or_create_list_by_name(account=account, name=urllist_name)
    return save_urllist_content_by_id(account, urllist.id, urls, uploadlog_id, pending_message)


def save_urllist_content_by_id(
    account: Account,
    urllist_id: id,
    unfiltered_urls: Dict[str, Dict[str, list]],
    uploadlog_id: int = None,
    pending_message: str = None,
) -> dict:
    urllist = UrlList.objects.all().filter(account=account, id=urllist_id, is_deleted=False).first()

    if not urllist:
        return {"error": True, "message": "add_domains_list_does_not_exist"}

    # this is extremely fast for 10k domains.
    urls, duplicates_removed = retrieve_possible_urls_from_unfiltered_input(", ".join(unfiltered_urls.keys()))
    cleaned_urls: Dict[str, List[str]] = clean_urls(urls)  # type: ignore

    proposed_number_of_urls = urllist.urls.all().count() + len(cleaned_urls["correct"])
    if proposed_number_of_urls > int(constance_cached_value("DASHBOARD_MAXIMUM_DOMAINS_PER_LIST")):
        return {"error": True, "message": "too_many_domains"}

    if cleaned_urls["correct"]:
        # this operation takes a while, to speed it up urls are added async.
        counters = _add_to_urls_to_urllist(
            account,
            urllist,
            urls=cleaned_urls["correct"],
            urls_with_tags_mapping=unfiltered_urls,
            uploadlog_id=uploadlog_id,
            pending_message=pending_message,
        )
    else:
        counters = {"added_to_list": 0, "already_in_list": 0}

    update_spreadsheet_upload_(
        uploadlog_id,
        "[2/3] Processing",
        f"{pending_message} Added {counters['added_to_list']} to {urllist.name}. "
        f"{counters['already_in_list']} already  list.",
        percentage=0,
    )

    return {
        "incorrect_urls": cleaned_urls["incorrect"],
        "added_to_list": counters["added_to_list"],
        "already_in_list": counters["already_in_list"],
        "duplicates_removed": duplicates_removed,
    }


@app.task(ignore_result=True)
def update_spreadsheet_upload_(
    upload_id: int, status: str = "pending", message: str = "", percentage: int = -1
) -> None:
    # double to prevent circulair import. This is not nice and should be removed.
    # user feedback is important on large uploads, as it may take a few minutes to hours it's nice to
    # get some feedback on how much stuff has been processed (if possible).
    uploads = UploadLog.objects.all().filter(id=upload_id).first()
    if not uploads:
        return

    if percentage != -1:
        uploads.percentage = percentage

    uploads.status = status
    uploads.message = message
    uploads.save()


@app.task(queue="storage")
def sleep():
    time.sleep(2)


def _add_to_urls_to_urllist(  # pylint: disable=too-many-positional-arguments too-many-arguments
    account: Account,
    current_list: UrlList,
    urls: List[str],
    urls_with_tags_mapping: Dict[str, Dict[str, list]] = None,
    uploadlog_id: int = None,
    pending_message: str = None,
) -> Dict[str, Any]:
    already_existing_urls = (
        UrlList.objects.all()
        .filter(account=account, id=current_list.id, urls__url__in=urls)
        .values_list("urls__url", flat=True)
    )

    new_urls = list(set(urls) - set(already_existing_urls))

    # run the database operations async to speed them up and to give faster user interaction
    # doing this in a group will create a memory overflow with 50k tasks, as each task contains the 50k other tasks
    # with each of them taking 250kb of ram. This quickly amounts to hundreds of megs or gigs. Therefore split
    # these tasks to individual tasks.
    # Run them a to z so there is a sense of progress per list.
    tasks = []
    for position, url in enumerate(sorted(new_urls)):
        tasks.append(
            group(
                add_new_url_to_list_async.si(url, current_list.id, urls_with_tags_mapping)
                # discovering endpoints is not a hard requirements, this is done before a scan starts anyway
                # and will only slow down creating the list.
                # | discover_endpoints.s()
                | update_spreadsheet_upload_.si(
                    uploadlog_id,
                    "[3/3] Processing",
                    f"{pending_message}. Added: {url} to {current_list.name}.",
                    percentage=round(100 * position / len(new_urls), 0),
                )
            )
        )

    # This might be performed earlier than above tasks in the queue
    for _ in range(4):
        tasks.append(
            group(
                # simulate the time it takes to add something...
                sleep.si()
                | update_spreadsheet_upload_.si(
                    uploadlog_id, "[3/3] Processing", f'[3/3] Processing completed for list "{current_list.name}".', 100
                )
            )
        )

    print(f"created {len(tasks)} tasks")

    # pytest async tests requires a running stack, which is more complex. Therefore trust that apply_async works.
    if "pytest" in sys.modules:
        for task in tasks:
            task.apply()
    else:
        for task in tasks:
            task.apply_async()

    return {
        "added_to_list": len(new_urls),
        "already_in_list": len(already_existing_urls),
    }


@app.task(queue="storage", ignore_result=True)
def add_new_url_to_list_async(url: str, current_list_id: int, urls_with_tags_mapping: Dict[str, Dict[str, set]] = None):
    db_url = Url.add(url)
    urllist = UrlList.objects.all().filter(id=current_list_id).first()
    if not urllist:
        return db_url

    urllist.urls.add(db_url)

    if urls_with_tags_mapping:
        add_tags_to_urls_in_urllist(db_url, urllist, urls_with_tags_mapping.get(url, {}).get("tags", []))

    return db_url.id


@app.task(queue="storage", ignore_result=True)
def discover_endpoints(url_id):
    # always try to find a few dns endpoints...
    compose_discover_task(urls_filter={"pk": url_id}).apply_async()


def add_tags_to_urls_in_urllist(existing_url: Url, current_list: UrlList, tags: List[str]) -> None:
    match = TaggedUrlInUrllist.objects.all().filter(url=existing_url, urllist=current_list).first()
    for tag in tags:
        if tag := tag.strip():
            match.tags.add(tag)


def _add_to_urls_to_urllist_nicer(account: Account, current_list: UrlList, urls: List[str]) -> Dict[str, List[str]]:
    counters: Dict[str, List[str]] = {
        "added_to_list": [],
        "already_in_list": [],
        "added_to_list_already_in_db": [],
        "added_to_list_new_in_db": [],
    }

    for url in urls:

        if UrlList.objects.all().filter(account=account, id=current_list.id, urls__url__iexact=url).exists():
            counters["already_in_list"].append(url)
            continue

        # if url already in database, we only need to add it to the list:
        if existing_url := Url.objects.all().filter(url=url).first():
            current_list.urls.add(existing_url)
            counters["added_to_list"].append(url)
            counters["added_to_list_already_in_db"].append(url)
        else:
            new_url = Url.add(url)

            # always try to find a few dns endpoints...
            compose_discover_task(urls_filter={"pk": new_url.id}).apply_async()

            current_list.urls.add(new_url)
            counters["added_to_list"].append(url)
            counters["added_to_list_new_in_db"].append(url)

    return counters


def clean_urls(urls: List[str]) -> Dict[str, List[str]]:
    """
    Incorrect urls are urls that are not following the uri scheme standard and don't have a recognizable suffix. They
    are returned for informational purposes and can contain utter garbage. The editor of the urls can then easily see
    if the urls are entered correctly and might correct some mistakes.

    :param urls:
    :return:
    """

    result: Dict[str, List[Union[str, int]]] = {"incorrect": [], "correct": []}

    for url in urls:
        # all urls in the system must be lowercase (if applicable to used character)
        url = url.lower()

        if not Url.is_valid_url(url):
            result["incorrect"].append(url)
        else:
            result["correct"].append(url)

    return result


def get_or_create_list_by_name(account, name: str, scan_type: str = "web") -> UrlList:
    if existing_list := UrlList.objects.all().filter(account=account, name=name, is_deleted=False).first():
        return existing_list

    urllist = UrlList(**{"name": name, "account": account, "scan_type": scan_type})
    urllist.save()
    return urllist


def delete_url_from_urllist(account: Account, urllist_id: int, url_id: int) -> bool:
    """
    While we delete the url in the urllist, the actual url is not deleted. It might be used by others, and
    all the same it might be used in the future by someone else. This will retrain the historic data.

    :param account:
    :param urllist_id:
    :param url_id:
    :return:
    """

    # make sure that the url is in this list and for the current account
    # we don't want other users to be able to delete urls of other lists.
    url_is_in_list = (
        Url.objects.all()
        .filter(urls_in_dashboard_list_2__account=account, urls_in_dashboard_list_2__id=urllist_id, id=url_id)
        .first()
    )

    if not url_is_in_list:
        return False

    urllist = UrlList.objects.all().get(id=urllist_id)
    urllist.urls.remove(url_is_in_list)

    return True


def download_as_spreadsheet(account: Account, urllist_id: int, file_type: str = "xlsx") -> Any:
    urls = (
        TaggedUrlInUrllist.objects.all()
        .filter(urllist__account=account, urllist__pk=urllist_id)
        .order_by("url__computed_domain", "url__computed_subdomain")
    )

    if not urls:
        return JsonResponse({})

    # results is a matrix / 2-d array / array with arrays.
    data: List[List[Any]] = []
    data += [["List(s)", "Domain(s)", "Tags"]]

    for url in urls.all():
        data += [[url.urllist.name, url.url.url, ", ".join(url.tags.values_list("name", flat=True))]]

    book = p.get_book(bookdict={"Domains": data})

    return create_spreadsheet_download("internet dashboard list", book, file_type)
