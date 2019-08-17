from datetime import timedelta
from typing import List

import simplejson as json
from django.db.models import Prefetch
from django.utils import timezone

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport


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


def get_urllist_report_graph_data(account: Account, urllist_id: int):
    """
    This is the data for a line / bar chart that shows information on _all_ findings in a report. The reports selected
    are all from the past 366 days. The more the reports there are, the more fine grained the statistics will be.

    Given there are over 50 findings, the chance that someone does everything right is very low. Probably
    the data needs some interpretation. This will be done at a later time.

    The numbers that are returned are for all findings. So every check that is performed is added. This explains
    why the numbers are pretty high.

    For example: when this is 0, then this and this are not important. But that information is not clear from the
    API and is under constant change and re-interpretation. Which means is has to be separated somewhere.
    For now, we'll just present the data as it is.

    Todo: There is probably a wish to have the statistics per 'category' and per 'issue'. These have to be created.
    Todo: is the scan frequency the same as the report frequency?

    :param account:
    :param urllist_id:
    :return:
    """
    one_year_ago = timezone.now() - timedelta(days=366)
    statistics_over_last_years_reports = Prefetch(
        'urllistreport_set',
        queryset=UrlListReport.objects.filter(at_when__gte=one_year_ago).order_by('at_when').only(
            'at_when', 'total_endpoints', 'total_urls', 'high', 'medium', 'low', 'ok'),
        to_attr='reports_from_the_last_year')

    # The actual query.
    urllist = UrlList.objects.all().filter(
        account=account,
        pk=urllist_id,
        is_deleted=False
    ).order_by('name').prefetch_related(statistics_over_last_years_reports).first()

    if not urllist:
        return []

    # add statistics:
    stats = []
    for per_report_statistcs in urllist.reports_from_the_last_year:
        not_ok = per_report_statistcs.high
        all = per_report_statistcs.ok + per_report_statistcs.high + per_report_statistcs.medium + \
            per_report_statistcs.low

        stats.append({
            'date': per_report_statistcs.at_when.date().isoformat(),
            'urls': per_report_statistcs.total_urls,
            'endpoints': per_report_statistcs.total_endpoints,
            'high': per_report_statistcs.high,
            'medium': per_report_statistcs.medium,
            'low': per_report_statistcs.low,
            'ok': per_report_statistcs.ok,
            'average_internet_nl_score': per_report_statistcs.average_internet_nl_score,

            # todo: these numbers might be added to the statics calculation?
            'not_ok': not_ok,
            'total_findings': all,

            # for internet.nl low and medium do not impact the score.
            # not_tested does (=high), not_testable and not_applicable don't.
            'pct_ok': round(
                ((per_report_statistcs.ok + per_report_statistcs.medium + per_report_statistcs.low) / all) * 100, 2),
            'pct_not_ok': round((not_ok / all) * 100, 2)
        })

    return stats


def get_report(account: Account, report_id: int):

    reports = list(UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).values())

    if not reports:
        return {}

    reports[0]['calculation'] = json.loads(reports[0]['calculation'])

    for report in reports:
        # perhaps we should already store this in the report. It does make the report a bit larger (which is ok?)
        remove_comply_or_explain(report)
        add_keyed_ratings(report)
        add_statistics_over_ratings(report)
        add_percentages_to_statistics(report)

    return reports


def get_previous_report(account: Account, urllist_id, at_when):
    report = UrlListReport.objects.all().filter(
        urllist_id=urllist_id,
        urllist__account=account,
        urllist__is_deleted=False,
        at_when__lt=at_when).order_by('-at_when').values('pk').first()
    if not report:
        return {}

    return get_report(account, report['pk'])[0]


def remove_comply_or_explain(report):
    # Also remove all comply or explain information as it costs a lot of data/memory on the client

    for url in report['calculation']['urls']:
        for endpoint in url['endpoints']:
            for rating in endpoint['ratings']:
                del rating['comply_or_explain_explanation']
                del rating['comply_or_explain_explained_on']
                del rating['comply_or_explain_explanation_valid_until']
                del rating['comply_or_explain_valid_at_time_of_report']


def add_keyed_ratings(report):
    # Re-key the issues so they can be instantly addressed.
    # This makes it less work / iterations to get certain data

    for url in report['calculation']['urls']:
        for endpoint in url['endpoints']:
            endpoint['ratings_by_type'] = {}
            for rating in endpoint['ratings']:
                endpoint['ratings_by_type'][rating['type']] = rating


def add_statistics_over_ratings(report):
    # works only after ratings by type.
    report['statistics_per_issue_type'] = {}

    possible_issues = []

    for url in report['calculation']['urls']:
        for endpoint in url['endpoints']:
            possible_issues += endpoint['ratings_by_type'].keys()
    possible_issues = set(possible_issues)

    # prepare the stats dict to have less expensive operations in the 3x nested loop
    for issue in possible_issues:
        # todo: could be a defaultdict. although explicit initialization is somewhat useful.
        report['statistics_per_issue_type'][issue] = {'high': 0, 'medium': 0, 'low': 0, 'ok': 0, 'not_ok': 0,
                                                      'not_testable': 0, 'not_applicable': 0}

    # count the numbers, can we do this with some map/add function that is way faster?
    for issue in possible_issues:
        for url in report['calculation']['urls']:
            for endpoint in url['endpoints']:
                rating = endpoint['ratings_by_type'].get(issue, None)
                if not rating:
                    continue
                report['statistics_per_issue_type'][issue]['high'] += rating['high']
                report['statistics_per_issue_type'][issue]['medium'] += rating['medium']
                report['statistics_per_issue_type'][issue]['low'] += rating['low']
                report['statistics_per_issue_type'][issue]['not_testable'] += rating['not_testable']
                report['statistics_per_issue_type'][issue]['not_applicable'] += rating['not_applicable']

                # things that are not_testable or not_applicable do not have impact on thigns being OK
                # see: https://github.com/internetstandards/Internet.nl-dashboard/issues/68
                if not any([rating['not_testable'], rating['not_applicable']]):
                    report['statistics_per_issue_type'][issue]['ok'] += rating['ok']
                    report['statistics_per_issue_type'][issue]['not_ok'] += \
                        rating['high'] + rating['medium'] + rating['low']


def add_percentages_to_statistics(report):
    for key, value in report['statistics_per_issue_type'].items():
        issue = report['statistics_per_issue_type'][key]
        all = issue['ok'] + issue['not_ok']

        report['statistics_per_issue_type'][key]['pct_high'] = round((issue['high'] / all) * 100, 2)
        report['statistics_per_issue_type'][key]['pct_medium'] = round((issue['medium'] / all) * 100, 2)
        report['statistics_per_issue_type'][key]['pct_low'] = round((issue['low'] / all) * 100, 2)

        # warning (=medium) and info(=low) do NOT have a score impact, only high has a score impact.
        # https://www.internet.nl/faqs/report/
        report['statistics_per_issue_type'][key]['pct_ok'] = round(
            ((issue['ok'] + issue['low'] + issue['medium']) / all) * 100, 2)

        report['statistics_per_issue_type'][key]['pct_not_ok'] = round((issue['not_ok'] / all) * 100, 2)
