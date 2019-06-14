import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint, InternetNLScan
from websecmap.scanners.scanner.internet_nl_mail import get_scan_status

from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Command that helps during development. As i don\'t know how to test file creation.'

    def handle(self, *args, **options):
        """
        scan_type = 'mail' or 'web'
        api_username = ''
        api_password = ''
        api_url =
        dashboard_account = ID (2)

        :param args:
        :param options:
        :return:
        """

        # so everything fits in one line instead of 3
        api_url = 'https://batch.internet.nl/api/batch/'
        forum_standardisation_magazine_2019_reports = [
            {'url': api_url + 'v1.1/results/e738da28c0724e188dc808580fdcdf0e/', 'type': 'web'},
            {'url': api_url + 'v1.1/results/68a44dbfb2634d939d8d608ed250e841/', 'type': 'web'},
            {'url': api_url + 'v1.1/results/83197bb1398746e299042183d6b37ab0/', 'type': 'web'},
            {'url': api_url + 'v1.1/results/724e93b2f64f4c3fb04ef3997b23d0a6/', 'type': 'web'},
            {'url': api_url + 'v1.1/results/6de3fda3265c4c0e83fbafdd56401cd5/', 'type': 'web'},

            {'url': api_url + 'v1.1/results/b7dd7f5b7d4049c79ee6e40c12cd6495/', 'type': 'mail_dashboard'},
            {'url': api_url + 'v1.1/results/f95466dfd1de42ebbe809d12145f3fe0/', 'type': 'mail_dashboard'},
            {'url': api_url + 'v1.1/results/300958ee114946cb8bda18118f86d7d6/', 'type': 'mail_dashboard'},
            {'url': api_url + 'v1.1/results/af6f08a240224f9aa30840e5ecc2ce59/', 'type': 'mail_dashboard'},
            {'url': api_url + 'v1.1/results/600747412c2b48f796b43acd7c5e79dc/', 'type': 'mail_dashboard'},
        ]

        account = Account.objects.all().get(pk=2)

        retroactively_import(forum_standardisation_magazine_2019_reports, account)


def retroactively_import(reports, account):

    log.info(f'Retroactively adding {len(reports)} reports to the database for account {account}.')

    for report in reports:
        # Step 1: download report, Step 2, 3, 4 and 5 included.
        response = get_scan_status(report['url'], account.internet_nl_api_username, account.decrypt_password())
        new_list = retroactively_add_domains_and_endpoints_from_report(response, report['type'], account)

        # Step 6: fake the scan so the normal procedure for importing and reporting works
        retroactively_add_scan(report, account, new_list)

        # Step 7: This should be it, check for updates on the scan using periodic tasks and create updates that way.
        log.info(f"Created urls for report {report['url']} or type {report['type']}")

    log.info('All done!')


def retroactively_add_scan(report, account, urllist):
    scan = InternetNLScan()
    scan.finished = False
    scan.status_url = report['url']
    scan.type = report['type']
    scan.finished_on = timezone.now()
    scan.started_on = timezone.now()
    scan.started = True
    scan.friendly_message = "Imported manually"
    scan.last_check = timezone.now()
    scan.save()

    accountscan = AccountInternetNLScan()
    accountscan.account = account
    accountscan.urllist = urllist
    accountscan.scan = scan
    accountscan.save()


def retroactively_add_domains_and_endpoints_from_report(http_response, scan_type, account):
    # Step 2: create list with urls from the report, with associated endpoints
    new_list = UrlList()
    new_list.name = http_response.get('data', {}).get('name', 'unnamed list')
    new_list.account = account
    new_list.scan_type = scan_type
    new_list.enable_scans = False
    new_list.save()

    # Step 3: add all urls from the report to the database.
    domains = http_response.get('data', {}).get('domains', {})
    new_urls = []
    for domain in domains:
        new_urls.append(domain['domain'])

    # Step 4: Make sure that all these urls get an endpoint that matches the scan type
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

    # Step 5: add all urls to a list, so a report on that list can be created.
    debug_output = _add_to_urls_to_urllist(account, new_list, new_urls)
    log.info(debug_output)

    return new_list
