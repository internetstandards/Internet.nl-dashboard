# SPDX-License-Identifier: Apache-2.0
from django.core.management import BaseCommand

from dashboard.internet_nl_dashboard.logic.internet_nl_translations import convert_internet_nl_content_to_vue


class Command(BaseCommand):
    """Get and replace the latest translation files from internet.nl"""

    help = __doc__

    def handle(self, *args, **options):
        convert_internet_nl_content_to_vue()
