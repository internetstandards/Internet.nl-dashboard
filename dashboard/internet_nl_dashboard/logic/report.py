# SPDX-License-Identifier: Apache-2.0
import gzip
import logging
import re
from copy import copy
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, Optional, Type, Union
from uuid import uuid4

import orjson
from actstream import action
from django.db.models import Model  # pylint: disable=unused-import
from django.db.models import Prefetch
from websecmap.organizations.models import Url
from websecmap.reporting.diskreport import location_on_disk, retrieve_report, store_report
from websecmap.reporting.report import relevant_urls_at_timepoint

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import (create_calculation_on_urls,
                                                                            sum_internet_nl_scores_over_rating)
from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport

log = logging.getLogger(__name__)


def get_recent_reports(account: Account) -> List[Dict[str, Any]]:
    # loading the calculation takes some time. In this case we don't need the calculation and as such we defer it.
    # also show the reports from deleted lists... urllist__is_deleted=False
    reports = UrlListReport.objects.all().filter(
        urllist__account=account).order_by('-pk').select_related(
        'urllist').defer('calculation')

    return create_report_response(reports)


def create_report_response(reports) -> List[Dict[str, Any]]:
    return [{
        'id': report.id,
        'report': report.id,
        # mask that there is a mail_dashboard variant.
        'type': report.report_type,
        'number_of_urls': report.total_urls,
        'list_name': report.urllist.name,
        'at_when': report.at_when.isoformat(),
        'urllist_id': report.urllist.id,
        'urllist_scan_type': report.urllist.scan_type,
    } for report in reports]


def ad_hoc_report_create(account: Account, report_id: int, tags: List[str], at_when: Optional[datetime]):
    # Get a list of urls based on tags, the simplest way: require all tags to be present.
    # Url Reports don't have to be re-created because you're piggy-backing on a specific, larger, report.
    # We're not opening that report and then filter in it, that will complicate the report: we'll just
    # make a new report. and at most store it in a cache. In the end we might even save it.

    # report_id is used to get a time-point for an ad-hoc report.
    # account is used to connect a session to the current report: so the correct user opens the report
    # tags is a list of tags that must all be present in the list of urls

    report = UrlListReport.objects.all().filter(
        urllist__account=account, urllist__is_deleted=False, id=report_id).first()
    if not report:
        return {}

    # This is an "AND" construction, each tag should be present:
    urls = Url.objects.all().filter(taggedurlinurllist__urllist=report.urllist)
    for tag in tags:
        urls = urls.filter(taggedurlinurllist__tags__name__icontains=tag)

    if at_when:
        report.at_when = at_when

    log.debug(f"Creating ad-hoc report with tags: {tags}, yielding in {len(urls)} urls.")

    # Get all relevant urls at this moment from the report... how do you know when the list changes?
    urls = relevant_urls_at_timepoint(urls, report.at_when)

    log.debug(f"At thiis moment in time: {report.at_when}, there are {len(urls)} urls.")

    # todo: probably add relevant endpoints at time point, otherwise very old stuff or new stuff will be added.
    calculation = create_calculation_on_urls(urls, when=report.at_when, scan_type=report.report_type)
    report.average_internet_nl_score = sum_internet_nl_scores_over_rating(calculation)
    optimize_calculation_and_add_statistics(calculation)

    # Do NOT save the calculation to the report(!) because it is not complete anymore:
    report.calculation = calculation

    return report


def save_ad_hoc_tagged_report(account: Account, report_id: int, tags: List[str], at_when: Optional[datetime]):
    report = ad_hoc_report_create(account, report_id, tags, at_when)
    # A new ID saves as a new record
    tmp_calculation = report.calculation
    report.calculation = None
    report.id = None
    report.save()

    store_report(report.pk, "UrlListReport", tmp_calculation)

    return operation_response(success=True)


def ad_hoc_tagged_report(account: Account, report_id: int, tags: List[str], at_when: Optional[datetime]):
    report = ad_hoc_report_create(account, report_id, tags, at_when)

    return '{' \
           f'"id": {report.id}, ' \
           f'"urllist_id": {report.urllist.id}, ' \
           f'"urllist_name": "{report.urllist.name}", ' \
           f'"average_internet_nl_score": {report.average_internet_nl_score}, ' \
           f'"total_urls": {len(report.calculation["urls"])}, ' \
           f'"is_publicly_shared": {"true" if report.is_publicly_shared else "false"}, ' \
           f'"at_when": "{report.at_when}", ' \
           f'"calculation": {orjson.dumps(report.calculation)}, ' \
           f'"report_type": "{report.report_type}", ' \
           f'"public_report_code": "{report.public_report_code}", ' \
           f'"public_share_code": "{report.public_share_code}" ' \
           '}'


