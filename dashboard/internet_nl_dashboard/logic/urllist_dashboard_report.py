# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytz
from celery import group
from deepdiff import DeepDiff
from websecmap.celery import Task, app
from websecmap.organizations.models import Url
from websecmap.reporting.report import (add_statistics_to_calculation, aggegrate_url_rating_scores,
                                        get_latest_urlratings_fast, relevant_urls_at_timepoint,
                                        remove_issues_from_calculation,
                                        statistics_over_url_calculation)

from dashboard.internet_nl_dashboard.logic import (MAIL_AUTH_FIELDS, MAIL_CATEGORIES,
                                                   MAIL_DNSSEC_FIELDS, MAIL_IPV6_FIELDS,
                                                   MAIL_LEGACY_FIELDS, MAIL_TLS_CERTIFICATE_FIELDS,
                                                   MAIL_TLS_DANE_FIELDS, MAIL_TLS_TLS_FIELDS,
                                                   WEB_APPSECPRIV_CATEGORY, WEB_APPSECPRIV_FIELDS,
                                                   WEB_DNSSEC_CATEGORY, WEB_DNSSEC_FIELDS,
                                                   WEB_IPV6_CATEGORY, WEB_IPV6_FIELDS,
                                                   WEB_LEGACY_FIELDS, WEB_TLS_CATEGORY,
                                                   WEB_TLS_CERTIFICATE_FIELDS, WEB_TLS_DANE_FIELDS,
                                                   WEB_TLS_HTTP_FIELDS, WEB_TLS_TLS_FIELDS)
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport

log = logging.getLogger(__package__)

urllist_report_content = {
    'mail': ['internet_nl_mail_dashboard_overall_score'] +
    MAIL_CATEGORIES + MAIL_IPV6_FIELDS + MAIL_DNSSEC_FIELDS + MAIL_TLS_CERTIFICATE_FIELDS +
    MAIL_TLS_TLS_FIELDS + MAIL_TLS_DANE_FIELDS + MAIL_AUTH_FIELDS + MAIL_LEGACY_FIELDS,

    'web': ['internet_nl_web_overall_score'] + WEB_IPV6_CATEGORY + WEB_IPV6_FIELDS + WEB_DNSSEC_CATEGORY +
    WEB_DNSSEC_FIELDS + WEB_TLS_CATEGORY + WEB_TLS_HTTP_FIELDS + WEB_TLS_TLS_FIELDS +
    WEB_TLS_CERTIFICATE_FIELDS + WEB_TLS_DANE_FIELDS + WEB_APPSECPRIV_CATEGORY + WEB_APPSECPRIV_FIELDS +
    WEB_LEGACY_FIELDS
}


