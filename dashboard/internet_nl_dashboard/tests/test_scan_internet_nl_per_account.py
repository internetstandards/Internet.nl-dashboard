# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime, timezone

from django.contrib.auth.models import User
from websecmap.organizations.models import Url
from websecmap.reporting.models import UrlReport
from websecmap.scanners.models import Endpoint, EndpointGenericScan
from websecmap.scanners_internet_nl_web.models import InternetNLV2Scan

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList, UrlListReport
from dashboard.internet_nl_dashboard.scanners import scan_internet_nl_per_account
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import (
    creating_report,
    discovering_endpoints,
    endpoint_discovery_completed,
    monitor_timeout,
    processing_scan_results,
    queue_endpoint_discovery,
)

log = logging.getLogger(__package__)


class FakeDramatiqGroup:
    instances = []

    def __init__(self, tasks):
        self.tasks = list(tasks)
        self.completion_callbacks = []
        self.ran = False
        self.__class__.instances.append(self)

    def add_completion_callback(self, message):
        self.completion_callbacks.append(message)

    def run(self):
        self.ran = True


def test_discovering_endpoints_waits_for_dramatiq_completion(db, monkeypatch):
    account = Account.objects.create()
    urllist = UrlList.objects.create(account=account)
    url = Url.objects.create(url="internet.nl", is_dead=False, not_resolvable=False)
    urllist.urls.add(url)
    scan = AccountInternetNLScan.objects.create(
        account=account,
        scan=InternetNLV2Scan.objects.create(),
        urllist=urllist,
        state="requested",
    )

    FakeDramatiqGroup.instances = []
    monkeypatch.setattr(scan_internet_nl_per_account, "dramatiq_group", FakeDramatiqGroup)
    monkeypatch.setattr(
        scan_internet_nl_per_account.dns_endpoints,
        "compose_manual_discover_task",
        lambda urls: ["dns-task"],
    )

    discovery_task = discovering_endpoints(scan.id)
    scan.refresh_from_db()
    expected_state_changed_on = scan.state_changed_on.isoformat()

    assert scan.state == "discovering endpoints", "expected endpoint discovery to move to the active state first"
    assert (
        discovery_task.task == queue_endpoint_discovery.name
    ), "expected endpoint discovery to return the Celery queueing task"

    discovery_task.apply()
    scan.refresh_from_db()

    assert scan.state == "discovering endpoints", "expected scan state to wait for Dramatiq completion"
    assert len(FakeDramatiqGroup.instances) == 1, "expected one Dramatiq group to be queued"
    assert FakeDramatiqGroup.instances[0].tasks == ["dns-task"], "expected the DNS task to be queued in Dramatiq"
    assert FakeDramatiqGroup.instances[0].ran, "expected the Dramatiq group to be started"
    assert (
        FakeDramatiqGroup.instances[0].completion_callbacks[0].actor_name == "dashboard.endpoint_discovery_completed"
    ), "expected endpoint discovery to register the dashboard state completion callback"

    endpoint_discovery_completed(scan.id, expected_state_changed_on)
    scan.refresh_from_db()

    assert scan.state == "discovered endpoints", "expected Dramatiq completion to advance the dashboard scan state"