def get_urllist_timeline_graph(account: Account, urllist_ids: str, report_type: str = "web"):
    """
    This is the data for a line / bar chart that shows information on the average internet.nl score.
    There can be multiple reports selected,

    Given there are over 50 findings, the chance that someone does everything right is very low. Probably
    the data needs some interpretation. This will be done at a later time.

    The numbers that are returned are for all findings. So every check that is performed is added. This explains
    why the numbers are pretty high.

    For example: when this is 0, then this and this are not important. But that information is not clear from the
    API and is under constant change and re-interpretation. Which means is has to be separated somewhere.
    For now, we'll just present the data as it is.

    :param account:
    :param urllist_id:
    :return:
    """

    csv = re.sub(r"[^,0-9]*", "", urllist_ids)
    list_split: List[str] = csv.split(",")

    while "" in list_split:
        list_split.remove("")

    if report_type not in ["web", "mail"]:
        report_type = "web"

    original_order = copy(list_split)

    # aside from casting, remove double lists. this orders the list.
    casted_list_split = list({int(list_id) for list_id in list_split})

    statistics_over_last_years_reports = Prefetch(
        'urllistreport_set',
        queryset=UrlListReport.objects.filter(report_type=report_type).order_by('at_when').only(
            'at_when', 'average_internet_nl_score', 'total_urls', 'urllist_id'),
        to_attr='reports_from_the_last_year')

    # The actual query, note that the ordering is asc on ID, whatever order you specify...
    urllists = UrlList.objects.all().filter(
        account=account,
        pk__in=casted_list_split,
        is_deleted=False
    ).only('id', 'name').prefetch_related(statistics_over_last_years_reports)

    if not urllists:
        return []

    # add statistics:
    stats = {}

    for urllist in urllists:
        stats[urllist.id] = {
            "id": urllist.id,
            "name": urllist.name,
            "data": [{
                'date': per_report_statistics.at_when.date().isoformat(),
                'urls': per_report_statistics.total_urls,
                'average_internet_nl_score': per_report_statistics.average_internet_nl_score,
                'report': per_report_statistics.id
                # mypy does not understand to_attr
            } for per_report_statistics in urllist.reports_from_the_last_year]  # type: ignore
        }

    # echo the results in the order you got them:
    handled = []
    ordered_lists = []
    for original_order_list_id in original_order:
        if int(original_order_list_id) not in handled and int(original_order_list_id) in stats:
            ordered_lists.append(stats[int(original_order_list_id)])

        handled.append(int(original_order_list_id))

    return ordered_lists


def get_report(account: Account, report_id: int) -> str:
    log.debug("Retrieve report data")
    # it's okay if the list is deleted. Still be able to see reports from the past
    # urllist__is_deleted=False,
    report = UrlListReport.objects.all().filter(
        urllist__account=account,
        pk=report_id
    ).values('id', 'urllist_id', 'calculation', 'average_internet_nl_score', 'total_urls', 'at_when', 'report_type',
             'urllist__name', 'is_publicly_shared', 'public_report_code', 'public_share_code'
             ).first()

    if not report:
        return "{}"

    log_report_access_async.apply_async([report_id, account.id])
    calculation_raw = retrieve_report_raw(report_id, "UrlListReport")

    log.debug("Dumping report to json")
    data = f"{dump_report_to_text_resembling_json(report, calculation_raw)}"
    log.debug("Returning the report")
    return data


@app.task(queue="storage", ignore_result=True)
def log_report_access_async(report_id: int, account_id: int):
    # do this async to speed up report retrieval. Don't execute extra queries when retrieving data...

    account = Account.objects.filter(pk=account_id).first()

    # Sprinkling an activity stream action.
    log.debug("Saving activity stream action")
    log_report = UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).only('id').first()
    action.send(account, verb='viewed report', target=log_report, public=False)


