# SPDX-License-Identifier: Apache-2.0
import logging

from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import overwrite_report

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = "Overwrite an existing report. This can be useful if the reporting logic has changed."

    def add_arguments(self, parser):
        parser.add_argument("--scan", type=int, required=True)
        super().add_arguments(parser)

    def handle(self, *args, **options):

        # See if we can find the scan
        if not options["scan"]:
            raise ValueError("No scan id given")

        scan = AccountInternetNLScan.objects.all().filter(scan=options["scan"]).first()

        if not scan:
            raise ValueError(f"Scan {options['scan']} does not exist")

        if not scan.report:
            raise ValueError(f"Scan {options['scan']} does not have a report attached")

        if not scan.report.at_when:
            raise ValueError(
                f"No report created for scan {options['scan']}, "
                "will not create a new report when the process is running."
            )

        overwrite_report(scan)
