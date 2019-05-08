import logging

from websecmap.app.management.commands._private import ScannerTaskCommand

from dashboard.internet_nl_dashboard.logic import ammend_reports

log = logging.getLogger(__name__)


class Command(ScannerTaskCommand):
    """Rebuild url ratings (fast) and add a report for today if things changed. Creates stats for two days."""

    help = __doc__

    def handle(self, *args, **options):

        try:
            self.scanner_module = ammend_reports
            return super().handle(self, *args, **options)
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt. Stopped.")
