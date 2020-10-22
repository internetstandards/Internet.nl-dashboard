"""
Compares reports, in a generic way.
"""
from dashboard.internet_nl_dashboard.logic.mail_admin_templates import store_template
from dashboard.internet_nl_dashboard.logic.report_comparison import (compare_report_in_detail,
                                                                     determine_changes_in_ratings,
                                                                     key_calculation, render_comparison_view,
                                                                     filter_comparison_report)
from dashboard.internet_nl_dashboard.tests.common import get_json_file


def test_key_report(current_path):
    calculation = key_calculation(get_json_file(f"{current_path}/test_report_comparison/report_1.json"))

    assert calculation['calculation']['urls_by_url']['acc.dashboard.internet.nl']['endpoints_by_key'][
        'dns_a_aaaa/0 IPv0']['ratings_by_type']['internet_nl_web_legacy_ipv6_webserver'][
        'test_result'] == "failed"


def test_compare_report_in_detail_equal_reports(current_path):
    calculation = key_calculation(get_json_file(f"{current_path}/test_report_comparison/report_1.json"))

    # there should be no differences when the report is compared to itself:
    result = compare_report_in_detail(calculation, calculation)
    assert result == {
        'comparison': {
            'acc.dashboard.internet.nl': {

                'changes': {
                    'improvement': 0,
                    'neutral': 31,
                    'regression': 0,
                    'neutral_metrics': ['internet_nl_web_https_http_hsts',
                                        'internet_nl_web_ipv6_ws_reach',
                                        'internet_nl_web_https_tls_version',
                                        'internet_nl_web_appsecpriv_x_frame_options',
                                        'internet_nl_web_https_tls_cipherorder',
                                        'internet_nl_web_appsecpriv_x_content_type_options',
                                        'internet_nl_web_https_tls_ciphers',
                                        'internet_nl_web_appsecpriv_referrer_policy',
                                        'internet_nl_web_https_dane_exist',
                                        'internet_nl_web_https_tls_ocsp',
                                        'internet_nl_web_appsecpriv_csp',
                                        'internet_nl_web_ipv6_ns_address',
                                        'internet_nl_web_https_tls_clientreneg',
                                        'internet_nl_web_ipv6_ns_reach',
                                        'internet_nl_web_https_http_compress',
                                        'internet_nl_web_https_cert_sig',
                                        'internet_nl_web_https_http_redirect',
                                        'internet_nl_web_https_dane_valid',
                                        'internet_nl_web_ipv6_ws_address',
                                        'internet_nl_web_https_tls_0rtt',
                                        'internet_nl_web_dnssec_exist',
                                        'internet_nl_web_https_cert_domain',
                                        'internet_nl_web_https_tls_keyexchangehash',
                                        'internet_nl_web_https_tls_secreneg',
                                        'internet_nl_web_ipv6_ws_similar',
                                        'internet_nl_web_dnssec_valid',
                                        'internet_nl_web_https_tls_compress',
                                        'internet_nl_web_https_cert_chain',
                                        'internet_nl_web_https_cert_pubkey',
                                        'internet_nl_web_https_http_available',
                                        'internet_nl_web_https_tls_keyexchange'],
                    'regressed_metrics': [],
                    'improved_metrics': [],
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'acc.dashboard',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/',
                    'score': 79
                },
                'old': {
                    'report': 'https://batch.internet.nl/site/acc.dashboard.internet.nl/200719/',
                    'score': 79
                },
                'url': 'acc.dashboard.internet.nl'
            },

            # this is an entirely empty report, thus there will be no data here...
            # Should we skip it in it's entirity? No final report should say something about no metrics.
            # just like on the dashboard.
            'pl.internet.nl': {
                # There is no endpoint to get changes from.
                'changes': {
                    'improvement': 0,
                    'neutral': 0,
                    'regression': 0,
                    'neutral_metrics': [],
                    'regressed_metrics': [],
                    'improved_metrics': [],
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'pl',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': False,
                # There is no endpoint and thus no comparison
                'new': {
                    'report': '',
                    'score': 0
                },
                'old': {
                    'report': '',
                    'score': 0
                },
                'url': 'pl.internet.nl'
            },

            # www.internet.nl is missing a few ratings, so the neutral should be lower
            # It misses 2: internet_nl_web_https_http_hsts, internet_nl_web_https_tls_ocsp
            'www.internet.nl': {
                'changes': {
                    'improvement': 0,
                    'neutral': 29,
                    'regression': 0,
                    'neutral_metrics': ['internet_nl_web_https_tls_version',
                                        'internet_nl_web_ipv6_ns_address',
                                        'internet_nl_web_https_tls_clientreneg',
                                        'internet_nl_web_ipv6_ns_reach',
                                        'internet_nl_web_https_http_compress',
                                        'internet_nl_web_https_cert_sig',
                                        'internet_nl_web_https_http_redirect',
                                        'internet_nl_web_https_dane_valid',
                                        'internet_nl_web_appsecpriv_x_frame_options',
                                        'internet_nl_web_https_tls_cipherorder',
                                        'internet_nl_web_ipv6_ws_address',
                                        'internet_nl_web_appsecpriv_x_content_type_options',
                                        'internet_nl_web_https_tls_0rtt',
                                        'internet_nl_web_dnssec_exist',
                                        'internet_nl_web_https_cert_domain',
                                        'internet_nl_web_https_tls_keyexchangehash',
                                        'internet_nl_web_https_dane_exist',
                                        'internet_nl_web_https_tls_secreneg',
                                        'internet_nl_web_ipv6_ws_similar',
                                        'internet_nl_web_dnssec_valid',
                                        'internet_nl_web_https_tls_compress',
                                        'internet_nl_web_https_cert_chain',
                                        'internet_nl_web_https_tls_ciphers',
                                        'internet_nl_web_https_cert_pubkey',
                                        'internet_nl_web_ipv6_ws_reach',
                                        'internet_nl_web_https_http_available',
                                        'internet_nl_web_https_tls_keyexchange',
                                        'internet_nl_web_appsecpriv_csp',
                                        'internet_nl_web_appsecpriv_referrer_policy'],
                    'regressed_metrics': [],
                    'improved_metrics': [],
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'www',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/200737/',
                    'score': 100
                },
                'old': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/200737/',
                    'score': 100
                },
                'url': 'www.internet.nl'
            }

        },

        'new': {
            'average_internet_nl_score': 96.54,
            'data_from': '2020-10-15 00:19:28.788709+00:00',
            'number_of_urls': 25,
            'report_id': 1267,
            'urllist_id': 1
        },
        'old': {
            'average_internet_nl_score': 96.54,
            'data_from': '2020-10-15 00:19:28.788709+00:00',
            'number_of_urls': 25,
            'report_id': 1267,
            'urllist_id': 1
        },
        'summary': {'improvement': 0, 'neutral': 60, 'regression': 0},
        # Should be an empty list, as both reports are the same
        'urls_exclusive_in_new_report': [],
        'urls_exclusive_in_old_report': []
    }


