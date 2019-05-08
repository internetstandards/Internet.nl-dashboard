import logging

from celery import group
from websecmap.celery import Task, app

from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllist_on_moment
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport, AccountInternetNLScan

log = logging.getLogger(__package__)


def compose_task(**kwargs
                 ) -> Task:
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [create_reports_on_finished_scans.si(urllist) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def create_reports_on_finished_scans(urllist: UrlList):
    """
    Figures out what scans have happened, and checks if there is a matching urllistreport. If there is not,
    a urllistreport will be created. This adds value to scan moments, as every finished scan will have a report.

    Algorithm
    Gets all the dates a urllistreport was made of a certain urllist. Then get all the dates when scans where made.
    The missing dates require a report made.

    It's ok to run this every minute. As this is a per scan basis and it's known that all scan results have been
    processed. This means you can have a report before the end of the day, nearly as soon as a scan is finished.

    :param urllist:
    :return:
    """

    scan_dates = set(AccountInternetNLScan.objects.all().filter(
        urllist=urllist,
        urllist__is_deleted=False,
        scan__finished=True,

        # only scans that have all results etc processed have finished on set to a date.
        scan__finished_on__isnull=False
    ).order_by('scan__finished_on').values_list('scan__finished_on', flat=True))

    # all reports are on 11:59 etc...
    scan_dates = set([date.replace(hour=23, minute=59, second=59, microsecond=999999) for date in scan_dates])

    report_dates = set(UrlListReport.objects.all().filter(
        urllist=urllist
    ).values_list('at_when', flat=True))

    missing_report_dates = scan_dates - report_dates

    for missing_report_date in missing_report_dates:
        # this will also find moments that had a scan completed, but nothing has changed.
        # To give a greater feeling of control and add value to 'scanning moments' each of these reports
        # should be added, even if it has the same content.
        log.info('Missing a report for list %s on %s. Creating it...' % (urllist, missing_report_date))
        rate_urllist_on_moment(urllist, missing_report_date, prevent_duplicates=False)
