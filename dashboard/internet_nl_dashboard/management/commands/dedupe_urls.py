# SPDX-License-Identifier: Apache-2.0
from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.logic.deduplication import dedupe_urls


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting")
        dedupe_urls()
        print("Done")
