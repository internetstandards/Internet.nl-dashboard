from datetime import datetime, timezone

from constance.test import override_config

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport
from dashboard.internet_nl_dashboard.tasks import autoshare_report_to_front_page


@override_config(DASHBOARD_FRONT_PAGE_URL_LISTS="1,2")
def test_autoshare_report_to_front_page(db):
    # setup a shared and unshared report
    account = Account.objects.create(pk="1")
    urllist1 = UrlList.objects.create(pk="1", account=account)
    urllist3 = UrlList.objects.create(pk="3", account=account)
    report1 = UrlListReport.objects.create(urllist=urllist1, at_when=datetime.now(timezone.utc))
    report3 = UrlListReport.objects.create(urllist=urllist3, at_when=datetime.now(timezone.utc))
    assert report1.is_publicly_shared is False
    assert report1.is_shared_on_homepage is False

    autoshare_report_to_front_page()

    # should be automatically shared
    report = UrlListReport.objects.all().get(pk=report1.pk)
    assert report.is_publicly_shared is True
    assert report.is_shared_on_homepage is True

    # 1 and 2 are not in the config override thus are not shared.
    report = UrlListReport.objects.all().get(pk=report3.pk)
    assert report.is_publicly_shared is False
    assert report.is_shared_on_homepage is False
