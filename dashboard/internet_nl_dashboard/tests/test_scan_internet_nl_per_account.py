# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.reporting.models import UrlReport
from websecmap.scanners.models import Endpoint, EndpointGenericScan, InternetNLV2Scan

from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan, UrlList,
                                                    UrlListReport)
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import (
    creating_report, monitor_timeout, processing_scan_results)

log = logging.getLogger(__package__)


def test_monitor_timeout(db):
    a = Account.objects.create()

    recoverable_states = ['discovering endpoints', 'retrieving scannable urls', 'registering scan at internet.nl']
    for rec_state in recoverable_states:
        scan = AccountInternetNLScan.objects.create(
            account=a,
            scan=InternetNLV2Scan.objects.create(),
            urllist=UrlList.objects.create(account=a),
            state=rec_state,
            state_changed_on=datetime(1996, 1, 1)
        )
        monitor_timeout(scan.id)
        updated_scan = AccountInternetNLScan.objects.get(id=scan.id)
        assert updated_scan.state_changed_on != datetime(1996, 1, 1)
        assert updated_scan.state_changed_on.year == datetime.now().year


def test_creating_report(db, redis_server, default_policy, default_scan_metadata):
    """
    We're entering the reporting phase, all data has been downloaded in the accountinternetnl scan, and
    a report will be generated. This includes statistics and such.

    This report will be able to deal with error situations, where a scan fully failed and all scan values are
    set to error. This is done with the vitesse.nl domain, as this occurred in real life.

    :return:
    """

    # preparing the data to use in this test:
    user, c = User.objects.all().get_or_create(first_name='testuser', last_name='test', username='test', is_active=True)
    account, c = Account.objects.all().get_or_create(name='testaccount')
    urllist, c = UrlList.objects.all().get_or_create(name='testlist', account=account)
    internetnlv2scan, c = InternetNLV2Scan.objects.all().get_or_create(type='web', scan_id=1,
                                                                       state='scan results stored')

    # fcwaalwijk is missing in the results, which is intended
    # note: also set discovered on and created on to a date in the past, otherwise they will not be in the report
    #  as they are not seen as relevant for the moment the report is made.
    for domain in ['vitesse.nl', 'dierenscheboys.nl', 'fcwaalwijk.nl']:
        mydomain, c = Url.objects.all().get_or_create(
            url=domain, is_dead=False, not_resolvable=False, created_on=datetime(2010, 1, 1))
        myendpoint, c = Endpoint.objects.all().get_or_create(
            url=mydomain, protocol='dns_a_aaaa', port=0, ip_version=0, is_dead=False, discovered_on=datetime(2010, 1, 1)
        )
        urllist.urls.add(mydomain)
        urllist.save()
        internetnlv2scan.subject_urls.add()

    accountinternetnlscan, c = AccountInternetNLScan.objects.all().get_or_create(
        account=account, scan=internetnlv2scan, urllist=urllist, started_on=timezone.now(),
        report=None, finished_on=None, state='scan results ready')

    # Add a separate endpoint to verify that error scores do not hinder creating reports or statistics:
    # 'internet_nl_mail_dashboard_overall_score', 'internet_nl_web_overall_score'
    vitesse_endpoint = Endpoint.objects.all().filter(url__url='vitesse.nl').first()
    EndpointGenericScan.objects.all().get_or_create(
        type='internet_nl_web_overall_score', rating="error", evidence="", endpoint=vitesse_endpoint,
        rating_determined_on=datetime(2010, 1, 1)
    )
    EndpointGenericScan.objects.all().get_or_create(
        type='web_https_tls_version', rating="failed", evidence="", endpoint=vitesse_endpoint,
        rating_determined_on=datetime(2010, 1, 1)
    )

    # here, vitesse.nl has an error from the API. This occurs when a crash happens in the api scanner, which is
    # rare, but can happen due to all kinds of weird setups it can encounter.
    internetnlv2scan.retrieved_scan_report = {
        'vitesse.nl': {'status': 'error'},
        'dierenscheboys.nl': {
            'status': 'ok',
            'report': {'url': 'https://batch.internet.nl/site/dierenscheboys.nl/219843/'},
            'scoring': {'percentage': 76}, 'results': {
                'categories': {'web_ipv6': {'verdict': 'failed', 'status': 'failed'},
                               'web_dnssec': {'verdict': 'passed', 'status': 'passed'},
                               'web_https': {'verdict': 'failed', 'status': 'failed'},
                               'web_appsecpriv': {'verdict': 'warning', 'status': 'warning'}},
                'tests': {'web_ipv6_ns_address': {'status': 'passed', 'verdict': 'good'},
                          'web_ipv6_ns_reach': {'status': 'passed', 'verdict': 'good'},
                          'web_ipv6_ws_address': {'status': 'failed', 'verdict': 'bad'},
                          'web_ipv6_ws_reach': {'status': 'not_tested', 'verdict': 'not-tested'},
                          'web_ipv6_ws_similar': {'status': 'not_tested', 'verdict': 'not-tested'},
                          'web_dnssec_exist': {'status': 'passed', 'verdict': 'good'},
                          'web_dnssec_valid': {'status': 'passed', 'verdict': 'good'},
                          'web_https_http_available': {'status': 'passed', 'verdict': 'good'},
                          'web_https_http_redirect': {'status': 'passed', 'verdict': 'good'},
                          'web_https_http_hsts': {'status': 'failed', 'verdict': 'bad'},
                          'web_https_http_compress': {'status': 'passed', 'verdict': 'good'},
                          'web_https_tls_keyexchange': {'status': 'failed', 'verdict': 'bad'},
                          'web_https_tls_ciphers': {'status': 'passed', 'verdict': 'good'},
                          'web_https_tls_cipherorder': {'status': 'warning', 'verdict': 'warning'},
                          'web_https_tls_version': {'status': 'warning', 'verdict': 'phase-out'},
                          'web_https_tls_compress': {'status': 'passed', 'verdict': 'good'},
                          'web_https_tls_secreneg': {'status': 'passed', 'verdict': 'good'},
                          'web_https_tls_clientreneg': {'status': 'passed', 'verdict': 'good'},
                          'web_https_cert_chain': {'status': 'passed', 'verdict': 'good'},
                          'web_https_cert_pubkey': {'status': 'passed', 'verdict': 'good'},
                          'web_https_cert_sig': {'status': 'passed', 'verdict': 'good'},
                          'web_https_cert_domain': {'status': 'passed', 'verdict': 'good'},
                          'web_https_dane_exist': {'status': 'info', 'verdict': 'bad'},
                          'web_https_dane_valid': {'status': 'not_tested', 'verdict': 'not-tested'},
                          'web_https_tls_0rtt': {'status': 'passed', 'verdict': 'na'},
                          'web_https_tls_ocsp': {'status': 'info', 'verdict': 'ok'},
                          'web_https_tls_keyexchangehash': {'status': 'passed', 'verdict': 'good'},
                          'web_appsecpriv_x_frame_options': {'status': 'warning', 'verdict': 'bad'},
                          'web_appsecpriv_referrer_policy': {'status': 'warning', 'verdict': 'bad'},
                          'web_appsecpriv_csp': {'status': 'info', 'verdict': 'bad'},
                          'web_appsecpriv_x_content_type_options': {'status': 'warning', 'verdict': 'bad'}},
                'custom': {'tls_1_3_support': 'no'}, 'calculated_results': {
                    'web_legacy_dnssec': {'status': 'passed', 'verdict': 'passed', 'technical_details': []},
                    'web_legacy_tls_available': {'status': 'passed', 'verdict': 'passed', 'technical_details': []},
                    'web_legacy_tls_ncsc_web': {'status': 'failed', 'verdict': 'failed', 'technical_details': []},
                    'web_legacy_https_enforced': {'status': 'passed', 'verdict': 'passed', 'technical_details': []},
                    'web_legacy_hsts': {'status': 'failed', 'verdict': 'failed', 'technical_details': []},
                    'web_legacy_ipv6_nameserver': {'status': 'passed', 'verdict': 'passed', 'technical_details': []},
                    'web_legacy_ipv6_webserver': {'status': 'failed', 'verdict': 'failed', 'technical_details': []},
                    'web_legacy_dane': {'status': 'info', 'verdict': 'info', 'technical_details': []},
                    'web_legacy_tls_1_3': {'status': 'failed', 'verdict': 'failed', 'technical_details': []},
                    'web_legacy_category_ipv6': {'status': 'failed', 'verdict': 'failed', 'technical_details': []}}}}
    }
    internetnlv2scan.save()

    # import the scan results to the database. Vitesse.nl will be empty here...
    tasks = processing_scan_results(accountinternetnlscan.id)
    tasks.apply()

    # Create report with statistics, should not error. Perhaps vitesse.nl is missing here?
    accountinternetnlscan = AccountInternetNLScan.objects.all().first()
    tasks = creating_report(accountinternetnlscan.id)
    tasks.apply()

    # vitesse was added, has a very old one and a new report with the error update.
    # dierenscheboys also has a report. fcwaalwijk has nothing.
    assert UrlReport.objects.all().count() == 3
    first_urlreport = UrlReport.objects.all().filter(url__url='dierenscheboys.nl').first()
    assert first_urlreport.high == 12
    assert first_urlreport.medium == 6
    assert first_urlreport.low == 3
    assert first_urlreport.ok == 22
    assert UrlReport.objects.all().filter(url__url='vitesse.nl').count() == 2
    # To see what the calculation is exactly: assert first_urlreport.calculation == {}

    # vitesse was added, has a very old one and a new report with the error update.
    # dierenscheboys also has a report
    assert UrlListReport.objects.all().count() == 1

    first_urllistreport = UrlListReport.objects.all().filter().first()
    # association was made during creating_report
    assert first_urllistreport.urllist == urllist
    assert first_urllistreport.high == 12
    assert first_urllistreport.average_internet_nl_score == 76
    # stats per issue types have been added

    # todo: opportunity to verify if the report output is correct.