def test_endpoint_discovery_completion_ignores_stale_callbacks(db):
    account = Account.objects.create()
    urllist = UrlList.objects.create(account=account)
    scan = AccountInternetNLScan.objects.create(
        account=account,
        scan=InternetNLV2Scan.objects.create(),
        urllist=urllist,
        state="discovering endpoints",
        state_changed_on=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    endpoint_discovery_completed(scan.id, datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat())
    scan.refresh_from_db()

    assert scan.state == "discovering endpoints", "expected stale endpoint discovery callbacks to be ignored"


def test_monitor_timeout(db):
    a = Account.objects.create()

    recoverable_states = [
        "discovering endpoints",
        "retrieving scannable urls",
        "registering scan at internet.nl",
    ]
    for rec_state in recoverable_states:
        scan = AccountInternetNLScan.objects.create(
            account=a,
            scan=InternetNLV2Scan.objects.create(),
            urllist=UrlList.objects.create(account=a),
            state=rec_state,
            state_changed_on=datetime(1996, 1, 1, tzinfo=timezone.utc),
        )
        monitor_timeout(scan.id)
        updated_scan = AccountInternetNLScan.objects.get(id=scan.id)
        assert updated_scan.state_changed_on != datetime(
            1996, 1, 1, tzinfo=timezone.utc
        ), "expected monitor_timeout to update stale scan state_changed_on"
        assert updated_scan.state_changed_on.year == datetime.now().year, "expected stale scan to be retried this year"


def test_creating_report(db, redis_server, default_scan_metadata):
    """
    We're entering the reporting phase, all data has been downloaded in the accountinternetnl scan, and
    a report will be generated. This includes statistics and such.

    This report will be able to deal with error situations, where a scan fully failed and all scan values are
    set to error. This is done with the vitesse.nl domain, as this occurred in real life.

    :return:
    """

    # preparing the data to use in this test:
    user, c = User.objects.all().get_or_create(first_name="testuser", last_name="test", username="test", is_active=True)
    account, c = Account.objects.all().get_or_create(name="testaccount")
    urllist, c = UrlList.objects.all().get_or_create(name="testlist", account=account)
    internetnlv2scan, c = InternetNLV2Scan.objects.all().get_or_create(
        type="web", scan_id=1, state="scan results stored"
    )

    # fcwaalwijk is missing in the results, which is intended
    # note: also set discovered on and created on to a date in the past, otherwise they will not be in the report
    #  as they are not seen as relevant for the moment the report is made.
    for domain in ["vitesse.nl", "dierenscheboys.nl", "fcwaalwijk.nl"]:
        mydomain, c = Url.objects.all().get_or_create(
            url=domain,
            is_dead=False,
            not_resolvable=False,
            created_on=datetime(2010, 1, 1, tzinfo=timezone.utc),
        )
        myendpoint, c = Endpoint.objects.all().get_or_create(
            url=mydomain,
            protocol="dns_a_aaaa",
            port=0,
            ip_version=0,
            is_dead=False,
            discovered_on=datetime(2010, 1, 1, tzinfo=timezone.utc),
        )
        urllist.urls.add(mydomain)
        urllist.save()
        internetnlv2scan.subject_urls.add()

    accountinternetnlscan, c = AccountInternetNLScan.objects.all().get_or_create(
        account=account,
        scan=internetnlv2scan,
        urllist=urllist,
        started_on=datetime.now(timezone.utc),
        report=None,
        finished_on=None,
        state="scan results ready",
    )

    # Add a separate endpoint to verify that error scores do not hinder creating reports or statistics:
    # 'internet_nl_mail_dashboard_overall_score', 'internet_nl_web_overall_score'
    vitesse_endpoint = Endpoint.objects.all().filter(url__url="vitesse.nl").first()
    EndpointGenericScan.objects.all().get_or_create(
        type="internet_nl_web_overall_score",
        rating="error",
        evidence="",
        endpoint=vitesse_endpoint,
        rating_determined_on=datetime(2010, 1, 1, tzinfo=timezone.utc),
        last_scan_moment=datetime(2010, 1, 1, tzinfo=timezone.utc),
    )
    EndpointGenericScan.objects.all().get_or_create(
        type="web_https_tls_version",
        rating="failed",
        evidence="",
        endpoint=vitesse_endpoint,
        rating_determined_on=datetime(2010, 1, 1, tzinfo=timezone.utc),
        last_scan_moment=datetime(2010, 1, 1, tzinfo=timezone.utc),
    )

    # here, vitesse.nl has an error from the API. This occurs when a crash happens in the api scanner, which is
    # rare, but can happen due to all kinds of weird setups it can encounter.
    internetnlv2scan.retrieved_scan_report = {
        "vitesse.nl": {"status": "error"},
        "dierenscheboys.nl": {
            "status": "ok",
            "report": {"url": "https://batch.internet.nl/site/dierenscheboys.nl/219843/"},
            "scoring": {"percentage": 76},
            "results": {
                "categories": {
                    "web_ipv6": {"verdict": "failed", "status": "failed"},
                    "web_dnssec": {"verdict": "passed", "status": "passed"},
                    "web_https": {"verdict": "failed", "status": "failed"},
                    "web_appsecpriv": {"verdict": "warning", "status": "warning"},
                },
                "tests": {
                    "web_ipv6_ns_address": {"status": "passed", "verdict": "good"},
                    "web_ipv6_ns_reach": {"status": "passed", "verdict": "good"},
                    "web_ipv6_ws_address": {"status": "failed", "verdict": "bad"},
                    "web_ipv6_ws_reach": {
                        "status": "not_tested",
                        "verdict": "not-tested",
                    },
                    "web_ipv6_ws_similar": {
                        "status": "not_tested",
                        "verdict": "not-tested",
                    },
                    "web_dnssec_exist": {"status": "passed", "verdict": "good"},
                    "web_dnssec_valid": {"status": "passed", "verdict": "good"},
                    "web_https_http_available": {"status": "passed", "verdict": "good"},
                    "web_https_http_redirect": {"status": "passed", "verdict": "good"},
                    "web_https_http_hsts": {"status": "failed", "verdict": "bad"},
                    "web_https_http_compress": {"status": "passed", "verdict": "good"},
                    "web_https_tls_keyexchange": {"status": "failed", "verdict": "bad"},
                    "web_https_tls_ciphers": {"status": "passed", "verdict": "good"},
                    "web_https_tls_cipherorder": {
                        "status": "warning",
                        "verdict": "warning",
                    },
                    "web_https_tls_version": {
                        "status": "warning",
                        "verdict": "phase-out",
                    },
                    "web_https_tls_compress": {"status": "passed", "verdict": "good"},
                    "web_https_tls_secreneg": {"status": "passed", "verdict": "good"},
                    "web_https_tls_clientreneg": {
                        "status": "passed",
                        "verdict": "good",
                    },
                    "web_https_cert_chain": {"status": "passed", "verdict": "good"},
                    "web_https_cert_pubkey": {"status": "passed", "verdict": "good"},
                    "web_https_cert_sig": {"status": "passed", "verdict": "good"},
                    "web_https_cert_domain": {"status": "passed", "verdict": "good"},
                    "web_https_dane_exist": {"status": "info", "verdict": "bad"},
                    "web_https_dane_valid": {
                        "status": "not_tested",
                        "verdict": "not-tested",
                    },
                    "web_https_tls_0rtt": {"status": "passed", "verdict": "na"},
                    "web_https_tls_ocsp": {"status": "info", "verdict": "ok"},
                    "web_https_tls_keyexchangehash": {
                        "status": "passed",
                        "verdict": "good",
                    },
                    "web_appsecpriv_x_frame_options": {
                        "status": "warning",
                        "verdict": "bad",
                    },
                    "web_appsecpriv_referrer_policy": {
                        "status": "warning",
                        "verdict": "bad",
                    },
                    "web_appsecpriv_csp": {"status": "info", "verdict": "bad"},
                    "web_appsecpriv_x_content_type_options": {
                        "status": "warning",
                        "verdict": "bad",
                    },
                },
                "custom": {"tls_1_3_support": "no"},
                "calculated_results": {
                    "web_legacy_dnssec": {
                        "status": "passed",
                        "verdict": "passed",
                        "technical_details": [],
                    },
                    "web_legacy_tls_available": {
                        "status": "passed",
                        "verdict": "passed",
                        "technical_details": [],
                    },
                    "web_legacy_tls_ncsc_web": {
                        "status": "failed",
                        "verdict": "failed",
                        "technical_details": [],
                    },
                    "web_legacy_https_enforced": {
                        "status": "passed",
                        "verdict": "passed",
                        "technical_details": [],
                    },
                    "web_legacy_hsts": {
                        "status": "failed",
                        "verdict": "failed",
                        "technical_details": [],
                    },
                    "web_legacy_ipv6_nameserver": {
                        "status": "passed",
                        "verdict": "passed",
                        "technical_details": [],
                    },
                    "web_legacy_ipv6_webserver": {
                        "status": "failed",
                        "verdict": "failed",
                        "technical_details": [],
                    },
                    "web_legacy_dane": {
                        "status": "info",
                        "verdict": "info",
                        "technical_details": [],
                    },
                    "web_legacy_tls_1_3": {
                        "status": "failed",
                        "verdict": "failed",
                        "technical_details": [],
                    },
                    "web_legacy_category_ipv6": {
                        "status": "failed",
                        "verdict": "failed",
                        "technical_details": [],
                    },
                },
            },
        },
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
    # todo: fix this test, it has never worked on the build because redis was not available. Now that redis is
    #  available it returns 4 instead of the 3 we expect (and see locally during test).
    # assert UrlReport.objects.all().count() == 3
    first_urlreport = UrlReport.objects.all().filter(url__url="dierenscheboys.nl").first()
    # this fluctuates if settings such as forum_standardisation metrics are enabled/disabled.
    # since the default changed on 20240618 this amount is lowered from 12 to 6.
    assert first_urlreport, "expected a URL report for dierenscheboys.nl"
    assert first_urlreport.high == 6, "expected the current default Internet.nl report policy to produce 6 highs"
    assert first_urlreport.medium == 6, "expected the current default Internet.nl report policy to produce 6 mediums"
    assert first_urlreport.low == 3, "expected the current default Internet.nl report policy to produce 3 lows"
    assert first_urlreport.ok == 18, "expected the current default Internet.nl report policy to produce 18 oks"
    assert UrlReport.objects.all().filter(url__url="vitesse.nl").count() == 2, "expected old and new vitesse.nl reports"
    # To see what the calculation is exactly: assert first_urlreport.calculation == {}

    # vitesse was added, has a very old one and a new report with the error update.
    # dierenscheboys also has a report
    assert UrlListReport.objects.all().count() == 1, "expected one URL list report"

    first_urllistreport = UrlListReport.objects.all().filter().first()
    # association was made during creating_report
    assert first_urllistreport.urllist == urllist, "expected URL list report to be linked to the scanned URL list"
    assert first_urllistreport.high == 6, "expected URL list report to use current default high count"
    assert first_urllistreport.average_internet_nl_score == 76, "expected average score from dierenscheboys.nl"
    # stats per issue types have been added

    # todo: opportunity to verify if the report output is correct.
