import logging

from celery import group
from websecmap.celery import Task

from dashboard.internet_nl_dashboard.models import UrlList
from dashboard.internet_nl_dashboard.tasks import create_reports_on_finished_scans

log = logging.getLogger(__package__)


def compose_task(**kwargs
                 ) -> Task:
    urllists = UrlList.objects.filter(is_deleted=False)
    tasks = [create_reports_on_finished_scans.si(urllist) for urllist in urllists]
    return group(tasks)
