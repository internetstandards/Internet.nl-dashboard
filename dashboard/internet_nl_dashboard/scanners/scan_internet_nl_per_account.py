import logging
from typing import List

from celery import Task, group
from websecmap.organizations.models import Url
from websecmap.scanners.models import InternetNLScan
from websecmap.scanners.scanner import add_model_filter
from websecmap.scanners.scanner.dns_endpoints import compose_discover_task
from websecmap.scanners.scanner.internet_nl_mail import (get_scan_status,
                                                         handle_running_scan_reponse, register_scan)

from dashboard.celery import app
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList

# done: create more flexible filters
# done: map mail scans to an endpoint (changed the scanner for it)
# done: make nice tracking name for internet nl that is echoed in the scan results.
# done: map web scans to endpoints
# done: check status of scan using each individual account
# done: possibly we need to check all relevant endpoints before starting the scan. This makes sure that all
#       latest changes have been picked up. Especially if manual scans will happen a lot. Probably just adding
#       a task before registering a scan. This might deliver some problems as we've seen before, with a chord
#       not being performed after the other task has finished. This might be a bit challenging.
#       Indeed: a chord does not work. A chain might. We can verify url filters when there is a larger set of domains.
#       Done: How do we get the correct list of urls at the time we're going to scan? We've to make that a task too.
#       Done: This is done using chains, where each step is executed in order.
# done: create a function for this, as it is twice the same code.
# todo: probably the urllist will contain information if a scan will be done for web or mail. This cannot be managed
#       yet, so this is not implemented yet.

log = logging.getLogger(__name__)


API_URL_MAIL = "https://batch.internet.nl/api/batch/v1.1/mail/"
API_URL_WEB = "https://batch.internet.nl/api/batch/v1.1/web/"


def compose_task(
    **kwargs
) -> Task:

    accounts = Account.objects.all().filter(
        enable_scans=True,
        internet_nl_api_username__isnull=False,
        internet_nl_api_password__isnull=False,
    )
    accounts = add_model_filter(accounts, **kwargs)

    # Then get all the lists. And create a scan per list.
    # The requirement for a 'per list' comes from the idea to be able to see what account uses what urls in the
    # back end.

    tasks: List[Task] = []

    for account in accounts:

        urllists = UrlList.objects.all().filter(account=account, enable_scans=True, is_deleted=False)
        urllists = add_model_filter(urllists, **kwargs)
        for urllist in urllists:
            tasks.append(create_dashboard_scan_tasks(urllist))

    return group(tasks)


@app.task(queue='storage')
def create_dashboard_scan_tasks(urllist):
    # No urls means that the scan will not be registered in the API. So that would be a useless call.
    if urllist.urls.count() == 0:
        return group([])

    tasks = []
    """
    Lists are split between their respective capabilities. This means that some urls will be scanned for web,
    some for mail and some both depending on the list content.
    """

    if urllist.scan_type == 'web':
        tasks.append(create_dashboard_scan_task(urllist.account, urllist, 'web', 'dns_a_aaaa'))

    if urllist.scan_type == 'mail':
        tasks.append(create_dashboard_scan_task(urllist.account, urllist, 'mail_dashboard', 'dns_soa'))

    return group(tasks)


def create_dashboard_scan_task(account: Account, urllist: UrlList, save_as_scan_type: str, endpoint_type: str) -> Task:

    # The scan name is arbitrary. Add a lot of info to it so the scan can be tracked.
    # A UUID will be added during registering
    scan_name = "{'source': 'Internet.nl Dashboard', 'type': '%s', 'account': '%s', 'list': '%s'}" % (
        save_as_scan_type, account.name, urllist.name)

    api_url = API_URL_WEB if save_as_scan_type == 'web' else API_URL_MAIL

    return (
        # Should we only try to get the specifically needed dns_endpoint? At what volume we should / must?
        # This discovers dns_endpoints. On the basis of this we know what urls we should scan an which
        # ones we should not. We'll only scan if there are valid endpoint, just like at internet.nl
        compose_discover_task(**{'urls_filter': {'urls_in_dashboard_list': urllist,
                                                 'is_dead': False, 'not_resolvable': False}})

        # Make sure that the discovery as listed above is actually used in the scan
        | get_relevant_urls.si(urllist, endpoint_type)

        # The urls are registered as part of the scan
        | register_scan.s(
            account.internet_nl_api_username,
            account.decrypt_password(),
            save_as_scan_type,
            api_url,
            scan_name)

        # When the scan is created, the scan is connected to the account for tracking purposes.
        # This is visualized in the scan monitor.
        | connect_scan_to_account.s(account, urllist))


@app.task(queue='storage')
def get_relevant_urls(urllist: UrlList, protocol: str, **kwargs) -> List:
    urls = Url.objects.all().filter(urls_in_dashboard_list=urllist, is_dead=False, not_resolvable=False,
                                    endpoint__protocol__in=[protocol])
    return list(set(add_model_filter(urls, **kwargs)))


@app.task(queue='storage')
def check_running_dashboard_scans(**kwargs) -> Task:
    """
    Gets status on all running scans from internet, per account.

    :return: None
    """
    if kwargs:
        account_scans = AccountInternetNLScan.objects.all()
        account_scans = add_model_filter(account_scans, **kwargs)
    else:
        account_scans = AccountInternetNLScan.objects.all().filter(scan__finished=False)

    tasks = []
    for account_scan in account_scans:
        scan = account_scan.scan
        account = account_scan.account

        tasks.append(
            get_scan_status.si(scan.status_url, account.internet_nl_api_username, account.decrypt_password())
            | handle_running_scan_reponse.s(scan)
        )

    return group(tasks)


@app.task(queue='storage')
def connect_scan_to_account(scan: InternetNLScan, account: Account, urllist: UrlList) -> AccountInternetNLScan:

    if not scan:
        raise ValueError('Scan is empty')

    if not account:
        raise ValueError('Account is empty')

    if not urllist:
        raise ValueError('Urllist is empty')

    scan_relation = AccountInternetNLScan()
    scan_relation.account = account
    scan_relation.scan = scan
    scan_relation.urllist = urllist
    scan_relation.save()

    return scan_relation
