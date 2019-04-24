from typing import List

import simplejson as json

from dashboard.internet_nl_dashboard.models import Account, UrlList, UrlListReport


# todo: this delivers a very slow report. make it faster.
def get_recent_reports(account: Account) -> List:

    # loading the calculation takes some time. In this case we don't need the calculation and as such we defer it.
    reports = UrlListReport.objects.all().filter(
        urllist__account=account).order_by('-pk')[0:30].select_related(
        'urllist').defer('calculation')

    return create_report_response(reports)


def get_reports_from_urllist(account: Account, urllist: UrlList):
    reports = UrlListReport.objects.all().filter(
        urllist__account=account,
        urllist=urllist
    ).order_by('-pk')[0:5].select_related(
        'urllist')

    return create_report_response(reports)


def create_report_response(reports):
    response = []
    for report in reports:

        response.append({
            'id': report.id,
            # mask that there is a mail_dashboard variant.
            'type': report.urllist.scan_type,
            'number_of_urls': report.total_urls,
            'list_name': report.urllist.name,
            'created_on': report.at_when,
        })

    return response


def get_report(account: Account, report_id: int):

    report = list(UrlListReport.objects.all().filter(
        urllist__account=account,
        pk=report_id
    ).values())

    if not report:
        return {}

    report[0]['calculation'] = json.loads(report[0]['calculation'])
    return report
