# SPDX-License-Identifier: Apache-2.0
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from constance import config

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, AccountInternetNLScanLog


def get_scan_monitor_data(account: Account) -> List[Dict[str, Union[str, int, bool, None]]]:
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

    response = []
    # don't show duplicate scans from running
    handled_scans = []
    for scan in latest_30_scans:
        handled_scans.append(scan.id)
        response.append(prepare_scan_data_for_display(scan))

    # add all scans that have not finished
    response.extend(prepare_scan_data_for_display(scan) for scan in unfinished_scans if scan.id not in handled_scans)
    return response


def prepare_scan_data_for_display(scan: Any):
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

    logs = AccountInternetNLScanLog.objects.all().filter(scan=scan).only("at_when", "state").order_by("-at_when")
    log_messages = [{"at_when": log.at_when, "state": log.state} for log in logs]

    data = {
        "id": scan.id,
        "state": scan.state,
        # mask that there is a mail_dashboard variant.
        "type": "",
        "last_check": None,
        "started": True,
        "started_on": scan.started_on,
        "finished": scan.finished,
        "finished_on": scan.finished_on,
        "status_url": "",
        "message": scan.state,
        "success": scan.finished,
        "list": "",
        "list_id": 0,
        "runtime": runtime_seconds,
        "last_report_id": last_report_id,
        "log": log_messages,
    }

    if scan.scan:
        # mask that there is a mail_dashboard variant.
        data["type"] = "web" if scan.scan.type == "web" else "all" if scan.scan.type == "all" else "mail"
        data["last_check"] = scan.scan.last_state_check
        data["status_url"] = f"{config.INTERNET_NL_API_URL}"
        data["status_url"] += f"/requests/{scan.scan.scan_id}"
    if scan.urllist:
        data["list"] = scan.urllist.name
        data["list_id"] = scan.urllist.id

    return data
