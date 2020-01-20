import json
import logging
from datetime import timedelta
from typing import List

import requests
from celery import Task, group
from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from websecmap.organizations.models import Url
from websecmap.reporting.report import recreate_url_reports
from websecmap.scanners.models import InternetNLScan
from websecmap.scanners.scanner import add_model_filter, dns_endpoints
from websecmap.scanners.scanner.internet_nl_mail import store

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic.report import (add_keyed_ratings,
                                                          add_percentages_to_statistics,
                                                          add_statistics_over_ratings,
                                                          remove_comply_or_explain)
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import create_dashboard_report
from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan,
                                                    AccountInternetNLScanLog, UrlList,
                                                    UrlListReport)

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
# Todo: add the scan ID to the report, so it's easier to find which scan is what. Is that possible?

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

            tasks.append(initialize_scan.si(urllist))

    return group(tasks)


@app.task(queue='storage')
def initialize_scan(urllist: UrlList):
    internetnlscan = InternetNLScan()

    # mail = websecmap, mail_dashboard = internet.nl dashboard, web is the same on both.
    translated_scan_types = {'web': 'web', 'mail': 'mail_dashboard'}
    internetnlscan.type = translated_scan_types[urllist.scan_type]
    internetnlscan.started_on = timezone.now()
    internetnlscan.last_check = timezone.now()  # more like: last update / pulse
    internetnlscan.started = True  # This field is now useless :)
    internetnlscan.save()

    # Should we already create an InternetNL scan? Yes, because the type is saved there.
    accountinternetnlscan = AccountInternetNLScan()
    accountinternetnlscan.account = urllist.account
    accountinternetnlscan.urllist = urllist
    accountinternetnlscan.scan = internetnlscan
    accountinternetnlscan.state = ""
    accountinternetnlscan.save()

    # and start the process.
    update_state("requested", accountinternetnlscan)

    return internetnlscan, accountinternetnlscan


@app.task(queue='storage')
def check_running_dashboard_scans(**kwargs) -> Task:
    """
    Gets status on all running scans from internet, per account.

    :return: None
    """
    if kwargs:
        scans = AccountInternetNLScan.objects.all()
        scans = add_model_filter(scans, **kwargs)
    else:
        scans = AccountInternetNLScan.objects.all().exclude(
            Q(state="finished")
            | Q(state__startswith="error")
            | Q(state__startswith="cancelled"))

    log.debug(f"Checking the state of scan {scans}.")
    tasks = [progress_running_scan(scan) for scan in scans]

    return group(tasks)


def progress_running_scan(scan: AccountInternetNLScan) -> Task:
    """
    This monitors the state of a dashboard scan. Depending on the state, it determines if an action is needed and
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

    :return:
    """

    """
    It's not possible to safely create a scan automagically: this might be called a few times in a row, and then
    you'll end up with several new scans. Therefore, to initiate a scan, you need to call another method.
    After the scan is initiated, this will pick it up and continue.
    """
    if not scan:
        return group([])

    steps = {
        # complete state progression, using active verbs to come to the next state:
        "requested": discovering_endpoints,
        "discovered endpoints": retrieving_scannable_urls,
        "retrieved scannable urls": registering_scan_at_internet_nl,
        "registered scan at internet.nl": running_scan,
        "ran scan": importing_scan_results,
        "imported scan results": creating_report,
        "created report": sending_mail,
        "sent mail": finishing_scan,
        "skipped sending mail: no e-mail addresses associated with account": finishing_scan,
        "skipped sending mail: no mail server configured": finishing_scan,
        # "finished"

        # support some nested state from the internet.nl API
        "running scan": running_scan,
        "running scan: preparing scan": continue_running_scan,
        "running scan: gathering data": continue_running_scan,
        "running scan: preparing results": continue_running_scan,

        # monitors on active states:
        "discovering endpoints": monitor_timeout,
        "retrieving scannable urls": monitor_timeout,
        "registering scan at internet.nl": monitor_timeout,
        "importing scan results": monitor_timeout,
        "creating report": monitor_timeout,
        "sending mail": monitor_timeout,
    }

    with transaction.atomic():
        # always get the latest state, so we'll not have outdated information if we had to wait in a queue a long while.
        # also run this in a transaction, so it's only possible to get a state and update it to an active state once.
        scan = AccountInternetNLScan.objects.get(id=scan.id)
        next_step = steps.get(scan.state, handle_unknown_state)
        return next_step(scan)


