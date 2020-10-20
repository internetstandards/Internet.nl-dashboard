import logging
from datetime import datetime

from tldextract import tldextract

log = logging.getLogger(__name__)

"""
Compare reports and create difference reports.

A high level comparison contains this data:

     41 	        10 	        40112
Improvements 	Regressions 	Neutral


A detailed comparison contains this data:
Domain 	        Report 	    Improvements 	    Metrics improved
Internet.nl 	Link_old,   3 	                internet_nl_web_https_cert_chain,
                link_new                        internet_nl_web_https_dane_exist,
                                                internet_nl_web_dnssec_valid
dashboard.i... 	Link 	    2 	                internet_nl_web_https_cert_domain,
                                                internet_nl_web_https_tls_compress
nu.nl 	        Link 	    15 	                internet_nl_web_https_cert_domain,
                                                internet_nl_web_https_http_redirect,
                                                internet_nl_web_https_cert_chain,
                                                internet_nl_web_https_tls_version,
                                                internet_nl_web_https_tls_clientreneg,
                                                internet_nl_web_https_tls_ciphers,
                                                ...
websecurity.org Link 	    2 	                internet_nl_web_https_cert_domain,
                                                internet_nl_web_https_tls_compress

"""


# https://github.com/internetstandards/Internet.nl-dashboard/issues/201

