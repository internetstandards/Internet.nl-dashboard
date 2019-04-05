import logging

from django.core.management.base import BaseCommand

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Command that helps during development. As i don\'t know how to test file creation.'

    def handle(self, *args, **options):
        from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet
        create_spreadsheet(41)