def get_public_reports():
    return list(UrlListReport.objects.all().filter(
        is_publicly_shared=True, is_shared_on_homepage=True
    ).values(
        'at_when', 'average_internet_nl_score', 'report_type', 'urllist__name', 'total_urls', 'public_report_code'
    ).order_by('-at_when'))


def get_shared_report(report_code: str, share_code: str = ""):
    # Check if report_code exists. If so see if a share code is required.
    report = UrlListReport.objects.all().filter(
        # A deleted list means that the report cannot be seen anymore
        urllist__is_deleted=False,

        # All other public sharing filters
        public_report_code=report_code,
        is_publicly_shared=True
    ).values('id', 'urllist_id', 'calculation', 'average_internet_nl_score', 'total_urls', 'at_when', 'report_type',
             'urllist__name', 'is_publicly_shared', 'public_report_code', 'public_share_code'
             ).first()

    if not report:
        # deter brute forcing
        log.debug("Could not find report with code %s", report_code)
        sleep(3)
        return []

    if report['public_share_code'] == share_code:
        # todo: prevent loads/dumps with report calculation, it is should be sent without any loading to speed up
        #  large reports
        calculation = retrieve_report_raw(report["id"], "UrlListReport")
        return f"{dump_report_to_text_resembling_json(report, calculation)}"

    # todo: should be a normal REST response
    return f'{{"authentication_required": true, "public_report_code": "{report_code}", "id": "{report["id"]}", ' \
           f'"urllist_name": "{report["urllist__name"]}", "at_when": "{report["at_when"]}"}}'


def dump_report_to_text_resembling_json(report, calculation):
    """
    Does _not_ create a python object of a report, because that's slow. Instead it relies on the capanility
    to store json as text and just dump it out there. This requires no conversion to python object or parsing first.

    todo: the new jsonfield works in a different way, automatically retrieving it as a python object instead of text.

    :param report:
    :return:
    """
    return '{' \
           f'"id": {report["id"]}, ' \
           f'"urllist_id": {report["urllist_id"]}, ' \
           f'"urllist_name": "{report["urllist__name"]}", ' \
           f'"average_internet_nl_score": {report["average_internet_nl_score"]}, ' \
           f'"total_urls": {report["total_urls"]}, ' \
           f'"is_publicly_shared": {"true" if report["is_publicly_shared"] else "false"}, ' \
           f'"at_when": "{report["at_when"]}", ' \
           f'"calculation": {calculation}, ' \
           f'"report_type": "{report["report_type"]}", ' \
           f'"public_report_code": "{report["public_report_code"]}", ' \
           f'"public_share_code": "{report["public_share_code"]}" ' \
           '}'


def get_report_directly(report_id):
    """
    Variant of get_report without the account or availability check.

    :param report_id:
    :return:
    """

    report = UrlListReport.objects.all().filter(
        pk=report_id
    ).values('id', 'urllist_id', 'average_internet_nl_score', 'total_urls', 'at_when').first()

    if not report:
        return {}

    # since this is stored on disk now, get this separately. Use this in the old flow as if nothing has changed.
    report["calculation"] = retrieve_report(report_id, "UrlListReport")
    if not report["calculation"]:
        log.warning(f"Report {report_id} has no calculation, returning empty json.")

    return dump_report_to_json(report)


def dump_report_to_json(report):
    """
    Creates a json variant of the report, used internally.
    :return:
    """
    return {
        'id': report["id"],
        'urllist_id': report["urllist_id"],
        'average_internet_nl_score': report["average_internet_nl_score"],
        'total_urls': report["total_urls"],
        'at_when': report["at_when"],
        'calculation': report["calculation"]
    }


