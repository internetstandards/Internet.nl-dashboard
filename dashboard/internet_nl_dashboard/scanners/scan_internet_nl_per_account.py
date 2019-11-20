import logging
from typing import List, Tuple

import requests
from celery import Task, group
from constance import config
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from websecmap.organizations.models import Url
from websecmap.scanners.models import InternetNLScan
from websecmap.scanners.scanner import add_model_filter, dns_endpoints
from websecmap.scanners.scanner.dns_endpoints import compose_discover_task
from websecmap.scanners.scanner.internet_nl_mail import (get_scan_status,
                                                         handle_running_scan_reponse, register_scan)

from dashboard.celery import app
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList, AccountInternetNLScanLog

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

    # Do not scan lists that exceed the maximum number of domains:
    max_urls = config.DASHBOARD_MAXIMUM_DOMAINS_PER_LIST

    for account in accounts:

        urllists = UrlList.objects.all().filter(
            account=account, enable_scans=True, is_deleted=False).annotate(num_urls=Count('urls'))

        urllists = add_model_filter(urllists, **kwargs)
        for urllist in urllists:

            # model_filters may circumvent the restriction we set, therefore we check it this way.
            # (A filter might still overwrite this?)
            if urllist.num_urls > max_urls:
                continue

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


@app.task(queue='storage')
def initialize_scan(account: Account, urllist: UrlList, scan_type: str):
    # todo: Also create the scan and scan name. Create the internet.nl scan and the accountinternetnlscan objects.

    scan_name = "{'source': 'Internet.nl Dashboard', 'type': '%s', 'account': '%s', 'list': '%s'}" % (
        scan_type, account.name, urllist.name)

    internetnlscan = InternetNLScan()
    internetnlscan.type = scan_type
    internetnlscan.save()

    # Should we already create an InternetNL scan? Yes, because the type is saved there.
    accountinternetnlscan = AccountInternetNLScan()
    accountinternetnlscan.account = account
    accountinternetnlscan.urllist = urllist
    accountinternetnlscan.scan = internetnlscan
    accountinternetnlscan.state = "requested"
    accountinternetnlscan.save()

    return internetnlscan, accountinternetnlscan


@app.task(queue='storage')
def monitor_scans() -> Task:
    """
    Collects the next tasks from the mail and web scan monitors. This can be run every second and it will still be fine.

    This is called from the
    :return:
    """

    tasks = []
    scans = AccountInternetNLScan.objects.all().exclude(Q(state="finished scan") | Q(state__startswith="error"))
    for scan in scans:
        if scan.scan.type == "web":
            pass
        if scan.scan.type == "mail":
            tasks.append(monitor_mail_scan(scan))

    return group(tasks)