def handle_unknown_state(scan):
    # probably nothing to be done...
    return group([])


def discovering_endpoints(scan: AccountInternetNLScan):
    # Always immediately update the current state, so the amount of double calls is minimal:
    #  "discovered endpoints" to "discovering endpoints" and cause an infinte loop.
    update_state("discovering endpoints", scan)
    return (
        dns_endpoints.compose_discover_task(**{
            'urls_filter': {'urls_in_dashboard_list': scan.urllist, 'is_dead': False, 'not_resolvable': False}})
        | update_state.si("discovered endpoints", scan)
    )


def retrieving_scannable_urls(scan: AccountInternetNLScan):
    # This step tries to prevent API calls with an empty list of urls.
    update_state("retrieving scannable urls", scan)
    relevant_scan_types = {"web": "dns_a_aaaa", "mail_dashboard": "dns_soa"}

    return (
        get_relevant_urls.si(scan.urllist, relevant_scan_types[scan.scan.type])
        | check_retrieved_scannable_urls.s()
        | update_state.s(scan)
    )


def registering_scan_at_internet_nl(scan: AccountInternetNLScan):
    update_state("registering scan at internet.nl", scan)

    # retrieving the API urls:
    api_url = config.DASHBOARD_API_URL_WEB_SCANS if scan.scan.type == "web" \
        else config.DASHBOARD_API_URL_MAIL_SCANS

    # todo: Also create the scan and scan name, next to the API version in the websecmap object.
    scan_name = {'source': 'Internet.nl Dashboard',
                 'type': scan.scan.type,
                 'account': scan.account.name,
                 'list': scan.urllist.name}

    relevant_scan_types = {"web": "dns_a_aaaa", "mail_dashboard": "dns_soa"}

    return (
        get_relevant_urls.si(scan.urllist, relevant_scan_types[scan.scan.type])
        | new_register_scan.s(
            scan.account.internet_nl_api_username,
            scan.account.decrypt_password(),
            api_url,
            json.dumps(scan_name))
        | check_registered_scan_at_internet_nl.s(scan)
        | update_state.s(scan)
    )


def running_scan(scan: AccountInternetNLScan):
    update_state("running scan", scan)

    return (get_scan_status_new.si(
        scan.account.internet_nl_api_username,
        scan.account.decrypt_password(),
        scan.scan.status_url)
        | update_state.s(scan))


def continue_running_scan(scan: AccountInternetNLScan):
    """
    Same as running scan, but will not set the state to "running scan" to prevent log spamming.
    """

    return (get_scan_status_new.si(
        scan.account.internet_nl_api_username,
        scan.account.decrypt_password(),
        scan.scan.status_url)
        | update_state.s(scan))


def importing_scan_results(scan: AccountInternetNLScan):
    update_state("importing scan results", scan)

    return (retrieve_data.s(
        scan.account.internet_nl_api_username,
        scan.account.decrypt_password(),
        scan.scan.status_url)
        | store.s(scan.scan.type)
        | update_state.si("imported scan results", scan))


def creating_report(scan: AccountInternetNLScan):
    update_state("creating report", scan)

    # Note that calling 'timezone.now()' at canvas creation time, means that you'll have a date in the past
    # at the moment the function is actually called. If you need accurate time in the function, make sure the
    # function calls 'timezone.now()' when the function is run.
    return (recreate_url_reports.si(list(scan.urllist.urls.all()))
            | create_dashboard_report.si(scan.urllist)
            | connect_urllistreport_to_accountinternetnlscan.s(scan)
            | upgrade_report_with_statistics.s()
            | upgrade_report_with_unscannable_urls.s(scan)
            | update_state.si("created report", scan))