def get_report_differences_compared_to_current_list(account: Account, report_id: int):
    """
    This method gives insight into the report, compared to the list the report originates from.

    It will give the differences compared to the list:
    - what domains are in the report, but are not in the list
    - what domains are in the list, but not in the report

    :param account:
    :param report_id:
    :return:
    """
    report = UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).values('urllist_id').first()

    if not report:
        return {}

    # since django 3.0 it's already retrieved as json
    calculation = retrieve_report(report_id, "UrlListReport")

    urls_in_report: List[str] = [url['url'] for url in calculation['urls']]

    urllist = UrlList.objects.all().filter(id=report['urllist_id']).first()
    # todo: "ManyToManyField[Sequence[Any], RelatedManager[Any]]" of "Union[ManyToManyField[Sequence[Any],
    #  RelatedManager[Any]], Any]" has no attribute "all"
    urls_in_list_queryset = urllist.urls.all()  # type: ignore
    urls_in_urllist = [url.url for url in urls_in_list_queryset]

    urls_in_urllist_but_not_in_report = list(set(urls_in_urllist) - set(urls_in_report))
    urls_in_report_but_not_in_urllist = list(set(urls_in_report) - set(urls_in_urllist))

    both_are_equal = not any([urls_in_urllist_but_not_in_report, urls_in_report_but_not_in_urllist])

    content_comparison = {
        "number_of_urls_in_urllist": len(urls_in_urllist),
        "number_of_urls_in_report": len(urls_in_report),
        "in_urllist_but_not_in_report": ", ".join(urls_in_urllist_but_not_in_report),
        "in_report_but_not_in_urllist": ", ".join(urls_in_report_but_not_in_urllist),
        "both_are_equal": both_are_equal,
    }

    return content_comparison


def get_previous_report(account: Account, urllist_id, at_when):
    report = UrlListReport.objects.all().filter(
        urllist_id=urllist_id,
        urllist__account=account,
        urllist__is_deleted=False,
        at_when__lt=at_when).order_by('-at_when').values('pk').first()
    if not report:
        return {}

    return get_report(account, report['pk'])[0]


def optimize_calculation_and_add_statistics(calculation: Dict[str, Any]):
    # This saves a lot of data / weight.
    remove_comply_or_explain(calculation)

    # This makes comparisons easy and fast in table layouts
    add_simple_verdicts(calculation)

    # This makes sorting on score easy.
    split_score_and_url(calculation)

    # this makes all scores directly accessible, for easy display
    # It will also remove the ratings as a list, as that contains a lot of data too (which takes costly parse time)
    add_keyed_ratings(calculation)

    # This adds some calculations over ratings
    add_statistics_over_ratings(calculation)
    add_percentages_to_statistics(calculation)

    clean_up_not_required_data_to_speed_up_report_on_client(calculation)

    return calculation


def remove_comply_or_explain(calculation: Dict[str, Any]):
    # Also remove all comply or explain information as it costs a lot of data/memory on the client

    for url in calculation['urls']:

        if "explained_total_issues" not in url:
            # explanations have already been removed.
            continue

        del url["explained_total_issues"]
        del url["explained_high"]
        del url["explained_medium"]
        del url["explained_low"]
        del url["explained_high_endpoints"]
        del url["explained_medium_endpoints"]
        del url["explained_low_endpoints"]
        del url["explained_total_url_issues"]
        del url["explained_url_issues_high"]
        del url["explained_url_issues_medium"]
        del url["explained_url_issues_low"]
        del url["explained_total_endpoint_issues"]
        del url["explained_endpoint_issues_high"]
        del url["explained_endpoint_issues_medium"]
        del url["explained_endpoint_issues_low"]

        for endpoint in url['endpoints']:
            del endpoint['explained_high']
            del endpoint['explained_medium']
            del endpoint['explained_low']

            for rating in endpoint['ratings']:
                del rating['is_explained']
                del rating['comply_or_explain_explanation']
                del rating['comply_or_explain_explained_on']
                del rating['comply_or_explain_explanation_valid_until']
                del rating['comply_or_explain_valid_at_time_of_report']

    if "explained_high" not in calculation:
        return calculation

    del calculation["explained_high"]
    del calculation["explained_medium"]
    del calculation["explained_low"]
    del calculation["explained_high_endpoints"]
    del calculation["explained_medium_endpoints"]
    del calculation["explained_low_endpoints"]
    del calculation["explained_high_urls"]
    del calculation["explained_medium_urls"]
    del calculation["explained_low_urls"]
    del calculation["explained_total_url_issues"]
    del calculation["explained_url_issues_high"]
    del calculation["explained_url_issues_medium"]
    del calculation["explained_url_issues_low"]
    del calculation["explained_total_endpoint_issues"]
    del calculation["explained_endpoint_issues_high"]
    del calculation["explained_endpoint_issues_medium"]
    del calculation["explained_endpoint_issues_low"]

    return calculation