def monitor_mail_scan(scan: AccountInternetNLScan) -> Task:
    """
    This monitors the state of a mail scan. Depending on the state, it determines if an action is needed and
    gathers them. This will not handle errors.

    This is used in conjunction with Celery: all tasks are performed async, which scales better.

    Steps are split into two: the active verb and the past tense verb. When something is happening, the active verb
    is used, otherwise the past tense verb. Such as: "scanning endpoints" and "scanned endpoints".
        An active verb means that something is currently being performed.
        A completed / past tense verb means that the process is ready to move on.

    All active verbs have a timeout. This timeout can be different for each verb. The timeout is set to a value that
    takes into account the possibility of the system being very busy and all queues full. Therefore, something that
    usually would last 10 seconds, will have a timeout of several hours. If this timeout triggers, there is something
    very wrong: either an unexpected exception stopped the process or there are deadlocks in the queues.
        These timeouts should never be triggered: if they do, it will mean manual intervention to fix a bug etc.

    When a timeout is reached on an active verb, it will change the state to something that is not processed in this
    monitor anymore. Manual action is required, after the manual action has been performed, the person handling it
    can set the state of the failed scan to something this process understands, and we'll happily try again.
        Note that celery can also perform several attempts on exceptions etc, this might or might not happen.
        Timeouts are stored as the following: timeout on [active verb]: timeout on scanning endpoints.

    To prevent duplicate tasks from spawning, this method will adjust the task before the actual content is called.

    This does not use django fsm, as that ties everything to a model. It also overcomplicates the process with
    branching and such. The on-error feature is nice though.

    Mail scans are performed like this:
    n  : requested -> discovering endpoints -> discovered endpoints
                                          -> timeout on ~
                                          -> error on ~: No endpoints found, will result in empty scan. Will retry N x.
                                          -> error on ~: No DNS service available. Will retry N x. (can this be in task)

    n+1: discovered endpoints -> retrieving scannable urls -> retrieved scannable urls

    n+1: retrieved scannable urls -> registering scan at internet.nl -> registered scan at internet.nl
                                                                   -> timeout on ~
                                                                   -> todo: network errors, API errors, not reachable.

    n+1: registered scan at internet.nl -> running scan -> ran scan

    n+1: ran scan -> importing scan results -> imported scan results

    n+1: imported scan results -> creating report -> created report

    n+1: created report -> sending mail -> sent mail

    n+1: sent mail -> finishing scan -> finished scan

    :return:
    """

    """
    It's not possible to safely create a scan automagically: this might be called a few times in a row, and then
    you'll end up with several new scans. Therefore, to initiate a scan, you need to call another method. 
    After the scan is initiated, this will pick it up and continue.
    """
    if not scan:
        return group([])

    # set up some variables:
    relevant_scan_types = {"web": "dns_a_aaaa", "mail": "dns_soa"}

    # always get the latest state, so we'll not have outdated information if we had to wait in a queue a long while.
    # also run this in a transaction, so it's only possible to get a state and update it to an active state once.
    with transaction.atomic():
        scan = AccountInternetNLScan.objects.get(id=scan.id)

        # todo: move state to the websecmap object, so that the new approach can also work in a next version of that sw.
        #  Both the state and the state log ofc.
        state = scan.state

        if state == "requested":
            # Always immediately update the current state, so the amount of double calls is minimal:
            #  "discovered endpoints" to "discovering endpoints" and cause an infinte loop.
            update_state("discovering endpoints", scan)
            return (
                    dns_endpoints.compose_discover_task(**{
                        'urls_filter': {'urls_in_dashboard_list': scan.urllist, 'is_dead': False, 'not_resolvable': False}})
                    | update_state.si("discovered endpoints", scan)
            )

        if state == "discovering endpoints":
            """Check the timeout of this methods. If it takes too long, escalate."""
            # and what if the timeout comes way later because this
            pass

        if state == "discovered endpoints":
            # This step tries to prevent API calls with an empty list of urls.
            update_state("retrieving scannable urls", scan)
            return (
                    get_relevant_urls.si(scan.urllist, relevant_scan_types[scan.scan.type])
                    | check_retrieved_scannable_urls.s()
                    | update_state.s(scan)
            )

        if state == "retrieving scannable urls":
            """Todo: check for timeout."""
            pass

        if state == "retrieved scannable urls":
            update_state("registering scan at internet.nl", scan)

            # retrieving the API urls:
            api_url = config.DASHBOARD_API_URL_WEB_SCANS if scan.scan.type == "web" \
                else config.DASHBOARD_API_URL_MAIL_SCANS

            # todo: register scan does too much, it should just register the scan, and not store things to the db there.
            #  also add refactor that at websecmap.
            return (
                    new_register_scan.si(
                        scan.account.internet_nl_api_username,
                        scan.account.decrypt_password(),
                        api_url)
                    | check_registered_scan_at_internet_nl.s(scan)
                    | update_state.s(scan)
            )

        if state == "registering scan at internet.nl":
            # todo: check for timeout.
            pass

        if state == "registered scan at internet.nl":
            update_state("running scan", scan)
            # todo: implement,
            """
            todo: handle running scan does too much: it handles both if the scan is finished, and creates
            a parallel task to import the results, which is the cause of the report dates being incorrect.
            Split that up in separate steps in this routine.
            get_scan_status.si(scan.status_url, account.internet_nl_api_username, account.decrypt_password())
            | handle_running_scan_reponse.s(scan)
            """