def compose_task(**kwargs) -> Task:
    """
    During scanning, both web and mail scans are triggered for everything. Suppose we change that, and make it possible
    to only perform mail or web scans, we still have a problem. The advantage is that fewer scans run, which saves
    everybody a lot of time. The disadvantage is, that when (for example) 'web' scans are disabled, old endpoints and
    such will still be added to the report. This means old data is on the report.
    At the same time, several lists can contain the url, and it might be totally fine to have those multiple endpoints.
    So, we have to figure out a way to tell the reporting engine what kinds of vulnerabilities are used (instead of
    all).
    What 'is_allowed_to_report', is currently defined in settings. We're not going to change those settings per report,
    as that would defeat the settings cache mechanism and because it's silly. We want to be able to influence that
    method in another way. For example: first let that play out, and then tell what we want to have. This way the
    settings still have precedence. The same url rating might also be used for different reports.
    The only option is to filter on aggregation for the specific report for a list. Therefore
    'aggegrate_url_rating_scores' (sic) contains a 'issue filter' option. The report that will be built is located in
    the urllist settings.

    :param kwargs:
    :return:
    """
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [rate_urllists_now.si([urllist]) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def create_dashboard_report(urllist_id: int):
    """
    Simplified (and perhaps straightforward) version of rate_urllists_now, which returns a report id.
    Only call this after a scan is performed.

    :param urllist:
    :return:
    """
    urllist = UrlList.objects.all().filter(id=urllist_id).first()
    if not urllist:
        return []

    log.debug(f"Creating dashboard report for urllist {urllist}.")

    # the time when a urlreport is created is rounded up to the end of a minute. This means that you'll never get
    # the latest results. It should not happen with scans that happened today, but it does. Therefore, we move
    # the report creation process one minute forward
    # todo: this should be fixed to be more accurate.
    now = datetime.now(pytz.utc) + timedelta(minutes=1)
    return rate_urllist_on_moment(urllist, when=now, prevent_duplicates=False)


@app.task(queue='storage')
def create_dashboard_report_at(urllist, at_when):
    """
    Simplified (and perhaps straightforward) version of rate_urllists_now, which returns a report id.
    Only call this after a scan is performed and a report was already created.

    :param urllist:
    :return:
    """

    return rate_urllist_on_moment(urllist, when=at_when, prevent_duplicates=False)


@app.task(queue='storage')
def rate_urllists_now(urllists: List[UrlList], prevent_duplicates: bool = True):
    for urllist in urllists:
        now = datetime.now(pytz.utc)
        rate_urllist_on_moment(urllist, now, prevent_duplicates)


@app.task(queue='storage')
def rate_urllist_on_moment(urllist: UrlList, when: datetime = None, prevent_duplicates: bool = True) -> int:
    """
    :param urllist:
    :param when: A moment in time of which data should be aggregated
    :param prevent_duplicates: If the last report had the same data, don't save a new report but return the last report
    instead.
    :return: UrlListReport id
    """
    # If there is no time slicing, then it's today.
    if not when:
        when = datetime.now(pytz.utc)

    log.info(f"Creating report for urllist {urllist} on {when}")

    if UrlListReport.objects.all().filter(urllist=urllist, at_when=when).exists():
        log.debug(f"UrllistReport already exists for {urllist} on {when}. Not overwriting.")
        existing_report = UrlListReport.objects.all().filter(urllist=urllist, at_when=when).first()
        return int(existing_report.id)

    urls = relevant_urls_at_timepoint_urllist(urllist=urllist, when=when)
    log.debug(f'Found {len(urls)} to be relevant at this moment.')
    all_url_ratings = get_latest_urlratings_fast(urls, when)

    # Clean the url_ratings to only include the content we need, only the content (being removed)
    # and only the endpoint types
    for urlrating in all_url_ratings:
        calculation = remove_issues_from_calculation(urlrating.calculation, urllist_report_content[urllist.scan_type])

        # Some endpoint types use the same ratings, such as dns_soa and dns_mx... This means that not
        # all endpoints will be removed for internet.nl. We need the following endpoints per scan:
        # -> note: urllist stores web/mail, they mean: web and mail_dashboard.
        endpoint_types_per_scan = {"web": "dns_a_aaaa", "mail": "dns_soa"}
        calculation = only_include_endpoint_protocols(calculation, [endpoint_types_per_scan[urllist.scan_type]])

        # This already overrides endpoint statistics, use the calculation you get from this.
        calculation, amount_of_issues = statistics_over_url_calculation(calculation)
        # overwrite the rest of the statistics.
        calculation = add_statistics_to_calculation(calculation, amount_of_issues)

        urlrating.calculation = calculation

    calculation = aggegrate_url_rating_scores(all_url_ratings)

    try:
        last = UrlListReport.objects.filter(urllist=urllist, at_when__lte=when).latest('at_when')
    except UrlListReport.DoesNotExist:
        last = UrlListReport()  # create a dummy one for comparison

    calculation['name'] = urllist.name

    if prevent_duplicates:
        if not DeepDiff(last.calculation, calculation, ignore_order=True, report_repetition=True):
            log.info(f"The report for {urllist} on {when} is the same as the report from {last.at_when}. Not saving.")
            return int(last.id)

    log.info(f"The calculation for {urllist} on {when} has changed, so we're saving this rating.")

    # remove urls and name from scores object, so it can be used as initialization parameters (saves lines)
    # this is by reference, meaning that the calculation will be affected if we don't work on a clone.
    init_scores = deepcopy(calculation)
    del init_scores['name']
    del init_scores['urls']

    report = UrlListReport(**init_scores)
    report.urllist = urllist
    report.report_type = urllist.scan_type
    report.at_when = when
    report.average_internet_nl_score = sum_internet_nl_scores_over_rating(calculation)
    report.calculation = calculation
    report.save()
    return int(report.id)


def only_include_endpoint_protocols(calculation, only_include_endpoint_types: List[str]):
    new_endpoints = [endpoint
                     for endpoint in calculation['endpoints'] if endpoint['protocol'] in only_include_endpoint_types]
    calculation['endpoints'] = new_endpoints
    return calculation


def relevant_urls_at_timepoint_urllist(urllist: UrlList, when: datetime):
    queryset = Url.objects.filter(urls_in_dashboard_list=urllist)

    return relevant_urls_at_timepoint(queryset=queryset, when=when)


def sum_internet_nl_scores_over_rating(url_ratings: Dict[str, Any]) -> float:
    score = 0
    number_of_scores = 0

    score_fields = ['internet_nl_mail_dashboard_overall_score', 'internet_nl_web_overall_score']

    for url in url_ratings.get('urls', []):
        for endpoint in url.get('endpoints', []):
            for rating in endpoint.get('ratings', []):
                if rating.get('type', "") in score_fields:
                    # explanation":"75 https://batch.internet.nl/mail/portaal.digimelding.nl/289480/",
                    value = rating['explanation'].split(" ")

                    # in case the internet.nl api fails for a domain, all scanned values are set to error.
                    # this value is ignored in the average, not influencing the average with a 0 or 100.
                    if value[0] == "error":
                        continue

                    score += int(value[0])
                    number_of_scores += 1

    if not number_of_scores:
        return 0

    return round(score / number_of_scores, 2)
