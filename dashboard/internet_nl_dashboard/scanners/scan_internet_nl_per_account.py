import logging
from copy import copy
from datetime import datetime, timedelta
from typing import List

import pytz
from actstream import action
from celery import Task, chain, group
from constance import config
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.reporting.report import recreate_url_reports
from websecmap.scanners.models import InternetNLV2Scan
from websecmap.scanners.scanner import add_model_filter, dns_endpoints, internet_nl_v2_websecmap
from websecmap.scanners.scanner.internet_nl_v2 import InternetNLApiSettings

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic.mail import (email_configration_is_correct,
                                                        send_scan_finished_mails)
from dashboard.internet_nl_dashboard.logic.report import (
    add_keyed_ratings, add_percentages_to_statistics, add_simple_verdicts,
    add_statistics_over_ratings, clean_up_not_required_data_to_speed_up_report_on_client,
    remove_comply_or_explain, split_score_and_url)
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


def create_api_settings(scan: InternetNLV2Scan):

    # figure out which AccountInternetNLScan object uses this scan. Retrieve the credentials from that account.
    account_scan = AccountInternetNLScan.objects.all().filter(scan=scan).first()

    s = InternetNLApiSettings()

    s.username = account_scan.account.internet_nl_api_username
    s.password = account_scan.account.decrypt_password()

    s.url = config.INTERNET_NL_API_URL
    # for convenience, remove trailing slashes from the url, this will be entered incorrectly.
    s.url = s.url.rstrip("/")

    s.maximum_domains = config.INTERNET_NL_MAXIMUM_URLS

    return s


