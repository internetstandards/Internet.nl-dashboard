import json
import logging
import re
from copy import copy
from typing import List

from actstream import action
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

    # Sprinkling an activity stream action.
    log_report = UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist__is_deleted=False,
        pk=report_id
    ).only('id').first()
    action.send(account, verb='viewed report', target=log_report, public=False)

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

    if "explained_high" not in report.calculation:
        report.save()
        return

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


def clean_up_not_required_data_to_speed_up_report_on_client(report: UrlListReport):
    """
    Loading in JSON objects in the client takes (a lot of) time. The larger the object, the more time.
    Especially with 500+ urls, shaving off data increases parse speed with over 50%. So this is a must

    :param report:
    :return:
    """

    for url in report.calculation['urls']:
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
                del endpoint['ratings_by_type'][rating_key]['since']
                del endpoint['ratings_by_type'][rating_key]['last_scan']
                del endpoint['ratings_by_type'][rating_key]['explanation']

                del endpoint['ratings_by_type'][rating_key]['type']  # is already in the key
                del endpoint['ratings_by_type'][rating_key]['scan_type']  # is already in the key

            # remove the original rating, as that slows parsing on the client down significantly.
            # with significantly == Vue will parse it, and for a 500 url list this will take 5 seconds.
            endpoint['ratings'] = []

    report.save()


def add_simple_verdicts(report: UrlListReport):
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

        'failed': 100,
        'warning': 200,
        'info': 300,

        # todo: still not clear what good_not_tested means.
        'good_not_tested': 380,
        'passed': 400,
    }

    for url in report.calculation['urls']:
        for endpoint in url['endpoints']:
            for rating in endpoint['ratings']:
                rating['simple_progression'] = progression_table.get(rating.get('test_result', ''), 0)

    report.save()


def split_score_and_url(report: UrlListReport):
    """
    Split the internet.nl score and the url to be instantly accessible.

    :param report:
    :return:
    """
    for url in report.calculation['urls']:
        for endpoint in url['endpoints']:
            score = 0
            url = ""
            scan = 0
            since = ""
            last_scan = ""
            for rating in endpoint['ratings']:
                if rating['type'] in ["internet_nl_web_overall_score", "internet_nl_mail_dashboard_overall_score"]:
                    # explanation	"78 https://batch.interne…zuiderzeeland.nl/886818/"
                    explanation = rating['explanation'].split(" ")
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
                    'test_result': score,
                    "scan": scan,
                    "since": since,
                    "last_scan": last_scan,
                    "explanation": "",
                }
            )

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

        # internet_nl_web_appsecpriv category is labelled as high, probably for some reason (could not find it quickly)
        # but the category is a medium category, which means the score should _always_ be 100.
        # So in this special case we will overwrite the pct_ok with 100%, even though it's lower:
        if key == "internet_nl_web_appsecpriv":
            report.calculation['statistics_per_issue_type'][key]['pct_ok'] = 100

    report.save()
