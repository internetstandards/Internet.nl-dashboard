import logging
from copy import deepcopy
from datetime import datetime, timedelta
from typing import List, Set

import pytz
from celery import group
from deepdiff import DeepDiff

from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport
from websecmap.celery import Task, app
from websecmap.organizations.models import Url
from websecmap.reporting.report import (aggegrate_url_rating_scores, get_latest_urlratings_fast,
                                        relevant_urls_at_timepoint)

log = logging.getLogger(__package__)

# todo: determine the moments things changed, using timeline.


def compose_task(**kwargs) -> Task:
    urllists = UrlList.objects.filter()
    tasks = [rate_urllists_now.si([urllist]) for urllist in urllists]
    return group(tasks)


@app.task(queue='storage')
def rate_urllists_now(urllists: List[UrlList]):
    for urllist in urllists:
        now = datetime.now(pytz.utc)
        rate_urllist_on_moment(urllist, now)


@app.task(queue='storage')
def rate_urllists_historically(urllists: List[UrlList]):
    # weekly, and for the last 14 days daily. 64 calculations
    # maybe this is not precise enough...
    weeks: List[datetime] = [datetime.now(pytz.utc) - timedelta(days=t) for t in range(365, 0, -7)]
    weeks += [datetime.now(pytz.utc) - timedelta(days=t) for t in range(14, 0, -1)]
    dates: Set[datetime] = set(weeks)

    today = datetime.now(pytz.utc).date()

    # round off days to the latest possible moment on that day, except for the last day, so to not overwrite.
    # note that if this is run every day, you'll still get reports for all days where things change (more inefficiently)
    dates = set([x.replace(hour=23, minute=59, second=59, microsecond=9999999) for x in dates if x.date() is not today])

    for urllist in urllists:
        for date in dates:
            rate_urllist_on_moment(urllist, date)


def rate_urllist_on_moment(urllist: UrlList, when: datetime = None):
    # If there is no time slicing, then it's today.
    if not when:
        when = datetime.now(pytz.utc)

    log.info("Creating report for urllist %s on %s" % (urllist, when, ))

    if UrlListReport.objects.all().filter(urllist=urllist, when=when).exists():
        log.debug("UrllistReport already exists for %s on %s. Not overwriting." % (urllist, when))
        return

    urls = relevant_urls_at_timepoint_urllist(urllist=urllist, when=when)
    all_url_ratings = get_latest_urlratings_fast(urls, when)
    scores = aggegrate_url_rating_scores(all_url_ratings)

    try:
        last = UrlListReport.objects.filter(urllist=urllist, when__lte=when).latest('when')
    except UrlListReport.DoesNotExist:
        last = UrlListReport()  # create a dummy one for comparison

    scores['name'] = urllist.name

    if not DeepDiff(last.calculation, scores, ignore_order=True, report_repetition=True):
        log.warning("The report for %s on %s is the same as the previous one. Not saving." % (urllist, when))
        return

    log.info("The calculation for %s on %s has changed, so we're saving this rating." % (urllist, when))

    # remove urls and name from scores object, so it can be used as initialization parameters (saves lines)
    # this is by reference, meaning that the calculation will be affected if we don't work on a clone.
    init_scores = deepcopy(scores)
    del(init_scores['name'])
    del(init_scores['urls'])

    report = UrlListReport(**init_scores)
    report.urllist = urllist
    report.when = when
    report.calculation = scores
    report.save()


def relevant_urls_at_timepoint_urllist(urllist: UrlList, when: datetime):
    queryset = Url.objects.filter(urls_in_dashboard_list=urllist)

    return relevant_urls_at_timepoint(queryset=queryset, when=when)
