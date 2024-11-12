from typing import Dict, List, Optional

from django.db.models import Prefetch

from dashboard.internet_nl_dashboard import log
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport


def get_latest_report_id_from_list_and_type(urllist_id: int, report_type: str = "") -> Dict[str, str]:
    report = UrlListReport.objects.filter(urllist=urllist_id, is_publicly_shared=True)

    if report_type in {"web", "mail"}:
        report = report.filter(report_type=report_type)

    found_report = report.last()

    return (
        {"latest_report_public_report_code": found_report.public_report_code}
        if found_report
        else {"latest_report_public_report_code": ""}
    )


def get_publicly_shared_lists_per_account_and_list_id(account_id: int, urllist_id: int) -> List[dict]:
    return get_publicly_shared_lists_per_account(account_id, urllist_id)


def get_publicly_shared_lists_per_account(account_id, urllist_id: Optional[int] = None) -> List[dict]:

    log.debug(f"get_publicly_shared_lists_per_account account_id: {account_id}")

    report_prefetch = Prefetch(
        "urllistreport_set",
        queryset=UrlListReport.objects.filter(is_publicly_shared=True)
        .order_by("-id")
        .only(
            "id",
            "at_when",
            "report_type",
            "public_share_code",
            "average_internet_nl_score",
            "public_report_code",
            "total_urls",
            "urllist_id",
        ),
        to_attr="reports",
    )

    urllists = (
        UrlList.objects.all()
        .filter(account=account_id, is_deleted=False, enable_report_sharing_page=True)
        .prefetch_related(report_prefetch)
    )

    if urllist_id:
        urllists = urllists.filter(id=urllist_id)

    # log.debug(f"urllists: {urllists}")

    return [
        {
            "list": {
                "id": my_list.id,
                "name": my_list.name,
                "scan_type": my_list.scan_type,
                "automatically_share_new_reports": my_list.automatically_share_new_reports,
                "automated_scan_frequency": my_list.automated_scan_frequency,
            },
            # for future use
            "account": {
                "public_name": "",
            },
            "number_of_reports": len(my_list.reports),
            "reports": [
                {
                    "id": report.id,
                    "at_when": report.at_when,
                    "report_type": report.report_type,
                    # don't send the code, only if there is password protection
                    "has_public_share_code": bool(report.public_share_code),
                    "average_internet_nl_score": report.average_internet_nl_score,
                    "public_report_code": report.public_report_code,
                    "total_urls": report.total_urls,
                    # be compatible with the frontpage report view:
                    "urllist__name": my_list.name,
                }
                for report in my_list.reports
            ],
        }
        for my_list in urllists
    ]
