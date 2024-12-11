# SPDX-License-Identifier: Apache-2.0
import logging
from uuid import uuid4

from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import UrlListReport

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = "Upgrades reports to early 2020 style, which is faster and more complete."

    def handle(self, *args, **options):
        add_share_codes_to_reports()


def add_share_codes_to_reports():
    reports = UrlListReport.objects.all()

    for report in reports:

        if report.public_report_code:
            continue

        report.public_report_code = str(uuid4())
        report.save()
