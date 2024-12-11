# SPDX-License-Identifier: Apache-2.0
import logging

from websecmap.app.management.commands._private import TaskCommand

from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import check_running_dashboard_scans

log = logging.getLogger(__name__)


class Command(TaskCommand):

    def add_arguments(self, parser):
        # https://stackoverflow.com/questions/8259001/python-argparse-command-line-flags-without-arguments
        parser.add_argument("--reimport", action="store_true", help="Execute the task directly or on remote workers.")

        return super().add_arguments(parser)

    def handle(self, *args, **options):

        try:
            return super().handle(self, *args, **options)
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt. Stopped.")
            return "{}"

    def compose(self, *args, **options):
        model_filter = {}

        if options["reimport"]:
            model_filter = {"accountinternetnlscan_filter": {"scan__finished": False}}

        return check_running_dashboard_scans(**model_filter)
