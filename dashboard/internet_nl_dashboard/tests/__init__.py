from datetime import datetime

import pytz
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, EndpointGenericScan, InternetNLV2Scan

from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllists_now
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList


def make_url_with_endpoint_and_scan():
    # Todo: should this just be a fixture?

    day_0 = datetime(day=1, month=1, year=2000, tzinfo=pytz.utc)
    day_1 = datetime(day=2, month=1, year=2000, tzinfo=pytz.utc)

    account, created = Account.objects.all().get_or_create(name="test")

    url, created = Url.objects.all().get_or_create(url='test.nl', created_on=day_0, not_resolvable=False)

    endpoint, created = Endpoint.objects.all().get_or_create(
        url=url, protocol='https', port='443', ip_version=4, discovered_on=day_1, is_dead=False)

    scan, created = EndpointGenericScan.objects.all().get_or_create(
        endpoint=endpoint, type='tls_qualys_encryption_quality', rating='A+', rating_determined_on=day_1,
        last_scan_moment=day_1, comply_or_explain_is_explained=False, is_the_latest_scan=True)

    return account, url, endpoint, scan


def create_scan_report(account: Account, urllist: UrlList):
    rate_urllists_now([urllist])

    # create a scan for this list,
    scan, created = InternetNLV2Scan.objects.all().get_or_create(
        pk=1, type='web', state="finished")

    ainls = AccountInternetNLScan()
    ainls.account = account
    ainls.urllist = urllist
    ainls.scan = scan
    scan.finished = True
    scan.finished_on = timezone.now()
    ainls.save()

    rate_urllists_now.si(urllist, prevent_duplicates=False)