def compare_report_in_detail(new_report, old_report):
    """

    Compares report 1 to report 2. Where report 1 is seen as the leading report, and report 2 are differences on
    that report. The goal is to run this only once and retrieve all reporting information from that: also for
    regressions and the high level data. The set returned is basically a 'table', which can be iterated for the right
    data.

    The data is very deep, that's because there might be different urls, endpoints, scans types.
    ['calculation']
        ['urls_by_url']
            ['acc.dashboard.internet.nl']
                ['endpoints_by_key']
                    ['dns_a_aaaa/0 IPv0']
                        ['ratings_by_type']
                            ['internet_nl_web_legacy_ipv6_webserver']
                                ['test_result']

    Data returned:
    {
        # we already made 'report compared to', no that's report compared to list.
        'urls_exclusive_in_new_report': [str, str, str...]
        'urls_exclusive_in_old_report': [str, str, str...]
        'old': {
            'average_internet_nl_score': 0,
            'number_of_urls': 0,
            'data_from': DateTime.isoformat(),
            'report_id': ...
        },
        'new': {
            'average_internet_nl_score': 0,
            'number_of_urls': 0,
            'data_from': DateTime.isoformat(),
            'report_id': ...
        },
        'summary': {
            'improvement': 2,
            'regression': 1,
            'neutral: 14
        },
        'comparison': {
            'internet.nl': {
                'url': 'internet.nl',
                'computed_suffix': '',
                'computed_domain': '',
                'computed_subdomain': '',
                'new': {
                    'report': 'https://',
                    'score': 42.42,
                },
                'old': {
                    'report': 'https://',
                    'score': 42.42,
                }
                # These are the objective changes compared on the same item.
                # This is _explicitly not_ num(new_failed) - num(old_failed), that would be a misleading number.
                'changes': {
                    'improvement': 2,
                    'regression': 1,
                    'neutral: 14,
                    'improved_metrics': [],
                    'regressed_metrics': [],
                    'neutral_metrics': [],
                },
                'test_result': {
                    # Totals for each measurement are not really valuable, because that's in the dashboard already
                    # in graphs. And we're not going to rebuild that here. Update mails serve to inform the user
                    # and get them to use the dashboard.
                }
            },
            ...
        }
    }

    :param new_report:
    :param old_report:
    :return:
    """

    comparison_report = {
        'urls_exclusive_in_new_report':
            list(
                set(new_report['calculation']['urls_by_url'].keys())
                - set(old_report['calculation']['urls_by_url'].keys())
            ),
        'urls_exclusive_in_old_report':
            list(
                set(old_report['calculation']['urls_by_url'].keys())
                - set(new_report['calculation']['urls_by_url'].keys())
            ),
        'old': {
            'average_internet_nl_score': old_report.get('average_internet_nl_score', 0),
            'number_of_urls': old_report.get('total_urls', 0),
            'data_from': old_report.get('at_when', datetime.now()),
            'report_id': old_report.get('id', 0),
            'urllist_id': old_report.get('urllist_id', 0)
            },
        'new': {
            'average_internet_nl_score': new_report.get('average_internet_nl_score', 0),
            'number_of_urls': new_report.get('total_urls', 0),
            'data_from': new_report.get('at_when', datetime.now()),
            'report_id': new_report.get('id', 0),
            'urllist_id': new_report.get('urllist_id', 0)
            },
        'comparison': {}
    }
    for url_key in new_report['calculation']['urls_by_url'].keys():
        # log.debug(f"Processing {url_key=}")
        new_url_data = new_report['calculation']['urls_by_url'][url_key]
        old_url_data = old_report['calculation']['urls_by_url'].get(url_key, {})

        my_extract = tldextract.extract(url_key)

        data = {
            'url': url_key,
            # Added for ordering the comparison results. So it's possible to sort like this:
            # - hyves.nl
            # - internet.nl
            # - acc.internet.nl
            # - beta.internet.nl
            # - justeat.nl
            'computed_suffix': my_extract.suffix,
            'computed_domain': my_extract.domain,
            'computed_subdomain': my_extract.subdomain,
            'computed_domain_and_suffix': f'{my_extract.domain}.{my_extract.suffix}',

            # In case there is no test data / no endpoint, this is set to False (the default).
            # You can see this being set to true with acc.internet.nl
            'test_results_from_internet_nl_available': False,

            # in case there was no endpoint, fill the report with some information:
            # This is done to reduce 'edge cases' and 'flags by values': it allows consistent summary of
            # the number of total issues, and it will also set a flag this could not be tested.
            'changes': {
                'improvement': 0,
                'neutral': 0,
                'regression': 0,
                'neutral_metrics': [],
                'regressed_metrics': [],
                'improved_metrics': [],
            },

            'old': {
                'report': '',
                'score': 0
            },
            'new': {
                'report': '',
                'score': 0
            }
        }

        # Looping through endpoints is not really useful, because we only recognize and can process internet.nl
        # endpoints. This also creates a possible bug where other endpoints are present (and empty), and thus
        # will leave new, old and changes empty
        endpoint_key = ""
        # web, the report type will be in the report itself soon, so that will be easier.
        if "dns_a_aaaa/0 IPv0" in new_url_data['endpoints_by_key'].keys():
            endpoint_key = "dns_a_aaaa/0 IPv0"
        # mail
        if "dns_soa/0 IPv0" in new_url_data['endpoints_by_key'].keys():
            endpoint_key = "dns_a_aaaa/0 IPv0"

        if endpoint_key:
            data['test_results_from_internet_nl_available'] = True

            new_endpoint_data = new_url_data['endpoints_by_key'][endpoint_key]
            old_endpoint_data = old_url_data.get('endpoints_by_key', {}).get(endpoint_key, {})

            # Our base is the 'new' domain. A scan might have failed in either case...
            if new_endpoint_data.get('ratings_by_type', None):
                data['new'] = {
                    'report': new_endpoint_data['ratings_by_type']['internet_nl_score']['internet_nl_url'],
                    'score': new_endpoint_data['ratings_by_type']['internet_nl_score']['internet_nl_score']
                }
            if old_endpoint_data.get('ratings_by_type', None):
                data['old'] = {
                    'report': old_endpoint_data['ratings_by_type']['internet_nl_score']['internet_nl_url'],
                    'score': old_endpoint_data['ratings_by_type']['internet_nl_score']['internet_nl_score']
                }

            data['changes'] = determine_changes_in_ratings(
                new_endpoint_data.get('ratings_by_type', {}),
                old_endpoint_data.get('ratings_by_type', {}),
            )

        comparison_report['comparison'][url_key] = data

        # add the summary to the report, which is just a simple loop with counters
        # this fits in one line and thus is easier to read:
        improvement, neutral, regression = 0, 0, 0
        for comparison_url_key in comparison_report['comparison'].keys():
            improvement += comparison_report['comparison'][comparison_url_key]['changes']['improvement']
            regression += comparison_report['comparison'][comparison_url_key]['changes']['regression']
            neutral += comparison_report['comparison'][comparison_url_key]['changes']['neutral']

        comparison_report['summary'] = {
            'improvement': improvement,
            'regression': regression,
            'neutral': neutral
        }

    return comparison_report


