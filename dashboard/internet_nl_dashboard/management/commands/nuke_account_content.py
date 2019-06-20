import logging
from argparse import ArgumentTypeError
from django.db import transaction

from django.core.management.base import BaseCommand
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, InternetNLScan
from websecmap.scanners.scanner.internet_nl_mail import get_scan_status, API_URL_MAIL

from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList, UrlListReport
from django.conf import settings

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Removes all user generated content of a user'

    def add_arguments(self, parser):
        parser.add_argument('--account-id', required=True,
                            help='To what account to associate results to.',
                            type=validate_account)

        super().add_arguments(parser)

    def handle(self, *args, **options):

        # if not settings.DEBUG:
        #     raise SystemError("Can only nuke account contents while debugging.")

        account = Account.objects.all().filter(id=options['account_id']).first()

        # No Reports
        UrlListReport.objects.all().filter(urllist__account=account).delete()

        # No lists
        UrlList.objects.all().filter(account=account).delete()

        # No scans
        AccountInternetNLScan.objects.all().filter(account=account).delete()


def validate_account(s):
    account = Account.objects.all().filter(id=s).first()
    if not account:
        raise ArgumentTypeError("Given account ID is not a existing account.")

    return s