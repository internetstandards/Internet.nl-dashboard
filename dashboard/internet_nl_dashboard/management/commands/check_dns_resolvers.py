# SPDX-License-Identifier: Apache-2.0
from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.check_dns import check_dns_resolvers


class Command(BaseCommand):
    def handle(self, *args, **options):
        check_dns_resolvers()
        print("Done!")