def test_compare_report_detail_differences():
    positive_report = {
        "id": 1,
        "urllist_id": 1,
        "average_internet_nl_score": 11.11,
        "total_urls": 1,
        "at_when": "2020-10-10 10:10:10.101010+00:00",
        "calculation": {
            "urls_by_url": {
                "www.internet.nl": {
                    "url": "www.internet.nl",
                    "ratings": [],
                    "endpoints_by_key": {
                        "dns_a_aaaa/0 IPv0": {
                            "id": 1,
                            "concat": "dns_a_aaaa/0 IPv0",
                            "ratings": [],
                            "ratings_by_type": {
                                "internet_nl_web_https_tls_version": {
                                    "test_result": "passed",
                                    "simple_progression": 400
                                },
                                # this is intentionally missing in the negative report, to verify
                                # that the correct keys are used from the correct report.
                                "internet_nl_web_https_tls_cipherorder": {
                                    "test_result": "passed",
                                    "simple_progression": 400
                                },
                                "internet_nl_score": {
                                    "internet_nl_score": 11.11,
                                    "internet_nl_url": "https://batch.internet.nl/site/www.internet.nl/1/"
                                }
                            }
                        }
                    }
                },
                # This is an extra domain that will be missing in the negative report.
                # This will create a neutral rating.
                "extradomain.internet.nl": {
                    "url": "extradomain.internet.nl",
                    "ratings": [],
                    "endpoints_by_key": {
                        "dns_a_aaaa/0 IPv0": {
                            "id": 1,
                            "concat": "dns_a_aaaa/0 IPv0",
                            "ratings": [],
                            "ratings_by_type": {
                                "internet_nl_web_https_tls_version": {
                                    "test_result": "passed",
                                    "simple_progression": 400
                                },
                                # this is intentionally missing in the negative report, to verify
                                # that the correct keys are used from the correct report.
                                "internet_nl_web_https_tls_cipherorder": {
                                    "test_result": "passed",
                                    "simple_progression": 400
                                },
                                "internet_nl_score": {
                                    "internet_nl_score": 11.11,
                                    "internet_nl_url": "https://batch.internet.nl/site/www.internet.nl/1/"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    negative_report = {
        "id": 2,
        "urllist_id": 2,
        "average_internet_nl_score": 22.22,
        "total_urls": 2,
        "at_when": "2020-02-02 20:20:20.202020+00:00",
        "calculation": {
            "urls_by_url": {
                "www.internet.nl": {
                    "url": "www.internet.nl",
                    "ratings": [],
                    "endpoints_by_key": {
                        "dns_a_aaaa/0 IPv0": {
                            "id": 2,
                            "concat": "dns_a_aaaa/0 IPv0",
                            "ratings": [],
                            "ratings_by_type": {
                                "internet_nl_web_https_tls_version": {
                                    "test_result": "failed",
                                    "simple_progression": 100
                                },
                                "internet_nl_score": {
                                    "internet_nl_score": 22.22,
                                    "internet_nl_url": "https://batch.internet.nl/site/www.internet.nl/2/"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    comparison = compare_report_in_detail(positive_report, negative_report)
    assert comparison == {
        'comparison': {
            'www.internet.nl': {
                'changes': {
                    'improvement': 1,
                    'neutral': 1,
                    'regression': 0,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                    'regressed_metrics': [],
                    'neutral_metrics': ['internet_nl_web_https_tls_cipherorder']
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'www',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/1/',
                    'score': 11.11
                },
                'old': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/2/',
                    'score': 22.22
                },
                'url': 'www.internet.nl'
            },
            # The extra domain is not in the negative report, it will thus not have 'old' data.
            'extradomain.internet.nl': {
                'changes': {
                    'improvement': 0,
                    'neutral': 2,
                    'regression': 0,
                    'improved_metrics': [],
                    'regressed_metrics': [],
                    'neutral_metrics': ['internet_nl_web_https_tls_version', 'internet_nl_web_https_tls_cipherorder']
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'extradomain',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/1/',
                    'score': 11.11
                },
                'old': {
                    'report': '',
                    'score': 0,
                },
                'url': 'extradomain.internet.nl'
            }
        },
        'new': {
            'average_internet_nl_score': 11.11,
            'data_from': '2020-10-10 10:10:10.101010+00:00',
            'number_of_urls': 1,
            'report_id': 1,
            'urllist_id': 1
        },
        'old': {
            'average_internet_nl_score': 22.22,
            'data_from': '2020-02-02 20:20:20.202020+00:00',
            'number_of_urls': 2,
            'report_id': 2,
            'urllist_id': 2
        },
        'summary': {'improvement': 1, 'neutral': 3, 'regression': 0},
        'urls_exclusive_in_new_report': ['extradomain.internet.nl'],
        'urls_exclusive_in_old_report': []}

    # now let's swap it around:
    comparison = compare_report_in_detail(negative_report, positive_report)
    assert comparison == {
        'comparison': {
            'www.internet.nl': {
                'changes': {
                    # only a regression, there are no further matching fields
                    'improvement': 0,
                    'neutral': 0,
                    'regression': 1,
                    'improved_metrics': [],
                    'regressed_metrics': ['internet_nl_web_https_tls_version'],
                    'neutral_metrics': []
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'www',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/2/',
                    'score': 22.22
                },
                'old': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/1/',
                    'score': 11.11
                },
                'url': 'www.internet.nl'
            },
        },
        'new': {
            'average_internet_nl_score': 22.22,
            'data_from': '2020-02-02 20:20:20.202020+00:00',
            'number_of_urls': 2,
            'report_id': 2,
            'urllist_id': 2
        },
        'old': {
            'average_internet_nl_score': 11.11,
            'data_from': '2020-10-10 10:10:10.101010+00:00',
            'number_of_urls': 1,
            'report_id': 1,
            'urllist_id': 1
        },
        'summary': {'improvement': 0, 'neutral': 0, 'regression': 1},
        'urls_exclusive_in_new_report': [],
        'urls_exclusive_in_old_report': ['extradomain.internet.nl']
    }


def test_filter_comparison_report():
    # Five domains are used so we can verify the order of the results is correct.
    # One domain before and after internet.nl and subdomain.
    # One domain is ignored because it has a regression instead of an improvement

    # the comparison reports have been made a little smaller, so they can be maintained
    # more easily and there is less code.
    comparison = {
        'comparison': {
            'www.internet.nl': {
                'changes': {
                    'improvement': 1,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                },
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'www',
                'url': 'www.internet.nl'
            },
            'internet.nl': {
                'changes': {
                    'improvement': 1,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                },
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': '',
                'url': 'internet.nl'
            },
            'example.com': {
                'changes': {
                    'improvement': 1,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                },
                'computed_domain_and_suffix': 'example.com',
                'computed_subdomain': '',
                'url': 'example.com'
            },
            'ignoreddomain.example.com': {
                'changes': {
                    'improvement': 0,
                    'regression': 1,
                    'improved_metrics': [],
                },
                'computed_domain_and_suffix': 'example.com',
                'computed_subdomain': '',
                'url': 'ignoreddomain.example.com'
            },
            'afterinternet.nl.wexample.com': {
                'changes': {
                    'improvement': 1,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                },
                'computed_domain_and_suffix': 'wexample.com',
                'computed_subdomain': 'afterinternet.nl',
                'url': 'afterinternet.nl.wexample.com'
            }
        }
    }

    # Expected:
    # ignoreddomain.example.com will be ignored
    output = filter_comparison_report(comparison, impact="improvement")
    assert output[0]['url'] == "example.com"
    assert output[1]['url'] == "internet.nl"
    assert output[2]['url'] == "www.internet.nl"
    assert output[3]['url'] == "afterinternet.nl.wexample.com"
    assert len(output) == 4


def test_render_comparison_view(db):
    # Make sure the template for comparisons is available from the database:
    store_template(
        "detailed_comparison_improvement_en",
        """
            {% for record in data %}
                <tr>
                    <td>{{ record.url }}</td>
                    <td><a href="{{ record.new.report }}" target="_blank">{{ record.new.score }}</a></td>
                    <td>{{ record.changes.improvement }}</td>
                    <td>
                        <ul>
                        {% for metric in record.changes.improved_metrics %}
                            <li>{{ metric }}</li>
                        {% endfor %}
                        </ul>
                    </td>
                </tr>
            {% endfor %} 
        """
    )

    # no input, no output and no crashes:
    output = render_comparison_view(
        {},
        impact="improvement",
        language="nl"
    )
    assert output == ""

    # See that rendering is happening, for both improvement and regression.
    # The point is to see that the templating stuff works, not so much what HTML is being generated.
    # And that translations are correct.
    comparison = {
        'comparison': {
            'www.internet.nl': {
                'changes': {
                    'improvement': 1,
                    'neutral': 0,
                    'regression': 1,
                    'improved_metrics': ['internet_nl_web_https_tls_version'],
                    'regressed_metrics': ['internet_nl_web_https_tls_version'],
                    'neutral_metrics': []
                },
                'computed_domain': 'internet',
                'computed_domain_and_suffix': 'internet.nl',
                'computed_subdomain': 'www',
                'computed_suffix': 'nl',
                'test_results_from_internet_nl_available': True,
                'new': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/2/',
                    'score': 22.22
                },
                'old': {
                    'report': 'https://batch.internet.nl/site/www.internet.nl/1/',
                    'score': 11.11
                },
                'url': 'www.internet.nl'
            },
        },
        'new': {
            'average_internet_nl_score': 22.22,
            'data_from': '2020-02-02 20:20:20.202020+00:00',
            'number_of_urls': 2,
            'report_id': 2,
            'urllist_id': 2
        },
        'old': {
            'average_internet_nl_score': 11.11,
            'data_from': '2020-10-10 10:10:10.101010+00:00',
            'number_of_urls': 1,
            'report_id': 1,
            'urllist_id': 1
        },
        'summary': {'improvement': 0, 'neutral': 0, 'regression': 1},
        'urls_exclusive_in_new_report': [],
        'urls_exclusive_in_old_report': ['extradomain.internet.nl']
    }

    # the first time called the correct translation language is used, the second time it's not...
    # as activating a translation catalog is done on per-thread basis and such change will affect
    # code running in the same thread.
    output = render_comparison_view(
        comparison,
        impact="improvement",
        language="nl"
    )

    # template engines add newlines and whitespace, which makes comparison harder.
    output = output.strip()

    assert output.startswith("<tr") is True
    assert output.endswith("</tr>") is True
    assert "www.internet.nl" in output
    # the metric should be translated, the original key should not be present.
    assert "internet_nl_web_https_tls_version" not in output
    # the translated key should also not be present, but be translated with djangos translation system
    # the translation is retrieved with the translation command
    assert "detail_web_tls_version" not in output
    # The label specifically should not be there...
    assert "detail_web_tls_version_label" not in output
    # The translation is now "TLS Versie" in Dutch...
    assert "TLS-versie" in output

    # test that translating to english also works.
    output = render_comparison_view(
        comparison,
        impact="improvement",
        language="en"
    )
    assert "TLS version" in output


def test_determine_changes(current_path):
    set_1 = {
        # The only metric that is included
        "internet_nl_web_https_http_hsts": {
            "test_result": "failed",
            "simple_progression": 100
        },
        # Categories are ignored
        "internet_nl_web_ipv6": {
            "test_result": "failed",
            "simple_progression": 100
        },
        # legacy fields are ignored
        "internet_nl_web_legacy_category_ipv6": {
            "test_result": "failed",
            "simple_progression": 100
        },
        # score fields are ignored:
        "internet_nl_score": {
            "test_result": 100,
        },
        # deleted field, will also be ignored:
        "internet_nl_web_appsecpriv_x_xss_protection": {
            "ok": 1,
            "scan": 51,
            "simple_progression": 0
        }
    }

    assert determine_changes_in_ratings(
        set_1,
        set_1
    ) == {'improvement': 0, 'neutral': 1, 'regression': 0,
          'improved_metrics': [], 'regressed_metrics': [], 'neutral_metrics': ['internet_nl_web_https_http_hsts']}

    # Test improvement
    assert determine_changes_in_ratings(
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "passed",
                "simple_progression": 400
            }
        },
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "failed",
                "simple_progression": 100
            }
        }
    ) == {'improvement': 1, 'neutral': 0, 'regression': 0,
          'improved_metrics': ['internet_nl_web_https_http_hsts'], 'regressed_metrics': [], 'neutral_metrics': []}

    # test regression
    assert determine_changes_in_ratings(
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "failed",
                "simple_progression": 100
            }
        },
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "passed",
                "simple_progression": 400
            }
        }
    ) == {'improvement': 0, 'neutral': 0, 'regression': 1,
          'improved_metrics': [], 'regressed_metrics': ['internet_nl_web_https_http_hsts'], 'neutral_metrics': []}

    # test missing key will result in neutral result
    assert determine_changes_in_ratings(
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "failed",
                "simple_progression": 100
            }
        },
        {
            "this_is_a_non_matching_result_and_will_return_into_no_comparison_thus_neutral": {
                "test_result": "passed",
                "simple_progression": 400
            }
        }
    ) == {'improvement': 0, 'neutral': 1, 'regression': 0,
          'improved_metrics': [], 'regressed_metrics': [], 'neutral_metrics': ['internet_nl_web_https_http_hsts']}

    # and test missing key with an entirely empty old report
    assert determine_changes_in_ratings(
        {
            "internet_nl_web_https_http_hsts": {
                "test_result": "failed",
                "simple_progression": 100
            }
        },
        {}
    ) == {'improvement': 0, 'neutral': 1, 'regression': 0,
          'improved_metrics': [], 'regressed_metrics': [], 'neutral_metrics': ['internet_nl_web_https_http_hsts']}
