import json
import logging
import re
from copy import copy
from typing import List

from django.db.models import Prefetch

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport

log = logging.getLogger(__name__)


def get_recent_reports(account: Account) -> List:

    # loading the calculation takes some time. In this case we don't need the calculation and as such we defer it.
    reports = UrlListReport.objects.all().filter(
        urllist__account=account, urllist__is_deleted=False).order_by('-pk').select_related(
        'urllist').defer('calculation')

    return create_report_response(reports)


def create_report_response(reports):
    response = []
    for report in reports:

        response.append({
            'id': report.id,
            'report': report.id,
            # mask that there is a mail_dashboard variant.
            'type': report.urllist.scan_type,
            'number_of_urls': report.total_urls,
            'list_name': report.urllist.name,
            'at_when': report.at_when.isoformat(),
            'urllist_id': report.urllist.id,
            'urllist_scan_type': report.urllist.scan_type,
        })

    return response


def get_urllist_timeline_graph(account: Account, urllist_ids: str):
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
    list_split = csv.split(",")

    while "" in list_split:
        list_split.remove("")

    original_order = copy(list_split)

    # aside from casting, remove double lists. this orders the list.
    list_split = list(set([int(id) for id in list_split]))

    statistics_over_last_years_reports = Prefetch(
        'urllistreport_set',
        queryset=UrlListReport.objects.filter().order_by('at_when').only(
            'at_when', 'average_internet_nl_score', 'total_urls'),
        to_attr='reports_from_the_last_year')

    # The actual query, note that the ordering is asc on ID, whatever order you specify...
    urllists = UrlList.objects.all().filter(
        account=account,
        pk__in=list_split,
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
            "data": []
        }

        for per_report_statistics in urllist.reports_from_the_last_year:
            stats[urllist.id]['data'].append({
                'date': per_report_statistics.at_when.date().isoformat(),
                'urls': per_report_statistics.total_urls,
                'average_internet_nl_score': per_report_statistics.average_internet_nl_score,
            })

    # echo the results in the order you got them:
    handled = []
    ordered_lists = []
    for original_order_list_id in original_order:
        if int(original_order_list_id) not in handled and int(original_order_list_id) in stats:
            ordered_lists.append(stats[int(original_order_list_id)])

        handled.append(int(original_order_list_id))

    return ordered_lists


def get_report(account: Account, report_id: int):

    report = UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).values('id', 'urllist_id', 'calculation', 'average_internet_nl_score', 'total_urls', 'at_when').first()

    if not report:
        return []

    # do NOT create a python object, because that's incredibly slow. Instead rely on the capabilities of
    # jsonfield to store json correctly and discard everything else.
    return f'[{{"id": {report["id"]}, ' \
           f'"urllist_id": {report["urllist_id"]}, ' \
           f'"average_internet_nl_score": {report["average_internet_nl_score"]}, ' \
           f'"total_urls": {report["total_urls"]}, ' \
           f'"at_when": "{report["at_when"]}", ' \
           f'"calculation": {report["calculation"]}}}]'


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
    ).values('urllist_id', 'calculation').first()

    if not report:
        return {}

    calculation = json.loads(report["calculation"])

    urls_in_report: List[str] = [url['url'] for url in calculation['urls']]

    urllist = UrlList.objects.all().filter(id=report['urllist_id']).first()
    urls_in_list_queryset = urllist.urls.all()
    urls_in_urllist = [url.url for url in urls_in_list_queryset]

    urls_in_urllist_but_not_in_report = list(set(urls_in_urllist) - set(urls_in_report))
    urls_in_report_but_not_in_urllist = list(set(urls_in_report) - set(urls_in_urllist))

    both_are_equal = False if urls_in_urllist_but_not_in_report or urls_in_report_but_not_in_urllist else True

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


def remove_comply_or_explain(report: UrlListReport):
    # Also remove all comply or explain information as it costs a lot of data/memory on the client

    for url in report.calculation['urls']:
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
            for rating in endpoint['ratings']:
                del rating['comply_or_explain_explanation']
                del rating['comply_or_explain_explained_on']
                del rating['comply_or_explain_explanation_valid_until']
                del rating['comply_or_explain_valid_at_time_of_report']

    del report.calculation["explained_high"]
    del report.calculation["explained_medium"]
    del report.calculation["explained_low"]
    del report.calculation["explained_high_endpoints"]
    del report.calculation["explained_medium_endpoints"]
    del report.calculation["explained_low_endpoints"]
    del report.calculation["explained_high_urls"]
    del report.calculation["explained_medium_urls"]
    del report.calculation["explained_low_urls"]
    del report.calculation["explained_total_url_issues"]
    del report.calculation["explained_url_issues_high"]
    del report.calculation["explained_url_issues_medium"]
    del report.calculation["explained_url_issues_low"]
    del report.calculation["explained_total_endpoint_issues"]
    del report.calculation["explained_endpoint_issues_high"]
    del report.calculation["explained_endpoint_issues_medium"]
    del report.calculation["explained_endpoint_issues_low"]

    report.save()


