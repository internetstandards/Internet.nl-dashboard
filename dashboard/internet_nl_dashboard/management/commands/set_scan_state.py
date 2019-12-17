import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.models import AccountInternetNLScan
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import update_state

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Example: set_scan_state id=7 state="create report"'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, required=True)
        parser.add_argument('--state', type=str, required=True)

        super().add_arguments(parser)

    def handle(self, *args, **options):

        if not settings.DEBUG:
            log.info('Can only be used in development environment.')

        if not options['id']:
            log.error('Specify the scan id: set_scan_state --id=7 --state="create report"')

        if not options['state']:
            log.error('specify the state: set_scan_state --id=7 --state="create report"')

        scan = AccountInternetNLScan.objects.all().filter(id=options['id']).first()
        if not scan:
            log.error("Scan does not exist.")

        scan.state = options['state']
        update_state(options['state'], scan)
        log.info(f"Scan {scan} is set to {options['state']}.")