def determine_changes_in_ratings(new_ratings_data, old_ratings_data):
    # a separate routine makes this more testable

    # we don't want to have statistics over these fields, they are processed elsewhere.
    ratings_to_ignore = [
        # Scoring can be ignored, it's included in the comparison elsewhere.
        'internet_nl_mail_dashboard_overall_score',
        'internet_nl_web_overall_score',
        'internet_nl_score',

        # Removed metrics that will not be used again, which thus will not have data:
        'internet_nl_web_appsecpriv_x_xss_protection',

        # Categories are just higher levels of metrics, and that will skew the results if included, because
        # if one subtest fails, the category is also wrong.
        'internet_nl_web_tls',
        'internet_nl_web_ipv6',
        'internet_nl_web_appsecpriv',
        'internet_nl_web_dnssec',
        'internet_nl_mail_dashboard_tls',
        'internet_nl_mail_dashboard_auth',
        'internet_nl_mail_dashboard_dnssec',
        'internet_nl_mail_dashboard_ipv6',
        #
    ]
    neutral_test_result_values = \
        ["unknown", "not_applicable", "not_testable", 'no_mx', 'unreachable', 'error_in_test', 'error']

    # todo: should categories be ignored? Such as internet_nl_web_appsecpriv?

    # prepare result
    changes = {
        'improvement': 0,
        'regression': 0,
        'neutral': 0,
        'improved_metrics': [],
        'regressed_metrics': [],
        'neutral_metrics': [],
    }

    for rating_key in new_ratings_data.keys():
        # log.debug(f"- {rating_key=}")

        # Note that the following logic should be extactly the same as in the dashboard report GUI.
        # skip internet.nl extra fields and the internet.nl score field handled above:
        if '_legacy_' in rating_key or rating_key in ratings_to_ignore:
            continue

        new_test_result = new_ratings_data[rating_key]['test_result']
        old_test_result = old_ratings_data.get(rating_key, {}).get('test_result', 'unknown')

        # in case of uncomparable results, a neutral verdict is given:
        # uncomparable includes all situations where the old_data was not present.
        if new_test_result in neutral_test_result_values or old_test_result in neutral_test_result_values:
            changes['neutral'] += 1
            changes['neutral_metrics'].append(rating_key)
            continue

        # in other cases there will be simple progression
        new_simple_progression = new_ratings_data[rating_key]['simple_progression']
        old_simple_progression = old_ratings_data[rating_key]['simple_progression']

        if new_simple_progression == old_simple_progression:
            changes['neutral'] += 1
            changes['neutral_metrics'].append(rating_key)
        elif new_simple_progression > old_simple_progression:
            changes['improvement'] += 1
            changes['improved_metrics'].append(rating_key)
        else:
            changes['regression'] += 1
            changes['regressed_metrics'].append(rating_key)

    return changes


def key_calculation(report_data):
    """
    IN:
    report_data = {
        'calculation':
            "urls": [
                {
                  "url": "acc.dashboard.internet.nl",
                  "ratings": [],
                  "endpoints": [
                    {
                      "concat": "dns_a_aaaa/0 IPv0",
                      "ratings_by_type": {
                        "internet_nl_web_legacy_ipv6_webserver": {
                          "test_result": "failed"
                        },

            OUT:
            "urls_by_url": {
                "acc.dashboard.internet.nl": {
                  "url": "acc.dashboard.internet.nl",
                  "ratings": [],
                  "endpoints_by_key": {
                    "dns_a_aaaa/0 IPv0": [
                    {
                      "concat": "dns_a_aaaa/0 IPv0",
                      "ratings_by_type": {
                        "internet_nl_web_legacy_ipv6_webserver": {
                          "test_result": "failed"
                        },

    :param report:
    :return:
    """

    urls_by_key = {}
    for url in report_data['calculation']['urls']:
        urls_by_key[url['url']] = url

    for url in urls_by_key.keys():
        endpoints_by_key = {}
        for endpoint in urls_by_key[url]['endpoints']:
            endpoints_by_key[endpoint['concat']] = endpoint
        urls_by_key[url]['endpoints_by_key'] = endpoints_by_key

    report_data['calculation']['urls_by_url'] = urls_by_key
    return report_data
