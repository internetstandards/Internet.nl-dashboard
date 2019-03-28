import logging

from celery import Task, group

from dashboard.celery import app
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList
from websecmap.organizations.models import Url
from websecmap.scanners.scanner import add_model_filter
from websecmap.scanners.scanner.internet_nl_mail import (get_scan_status,
                                                         handle_running_scan_reponse, register_scan)

# done: create more flexible filters
# done: map mail scans to an endpoint (changed the scanner for it)
# done: make nice tracking name for internet nl that is echoed in the scan results.
# done: map web scans to endpoints
# done: check status of scan using each individual account

log = logging.getLogger(__name__)


API_URL_MAIL = "https://batch.internet.nl/api/batch/v1.0/mail/"
API_URL_WEB = "https://batch.internet.nl/api/batch/v1.0/web/"


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

    tasks = []

    for account in accounts:

        urllists = UrlList.objects.all().filter(account=account, enable_scans=True)
        urllists = add_model_filter(urllists, **kwargs)
        for urllist in urllists:
            """
            Lists are split between their respective capabilities. This means that some urls will be scanned for web,
            some for mail and some not at all.
            """

            urls = Url.objects.all().filter(urls_in_dashboard_list=urllist, is_dead=False, not_resolvable=False,
                                            endpoint__protocol__in=['dns_a_aaaa'])
            urls_for_web_scan = list(set(add_model_filter(urls, **kwargs)))

            if urls_for_web_scan:
                scan_name = "Internet.nl Dashboard, Type: Web, Account: %s, List: %s" % (account.name, urllist.name)

                tasks.append(register_scan.si(
                    urls=urls,
                    username=account.internet_nl_api_username,
                    password=account.decrypt_password(),
                    internet_nl_scan_type='web',
                    api_url=API_URL_WEB,
                    scan_name=scan_name
                ) | connect_scan_to_account.s(account, urllist))

            urls = Url.objects.all().filter(urls_in_dashboard_list=urllist, is_dead=False, not_resolvable=False,
                                            endpoint__protocol__in=['dns_soa'])
            urls_for_mail_scan = list(set(add_model_filter(urls, **kwargs)))

            if urls_for_mail_scan:
                scan_name = "Internet.nl Dashboard, Type: Web, Account: %s, List: %s" % (account.name, urllist.name)

                tasks.append(register_scan.si(
                    urls=urls,
                    username=account.internet_nl_api_username,
                    password=account.decrypt_password(),
                    internet_nl_scan_type='mail_dashboard',
                    api_url=API_URL_MAIL,
                    scan_name=scan_name
                ) | connect_scan_to_account.s(account, urllist))

    return group(tasks)


@app.task(queue='storage')
def check_running_scans():
    """
    Gets status on all running scans from internet, per account.

    :return: None
    """
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
def connect_scan_to_account(scan, account, urllist):

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
