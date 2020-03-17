from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.management.commands.test_api_1_1 import submit_scan

API_URL = "https://test.batch.internet.nl/api/batch/v1.1/web/"


class Command(BaseCommand):
    def handle(self, *args, **options):
        submit_scan(API_URL)
