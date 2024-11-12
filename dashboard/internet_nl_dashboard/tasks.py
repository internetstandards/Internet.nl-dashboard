# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime, timedelta, timezone
from modulefinder import Module
from typing import List

from celery import Task, group
from constance import config

from dashboard.celery import app
from dashboard.internet_nl_dashboard.models import UrlList, UrlListReport
from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account, subdomains
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import initialize_scan

log = logging.getLogger(__name__)

# Todo: after rebuilding the virtual environment and removing this tasks.py file, the tasks from scan_internet_nl_
#   per_account where still discovered, and the tasks in tasks.py (below) where not. One difference is @app was defined
#   from websecmap.celery, not from dashboard.celery. Which still doesn't solve it after changing.


@app.task(queue="storage")
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
            tasks.append(initialize_scan.si(urllist.id))

        # placed here, as otherwise the list is never due for scanning as the date might be updated to something
        # new in the future.
        urllist.renew_scan_moment()

    # using this in create_function_job so a job is created, allowing for tracking this a bit
    return group(tasks)


# explicitly declare the imported modules as this modules 'content', prevents pyflakes issues
# Todo: List item 0 has incompatible type Module; expected Module
__all__: List[Module] = [scan_internet_nl_per_account, subdomains]  # type: ignore


@app.task(queue="storage", ignore_result=True)
def autoshare_report_to_front_page():
    ids = config.DASHBOARD_FRONT_PAGE_URL_LISTS
    if not ids:
        return

    ids = ids.split(",")

    ints = [int(id_) for id_ in ids]

    # Do not publish historic reports, things can actually stay offline if there was an error with a report
    UrlListReport.objects.filter(
        urllist__id__in=ints, at_when__gte=datetime.now(timezone.utc) - timedelta(hours=24)
    ).update(
        is_publicly_shared=True,
        is_shared_on_homepage=True,
    )
