import logging

from dashboard.internet_nl_dashboard.logic import urllist_dashboard_report
from websecmap.app.management.commands._private import ScannerTaskCommand

log = logging.getLogger(__name__)


class Command(ScannerTaskCommand):
    """Rebuild url ratings (fast) and add a report for today if things changed. Creates stats for two days."""

    help = __doc__

    def handle(self, *args, **options):

        try:
            self.scanner_module = urllist_dashboard_report
            return super().handle(self, *args, **options)
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt. Stopped.")