@app.task(queue="storage", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 10},
          retry_jitter=False)
def new_register_scan(urls: List[Url], username, password, api_url: str = "", scan_name: str = "") -> (str, str):
    """
    This registers a scan and results the URL where the scan results can be found later on.
    :return: (message, tracking url)
    """

    """
    POST /api/batch/v1.0/web/ HTTP/1.1
    {
        "name": "My web test",
        "domains": ["dashboard.internet.nl", "websecmap.org"]
    }
    """

    data = {"name": scan_name, "domains": urls}

    # todo: handle all types of network errors. It should auto retry for those... replace exception above.
    answer = requests.post(api_url, json=data, auth=HTTPBasicAuth(username, password), timeout=(300, 300))
    log.debug("Received answer from internet.nl: %s" % answer.content)

    """
    Expected answer:
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
        "success": true,
        "message": "OK",
        "data": {
            "results": "https://batch.internet.nl/api/batch/v1.0/results/01c70c7972e143ffb0c5b45d5b8116cb/"
        }
    }
    """
    answer = answer.json()

    # Makes no sense to retry on an incorrect user. Quit.
    if answer.get("message", None) == "Unknown user":
        return "error: Unknown Internet.nl User. Are the username and password configured for this account?", ""

    # No status url, an unexpected error perhaps?
    status_url = answer.get('data', {}).get('results', "")
    if not status_url:
        return f"error: could not get scanning status url. Response from server: {answer}", ""

    return "Retrieved status successfully!", status_url


@app.task(queue='storage')
def check_registered_scan_at_internet_nl(value, scan):
    # untangle the set
    message, url = value

    if message == "Retrieved status successfully!":
        scan.scan.url = url
        scan.scan.save()
        return "registered scan at internet.nl"

    # all error scenario's will result in an error, which is not a state we can handle, and the process will be stuck
    # there...
    return message


@app.task(queue='storage')
def check_retrieved_scannable_urls(urls: List):
    """ Influences the process, see if we can continue. """
    if not urls:
        return "error retrieving scannable urls: " \
               "no urls to scan found. Will not continue as the report will be empty."

    return "retrieved scannable urls"


@app.task(queue='storage')
def update_state(state, scan):
    """Update the current scan state. Also write it to the scan log. From this log we should also be able to see
    retries... when celery retries on exceptions etc..."""

    scan.state = state
    scan.state_changed_on = timezone.now()
    scan.save()

    scanlog = AccountInternetNLScanLog()
    scanlog.scan = scan
    scanlog.at_when = timezone.now()
    scanlog.state = state
    scanlog.save()


def create_dashboard_scan_task(account: Account, urllist: UrlList, save_as_scan_type: str, endpoint_type: str) -> Task:
    # This is done here, because it will be re-initialized every function call instead of every reboot of the dashboard
    # (as with contants on top in the module). This might not be as efficient, but it saves a django reboot.
    api_url_mail = config.DASHBOARD_API_URL_MAIL_SCANS
    api_url_web = config.DASHBOARD_API_URL_WEB_SCANS

    # The scan name is arbitrary. Add a lot of info to it so the scan can be tracked.
    # A UUID will be added during registering
    scan_name = "{'source': 'Internet.nl Dashboard', 'type': '%s', 'account': '%s', 'list': '%s'}" % (
        save_as_scan_type, account.name, urllist.name)

    api_url = api_url_web if save_as_scan_type == 'web' else api_url_mail

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
