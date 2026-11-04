# SPDX-License-Identifier: Apache-2.0
"""A durable, ordered import shared by all domain-addition interfaces.

Only DNS runs in a bounded thread pool. Database writes stay on the worker thread;
progress is committed alongside each result, and messages contain only a batch ID.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from io import StringIO
from itertools import islice
from pathlib import Path
from uuid import uuid4

import dramatiq
import pyexcel
from constance import config
from django.db import transaction
from django.db.models import Count, F, Q
from django.utils.timezone import now
from dns.exception import DNSException
from ninja import Schema
from pydantic import Field
from websecmap import tldextract
from websecmap.organizations.models import Url
from websecmap.scanners_internet_nl_dns_endpoints.tasks import has_a_or_aaaa, has_soa

from dashboard.internet_nl_dashboard.logic.domains import add_tags_to_urls_in_urllist, get_or_create_list_by_name
from dashboard.internet_nl_dashboard.logic.spreadsheet import (
    SpreadsheetStorageUnavailable,
    is_valid_extension,
    is_valid_mimetype,
    save_file,
)
from dashboard.internet_nl_dashboard.logic.tags import parse_tags_from_csv_data
from dashboard.internet_nl_dashboard.models import (
    TAG_MAX_LENGTH,
    Account,
    DashboardUser,
    DomainBatch,
    DomainBatchItem,
    UrlList,
)
from dashboard.internet_nl_dashboard.problems import ApiError, DocumentedApiError, ProblemType, raises

log = logging.getLogger(__name__)
REJECTED = ("invalid", "unresolvable", "limit")
LEASE = timedelta(minutes=15)
CHUNK_SIZE = 32


class BatchQueueUnavailable(DocumentedApiError):
    status = 503
    detail = "The domain import queue is temporarily unavailable. Please retry this batch later."
    problem_type = ProblemType.SPREADSHEET_QUEUE_UNAVAILABLE


class BatchInputSchema(Schema):
    raw_urls: str = Field(min_length=1, max_length=10_000_000)


class BatchConfirmSchema(Schema):
    overwrite: bool = False
    confirmation: str = ""


class BatchListSchema(Schema):
    id: int
    name: str


class CorrectionSchema(Schema):
    id: int
    value: str = Field(max_length=10_000)
    list_name: str | None = Field(default=None, max_length=120)


class CorrectionsSchema(Schema):
    corrections: list[CorrectionSchema] = Field(min_length=1)


class BatchItemSchema(Schema):
    id: int
    row: int
    list_name: str
    raw_domain: str
    domain: str
    status: str
    reason: str


class ListCapacitySchema(Schema):
    name: str
    existing: int
    new: int
    available: int
    over_limit: int
    maximum: int
    incoming: int


class BatchSchema(Schema):
    id: int
    filename: str
    source: str
    target_list: bool
    overwrite: bool = False
    lists: list[BatchListSchema] = Field(default_factory=list)
    stage: str
    status: str
    message: str
    total: int
    processed: int
    percentage: int
    counts: dict[str, int]
    limits: list[ListCapacitySchema]
    resumable: bool
    created_on: datetime


def owned_batch(account: Account, batch_id: int) -> DomainBatch:
    batch = DomainBatch.objects.filter(id=batch_id, account=account).first()
    if not batch:
        raise ApiError(404, "Domain batch does not exist.")
    return batch


def batch_summary(batch: DomainBatch) -> dict:
    counts = {entry["status"]: entry["count"] for entry in batch.items.values("status").annotate(count=Count("id"))}
    limit = int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST)
    capacities = []
    for entry in (
        batch.items.filter(status__in=("valid", "existing"))
        .values("list_name")
        .annotate(count=Count("id", filter=Q(status="valid")), incoming=Count("id"))
    ):
        urllist = (
            batch.urllist
            if batch.target_list
            else UrlList.objects.filter(account=batch.account, name=entry["list_name"], is_deleted=False).first()
        )
        existing = urllist.urls.count() if urllist else 0
        available = max(0, limit - existing)
        capacities.append(
            {
                "name": entry["list_name"],
                "existing": existing,
                "new": entry["count"],
                "available": available,
                "over_limit": max(0, entry["count"] - available),
                "maximum": limit,
                "incoming": entry["incoming"],
            }
        )
    lists = []
    if batch.status in {"completed", "cancelled", "failed"}:
        if batch.target_list:
            if batch.urllist and not batch.urllist.is_deleted:
                lists.append({"id": batch.urllist.id, "name": batch.urllist.name})
        else:
            for name in batch.items.values_list("list_name", flat=True).distinct().iterator():
                urllist = UrlList.objects.filter(account=batch.account, name=name, is_deleted=False).first()
                if urllist:
                    lists.append({"id": urllist.id, "name": urllist.name})
    total = batch.total
    processed = batch.processed
    if batch.stage == "addition":
        total = sum(
            counts.get(status, 0)
            for status in ("valid", "existing", "prepared", "added", "existing_done", "unresolvable", "limit")
        )
        processed = sum(
            counts.get(status, 0) for status in ("prepared", "added", "existing_done", "unresolvable", "limit")
        )
    return {
        "id": batch.id,
        "filename": batch.filename,
        "source": batch.source,
        "target_list": batch.target_list,
        "overwrite": batch.overwrite,
        "lists": lists,
        "stage": batch.stage,
        "status": batch.status,
        "message": batch.message,
        "total": total,
        "processed": processed,
        "percentage": min(100, int(100 * processed / total)) if total else (100 if batch.status == "completed" else 0),
        "counts": counts,
        "limits": capacities,
        "resumable": batch.status == "failed"
        or (batch.status in {"running", "queued"} and batch.updated_on < now() - LEASE),
        "created_on": batch.created_on.isoformat(),
    }


def enqueue_batch(batch: DomainBatch) -> None:
    try:
        process_domain_batch.send(batch.id)
    except Exception as exc:
        log.exception("Could not enqueue domain batch %s", batch.id)
        DomainBatch.objects.filter(id=batch.id, status="queued").update(
            status="failed", message=BatchQueueUnavailable.detail, updated_on=now()
        )
        raise BatchQueueUnavailable() from exc


@raises(SpreadsheetStorageUnavailable, BatchQueueUnavailable)
def start_batch(user: DashboardUser, *, urllist_id: int | None = None, raw_urls: str = "", file=None) -> dict:
    urllist = None
    if urllist_id is not None:
        urllist = UrlList.objects.filter(id=urllist_id, account=user.account, is_deleted=False).first()
        if not urllist:
            raise ApiError(404, "List does not exist.", ProblemType.LIST_NOT_FOUND)
    saved_file = save_file(file) if file else ""
    batch = DomainBatch.objects.create(
        account=user.account,
        user=user,
        urllist=urllist,
        target_list=urllist is not None,
        raw_text=raw_urls,
        file_path=saved_file,
        source="spreadsheet" if file else "text",
        filename=Path(file.name).name if file else "",
    )
    enqueue_batch(batch)
    return batch_summary(batch)


def _input_items(batch: DomainBatch):
    """Preserve row order and original malformed input; never silently drop cells."""
    if not batch.file_path:
        for row, line in enumerate(StringIO(batch.raw_text), 1):
            for value in re.split(r"[,;\s]+", line.strip()):
                if value:
                    yield {"row": row, "list_name": batch.urllist.name, "raw_domain": value, "tags": []}
        return
    if not is_valid_extension(batch.file_path.lower()) or not is_valid_mimetype(batch.file_path):
        raise ValueError("Please upload a CSV, XLS, XLSX or ODS spreadsheet.")
    try:
        try:
            sheet = pyexcel.get_sheet(
                file_name=batch.file_path, auto_detect_int=False, auto_detect_float=False, auto_detect_datetime=False
            )
        except Exception as exc:
            raise ValueError(
                "The spreadsheet could not be read. Check its format or use one of the sample files."
            ) from exc
        rows = iter(sheet)
        header = [str(value).strip().lower() for value in next(rows, [])]
        # These are the columns used by the supplied sample spreadsheets. Recognized
        # headers also allow users to fix swapped Domain/Tags columns without data loss.
        domains = {"domain", "domains", "website", "websites", "url", "urls", "domein", "domeinen", "internet address"}
        categories = {"category / list", "category", "list", "list name", "lijst", "categorie", "category/list"}
        domain_column = next((i for i, name in enumerate(header) if name in domains), None)
        list_column = next((i for i, name in enumerate(header) if name in categories), None)
        tag_column = next((i for i, name in enumerate(header) if name in {"tag", "tags"}), 2)
        if domain_column is None or (list_column is None and not batch.target_list):
            raise ValueError(
                "Missing spreadsheet headers. Use Category / List, Domain and Tags, as in the sample files."
            )
        for row_number, row in enumerate(rows, 2):
            if not any(str(value).strip() for value in row):
                continue
            value = str(row[domain_column]).strip() if domain_column < len(row) else ""
            names = (
                [batch.urllist.name]
                if batch.target_list
                else (str(row[list_column]).split(",") if list_column < len(row) else [""])
            )
            tags = parse_tags_from_csv_data(row[tag_column]) if tag_column is not None and tag_column < len(row) else []
            for name in names:
                for domain in value.split(","):
                    yield {"row": row_number, "list_name": name.strip(), "raw_domain": domain.strip(), "tags": tags}
    finally:
        pyexcel.free_resources()


def _batch_is_running(batch: DomainBatch, token: str) -> bool:
    return DomainBatch.objects.filter(id=batch.id, worker_token=token, status="running").exists()


def _initialize_items(batch: DomainBatch, token: str) -> None:
    if not _batch_is_running(batch, token) or batch.items.exists():
        return
    maximum = int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET)
    names = set()
    count = 0
    with transaction.atomic():
        source = iter(_input_items(batch))
        while rows := tuple(islice(source, 500)):
            if not _batch_is_running(batch, token):
                return
            entries = []
            for row in rows:
                names.add(row["list_name"])
                count += 1
                if count > maximum:
                    raise ValueError(f"This batch exceeds the configured input limit of {maximum} domains.")
                if len(names) > int(config.DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET):
                    raise ValueError("This spreadsheet exceeds the configured number of lists. Please split the file.")
                entries.append(DomainBatchItem(batch=batch, position=count, **row))
            DomainBatchItem.objects.bulk_create(entries, batch_size=500)
        if count == 0:
            raise ValueError("The input contains no domains. Check the spreadsheet headers and domain column.")
        DomainBatch.objects.filter(id=batch.id, worker_token=token, status="running").update(
            total=count, processed=0, updated_on=now()
        )
    batch.total = count


def _validate_batch(batch: DomainBatch, token: str) -> None:
    _initialize_items(batch, token)
    seen = {}
    existing = {}
    # Re-read persisted canonical rows on a resumed validation. Order is the supplied order.
    for item in batch.items.exclude(status="pending").order_by("position").iterator():
        if item.domain and item.status != "duplicate":
            seen[(item.list_name, item.domain)] = item
    processed = batch.items.exclude(status="pending").count()
    for item in batch.items.filter(status="pending").order_by("position").iterator(chunk_size=500):
        if not _batch_is_running(batch, token):
            return
        item.domain, item.reason = "", ""
        value = item.raw_domain.strip().lower().rstrip(".")
        try:
            domain = tldextract.extract(value).fqdn
            valid = bool(domain and Url.is_valid_url(domain))
        except (ValueError, UnicodeError):
            domain, valid = "", False
        with transaction.atomic():
            Account.objects.filter(id=batch.account.id).update(name=F("name"))
            if not _batch_is_running(batch, token):
                return
            if not item.list_name or len(item.list_name) > 120:
                item.status, item.reason = "invalid", "A list name of 1 to 120 characters is required."
            elif not valid or any(character.isspace() for character in value) or "@" in value:
                item.status, item.reason = "invalid", "Enter a valid domain name with a recognized extension."
            elif any(len(tag) > TAG_MAX_LENGTH for tag in item.tags):
                item.status, item.reason = "invalid", f"Tags may contain at most {TAG_MAX_LENGTH} characters."
            else:
                item.domain = domain
                key = (item.list_name, domain)
                if key in seen:
                    original = seen[key]
                    original.tags = list(dict.fromkeys((*original.tags, *item.tags)))
                    original.save(update_fields=["tags"])
                    if original.status in {"added", "existing_done"}:
                        # A corrected row may supply tags for a domain added in an earlier
                        # round. Apply those tags only after the next confirmation.
                        item.status = "existing"
                        seen[key] = item
                    else:
                        item.status = "duplicate"
                else:
                    seen[key] = item
                    if item.list_name not in existing:
                        urllist = (
                            batch.urllist
                            if batch.target_list
                            else UrlList.objects.filter(
                                account=batch.account, name=item.list_name, is_deleted=False
                            ).first()
                        )
                        existing[item.list_name] = set(urllist.urls.values_list("url", flat=True)) if urllist else set()
                    item.status = "existing" if domain in existing[item.list_name] else "valid"
            item.save(update_fields=["domain", "status", "reason"])
            processed += 1
            DomainBatch.objects.filter(id=batch.id, worker_token=token).update(processed=processed, updated_on=now())
    DomainBatch.objects.filter(id=batch.id, worker_token=token, status="running").update(
        status="review", message="Review the validation results before adding domains.", updated_on=now()
    )


def resolve_domain(domain: str | None) -> tuple[bool, str]:
    if domain is None:
        return True, ""
    try:
        return (
            (True, "") if has_a_or_aaaa(domain) or has_soa(domain) else (False, "No website or mail DNS records found.")
        )
    except (DNSException, OSError):
        return False, "DNS lookup failed or timed out. You can retry this domain."


def _add_batch(batch: DomainBatch, token: str) -> None:
    processed = batch.items.exclude(status__in=("valid", "existing")).count()
    with ThreadPoolExecutor(max_workers=8, thread_name_prefix="domain-import-dns") as pool:
        while items := tuple(batch.items.filter(status__in=("valid", "existing")).order_by("position")[:CHUNK_SIZE]):
            if not _batch_is_running(batch, token):
                return
            full_lists = set()
            for name in dict.fromkeys(item.list_name for item in items):
                urllist = (
                    batch.urllist
                    if batch.target_list
                    else UrlList.objects.filter(account=batch.account, name=name, is_deleted=False).first()
                )
                if urllist and urllist.urls.count() >= int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST):
                    full_lists.add(name)
            # map yields results in input order, even when DNS replies arrive out of order.
            results = pool.map(
                resolve_domain,
                (
                    item.domain if item.status == "valid" and item.list_name not in full_lists else None
                    for item in items
                ),
            )
            for item, (resolves, reason) in zip(items, results):
                with transaction.atomic():
                    # Updating the account row also serializes SQLite writers. All batch
                    # additions for this account share this lock before checking capacity.
                    Account.objects.filter(id=batch.account.id).update(name=F("name"))
                    current = DomainBatch.objects.get(id=batch.id)
                    if current.worker_token != token or current.status != "running":
                        return
                    urllist = (
                        current.urllist
                        if batch.target_list
                        else get_or_create_list_by_name(batch.account, item.list_name)
                    )
                    if not urllist or urllist.is_deleted:
                        raise ValueError("The target list was deleted. No further domains have been added.")
                    existing_url = urllist.urls.filter(url=item.domain).first()
                    if existing_url:
                        item.status = "existing_done"
                        add_tags_to_urls_in_urllist(existing_url, urllist, item.tags)
                    elif urllist.urls.count() >= int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST):
                        item.status, item.reason = "limit", "The list domain limit has been reached."
                    elif not resolves:
                        item.status, item.reason = "unresolvable", reason
                    else:
                        url = Url.add(item.domain)
                        urllist.urls.add(url)
                        add_tags_to_urls_in_urllist(url, urllist, item.tags)
                        item.status = "added"
                    item.save(update_fields=["status", "reason"])
                    processed += 1
                    DomainBatch.objects.filter(id=batch.id, worker_token=token).update(
                        processed=processed, updated_on=now()
                    )
    DomainBatch.objects.filter(id=batch.id, worker_token=token, status="running").update(
        status="completed", processed=batch.total, message="Domain processing completed.", updated_on=now()
    )


def _replace_list(batch: DomainBatch, token: str) -> None:
    """Prepare the entire replacement, then atomically swap membership and tags.

    Cancellation or failure while resolving leaves the original list intact. A
    failed final transaction rolls back both the list and its per-row outcomes.
    """
    prepared_count = batch.items.filter(status="prepared").count()
    with ThreadPoolExecutor(max_workers=8, thread_name_prefix="domain-replace-dns") as pool:
        while items := tuple(batch.items.filter(status__in=("valid", "existing")).order_by("position")[:CHUNK_SIZE]):
            if not _batch_is_running(batch, token):
                return
            results = pool.map(resolve_domain, (item.domain if item.status == "valid" else None for item in items))
            for item, (resolves, reason) in zip(items, results):
                with transaction.atomic():
                    Account.objects.filter(id=batch.account.id).update(name=F("name"))
                    if not _batch_is_running(batch, token):
                        return
                    if prepared_count >= int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST):
                        item.status, item.reason = "limit", "The list domain limit has been reached."
                    elif not resolves:
                        item.status, item.reason = "unresolvable", reason
                    else:
                        item.status = "prepared"
                        prepared_count += 1
                    item.save(update_fields=["status", "reason"])
                    DomainBatch.objects.filter(id=batch.id, worker_token=token).update(updated_on=now())
    with transaction.atomic():
        Account.objects.filter(id=batch.account.id).update(name=F("name"))
        current = DomainBatch.objects.select_related("urllist").get(id=batch.id)
        if current.worker_token != token or current.status != "running":
            return
        urllist = current.urllist
        if not urllist or urllist.is_deleted:
            raise ValueError("The target list was deleted. The replacement has not been applied.")
        prepared = batch.items.filter(status="prepared").order_by("position")
        maximum = int(config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST)
        if maximum < 1 or not prepared.exists():
            raise ValueError("No resolvable domains could be added. The existing list has been kept.")
        urllist.urls.clear()
        for position, item in enumerate(prepared.iterator()):
            if position >= maximum:
                item.status, item.reason = "limit", "The list domain limit has been reached."
            else:
                url = Url.add(item.domain)
                urllist.urls.add(url)
                add_tags_to_urls_in_urllist(url, urllist, item.tags)
                item.status = "added"
            item.save(update_fields=["status", "reason"])
        DomainBatch.objects.filter(id=batch.id, worker_token=token).update(
            status="completed", processed=batch.total, message="List replacement completed.", updated_on=now()
        )


@dramatiq.actor(queue_name="storage", actor_name="dashboard.process_domain_batch", max_retries=0, time_limit=86_400_000)
def process_domain_batch(batch_id: int) -> None:
    token = str(uuid4())
    claimed = DomainBatch.objects.filter(id=batch_id, status="queued").update(
        status="running", worker_token=token, updated_on=now()
    )
    if not claimed:
        return
    batch = DomainBatch.objects.select_related("account", "user", "urllist").get(id=batch_id)
    try:
        if batch.target_list and (not batch.urllist or batch.urllist.is_deleted):
            raise ValueError("The target list was deleted.")
        if batch.stage == "validation":
            _validate_batch(batch, token)
        elif batch.overwrite:
            _replace_list(batch, token)
        else:
            _add_batch(batch, token)
    except Exception as exc:
        log.exception("Domain batch %s failed", batch.id)
        message = (
            str(exc) if isinstance(exc, ValueError) else "Processing stopped. Please retry to continue this batch."
        )
        DomainBatch.objects.filter(id=batch.id, worker_token=token).update(
            status="failed", message=message, updated_on=now()
        )


def confirm_batch(account: Account, batch_id: int, overwrite: bool = False, confirmation: str = "") -> dict:
    with transaction.atomic():
        Account.objects.filter(id=account.id).update(name=F("name"))
        batch = owned_batch(account, batch_id)
        if batch.status != "review":
            raise ApiError(409, "This batch is not ready for confirmation.")
        if overwrite:
            if not batch.target_list or batch.source != "spreadsheet":
                raise ApiError(400, "Only a spreadsheet uploaded to an existing list can overwrite that list.")
            if batch.items.filter(status__in=("added", "existing_done")).exists():
                raise ApiError(
                    409, "This import has already been processed. Upload a new spreadsheet to replace the list."
                )
            if confirmation.strip().casefold() not in {"overwrite", "overschrijven"}:
                raise ApiError(
                    400, "Type overwrite or overschrijven to confirm replacing the current list.", field="confirmation"
                )
            if not batch.items.filter(status__in=("valid", "existing")).exists():
                raise ApiError(400, "An overwrite requires at least one valid domain.")
        if DomainBatch.objects.filter(account=account, stage="addition", status__in=("queued", "running")).exists():
            raise ApiError(409, "Another batch is being added to this account. Please wait for it to finish.")
        batch.stage, batch.status, batch.message = "addition", "queued", "Waiting to resolve and add domains."
        batch.overwrite = overwrite
        batch.processed = batch.items.exclude(status__in=("valid", "existing")).count()
        batch.updated_on = now()
        batch.save(update_fields=["stage", "status", "message", "processed", "updated_on", "overwrite"])
    enqueue_batch(batch)
    return batch_summary(batch)


def correct_batch(account: Account, batch_id: int, corrections: list[CorrectionSchema]) -> dict:
    with transaction.atomic():
        batch = DomainBatch.objects.select_for_update().get(id=owned_batch(account, batch_id).id)
        if batch.status not in {"review", "completed"}:
            raise ApiError(409, "Wait for processing to finish before correcting domains.")
        for correction in corrections:
            item = batch.items.filter(id=correction.id, status__in=REJECTED).first()
            if not item:
                raise ApiError(400, "Only rejected rows in this batch can be corrected.")
            if correction.list_name is not None:
                if batch.target_list:
                    raise ApiError(400, "The target list of this batch cannot be changed.")
                item.list_name = correction.list_name.strip()
            item.raw_domain = correction.value.strip()
            item.status = "pending" if item.raw_domain else "removed"
            item.domain, item.reason = "", ""
            item.save(update_fields=["raw_domain", "status", "domain", "reason", "list_name"])
        # Revalidate in original order, including earlier duplicates and limit estimates.
        batch.items.exclude(status__in=("added", "existing_done", "removed")).update(status="pending", reason="")
        batch.stage, batch.status, batch.processed = "validation", "queued", 0
        batch.updated_on = now()
        batch.save(update_fields=["stage", "status", "processed", "updated_on"])
    enqueue_batch(batch)
    return batch_summary(batch)


def retry_batch(account: Account, batch_id: int) -> dict:
    with transaction.atomic():
        Account.objects.filter(id=account.id).update(name=F("name"))
        batch = owned_batch(account, batch_id)
        if not batch_summary(batch)["resumable"]:
            raise ApiError(409, "This batch is still running or does not need to be resumed.")
        if (
            batch.stage == "addition"
            and DomainBatch.objects.filter(account=account, stage="addition", status__in=("queued", "running"))
            .exclude(id=batch.id)
            .exists()
        ):
            raise ApiError(409, "Another batch is being added to this account. Please wait for it to finish.")
        claimed = DomainBatch.objects.filter(id=batch.id, status=batch.status, updated_on=batch.updated_on).update(
            status="queued", worker_token="", updated_on=now()
        )
        if not claimed:
            raise ApiError(409, "The batch state changed. Refresh its progress.")
        batch.refresh_from_db()
    enqueue_batch(batch)
    return batch_summary(batch)


def cancel_batch(account: Account, batch_id: int) -> None:
    with transaction.atomic():
        # Share the writer lock with the worker. Once cancellation commits, no
        # later domain/tag write can pass its status and ownership check.
        Account.objects.filter(id=account.id).update(name=F("name"))
        batch = owned_batch(account, batch_id)
        if batch.status == "cancelled":
            return
        if batch.status == "completed":
            raise ApiError(409, "Completed domain batches cannot be cancelled.")
        batch.status = "cancelled"
        batch.worker_token = ""
        batch.message = "Processing cancelled. Domains and tags already added remain in the list."
        batch.updated_on = now()
        batch.save(update_fields=["status", "worker_token", "message", "updated_on"])
