# SPDX-License-Identifier: Apache-2.0
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from actstream import action
from constance import config
from ninja import Schema

from dashboard.internet_nl_dashboard.logic import OperationResponseSchema, operation_response
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, AccountInternetNLScanLog
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import update_state


class ScanLogEntrySchema(Schema):
    at_when: datetime = None
    state: str = ""


class ScanMonitorItemSchema(Schema):
    id: int
    state: str
    type: str
    last_check: datetime | None
    started: bool
    started_on: datetime
    finished: bool
    finished_on: datetime | None
    status_url: str
    message: str
    success: bool
    list_name: str
    list_id: int
    runtime: int
    last_report_id: int | None
    log: list[ScanLogEntrySchema] = []


def get_scan_monitor_data(account: Account) -> list[ScanMonitorItemSchema]:
    latest_30_scans = (
        AccountInternetNLScan.objects.all()
        .filter(account=account, urllist__is_deleted=False)
        .order_by("-pk")[:30]
        .select_related("urllist", "scan", "report")
        .only(
            "id",
            "state",
            "started_on",
            "finished_on",
            "scan__type",
            "scan__id",
            "scan__scan_id",
            "scan__last_state_check",
            "urllist_id",
            "urllist__name",
            "report__id",
        )
    )

    # append all scans that are still running or any state except finished
    unfinished_scans = (
        AccountInternetNLScan.objects.all()
        .filter(
            account=account,
            urllist__is_deleted=False,
        )
        .exclude(state__in=["finished", "cancelled"])
        .order_by("-pk")
        .select_related("urllist", "scan", "report")
        .only(
            "id",
            "state",
            "started_on",
            "finished_on",
            "scan__type",
            "scan__id",
            "scan__scan_id",
            "scan__last_state_check",
            "urllist_id",
            "urllist__name",
            "report__id",
        )
    )

    scans_for_response: list[AccountInternetNLScan] = []
    handled_scan_ids: set[int] = set()

    # Keep existing ordering: latest finished/history first, then currently running not in latest list.
    for scan in latest_30_scans:
        handled_scan_ids.add(scan.id)
        scans_for_response.append(scan)
    for scan in unfinished_scans:
        if scan.id not in handled_scan_ids:
            scans_for_response.append(scan)

    logs_by_scan_id = _load_scan_logs_by_scan_id([scan.id for scan in scans_for_response])
    return [prepare_scan_data_for_display(scan, logs_by_scan_id.get(scan.id, [])) for scan in scans_for_response]


def _load_scan_logs_by_scan_id(scan_ids: list[int]) -> dict[int, list[ScanLogEntrySchema]]:
    if not scan_ids:
        return {}

    logs_qs = (
        AccountInternetNLScanLog.objects.all()
        .filter(scan_id__in=scan_ids)
        .only("scan_id", "at_when", "state")
        .order_by("scan_id", "-at_when")
    )
    logs_by_scan_id: dict[int, list[ScanLogEntrySchema]] = defaultdict(list)
    for log in logs_qs:
        logs_by_scan_id[log.scan_id].append(ScanLogEntrySchema(at_when=log.at_when, state=log.state))

    return dict(logs_by_scan_id)


def prepare_scan_data_for_display(
    scan: Any,
    log_messages: list[ScanLogEntrySchema] | None = None,
) -> ScanMonitorItemSchema:
    last_report_id = None
    if scan.state == "finished" and scan.report is not None:
        last_report_id = scan.report.id

    if scan.state == "finished" and scan.finished_on:
        moment = scan.finished_on
    else:
        moment = datetime.now(timezone.utc)

    runtime_seconds = 0
    if scan.started_on:
        runtime = moment - scan.started_on
        runtime_seconds = int(runtime.total_seconds() * 1000)

    if log_messages is None:
        log_messages = []

    # Start with defaults and then enrich if related objects are present
    item = ScanMonitorItemSchema(
        id=scan.id,
        state=scan.state,
        # mask that there is a mail_dashboard variant.
        type="",
        last_check=None,
        started=True,
        started_on=scan.started_on,
        finished=scan.finished,
        finished_on=scan.finished_on,
        status_url="",
        message=scan.state,
        success=scan.finished,
        list_name="",
        list_id=0,
        runtime=runtime_seconds,
        last_report_id=last_report_id,
        log=log_messages,
    )

    if scan.scan:
        # mask that there is a mail_dashboard variant.
        item.type = "web" if scan.scan.type == "web" else "all" if scan.scan.type == "all" else "mail"
        item.last_check = scan.scan.last_state_check
        item.status_url = f"{config.INTERNET_NL_API_URL}/requests/{scan.scan.scan_id}"

    if scan.urllist:
        item.list_name = scan.urllist.name
        item.list_id = scan.urllist.id

    return item


def cancel_scan(account: Account, scan_id: int) -> OperationResponseSchema:
    """
    :param account: Account
    :param scan_id: AccountInternetNLScan ID
    :return:
    """

    scan = AccountInternetNLScan.objects.all().filter(account=account, pk=scan_id).first()

    if not scan:
        return operation_response(error=True, message="scan not found")

    if scan.state == "finished":
        return operation_response(success=True, message="scan already finished")

    if scan.state == "cancelled":
        return operation_response(success=True, message="scan already cancelled")

    scan.finished_on = datetime.now(timezone.utc)
    scan.save()
    update_state("cancelled", scan.id)

    # Sprinkling an activity stream action.
    action.send(account, verb="cancelled scan", target=scan, public=False)

    return operation_response(success=True, message="scan cancelled")
