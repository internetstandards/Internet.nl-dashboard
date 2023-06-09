# SPDX-License-Identifier: Apache-2.0
"""
Validate that a report is correctly upgraded

Run these tests with make testcase case=test_reoprt_upgrade
"""
from datetime import datetime, timezone

from websecmap.organizations.models import Url
from websecmap.reporting.diskreport import retrieve_report

from dashboard.internet_nl_dashboard.logic.report import (add_keyed_ratings, add_percentages_to_statistics,
                                                          add_statistics_over_ratings, remove_comply_or_explain)
from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, UrlList, UrlListReport
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import upgrade_report_with_unscannable_urls


def test_report_upgrade(db, monkeypatch) -> None:
    # Create urllist with a lot of unscannable domains, only apple.com is scannable.
    # megaupload.com will never be scannable, and the rest can have an endpoint and might be in the report
    # already because of this (but without endpoints)

    urls = ['akamaihd.net', 'apple.com', 'bp.blogspot.com', 'clickbank.net', 'cocolog-nifty.com', 'fda.gov',
            'geocities.jp', 'ggpht.com', 'googleusercontent.com', 'megaupload.com', 'nhk.or.jp',
            'ssl-images-amazon.com', 'ytimg.com']

    # create the list, code from test domain management:
    account, created = Account.objects.all().get_or_create(name="test")
    urllist = UrlList()
    urllist.name = "upgrade"
    urllist.account = account
    urllist.save()

    scan = AccountInternetNLScan()
    scan.urllist = urllist
    scan.account = account
    scan.save()

    for url in urls:
        new_url = Url()
        new_url.url = url
        new_url.save()
        urllist.urls.add(new_url)
        urllist.save()

    # fake a report on these domains, without any upgrades, taken from the acc environment:
    fake_calculation = {
        "high": 19,
        "medium": 4,
        "low": 3,
        "ok": 15,
        "total_urls": 1,
        "high_urls": 1,
        "medium_urls": 0,
        "low_urls": 0,
        "ok_urls": 0,
        "explained_high": 0,
        "explained_medium": 0,
        "explained_low": 0,
        "explained_high_endpoints": 0,
        "explained_medium_endpoints": 0,
        "explained_low_endpoints": 0,
        "explained_high_urls": 0,
        "explained_medium_urls": 0,
        "explained_low_urls": 0,
        "explained_total_url_issues": 0,
        "explained_url_issues_high": 0,
        "explained_url_issues_medium": 0,
        "explained_url_issues_low": 0,
        "explained_total_endpoint_issues": 0,
        "explained_endpoint_issues_high": 0,
        "explained_endpoint_issues_medium": 0,
        "explained_endpoint_issues_low": 0,
        "total_endpoints": 1,
        "high_endpoints": 1,
        "medium_endpoints": 0,
        "low_endpoints": 0,
        "ok_endpoints": 0,
        "total_url_issues": 0,
        "total_endpoint_issues": 26,
        "url_issues_high": 0,
        "url_issues_medium": 0,
        "url_issues_low": 0,
        "endpoint_issues_high": 19,
        "endpoint_issues_medium": 4,
        "endpoint_issues_low": 3,
        "urls": [
            {
                "url": "apple.com",
                "ratings": [],
                "endpoints": [
                    {
                        "id": 4599,
                        "concat": "dns_a_aaaa/0 IPv0",
                        "ip": 0,
                        "ip_version": 0,
                        "port": 0,
                        "protocol": "dns_a_aaaa",
                        "v4": False,
                        "ratings": [
                            {
                                "type": "internet_nl_web_ipv6_ws_address",
                                "explanation": "Test internet_nl_web_ipv6_ws_address resulted in failed.",
                                "since": "2020-01-15T13:00:01.116013+00:00",
                                "last_scan": "2020-01-15T13:00:01.116689+00:00",
                                "high": 1,
                                "medium": 0,
                                "low": 0,
                                "ok": 0,
                                "not_testable": False,
                                "not_applicable": False,
                                "error_in_test": False,
                                "is_explained": False,
                                "comply_or_explain_explanation": "",
                                "comply_or_explain_explained_on": "",
                                "comply_or_explain_explanation_valid_until": "",
                                "comply_or_explain_valid_at_time_of_report": False,
                                "scan": 114575,
                                "scan_type": "internet_nl_web_ipv6_ws_address"
                            },
                            {
                                "type": "internet_nl_web_dnssec_valid",
                                "explanation": "Test internet_nl_web_dnssec_valid resulted in failed.",
                                "since": "2020-01-15T13:00:00.684906+00:00",
                                "last_scan": "2020-01-15T13:00:00.685193+00:00",
                                "high": 1,
                                "medium": 0,
                                "low": 0,
                                "ok": 0,
                                "not_testable": False,
                                "not_applicable": False,
                                "error_in_test": False,
                                "is_explained": False,
                                "comply_or_explain_explanation": "",
                                "comply_or_explain_explained_on": "",
                                "comply_or_explain_explanation_valid_until": "",
                                "comply_or_explain_valid_at_time_of_report": False,
                                "scan": 114556,
                                "scan_type": "internet_nl_web_dnssec_valid"
                            },
                        ],
                        "high": 19,
                        "medium": 4,
                        "low": 3,
                        "ok": 15,
                        "explained_high": 0,
                        "explained_medium": 0,
                        "explained_low": 0
                    }
                ],
                "total_issues": 26,
                "high": 19,
                "medium": 4,
                "low": 3,
                "ok": 15,
                "total_endpoints": 1,
                "high_endpoints": 1,
                "medium_endpoints": 0,
                "low_endpoints": 0,
                "ok_endpoints": 0,
                "total_url_issues": 0,
                "url_issues_high": 0,
                "url_issues_medium": 0,
                "url_issues_low": 0,
                "url_ok": 0,
                "total_endpoint_issues": 26,
                "endpoint_issues_high": 19,
                "endpoint_issues_medium": 4,
                "endpoint_issues_low": 3,
                "explained_total_issues": 0,
                "explained_high": 0,
                "explained_medium": 0,
                "explained_low": 0,
                "explained_high_endpoints": 0,
                "explained_medium_endpoints": 0,
                "explained_low_endpoints": 0,
                "explained_total_url_issues": 0,
                "explained_url_issues_high": 0,
                "explained_url_issues_medium": 0,
                "explained_url_issues_low": 0,
                "explained_total_endpoint_issues": 0,
                "explained_endpoint_issues_high": 0,
                "explained_endpoint_issues_medium": 0,
                "explained_endpoint_issues_low": 0
            }
        ],
        "total_issues": 26,
        "name": "Unscannable Web + one scannable"
    }

    fake_report = UrlListReport()
    fake_report.calculation = fake_calculation
    fake_report.urllist = urllist
    fake_report.at_when = datetime.now(timezone.utc)
    fake_report.save()

    # First check if we are removing the comply_or_explain keys, mainly to save data:
    remove_comply_or_explain(fake_calculation)
    assert "explained_endpoint_issues_high" not in fake_calculation['urls'][0]
    assert "comply_or_explain_explanation" not in fake_calculation['urls'][0]['endpoints'][0]["ratings"][0]

    # Now add ratings based on keys, which makes direct access possible:
    add_keyed_ratings(fake_calculation)
    assert "ratings_by_type" in fake_calculation['urls'][0]['endpoints'][0]
    assert "internet_nl_web_ipv6_ws_address" in fake_calculation['urls'][0]['endpoints'][0]['ratings_by_type']

    # Add graph statistics, so the graphs can be instantly created based on report data
    add_statistics_over_ratings(fake_calculation)
    assert "statistics_per_issue_type" in fake_calculation
    assert "internet_nl_web_ipv6_ws_address" in fake_calculation["statistics_per_issue_type"]
    # todo: we can add some tests here to see if the aggregation is correct

    # add some statistics over all these metrics
    add_percentages_to_statistics(fake_calculation)

    assert "pct_ok" in fake_calculation["statistics_per_issue_type"]["internet_nl_web_ipv6_ws_address"]

    # and make sure the report is complete: meaning that all urls requested are present, even though they
    # could not be scanned. So a top 100 stays a top 100.
    assert (len(fake_calculation['urls']) == 1)
    upgrade_report_with_unscannable_urls(fake_report.id, scan.id)
    fake_report = UrlListReport.objects.all().first()
    fake_report_calculation = retrieve_report(fake_report.id, "UrlListReport")
    assert (len(fake_report_calculation['urls']) == len(urls))

    # the first url should still be by apple:
    assert fake_report_calculation['urls'][0]['url'] == "akamaihd.net"
    assert fake_report_calculation['urls'][1]['url'] == "apple.com"
