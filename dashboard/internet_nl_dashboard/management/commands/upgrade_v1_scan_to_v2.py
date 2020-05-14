import logging

from django.utils import timezone
from websecmap.app.management.commands._private import ScannerTaskCommand
from websecmap.scanners.models import InternetNLScan, InternetNLV2Scan

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan

log = logging.getLogger(__name__)


class Command(ScannerTaskCommand):
    def handle(self, *args, **options):
        upgrade_v1_to_v2()


def upgrade_v1_to_v2():
    # create equivalent scans, to have all foreign keys in order.
    scans = InternetNLScan.objects.all()
    for scan in scans:
        s = InternetNLV2Scan()
        s.pk = scan.pk
        s.type = scan.type
        # Store the scan id, even though it's not backwards compatible.
        s.scan_id = scan.status_url[-33:-1] if scan.status_url else ""
        s.state = "finished"
        s.state_message = "Upgraded to api v2"
        s.last_state_check = timezone.now()
        s.last_state_change = timezone.now()
        s.save()

    # some fields have migrated to the dashboard
    aiiss = AccountInternetNLScan.objects.all()
    for aiis in aiiss:
        # we just moved the old scan data to the new one. Fetch the started_on and finished_on and state_changed_on
        if aiis.scan:
            old_scan = InternetNLScan.objects.filter(id=aiis.scan.pk).first()
            if old_scan:
                aiis.started_on = old_scan.started_on
                aiis.finished_on = old_scan.finished_on
                aiis.state_changed_on = old_scan.last_check
                aiis.save()