def add_keyed_ratings(calculation: Dict[str, Any]):
    """
    This creates issues that are directly accessible by keyword, instead of iterating over a list and finding them.
    This is much faster when showing a report of course. Issues are never duplicated anyway, so not doing this was
    probably a design omission.

    :param report:
    :return:
    """

    for url in calculation['urls']:
        for endpoint in url['endpoints']:
            endpoint['ratings_by_type'] = {}
            for rating in endpoint['ratings']:
                endpoint['ratings_by_type'][rating['type']] = rating


def clean_up_not_required_data_to_speed_up_report_on_client(calculation: Dict[str, Any]):
    """
    Loading in JSON objects in the client takes (a lot of) time. The larger the object, the more time.
    Especially with 500+ urls, shaving off data increases parse speed with over 50%. So this is a must

    :param report:
    :return:
    """

    for url in calculation['urls']:
        for endpoint in url['endpoints']:
            for rating_key in endpoint['ratings_by_type']:
                # clean up fields we don't need, to make the report show even quicker
                # a lot of stuff from web sec map is nice, but not really useful for us at this moment.
                # perhaps later

                # These values are used in add_statistics_over_ratings and. Only OK is used in the spreadsheet
                # export (which could also be pre-generated).
                del endpoint['ratings_by_type'][rating_key]['high']  # high is used in add_statistics_over_ratings
                del endpoint['ratings_by_type'][rating_key]['medium']  # only 'ok' is used in spreadsheet export.
                del endpoint['ratings_by_type'][rating_key]['low']  # only 'ok' is used in spreadsheet export.
                del endpoint['ratings_by_type'][rating_key]['not_testable']  # only 'ok' is used in spreadsheet export.
                del endpoint['ratings_by_type'][rating_key]['not_applicable']  # only 'ok' is used in spreadsheet export
                del endpoint['ratings_by_type'][rating_key]['error_in_test']  # only 'ok' is used in spreadsheet export
                del endpoint['ratings_by_type'][rating_key]['last_scan']  # not used in front end

                # the since field can be unix timestamp, which is less data
                try:
                    endpoint['ratings_by_type'][rating_key]['since'
                                                            ] = datetime.fromisoformat(
                        endpoint['ratings_by_type'][rating_key]['since']).timestamp()
                except ValueError:
                    # then don't update it.
                    ...

                # Because of the 'ad hoc' reports, it's valuable to show when a measurement was performed
                # as a report can contain metrics from various moments in time (due to re-scans on measurement errors)
                # del endpoint['ratings_by_type'][rating_key]['since']
                # del endpoint['ratings_by_type'][rating_key]['last_scan']
                del endpoint['ratings_by_type'][rating_key]['explanation']

                del endpoint['ratings_by_type'][rating_key]['type']  # is already in the key
                del endpoint['ratings_by_type'][rating_key]['scan_type']  # is already in the key

            # remove the original rating, as that slows parsing on the client down significantly.
            # with significantly == Vue will parse it, and for a 500 url list this will take 5 seconds.
            del endpoint['ratings']

        del url['total_endpoints']
        del url['high_endpoints']
        del url['medium_endpoints']
        del url['low_endpoints']
        del url['ok_endpoints']

        del url['total_url_issues']
        del url['url_issues_high']
        del url['url_issues_medium']
        del url['url_issues_low']
        del url['url_ok']

        del url['total_endpoint_issues']
        del url['endpoint_issues_high']
        del url['endpoint_issues_medium']
        del url['endpoint_issues_low']


def add_simple_verdicts(calculation: Dict[str, Any]):
    """
    # Todo: this value is already available, and more accurately, from the API. So use the value that got returned
    # from the API instead.

    Reduces the rating fields to a single string value, so the correct rating can be retrieved instantly.

    // these are in ranges of 10's so at later moments some values can be added in between.
    // these are used to compare these ratings without having to convert them in javascript dynamically
    Simple values match the current possible {'passed': 400, 'info': 300, 'warning': 200, 'failed': 100};

    :param report:
    :return:
    """

    # <50 will not be compared
    progression_table = {
        'not_applicable': 0,
        'not_testable': 0,
        'error_in_test': 0,
        'no_mx': 0,
        'unreachable': 0,

        'failed': 100,
        'warning': 200,
        'info': 300,
        'good_not_tested': 380,
        'passed': 400,
    }

    for url in calculation['urls']:
        for endpoint in url['endpoints']:
            for rating in endpoint['ratings']:
                rating['simple_progression'] = progression_table.get(rating.get('test_result', ''), 0)


