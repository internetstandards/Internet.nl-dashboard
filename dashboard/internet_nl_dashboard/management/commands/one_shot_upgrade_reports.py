# SPDX-License-Identifier: Apache-2.0
import logging

from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan, UrlListReport
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import (upgrade_report_with_statistics,
                                                                                   upgrade_report_with_unscannable_urls)

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Upgrades reports to early 2020 style, which is faster and more complete.'

    def handle(self, *args, **options):

        reports = UrlListReport.objects.all()

        for report in reports:

            # see if the report is not upgraded:
            if "explained_high" not in report.calculation:
                log.debug(f"Report {report} was already upgraded.")
                continue

            upgrade_report_with_statistics(report)

            # figure out which scan this report belongs to:
            # This will probably mess up older list content
            scan = AccountInternetNLScan.objects.all().filter(urllist=report.urllist).last()
            upgrade_report_with_unscannable_urls(report, scan)

            log.debug(f"Report {report} upgraded.")