def sending_mail(scan: AccountInternetNLScan):
    update_state("sending mail", scan)

    return (send_after_scan_mail.si(scan)
            | update_state.s(scan))


def finishing_scan(scan: AccountInternetNLScan):
    # No further actions, so not setting "finishing scan" as a state, but set it to "scan finished" directly.
    scan.scan.finished_on = timezone.now()
    scan.scan.finished = True
    scan.scan.success = True  # This is not used anymore.
    scan.scan.save()

    update_state("finished", scan)
    return group([])


def monitor_timeout(scan):
    """
    A timeout is set for a day. If the same state is static for 24 hours, the scan will be set to the previous state.
    Except when a scan is requested: the scan might be so large, and the time to process it might be so high,
    we will accept three days of timeout.

    :param scan:
    :return:
    """

    recovering_strategies = {
        "discovering endpoints":
            {"timeout in minutes": 24 * 60, "state after timeout": "requested"},
        "retrieving scannable urls":
            {"timeout in minutes": 24 * 60, "state after timeout": "discovered endpoints"},
        "registering scan at internet.nl":
            {"timeout in minutes": 24 * 60, "state after timeout": "retrieved scannable urls"},
        "importing scan results":
            {"timeout in minutes": 24 * 60, "state after timeout": "ran scan"},
        "creating report":
            {"timeout in minutes": 24 * 60, "state after timeout": "imported scan results"},
        "sending mail":
            {"timeout in minutes": 24 * 60, "state after timeout": "created report"},
    }

    strategy = recovering_strategies.get(scan.state, {})
    if not strategy:
        # Trying to monitor something we don't know. Raise exception, we only want to handle known states.
        raise ValueError(f"Scan is at {scan.state} for which no recovery is defined.")

    # determine if there is an actual timeout.
    scan_will_timeout_on = scan.state_changed_on + timedelta(minutes=strategy['timeout in minutes'])
    if timezone.now() > scan_will_timeout_on:
        update_state(f"timeout reached for: '{scan.state}', performing recovery to '{strategy['state after timeout']}'",
                     scan)
        update_state(strategy['state after timeout'], scan)

    # No further work to do...
    return group([])


@app.task(queue="storage", autoretry_for=(requests.RequestException, ),
          retry_backoff=True,
          retry_kwargs={'max_retries': 10},
          retry_jitter=False)
def retrieve_data(username, password, api_url):
    # 300 seconds, because the report could be HUGE and internet could be slow.
    response = requests.get(api_url, auth=HTTPBasicAuth(username, password), timeout=(300, 300))
    return response.json()


