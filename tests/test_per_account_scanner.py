"""
These testcases make sure we can create scans.

Run these tests with tox -e test -- -k test_per_acount_scanner
"""
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint

from dashboard.internet_nl_dashboard.models import Account, UrlList
from dashboard.internet_nl_dashboard.scanners.web_per_account import compose_task


def test_per_acount_scanner(db) -> None:
    account, created = Account.objects.all().get_or_create(name="test",
                                                           internet_nl_api_username='test',
                                                           internet_nl_api_password='test',)

    # some test urls
    urls = [
        Url.objects.all().get_or_create(url='www.internet.nl', is_dead=False, not_resolvable=False),
        Url.objects.all().get_or_create(url='internet.nl', is_dead=False, not_resolvable=False),
        Url.objects.all().get_or_create(url='nu.nl', is_dead=False, not_resolvable=False)
    ]

    # make sure there are endpoints for these urls, as without endpoints, no scans will happen
    Endpoint(**{'url': urls[0], 'protocol': 'soa_mx', 'port': 25, 'ip_version': 4, 'is_dead': False})
    Endpoint(**{'url': urls[1], 'protocol': 'soa_mx', 'port': 25, 'ip_version': 4, 'is_dead': False})

    # a set of standard endpoints
    Endpoint(**{'url': urls[0], 'protocol': 'http', 'port': 80, 'ip_version': 4, 'is_dead': False})
    Endpoint(**{'url': urls[0], 'protocol': 'https', 'port': 443, 'ip_version': 4, 'is_dead': False})
    Endpoint(**{'url': urls[0], 'protocol': 'http', 'port': 80, 'ip_version': 6, 'is_dead': False})
    Endpoint(**{'url': urls[0], 'protocol': 'https', 'port': 443, 'ip_version': 6, 'is_dead': False})
    Endpoint(**{'url': urls[1], 'protocol': 'http', 'port': 80, 'ip_version': 4, 'is_dead': False})
    Endpoint(**{'url': urls[1], 'protocol': 'https', 'port': 443, 'ip_version': 4, 'is_dead': False})
    Endpoint(**{'url': urls[1], 'protocol': 'http', 'port': 80, 'ip_version': 6, 'is_dead': False})
    Endpoint(**{'url': urls[1], 'protocol': 'https', 'port': 443, 'ip_version': 6, 'is_dead': False})

    # create an url list for this account:
    UrlList.objects.all().get_or_create(name='test', account=account, urls=urls)

    # When filtering for an existing account, as created above, a single scan task should be created for this account.
    filters = {'account_filters': {'name': 'test'}}
    # web_per_account
    scan_tasks = compose_task(**filters)
    assert len(scan_tasks) == 1

    # This should not result in any scans, as the account does not exist
    filters = {'account_filters': {'name': 'not existing'}}
    # web_per_account
    scan_tasks = compose_task(**filters)
    assert len(scan_tasks) == 0
