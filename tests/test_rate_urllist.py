"""
These testcases help to validate the working of the listmanagement API.

Run these tests with tox -e test -- -k test_urllist_management
"""
from datetime import datetime

import pytz
import websecmap
from websecmap.organizations.models import Url
from websecmap.reporting.models import UrlReport
from websecmap.reporting.report import create_timeline, create_url_report
from websecmap.scanners import ALL_SCAN_TYPES
from websecmap.scanners.models import Endpoint, EndpointGenericScan

from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllists_now
from dashboard.internet_nl_dashboard.logic.urllist_management import create_list
from dashboard.internet_nl_dashboard.models import Account, UrlListReport

# mock get_allowed_to_report as constance tries to connect to redis.


def test_rate_urllists(db, monkeypatch) -> None:

    # report everything and don't contact redis for constance values.
    monkeypatch.setattr(websecmap.reporting.report, 'get_allowed_to_report', lambda: ALL_SCAN_TYPES)

    day_0 = datetime(day=1, month=1, year=2000, tzinfo=pytz.utc)
    day_1 = datetime(day=2, month=1, year=2000, tzinfo=pytz.utc)

    account, created = Account.objects.all().get_or_create(name="test")

    list_1 = create_list(account, "test list 1")

    url, created = Url.objects.all().get_or_create(url='test.nl', created_on=day_0, not_resolvable=False)

    first_endpoint, created = Endpoint.objects.all().get_or_create(
        url=url, protocol='https', port='443', ip_version=4, discovered_on=day_1, is_dead=False)

    perfect_scan, created = EndpointGenericScan.objects.all().get_or_create(
        endpoint=first_endpoint, type='tls_qualys_encryption_quality', rating='A+', rating_determined_on=day_1,
        last_scan_moment=day_1, comply_or_explain_is_explained=False, is_the_latest_scan=True)

    # first rate the urls.

    UrlReport.objects.all().delete()
    create_url_report(create_timeline(url), url)

    rate_urllists_now([list_1])

    # We now should have 1 UrlListReport

    assert UrlListReport.objects.all().count() == 1