@app.task(queue="storage", autoretry_for=(requests.RequestException, ),
          retry_backoff=True,
          retry_kwargs={'max_retries': 10},
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


@app.task(queue="storage", autoretry_for=(requests.RequestException, ),
          retry_backoff=True,
          retry_kwargs={'max_retries': 10},
          retry_jitter=False)
def get_scan_status_new(username, password, api_url):
    # 300 seconds, because the report could be HUGE and internet could be slow.
    response = requests.get(api_url, auth=HTTPBasicAuth(username, password), timeout=(300, 300))

    if response.status_code != 200:
        return f"error: running scan: received a {response.status_code} status code instead of 200. Is the scan " \
               f"service malfunctioning?"

    try:
        response = response.json()
    except ValueError:
        return "error: running scan: could not read json from the API. Is the API running well?"

    """
    From: https://github.com/NLnetLabs/Internet.nl/blob/4380e9d4fac3ee8e851abc6bc71a29b9c71d3006/checks/batch/views.py

    The normal process:                         State set to:

    - Batch request is registering domains      running scan: preparing scan
    - Batch request is running                  running scan: gathering data
    - Report is being generated                 running scan: preparing results
    - OK                                        ran scan

    Errors:
    All errors are returned verbatim with "error: running scan: " prepended.

    - Unknown batch request                     error: running scan: Unknown batch request
    - Error while registering the domains       running scan: Error whihle registering
    - Results could not be generated            ...
    - Batch request was cancelled by user       ...
    - Problem parsing domains                   ...
    """

    if "message" not in response:
        return "error: running scan: no message found in response."

    positive_responses = {
        "Batch request is registering domains": "running scan: preparing scan",
        "Batch request is running": "running scan: gathering data",
        "Report is being generated": "running scan: preparing results",
        "OK": "ran scan"
    }

    positive_response = positive_responses.get(response['message'], "")

    if positive_response:

        # All intermediate states have the success==false:
        if response['success'] is False:
            return positive_response

        # A completed scan has success==true, and will also have the message 'OK' and will have a list of domains

        if positive_response == "ran scan":
            # Validate the positive response, to at least contain a single domain.
            # Negative responses don't contain domains.
            domains = response.get('data', {}).get('domains', {})
            if not domains:
                return "error: running scan: scan completed without useful data. Did the scan start on an empty list?"

            return positive_response

        # handle success==true, with a positive response, which would be wrong.
        return f"error: running scan: " \
               f"scan was received as successful, but the message associated with it was wrong: {positive_response}"

    negative_responses = {
        "Unknown batch request": "error: running scan: unknown batch request",
        "Error while registering the domains": "error: running scan: error while registering the domains",
        "Results could not be generated": "error: running scan: results could not be generated",
        "Batch request was cancelled by user": "error: running scan: batch request was cancelled by user",
        "Problem parsing domains": "error: running scan: problem parsing domains",
    }

    negative_response = negative_responses.get(response['message'], "")

    if negative_response:
        return negative_response

    # These are really unexpected results.
    return f"error: running scan: unexpected error with data: {response['message']}"


@app.task(queue='storage')
def connect_urllistreport_to_accountinternetnlscan(urllistreport: UrlListReport, scan: AccountInternetNLScan):
    scan.report = urllistreport
    scan.save()

    return urllistreport


@app.task(queue='storage')
def upgrade_report_with_statistics(urllistreport: UrlListReport):
    # todo: also upgrade existing reports and store them, this also speeds up report retrieval

    remove_comply_or_explain(urllistreport)
    add_keyed_ratings(urllistreport)
    add_statistics_over_ratings(urllistreport)
    add_percentages_to_statistics(urllistreport)

    return UrlListReport.objects.all().get(pk=urllistreport.pk)


@app.task(queue='storage')
def upgrade_report_with_unscannable_urls(urllistreport: UrlListReport, scan: AccountInternetNLScan):
    """
    Urls that cannot be scanned using the internet.nl website are not allowed to be scanned. This is where endpoint
    detection comes into view. Only domains with valid endpoints are (should) be scanned. Other domains have to
    be ignored.

    Yet, when we publish a list of "top 500" domains, only 499 show up in the report. This is due to a number of
    complications.

    1: some domains show up where it is stated that the requirements for scanning where not met. Yet, somehow,
    this domain is in the report while it shouldn't be. This seems to be a bug in the reporting engine (todo) that
    tries to retrieve all results, and if the domain has another endpoint, it is added to the report (alas empty).
    These empty domains are accounted for, and are displayed correctly in the report as being ignored.

    2: some domains do not have any endpoints, such as megaupload.com. Also these should not be scanned.
    These domains however short be reflected in the report, the same as the domains that have a single endpoint.

    To account for these issues, after report generation an extra step is needed that upgrades the report. (There
    already is report upgrading code.) The upgrade will check if all domains are in the report, and if not, add
    the url as being empty. This way all urls that are requested are in the report, and if they are empty, they
    are ignored in all statistics.

    :param urllist:
    :param protocol:
    :return:
    """

    # See if all urls in the list are also mentioned in the report, if not, add them and also make sure the stats
    # for the report are correct(!). This means all unscannable domains _will_ be in the report, as that matches
    # the list of domains to scan. (todo: also add an "unreachable" stat to the report / stats to the report).

    urls_in_report: List[str] = [url['url'] for url in urllistreport.calculation['urls']]
    urls_in_list: List[Url] = list(scan.urllist.urls.all())
    urls_not_in_report = [url.url for url in urls_in_list if url.url not in urls_in_report]

    # An empty url looks like this:
    empty_url_template = {
        "url": "",
        "ratings": [],
        "endpoints": [],
        "total_issues": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "ok": 0,
        "total_endpoints": 0,
        "high_endpoints": 0,
        "medium_endpoints": 0,
        "low_endpoints": 0,
        "ok_endpoints": 0,
        "total_url_issues": 0,
        "url_issues_high": 0,
        "url_issues_medium": 0,
        "url_issues_low": 0,
        "url_ok": 0,
        "total_endpoint_issues": 0,
        "endpoint_issues_high": 0,
        "endpoint_issues_medium": 0,
        "endpoint_issues_low": 0,
    }

    for url_not_in_report in urls_not_in_report:
        # log.debug(f"{url_not_in_report} not present")
        empty_url_template['url'] = url_not_in_report
        urllistreport.calculation['urls'].append(empty_url_template)

    # also update the total urls, as that can be influenced:
    urllistreport.calculation['total_urls'] = len(urllistreport.calculation['urls'])
    urllistreport.total_urls = len(urllistreport.calculation['urls'])
    urllistreport.save()

    return urllistreport


@app.task(queue='storage')
def send_after_scan_mail(scan: AccountInternetNLScan):

    # Do not try to send mail if no mailserver is configured
    if not all([settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD]):
        return "skipped sending mail: no mail server configured"

    scan_type = scan.scan.type
    list_name = scan.urllist.name

    subject = f'Your {scan_type} scan on {list_name} has finished!'
    report = UrlListReport.objects.all().filter(urllist=scan.urllist).order_by("-id").first()

    # Only send mail to users that are active and of course have a mail address...
    users = User.objects.all().filter(dashboarduser__account=scan.account, email__isnull=False, is_active=True)

    if not users:
        return "skipped sending mail: no e-mail addresses associated with account"

    for user in users:

        # figure out the best possible name:
        if user.first_name:
            addressing = user.first_name
        elif user.last_name:
            addressing = user.last_name
        else:
            addressing = user.username

        content = f"""Hi {addressing},<br>
        <br>
        Good news! Your scan on {list_name} has finished.<br>
        <br>
        View the report here: <a href="https://dashboard.internet.nl/spa/#/report/{report.id}">
        https://dashboard.internet.nl/spa/#/report/{report.id}</a><br>
        <br>
        If you have any questions, please contact us via vraag@internet.nl<br>
        <br>
        Regards,<br>
        internet.nl
        """
        send_mail(
            subject,
            content,
            'vraag@internet.nl',
            [user.email],
            fail_silently=False,
            html_message=content
        )

    return "sent mail"


@app.task(queue='storage')
def check_registered_scan_at_internet_nl(value, scan: AccountInternetNLScan):
    # untangle the set
    message, url = value

    if message == "Retrieved status successfully!":
        scan.scan.status_url = url
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
def update_state(state: str, scan: AccountInternetNLScan) -> None:
    """Update the current scan state. Also write it to the scan log. From this log we should also be able to see
    retries... when celery retries on exceptions etc..."""

    # if the state is still the same, just update the last_check, don't append the log.
    # Don't get it from the scan object, that info might be obsolete.
    last_state_for_scan = AccountInternetNLScanLog.objects.all().filter(scan=scan).order_by("-at_when").first()

    if last_state_for_scan:
        if last_state_for_scan.state == state:
            scan.scan.last_check = timezone.now()
            scan.scan.save()
            return

    # First state, or a new state.
    # New log message:
    scan.state = state
    scan.state_changed_on = timezone.now()
    scan.save()

    # update the internet.nl scan, because something happened.
    scan.scan.last_check = timezone.now()
    scan.scan.save()

    scanlog = AccountInternetNLScanLog()
    scanlog.scan = scan
    scanlog.at_when = timezone.now()
    scanlog.state = state
    scanlog.save()


@app.task(queue='storage')
def get_relevant_urls(urllist: UrlList, protocol: str) -> List:
    urls = Url.objects.all().filter(urls_in_dashboard_list=urllist, is_dead=False, not_resolvable=False,
                                    endpoint__protocol__in=[protocol]).values_list('url', flat=True)
    return list(set(urls))
