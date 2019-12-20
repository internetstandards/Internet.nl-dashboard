"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test -- -k test_urllist_management
"""
"""
Disabled test because of refactoring, some methods have been removed.

import websecmap
from django.utils import timezone
from websecmap.reporting.models import UrlReport
from websecmap.reporting.report import create_timeline, create_url_report
from websecmap.scanners import ALL_SCAN_TYPES
from websecmap.scanners.models import InternetNLScan

from dashboard.internet_nl_dashboard.logic.domains import (_add_to_urls_to_urllist,
                                                           get_or_create_list_by_name)
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllists_now
from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlListReport
from dashboard.internet_nl_dashboard.tasks import create_reports_on_finished_scans
from dashboard.internet_nl_dashboard.tests import make_url_with_endpoint_and_scan


def test_rate_urllists(db, monkeypatch) -> None:

    # mock get_allowed_to_report as constance tries to connect to redis.
    # report everything and don't contact redis for constance values.
    monkeypatch.setattr(websecmap.reporting.report, 'get_allowed_to_report', lambda: ALL_SCAN_TYPES)

    account, url, endpoint, scan = make_url_with_endpoint_and_scan()

    list = get_or_create_list_by_name(account, "test list 1")
    _add_to_urls_to_urllist(account, list, [url])

    # first rate the urls.
    UrlReport.objects.all().delete()
    create_url_report(create_timeline(url), url)

    rate_urllists_now([list])

    # We now should have 1 UrlListReport
    assert UrlListReport.objects.all().count() == 1

    #
    #
    #
    #
    # Now test on the creation of reports on finished scans.
    #
    #
    #
    #
    UrlListReport.objects.all().delete()

    # Then create a scan, in such a state that it cannot create a report:
    # In this case there is no scan for this list at all. Should not result in any report.
    create_reports_on_finished_scans(list)
    assert UrlListReport.objects.all().count() == 0

    # create a scan for this list,
    scan, created = InternetNLScan.objects.all().get_or_create(
        pk=1, type='web', success=False, started=False, finished=False)

    ainls = AccountInternetNLScan()
    ainls.account = account
    ainls.urllist = list
    ainls.scan = scan
    ainls.save()

    # scan has not finished yet, so no reports:
    create_reports_on_finished_scans(list)
    assert UrlListReport.objects.all().count() == 0

    scan.finished = True
    scan.save()

    # While the scan has finished, the finished_on field is not set. This means that the results from the report have
    # not yet been parsed.
    create_reports_on_finished_scans(list)
    assert UrlListReport.objects.all().count() == 0

    scan.finished_on = timezone.now()
    scan.save()

    # finished on is set, so we can make a report now...
    create_reports_on_finished_scans(list)
    assert UrlListReport.objects.all().count() == 1
"""