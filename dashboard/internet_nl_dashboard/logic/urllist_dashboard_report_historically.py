import logging
from datetime import datetime, timedelta
from typing import List

import pytz
from celery import group
from websecmap.celery import Task, app
from websecmap.pro.urllist_report import rate_urllist_on_moment

from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport

log = logging.getLogger(__package__)


def compose_task(**kwargs
                 ) -> Task:
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [rate_urllists_historically.si([urllist]) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def rate_urllists_historically(urllists: List[UrlList]):

    # take into account it's possible urls have been added that influence the history of this rating.
    UrlListReport.objects.all().filter(urllist__in=urllists).delete()

    # weekly, and for the last 14 days daily. 64 calculations
    # maybe this is not precise enough...
    weeks = [datetime.now(pytz.utc) - timedelta(days=t) for t in range(365, 0, -7)]
    weeks += [datetime.now(pytz.utc) - timedelta(days=t) for t in range(14, 0, -1)]
    dates = set(weeks)

    today = datetime.now(pytz.utc).date()

    # round off days to the latest possible moment on that day, except for the last day, so to not overwrite.
    # note that if this is run every day, you'll still get reports for all days where things change (more inefficiently)
    dates = set([x.replace(hour=23, minute=59, second=59, microsecond=999999) for x in dates if x.date() is not today])

    for urllist in urllists:
        for date in dates:
            rate_urllist_on_moment(urllist, date)
