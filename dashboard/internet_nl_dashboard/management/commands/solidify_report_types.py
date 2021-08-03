from django.core.management.base import BaseCommand
from dashboard.internet_nl_dashboard.models import UrlListReport


class Command(BaseCommand):
    def handle(self, *args, **options):

        for report in UrlListReport.objects.all():
            report.report_type = report.urllist.scan_type
            report.save()

    print("Updated")
