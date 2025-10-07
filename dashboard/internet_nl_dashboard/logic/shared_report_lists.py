from typing import Dict, List, Optional

from django.db.models import Prefetch
from ninja import Schema

from dashboard.internet_nl_dashboard import log
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport


class SharedListSchema(Schema):
    id: int
    name: str
    scan_type: str
    automatically_share_new_reports: bool
    automated_scan_frequency: str


class PubliclySharedReportSchema(Schema):
    id: int
    at_when: str
    report_type: str
    has_public_share_code: bool
    average_internet_nl_score: float
    public_report_code: str
    total_urls: int
    # Keep compatibility with existing frontend key
    urllist__name: str


class PubliclySharedListResponseSchema(Schema):
    list: SharedListSchema
    # For future use; keeping structure compatible
    account: Dict[str, str]
    number_of_reports: int
    reports: List[PubliclySharedReportSchema]


class LatestReportCodeSchema(Schema):
    latest_report_public_report_code: str


def get_latest_report_id_from_list_and_type(urllist_id: int, report_type: str = "") -> LatestReportCodeSchema:
    report = UrlListReport.objects.filter(urllist=urllist_id, is_publicly_shared=True)

    if report_type in {"web", "mail"}:
        report = report.filter(report_type=report_type)

    found_report = report.last()

    return (
        LatestReportCodeSchema(latest_report_public_report_code=found_report.public_report_code)
        if found_report
        else LatestReportCodeSchema(latest_report_public_report_code="")
    )


def get_publicly_shared_lists_per_account_and_list_id(
    account_id: int, urllist_id: int
) -> List[PubliclySharedListResponseSchema]:
    return get_publicly_shared_lists_per_account(account_id, urllist_id)


def get_publicly_shared_lists_per_account(
    account_id, urllist_id: Optional[int] = None
) -> List[PubliclySharedListResponseSchema]:

    log.debug("get_publicly_shared_lists_per_account account_id: %s", account_id)

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
        PubliclySharedListResponseSchema(
            list=SharedListSchema(
                id=my_list.id,
                name=my_list.name,
                scan_type=my_list.scan_type,
                automatically_share_new_reports=my_list.automatically_share_new_reports,
                automated_scan_frequency=my_list.automated_scan_frequency,
            ),
            account={"public_name": ""},
            number_of_reports=len(my_list.reports),
            reports=[
                PubliclySharedReportSchema(
                    id=report.id,
                    at_when=report.at_when.isoformat() if hasattr(report.at_when, "isoformat") else str(report.at_when),
                    report_type=report.report_type,
                    has_public_share_code=bool(report.public_share_code),
                    average_internet_nl_score=report.average_internet_nl_score,
                    public_report_code=report.public_report_code,
                    total_urls=report.total_urls,
                    urllist__name=my_list.name,
                )
                for report in my_list.reports
            ],
        )
        for my_list in urllists
    ]
