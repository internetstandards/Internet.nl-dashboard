import logging

from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import \
    check_running_scans
from websecmap.app.management.commands._private import TaskCommand

log = logging.getLogger(__name__)


class Command(TaskCommand):

    def handle(self, *args, **options):

        try:
            return super().handle(self, *args, **options)
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt. Stopped.")

    def compose(self, *args, **options):
        return check_running_scans()
