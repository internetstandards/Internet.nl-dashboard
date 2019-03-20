import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import UrlList

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Resets all urllists in the database, if you made too many during development'

    def handle(self, *args, **options):

        if not settings.DEBUG:
            log.info('Can only be used in development environment.')

        UrlList.objects.all().delete()
