import logging

from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import \
    check_running_scans

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Checks running internet nl scans."""

    help = __doc__

    def handle(self, *args, **options):
        check_running_scans()