def add_keyed_ratings(report: UrlListReport):
    """
    This creates issues that are directly accessible by keyword, instead of iterating over a list and finding them.
    This is much faster when showing a report of course. Issues are never duplicated anyway, so not doing this was
    probably a design omission.

    :param report:
    :return:
    """

    for url in report.calculation['urls']:
        for endpoint in url['endpoints']:
            endpoint['ratings_by_type'] = {}
            for rating in endpoint['ratings']:
                endpoint['ratings_by_type'][rating['type']] = rating

    report.save()


def add_statistics_over_ratings(report: UrlListReport):
    # works only after ratings by type.
    # todo: in report section, move statistics_per_issue_type to calculation

    report.calculation['statistics_per_issue_type'] = {}

    possible_issues = []

    for url in report.calculation['urls']:
        for endpoint in url['endpoints']:
            possible_issues += endpoint['ratings_by_type'].keys()
    possible_issues = set(possible_issues)

    # prepare the stats dict to have less expensive operations in the 3x nested loop
    for issue in possible_issues:
        # todo: could be a defaultdict. although explicit initialization is somewhat useful.
        report.calculation['statistics_per_issue_type'][issue] = {
            'high': 0, 'medium': 0, 'low': 0, 'ok': 0, 'not_ok': 0, 'not_testable': 0, 'not_applicable': 0}

    # count the numbers, can we do this with some map/add function that is way faster?
    for issue in possible_issues:
        for url in report.calculation['urls']:
            for endpoint in url['endpoints']:
                rating = endpoint['ratings_by_type'].get(issue, None)
                if not rating:
                    continue
                report.calculation['statistics_per_issue_type'][issue]['high'] += rating['high']
                report.calculation['statistics_per_issue_type'][issue]['medium'] += rating['medium']
                report.calculation['statistics_per_issue_type'][issue]['low'] += rating['low']
                report.calculation['statistics_per_issue_type'][issue]['not_testable'] += rating['not_testable']
                report.calculation['statistics_per_issue_type'][issue]['not_applicable'] += rating['not_applicable']

                # things that are not_testable or not_applicable do not have impact on thigns being OK
                # see: https://github.com/internetstandards/Internet.nl-dashboard/issues/68
                if not any([rating['not_testable'], rating['not_applicable']]):
                    report.calculation['statistics_per_issue_type'][issue]['ok'] += rating['ok']
                    report.calculation['statistics_per_issue_type'][issue]['not_ok'] += \
                        rating['high'] + rating['medium'] + rating['low']

    report.save()


def add_percentages_to_statistics(report: UrlListReport):

    for key, value in report.calculation['statistics_per_issue_type'].items():
        issue = report.calculation['statistics_per_issue_type'][key]

        all = issue['ok'] + issue['not_ok']
        if all == 0:
            # This happens when everything tested is not applicable or not testable: thus no stats:
            report.calculation['statistics_per_issue_type'][key]['pct_high'] = 0
            report.calculation['statistics_per_issue_type'][key]['pct_medium'] = 0
            report.calculation['statistics_per_issue_type'][key]['pct_low'] = 0
            report.calculation['statistics_per_issue_type'][key]['pct_ok'] = 0
            report.calculation['statistics_per_issue_type'][key]['pct_not_ok'] = 0
            continue

        report.calculation['statistics_per_issue_type'][key]['pct_high'] = round((issue['high'] / all) * 100, 2)
        report.calculation['statistics_per_issue_type'][key]['pct_medium'] = round((issue['medium'] / all) * 100, 2)
        report.calculation['statistics_per_issue_type'][key]['pct_low'] = round((issue['low'] / all) * 100, 2)

        # warning (=medium) and info(=low) do NOT have a score impact, only high has a score impact.
        # https://www.internet.nl/faqs/report/
        report.calculation['statistics_per_issue_type'][key]['pct_ok'] = round(
            ((issue['ok'] + issue['low'] + issue['medium']) / all) * 100, 2)

        report.calculation['statistics_per_issue_type'][key]['pct_not_ok'] = round((issue['not_ok'] / all) * 100, 2)

    report.save()
