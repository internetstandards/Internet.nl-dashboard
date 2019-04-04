"""
These testcases make sure we can create scans.

Run these tests with tox -e test -- -k test_per_acount_scanner
"""
import logging

from dashboard.internet_nl_dashboard.models import Account, UrlList
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import compose_task
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint

log = logging.getLogger('test')


def test_per_acount_scanner(db) -> None:
    account, created = Account.objects.all().get_or_create(name="test",
                                                           internet_nl_api_username='test',
                                                           internet_nl_api_password=Account.encrypt_password('test'),)

    # some test urls
    url1, created = Url.objects.all().get_or_create(url='www.internet.nl', is_dead=False, not_resolvable=False)
    url2, created = Url.objects.all().get_or_create(url='internet.nl', is_dead=False, not_resolvable=False)
    url3, created = Url.objects.all().get_or_create(url='nu.nl', is_dead=False, not_resolvable=False)

    urls = [url1, url2, url3]

    # a set of standard endpoints
    ep = Endpoint(**{'url': urls[0], 'protocol': 'dns_a_aaaa', 'port': 0, 'ip_version': 0, 'is_dead': False})
    ep.save()
    ep = Endpoint(**{'url': urls[1], 'protocol': 'dns_soa', 'port': 0, 'ip_version': 0, 'is_dead': False})
    ep.save()

    # create an url list for this account:
    urllist, created = UrlList.objects.all().get_or_create(name='test', account=account, scan_type='web')

    for url in urls:
        urllist.urls.add(url)
        urllist.save()

    # When filtering for an existing account, as created above, there should be two tasks created.
    filters = {'account_filters': {'name': 'test'}}
    scan_tasks = compose_task(**filters)
    # two tasks: one for mail_dashboard, one for web, no type delivers one task but no content (should improve test).
    assert len(scan_tasks.kwargs.get('tasks')) == 1

    # This should not result in any scans, as the account does not exist, an empty group is returned.
    filters = {'account_filters': {'name': 'not existing'}}
    scan_tasks = compose_task(**filters)
    log.debug(scan_tasks)
    assert scan_tasks.kwargs.get('tasks') == []
