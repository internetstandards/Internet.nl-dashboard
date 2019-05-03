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
            'created_on': report.at_when,
            'urllist_id': report.urllist.id,
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
        not_ok = per_report_statistcs.high + per_report_statistcs.medium + per_report_statistcs.low
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

            # todo: these numbers might be added to the statics calculation?
            'not_ok': not_ok,
            'total_findings': not_ok + per_report_statistcs.low,
            'pct_ok': round((per_report_statistcs.ok / all) * 100, 2),
            'pct_not_ok': round((not_ok / all) * 100, 2)
        })

    return stats


def get_report(account: Account, report_id: int):

    report = list(UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).values())

    if not report:
        return {}

    report[0]['calculation'] = json.loads(report[0]['calculation'])

    return report
