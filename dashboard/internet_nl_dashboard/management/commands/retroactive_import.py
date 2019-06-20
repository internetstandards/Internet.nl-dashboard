import logging
from argparse import ArgumentTypeError
from django.db import transaction

from django.core.management.base import BaseCommand
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, InternetNLScan
from websecmap.scanners.scanner.internet_nl_mail import get_scan_status, API_URL_MAIL

from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList

log = logging.getLogger(__package__)

REPORT_BASE_URL = 'https://batch.internet.nl/api/batch/v1.1/results/'

"""
forum_standardisation_magazine_2019_reports:
https://magazine.forumstandaardisatie.nl/nl_NL/13737/195378/cover.html

dashboard retroactive_import --report-id=e738da28c0724e188dc808580fdcdf0e --scan-type=web --account-id=2
dashboard retroactive_import --report-id=68a44dbfb2634d939d8d608ed250e841 --scan-type=web --account-id=2
dashboard retroactive_import --report-id=83197bb1398746e299042183d6b37ab0 --scan-type=web --account-id=2
dashboard retroactive_import --report-id=724e93b2f64f4c3fb04ef3997b23d0a6 --scan-type=web --account-id=2
dashboard retroactive_import --report-id=6de3fda3265c4c0e83fbafdd56401cd5 --scan-type=web --account-id=2
dashboard retroactive_import --report-id=b7dd7f5b7d4049c79ee6e40c12cd6495 --scan-type=mail_dashboard --account-id=2
dashboard retroactive_import --report-id=f95466dfd1de42ebbe809d12145f3fe0 --scan-type=mail_dashboard --account-id=2
dashboard retroactive_import --report-id=300958ee114946cb8bda18118f86d7d6 --scan-type=mail_dashboard --account-id=2
dashboard retroactive_import --report-id=af6f08a240224f9aa30840e5ecc2ce59 --scan-type=mail_dashboard --account-id=2
dashboard retroactive_import --report-id=600747412c2b48f796b43acd7c5e79dc --scan-type=mail_dashboard --account-id=2
"""

# todo: the reachability of the reported urls might be different on the scan day. This might result that
# some scan results are not included as the endpoint is not reachable anymore... In the test case this is not a problem
# as everything is reachable.


class Command(BaseCommand):
    help = 'Retroactively import reports.'

    def add_arguments(self, parser):
        parser.add_argument('--report-id', type=validate_report_id, required=True,
                            help='Before starting server run Django migrations.')
        parser.add_argument('--scan-type', type=validate_scan_type, required=True,
                            help='web, mail or mail_dashboard (internet.nl dashboard).')
        parser.add_argument('--account-id', required=True,
                            help='To what account to associate results to.',
                            type=validate_account)

        super().add_arguments(parser)

    def handle(self, *args, **options):
        retroactively_import(options)
        log.info('All done!')


def validate_account(s):
    account = Account.objects.all().filter(id=s).first()
    if not account:
        raise ArgumentTypeError("Given account ID is not a existing account.")

    return s


def validate_report_id(s):
    if len(s) != 32:
        raise ArgumentTypeError("report_id is a hexidecamal string of 32 characters")

    return s


def validate_scan_type(s):

    if s not in ['web', 'mail', 'mail_dashboard']:
        raise ArgumentTypeError("Scan type can only be web, mail or mail_dashboard")

    return s


@transaction.atomic
def retroactively_import(report):
    account = Account.objects.all().get(pk=report['account_id'])
    log.debug(f"Retroactively trying to import a scan from account "
              f"{account} with username {account.internet_nl_api_username}")

    report_url = f"{REPORT_BASE_URL}{report['report_id']}/"
    log.debug(f"The report will be stored at {report_url}")

    log.debug("Step 0: check if the report already has been created. In that case, all urls and such would already "
              "be available.")
    exists = AccountInternetNLScan.objects.all().filter(scan__status_url=report_url, account=account).first()
    if exists:
        raise ImportError(f"This scan already exists in the database, try a re-import. "
                          f"See AccountInternetNLScan {exists.id}.")

    log.debug("Step 1: download report.")
    response = get_scan_status(report_url, account.internet_nl_api_username, account.decrypt_password())
    if valid_response(response):
        new_list = retroactively_add_domains_and_endpoints_from_report(response, report['scan_type'], account)

        log.debug("Step 6: fake the scan so the normal procedure for importing and reporting works")
        retroactively_add_scan(report, account, new_list)

        log.debug("Step 7: This should be it, check for updates on the scan using periodic tasks and create "
                  "updates that way.")
        log.info(f"Created urls for report {report['report_id']} of type {report['scan_type']}")


def valid_response(report_response):
    if report_response['success'] is False:
        raise ImportError(report_response['message'])

    return True


def retroactively_add_scan(report, account, urllist):
    scan = InternetNLScan()

    # The scan is already perfomed and complete. This means finished=True.
    scan.finished = True
    scan.success = True
    scan.status_url = f"{REPORT_BASE_URL}/{report['report_id']}/"
    scan.type = report['scan_type']
    scan.finished_on = timezone.now()
    scan.started_on = timezone.now()
    scan.started = True
    scan.message = "Imported manually"
    scan.friendly_message = "Imported manually"
    scan.last_check = timezone.now()
    scan.save()

    accountscan = AccountInternetNLScan()
    accountscan.account = account
    accountscan.urllist = urllist
    accountscan.scan = scan
    accountscan.save()


def retroactively_add_domains_and_endpoints_from_report(http_response, scan_type, account):
    log.debug("Step 2: create list with urls from the report, with associated endpoints.")
    new_list = UrlList()
    new_list.name = http_response.get('data', {}).get('name', 'unnamed list')
    new_list.account = account
    new_list.scan_type = scan_type
    new_list.enable_scans = False
    new_list.save()

    log.debug("Step 3: add all urls from the report to the database.")
    domains = http_response.get('data', {}).get('domains', {})
    new_urls = []
    for domain in domains:
        new_urls.append(domain['domain'])

    log.debug("Step 4: Make sure that all these urls get an endpoint that matches the scan type.")
    # The endpoint must be alive.
    scan_type_to_protocol = {'mail': 'dns_mx_no_cname', 'mail_dashboard': 'dns_soa', 'web': 'dns_a_aaaa'}

    for new_url in new_urls:
        existing_endpoint = Endpoint.objects.all().filter(
            protocol=scan_type_to_protocol[scan_type], url__url=new_url, is_dead=False).first()
        if not existing_endpoint:
            ep = Endpoint()
            ep.url = Url.objects.all().filter(url=new_url).first()
            ep.discovered_on = timezone.now()
            ep.port = 0
            ep.ip_version = 0
            ep.protocol = scan_type_to_protocol[scan_type]
            ep.is_dead = False
            ep.save()

    log.debug("Step 5: add all urls to a list, so a report on that list can be created.")
    debug_output = _add_to_urls_to_urllist(account, new_list, new_urls)
    log.info(debug_output)

    return new_list
