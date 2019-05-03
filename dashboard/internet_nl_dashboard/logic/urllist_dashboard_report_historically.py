import logging
from typing import List

from celery import group
from websecmap.celery import Task, app

from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllist_on_moment
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport, AccountInternetNLScan

log = logging.getLogger(__package__)


def compose_task(**kwargs
                 ) -> Task:
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [rate_urllists_historically.si([urllist]) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def rate_urllists_historically(urllists: List[UrlList]):

    # todo: this now crashes
    # todo: create reports at the moments scans where finished, instead of at random moments...

    # take into account it's possible urls have been added that influence the history of this rating.
    UrlListReport.objects.all().filter(urllist__in=urllists).delete()

    scans = AccountInternetNLScan.objects.all().filter(urllist__in=urllists, urllist__is_deleted=False,
                                                       scan__finished=True)

    for scan in scans:
        rate_urllist_on_moment(scan.urllist, scan.scan.finished_on)
