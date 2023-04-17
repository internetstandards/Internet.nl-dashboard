# SPDX-License-Identifier: Apache-2.0
from websecmap.reporting.report import create_url_reports

from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist, get_or_create_list_by_name
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllists_now
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.tests import make_url_with_endpoint_and_scan


def test_rate_urllists_now(db) -> None:  # pylint: disable=invalid-name, unused-argument
    account, url, _, _ = make_url_with_endpoint_and_scan()
    my_list = get_or_create_list_by_name(account, name="test list 1", scan_type="mail")
    _add_to_urls_to_urllist(account, my_list, [url])

    # first rate the urls.
    create_url_reports(url)
    rate_urllists_now([my_list], True, my_list.scan_type)

    # We now should have 1 UrlListReport
    assert UrlListReport.objects.all().count() == 1
    urllistreport = UrlListReport.objects.first()
    assert urllistreport.report_type == "mail"


#     UrlListReport.objects.all().delete()
#
#     # Then create a scan, in such a state that it cannot create a report:
#     # In this case there is no scan for this list at all. Should not result in any report.
#     create_reports_on_finished_scans(list)
#     assert UrlListReport.objects.all().count() == 0
#
#     # create a scan for this list,
#     scan, created = InternetNLScan.objects.all().get_or_create(
#         pk=1, type='web', success=False, started=False, finished=False)
#
#     ainls = AccountInternetNLScan()
#     ainls.account = account
#     ainls.urllist = list
#     ainls.scan = scan
#     ainls.save()
#
#     # scan has not finished yet, so no reports:
#     create_reports_on_finished_scans(list)
#     assert UrlListReport.objects.all().count() == 0
#
#     scan.finished = True
#     scan.save()
#
#     # While the scan has finished, the finished_on field is not set. This means that the results from the report have
#     # not yet been parsed.
#     create_reports_on_finished_scans(list)
#     assert UrlListReport.objects.all().count() == 0
#
#     scan.finished_on = timezone.now()
#     scan.save()
#
#     # finished on is set, so we can make a report now...
#     create_reports_on_finished_scans(list)
#     assert UrlListReport.objects.all().count() == 1
