import logging

from websecmap.app.management.commands._private import ScannerTaskCommand

from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account

log = logging.getLogger(__name__)


class Command(ScannerTaskCommand):
    def handle(self, *args, **options):

        try:
            self.scanner_module = scan_internet_nl_per_account
            return super().handle(self, *args, **options)

        except KeyboardInterrupt:
            log.info("Received keyboard interrupt. Stopped.")