def split_score_and_url(calculation: Dict[str, Any]):
    """
    Split the internet.nl score and the url to be instantly accessible.

    :param report:
    :return:
    """
    for url in calculation['urls']:
        for endpoint in url['endpoints']:
            score: Union[int, str] = 0
            url = ""
            scan = 0
            since = ""
            last_scan = ""
            for rating in endpoint['ratings']:
                if rating['type'] in ["internet_nl_web_overall_score", "internet_nl_mail_dashboard_overall_score"]:
                    # explanation	"78 https://batch.interne…zuiderzeeland.nl/886818/"
                    explanation = rating['explanation'].split(" ")  # type: ignore
                    if explanation[0] == "error":
                        rating['internet_nl_score'] = score = "error"
                    else:
                        rating['internet_nl_score'] = score = int(explanation[0])
                    rating['internet_nl_url'] = url = explanation[1]
                    scan = rating['scan']
                    since = rating['since']
                    last_scan = rating['last_scan']

            # Now that we had all ratings, add a single value for the score, so we don't have to switch between
            # web or mail, which is severely annoying.
            # there is only one rating per set endpoint. So this is safe
            endpoint['ratings'].append(
                {
                    "type": "internet_nl_score",
                    "scan_type": "internet_nl_score",
                    "internet_nl_score": score,
                    "internet_nl_url": url,

                    # to comply with the rating structure
                    "high": 0,
                    "medium": 1,  # make sure to match simple verdicts as defined above.
                    "low": 0,
                    "ok": 0,
                    "not_testable": False,
                    "not_applicable": False,
                    "error_in_test": False,
                    'test_result': score,
                    "scan": scan,
                    "since": since,
                    "last_scan": last_scan,
                    "explanation": "",
                }
            )


def add_statistics_over_ratings(calculation: Dict[str, Any]):
    # works only after ratings by type.
    # todo: in report section, move statistics_per_issue_type to calculation

    calculation['statistics_per_issue_type'] = {}

    possible_issues = []

    for url in calculation['urls']:
        for endpoint in url['endpoints']:
            possible_issues += endpoint['ratings_by_type'].keys()
    possible_issues = list(set(possible_issues))

    # prepare the stats dict to have less expensive operations in the 3x nested loop
    for issue in possible_issues:
        # todo: could be a defaultdict. although explicit initialization is somewhat useful.
        calculation['statistics_per_issue_type'][issue] = {
            'high': 0, 'medium': 0, 'low': 0, 'ok': 0, 'not_ok': 0, 'not_testable': 0, 'not_applicable': 0,
            'error_in_test': 0}

    # count the numbers, can we do this with some map/add function that is way faster?
    for issue in possible_issues:
        for url in calculation['urls']:
            for endpoint in url['endpoints']:
                rating = endpoint['ratings_by_type'].get(issue, None)
                if not rating:
                    continue
                calculation['statistics_per_issue_type'][issue]['high'] += rating['high']
                calculation['statistics_per_issue_type'][issue]['medium'] += rating['medium']
                calculation['statistics_per_issue_type'][issue]['low'] += rating['low']
                calculation['statistics_per_issue_type'][issue]['not_testable'] += rating['not_testable']
                calculation['statistics_per_issue_type'][issue]['not_applicable'] += rating['not_applicable']
                calculation['statistics_per_issue_type'][issue]['error_in_test'] += rating['error_in_test']

                # things that are not_testable or not_applicable do not have impact on thigns being OK
                # see: https://github.com/internetstandards/Internet.nl-dashboard/issues/68
                if not any([rating['not_testable'], rating['not_applicable'], rating['error_in_test']]):
                    calculation['statistics_per_issue_type'][issue]['ok'] += rating['ok']
                    # these can be summed because only one of high, med, low is 1
                    calculation['statistics_per_issue_type'][issue]['not_ok'] += \
                        rating['high'] + rating['medium'] + rating['low']