# overwrite the create API settings with one that handles credentials for every separate account. This is needed
# for internet.nl to generate some statistics over API usage.
internet_nl_v2_websecmap.create_api_settings = create_api_settings


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
def initialize_scan(urllist: UrlList, manual_or_scheduled: str = "scheduled"):
    # We need to store the scan type in the InternetNLV2Scan at creation, because the type in the list might change:
    translated_scan_types = {'web': 'web', 'mail': 'mail_dashboard'}
    new_scan = InternetNLV2Scan()
    new_scan.type = translated_scan_types[urllist.scan_type]
    new_scan.save()
    internet_nl_v2_websecmap.update_state(new_scan, "requested and empty",
                                          "requested a scan to be performed on internet.nl api")

    accountinternetnlscan = AccountInternetNLScan()
    accountinternetnlscan.account = urllist.account
    accountinternetnlscan.urllist = urllist
    accountinternetnlscan.started_on = datetime.now(pytz.utc)
    accountinternetnlscan.scan = new_scan
    accountinternetnlscan.state = ""
    accountinternetnlscan.save()

    # and start the process.
    update_state("requested", accountinternetnlscan)

    # Sprinkling an activity stream action.
    action.send(urllist.account, verb=f'started {manual_or_scheduled} scan', target=accountinternetnlscan, public=False)

    return accountinternetnlscan


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
        log.debug("No scan received to progress...")
        return group([])

    steps = {
        # complete state progression, using active verbs to come to the next state:cl
        "requested": discovering_endpoints,
        "discovered endpoints": retrieving_scannable_urls,
        "retrieved scannable urls": registering_scan_at_internet_nl,
        "registered scan at internet.nl": running_scan,
        # registered is a old state that somehow, due to unknown factors ends up in the state
        "registered": running_scan,
        "running scan": running_scan,
        "scan results ready": storing_scan_results,
        "scan results stored": processing_scan_results,
        "imported scan results": creating_report,
        "created report": sending_mail,
        "sent mail": finishing_scan,
        "skipped sending mail: no e-mail addresses associated with account": finishing_scan,
        "skipped sending mail: no mail server configured": finishing_scan,
        # "finished"

        # handle error situations of the scan in websecmap:
        "network_error": continue_running_scan,
        "configuration_error": continue_running_scan,
        "timeout": continue_running_scan,


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


@app.task(queue="storage")
def recover_and_retry(scan: AccountInternetNLScan):
    # check the latest valid state from progress running scan, set the state to that state.

    valid_states = ['requested', 'discovered endpoints', 'retrieved scannable urls', 'registered scan at internet.nl',
                    'registered', "running scan", "scan results ready", "scan results stored", "created report",
                    "sent mail", "skipped sending mail: no e-mail addresses associated with account",
                    "skipped sending mail: no mail server configured"]
    error_states = ["network_error", "configuration_error", "timeout"]

    if scan.state in valid_states:
        # no recovery needed
        return group([])

    # get the latest valid state from the scan log:
    latest_valid = AccountInternetNLScanLog.objects.all().filter(
        scan=scan, state__in=valid_states).order_by('-id').first()

    log.debug(f"AccountInternetNLScan scan #{scan.id} is rolled back to retry from "
              f"'{scan.state}' to '{latest_valid.state}'.")

    if scan.state in error_states:
        update_state(latest_valid.state, scan)
    else:
        update_state(latest_valid.state, scan)

    # Also have to rollback the underlying scan, if there already is one.
    if scan.scan:
        internet_nl_v2_websecmap.recover_and_retry(scan.scan)

    return group([])


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

    # mail was added here, due to a problem while registering scans. We always want dns_soa endpoints.
    relevant_scan_types = {"web": "dns_a_aaaa", "mail_dashboard": "dns_soa", "mail": "dns_soa"}

    return (
        get_relevant_urls.si(scan.urllist, relevant_scan_types[scan.scan.type])
        | check_retrieved_scannable_urls.s()
        | update_state.s(scan)
    )


def registering_scan_at_internet_nl(scan: AccountInternetNLScan):
    update_state("registering scan at internet.nl", scan)

    # mail = websecmap, mail_dashboard = internet.nl dashboard, web is the same on both. Mail here is a fallback
    # because the dashboard only understands dns_soa endpoints.
    relevant_endpoint_types = {"web": "dns_a_aaaa", "mail_dashboard": "dns_soa",  "mail": "dns_soa"}

    # auto saved.
    scan.scan.subject_urls.set(get_relevant_urls(scan.urllist, relevant_endpoint_types[scan.scan.type]))

    internet_nl_v2_websecmap.update_state(
        scan.scan, "requested", "requested a scan to be performed on internet.nl api")

    return chain(internet_nl_v2_websecmap.progress_running_scan(scan.scan) | copy_state_from_websecmap_scan.si(scan))


def running_scan(scan: AccountInternetNLScan):
    update_state("running scan", scan)
    return chain(internet_nl_v2_websecmap.progress_running_scan(scan.scan) | copy_state_from_websecmap_scan.si(scan))


def continue_running_scan(scan: AccountInternetNLScan):
    # Used to progress in error situations.
    return chain(internet_nl_v2_websecmap.progress_running_scan(scan.scan) | copy_state_from_websecmap_scan.si(scan))


def storing_scan_results(scan: AccountInternetNLScan):
    update_state("storing scan results", scan)
    return chain(internet_nl_v2_websecmap.progress_running_scan(scan.scan) | copy_state_from_websecmap_scan.si(scan))


def processing_scan_results(scan: AccountInternetNLScan):
    update_state("processing scan results", scan)
    return chain(internet_nl_v2_websecmap.progress_running_scan(scan.scan) | copy_state_from_websecmap_scan.si(scan))


@app.task(queue="storage")
def copy_state_from_websecmap_scan(scan: AccountInternetNLScan):

    up_to_date_scan_information = InternetNLV2Scan.objects.all().get(id=scan.scan.pk)
    current_state = up_to_date_scan_information.state

    log.debug(f"Copying state from websecmap, current state: '{current_state}'. ")

    # conflicting state, make sure it's ignored
    if current_state == "requested":
        new_state = scan.state

    # the websecmap scan progress is not as chatty, make it nicer to better understand scan progress
    # the websecmap scan progress is not as chatty, make it nicer to better understand scan progress
    elif current_state == "registered":
        new_state = "registered scan at internet.nl"

    # there is more to do than finishing the scan
    elif current_state == "finished":
        new_state = "imported scan results"

    else:
        new_state = scan.scan.state

    update_state(new_state, scan)


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
    scan.finished_on = datetime.now(pytz.utc)
    scan.save()

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

    # todo: recover from websecmap errors, by trying to recover there and writing the status to the dashboard.
    recovering_strategies = {
        "discovering endpoints":
            {"timeout in minutes": 24 * 60, "state after timeout": "requested"},
        "retrieving scannable urls":
            {"timeout in minutes": 24 * 60, "state after timeout": "discovered endpoints"},
        "registering scan at internet.nl":
            {"timeout in minutes": 24 * 60, "state after timeout": "retrieved scannable urls"},
        "importing scan results":
            {"timeout in minutes": 24 * 60, "state after timeout": "scan results stored"},
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


@app.task(queue='storage')
def connect_urllistreport_to_accountinternetnlscan(urllistreport: UrlListReport, scan: AccountInternetNLScan):
    scan.report = urllistreport
    scan.save()

    return urllistreport


@app.task(queue='storage')
def upgrade_report_with_statistics(urllistreport: UrlListReport):
    # This saves a lot of data / weight.
    remove_comply_or_explain(urllistreport)

    # This makes comparisons easy and fast in table layouts
    add_simple_verdicts(urllistreport)

    # This makes sorting on score easy.
    split_score_and_url(urllistreport)

    # this makes all scores directly accessible, for easy display
    # It will also remove the ratings as a list, as that contains a lot of data too (which takes costly parse time)
    add_keyed_ratings(urllistreport)

    # This adds some calculations over ratings
    add_statistics_over_ratings(urllistreport)
    add_percentages_to_statistics(urllistreport)

    clean_up_not_required_data_to_speed_up_report_on_client(urllistreport)

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

    :param urllistreport:
    :param scan:
    :return:
    """

    # See if all urls in the list are also mentioned in the report, if not, add them and also make sure the stats
    # for the report are correct(!). This means all unscannable domains _will_ be in the report, as that matches
    # the list of domains to scan.

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
        # Copy the template, otherwise all instances will point to the same text (the last domain in the list of
        # missing domains).
        tmp_empty_url_template = copy(empty_url_template)
        tmp_empty_url_template['url'] = url_not_in_report
        urllistreport.calculation['urls'].append(tmp_empty_url_template)

    # also update the total urls, as that can be influenced:
    urllistreport.calculation['total_urls'] = len(urllistreport.calculation['urls'])
    urllistreport.total_urls = len(urllistreport.calculation['urls'])
    urllistreport.save()

    return urllistreport


@app.task(queue='storage')
def send_after_scan_mail(scan: AccountInternetNLScan):

    # Do not try to send mail if no mailserver is configured
    if not email_configration_is_correct():
        return "skipped sending mail: no mail server configured"

    mails_sent = send_scan_finished_mails(scan)
    if not mails_sent:
        return "skipped sending mail: no e-mail addresses associated with account"

    return "sent mail"


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
        # see: test_update_state
        if last_state_for_scan.state == state == scan.state:
            return

    # do not update a cancelled scan (#159), even if a certain task has finished after a cancel was issued (letting the
    # task overwriting the cancelled state, continuing the scan)
    if last_state_for_scan == "cancelled":
        return

    # First state, or a new state.
    # New log message:
    scan.state = state
    scan.state_changed_on = timezone.now()
    scan.save()

    scanlog = AccountInternetNLScanLog()
    scanlog.scan = scan
    scanlog.at_when = timezone.now()
    scanlog.state = state
    scanlog.save()


@app.task(queue='storage')
def get_relevant_urls(urllist: UrlList, protocol: str) -> List:
    urls = Url.objects.all().filter(urls_in_dashboard_list=urllist, is_dead=False, not_resolvable=False,
                                    endpoint__protocol__in=[protocol])
    return list(set(urls))
