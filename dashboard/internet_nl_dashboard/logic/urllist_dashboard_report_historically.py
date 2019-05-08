import logging
from typing import List

from celery import group
from websecmap.celery import Task, app

from dashboard.internet_nl_dashboard.logic.urllist_dashboard_report import rate_urllist_on_moment
from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlList, UrlListReport

log = logging.getLogger(__package__)


def compose_task(**kwargs
                 ) -> Task:
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [rate_urllists_historically.si([urllist]) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def rate_urllists_historically(urllists: List[UrlList]):
    log.warning('Make sure your url reports are up to date! Run rebuild_url_reports to be sure.')

    # take into account it's possible urls have been added that influence the history of this rating.
    UrlListReport.objects.all().filter(urllist__in=urllists).delete()

    scans = AccountInternetNLScan.objects.all().filter(
        urllist__in=urllists,
        urllist__is_deleted=False,
        scan__finished=True,

        # only scans that have all results etc processed have finished on set to a date.
        scan__finished_on__isnull=False
    ).order_by('scan__finished_on')

    for scan in scans:
        # So the storage of the result has catched up. (Usually 'finished on' is in many cases the same second etc as
        # the moment some scan results were written to the database.
        # Also: urls are rated only once a day (since there can be many, many results at different moments throughout
        # the day. Which would cause insane amounts of data otherwise. So we will have to set the moment of finished
        # on to the last minute and seocnd of the day. Then it will work fine.

        # todo: make a 'complete reports' that writes reports for all urllists on all scan moments and only adds where
        # they don't exist. This way only new reports are written and keys for reports stay the same (which is relevant)
        moment = scan.scan.finished_on.replace(hour=23, minute=59, second=59, microsecond=999999)
        rate_urllist_on_moment(scan.urllist, moment)