def add_percentages_to_statistics(calculation: Dict[str, Any]):
    for key, _ in calculation['statistics_per_issue_type'].items():
        issue = calculation['statistics_per_issue_type'][key]

        # may 2020: we want to see the other issues in the graphs as being gray.
        graphs_all = sum([issue['ok'], issue['high'], issue['medium'], issue['low'],
                          issue['not_testable'], issue['not_applicable'], issue['error_in_test']])
        if graphs_all == 0:
            # This happens when everything tested is not applicable or not testable: thus no stats:
            calculation['statistics_per_issue_type'][key]['pct_high'] = 0
            calculation['statistics_per_issue_type'][key]['pct_medium'] = 0
            calculation['statistics_per_issue_type'][key]['pct_low'] = 0
            calculation['statistics_per_issue_type'][key]['pct_ok'] = 0
            calculation['statistics_per_issue_type'][key]['pct_not_ok'] = 0
            continue

        tcskp = calculation['statistics_per_issue_type'][key]
        tcskp['pct_high'] = round((issue['high'] / graphs_all) * 100, 2)
        tcskp['pct_medium'] = round((issue['medium'] / graphs_all) * 100, 2)
        tcskp['pct_low'] = round((issue['low'] / graphs_all) * 100, 2)
        # all other possible stuff. Note that no_mx, unreachable and such have been mapped to one of these.
        tcskp['pct_not_applicable'] = round((issue['not_applicable'] / graphs_all) * 100, 2)
        tcskp['pct_not_testable'] = round((issue['not_testable'] / graphs_all) * 100, 2)
        tcskp['pct_error_in_test'] = round((issue['error_in_test'] / graphs_all) * 100, 2)

        # May 2019 warning (=medium) and info(=low) do NOT have a score impact, only high has a score impact.
        # https://www.internet.nl/faqs/report/
        # This has been altered in May 2020 to avoid confusion and show different kinds of values, it's now just OK
        # instead of including medium and low as ok.
        tcskp['pct_ok'] = round(((issue['ok']) / graphs_all) * 100, 2)
        tcskp['pct_not_ok'] = round((issue['not_ok'] / graphs_all) * 100, 2)


def share(account, report_id, share_code):
    report = get_report_for_sharing(account, report_id, False)

    if not report:
        return operation_response(error=True, message="response_no_report_found")

    report.is_publicly_shared = True
    report.public_share_code = share_code

    # Keep the report link the same when disabling and re-enabling sharing.
    if not report.public_report_code:
        report.public_report_code = str(uuid4())
    report.save()

    return operation_response(success=True, message="response_shared", data=report_sharing_data(report))


def unshare(account, report_id):
    report = get_report_for_sharing(account, report_id, True)

    if not report:
        return operation_response(error=True, message="response_no_report_found")

    report.is_publicly_shared = False
    report.save()

    return operation_response(success=True, message="response_unshared", data=report_sharing_data(report))


def update_share_code(account, report_id, share_code):
    report = get_report_for_sharing(account, report_id, True)

    if not report:
        return operation_response(error=True, message="response_no_report_found")

    report.public_share_code = share_code
    report.save()

    return operation_response(success=True, message="response_updated_share_code", data=report_sharing_data(report))


def update_report_code(account, report_id):
    report = get_report_for_sharing(account, report_id, True)

    if not report:
        return operation_response(error=True, message="response_no_report_found")

    report.public_report_code = str(uuid4())
    report.save()

    return operation_response(success=True, message="response_updated_report_code", data=report_sharing_data(report))


def get_report_for_sharing(account: Account, report_id: int, is_publicly_shared: bool) -> Any:
    return UrlListReport.objects.all().filter(
        urllist__account=account, urllist__is_deleted=False, id=report_id, is_publicly_shared=is_publicly_shared
    ).defer('calculation').first()


def report_sharing_data(report: UrlListReport) -> Dict[str, Any]:
    return {
        'public_report_code': report.public_report_code,
        'public_share_code': report.public_share_code,
        'is_publicly_shared': report.is_publicly_shared
    }


def retrieve_report_raw(report_id: Union[int, str], model: Union[str, Type["Model"]] = "UrlListReport"):
    # used for direct dumping to output, not parsing any json here to speed up things!
    return _read_raw_data_from_gzip(location_on_disk(report_id, model))


def _read_raw_data_from_gzip(location):
    try:
        # log.debug(f"Reading report file: {location}")
        with gzip.open(location, "rt") as file:
            return file.read()
    except FileNotFoundError:
        log.info("Report does not exist on location %s.", location)
        return ""
