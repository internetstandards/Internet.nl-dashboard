import logging
from modulefinder import Module
from typing import List

from celery import Task, group
from websecmap.reporting.report import recreate_url_reports

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllist_on_moment
from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlList, UrlListReport
from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import \
    create_dashboard_scan_tasks

log = logging.getLogger(__name__)

# Todo: after rebuilding the virtual environment and removing this tasks.py file, the tasks from scan_internet_nl_
#   per_account where still discovered, and the tasks in tasks.py (below) where not. One difference is @app was defined
#   from websecmap.celery, not from dashboard.celery. Which still doesn't solve it after changing.


@app.task(queue='storage')
def start_scans_for_lists_who_are_up_for_scanning() -> Task:
    """
    This can be run every minute, only the ones that are up for scanning will be scanned. It will update all
    urllists (even delted and not eligeble for scanning) so that a next scan is happening on the right time.
    """

    tasks = []

    for urllist in UrlList.objects.all().filter():
        # this also gets the lists that are not scanned. The scan date needs to progress, otherwise it will be
        # scanned instantly when the list will be enabled. This also goes for deleted lists.
        if urllist.enable_scans is False or urllist.is_deleted is True:
            urllist.renew_scan_moment()
            continue

        if urllist.is_due_for_scanning():
            tasks.append(create_dashboard_scan_tasks(urllist))

        # placed here, as otherwise the list is never due for scanning as the date might be updated to something
        # new in the future.
        urllist.renew_scan_moment()

    # using this in create_function_job so a job is created, allowing for tracking this a bit
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

    # make sure that the latest urlreports are created... otherwise outdated data / no data will be used.
    recreate_url_reports(urllist.urls)

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


# explicitly declare the imported modules as this modules 'content', prevents pyflakes issues
__all__: List[Module] = [scan_internet_nl_per_account]
