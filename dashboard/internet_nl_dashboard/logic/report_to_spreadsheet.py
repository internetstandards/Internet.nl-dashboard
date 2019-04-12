import itertools
import logging
from string import ascii_uppercase
from typing import Any, Dict, List

import pyexcel as p
from django.utils.text import slugify

from dashboard.internet_nl_dashboard.models import Account, UrlListReport

"""
Creates spreadsheets containing report data.

Done: make sure the columns are in a custom order. Columns are defined in scanners. The order of the columns isn't.
Done: make sure you can download the spreadsheet in a single click
Done: add a sane logic to the spreadsheet content
Done: support ods and xlsx.
Done: can we support sum rows at the top for boolean values(?), only for excel. Not for ods, which is too bad.

Todo: get column translations. From internet.nl PO files? How do they map to these variables?
Todo: write some tests for these methods, once they are more table.
"""

log = logging.getLogger(__package__)

SANE_COLUMN_ORDER = {
    # scanner
    'dns_soa': {
        # any grouping, every group has a empty column between them. The label is not used.
        'overall': [
            'internet_nl_mail_dashboard_overall_score'
        ],
        'auth': [
            'internet_nl_mail_dashboard_auth',
            'internet_nl_mail_auth_spf_exist',
            'internet_nl_mail_auth_spf_policy',
            'internet_nl_mail_auth_dkim_exist',
            'internet_nl_mail_auth_dmarc_exist',
            'internet_nl_mail_auth_dmarc_policy',
        ],
        'ipv6': [
            'internet_nl_mail_dashboard_ipv6',
            'internet_nl_mail_ipv6_ns_reach',
            'internet_nl_mail_ipv6_ns_address',
            'internet_nl_mail_ipv6_mx_reach',
            'internet_nl_mail_ipv6_mx_address',
        ],
        'dnssec': [
            'internet_nl_mail_dashboard_dnssec',
            'internet_nl_mail_dnssec_mx_exist',
            'internet_nl_mail_dnssec_mx_valid',
            'internet_nl_mail_dnssec_mailto_exist',
            'internet_nl_mail_dnssec_mailto_valid',
        ],
        # perhaps split these into multiple groups.
        'tls': [
            'internet_nl_mail_dashboard_tls',
            'internet_nl_mail_starttls_tls_version',
            'internet_nl_mail_starttls_tls_ciphers',
            'internet_nl_mail_starttls_tls_secreneg',
            'internet_nl_mail_starttls_tls_clientreneg',
            'internet_nl_mail_starttls_tls_keyexchange',
            'internet_nl_mail_starttls_tls_compress',
            'internet_nl_mail_starttls_cert_domain',
            'internet_nl_mail_starttls_cert_chain',
            'internet_nl_mail_starttls_cert_sig',
            'internet_nl_mail_starttls_cert_pubkey',
            'internet_nl_mail_starttls_dane_exist',
            'internet_nl_mail_starttls_dane_valid',
            'internet_nl_mail_starttls_dane_rollover',
        ],
        'legacy': [
            'internet_nl_mail_legacy_dane',
            'internet_nl_mail_legacy_tls_available',
            'internet_nl_mail_legacy_spf',
            'internet_nl_mail_legacy_dkim',
            'internet_nl_mail_legacy_dmarc',
            'internet_nl_mail_legacy_dnsssec_mailserver_domain',
            'internet_nl_mail_legacy_dnssec_email_domain',
            'internet_nl_mail_legacy_ipv6_mailserver',
            'internet_nl_mail_legacy_ipv6_nameserver',
        ]
    },
    'dns_a_aaaa': {
        'overall': [
            'internet_nl_web_overall_score',
        ],

        'ipv6': [
            'internet_nl_web_ipv6',
            'internet_nl_web_ipv6_ws_address',
            'internet_nl_web_ipv6_ns_reach',
            'internet_nl_web_ipv6_ns_address',
            'internet_nl_web_ipv6_ws_reach',
            'internet_nl_web_ipv6_ws_similar',
        ],

        'dnssec': [
            'internet_nl_web_dnssec',
            'internet_nl_web_dnssec_exist',
            'internet_nl_web_dnssec_valid',
        ],

        'tls': [
            'internet_nl_web_tls',
            'internet_nl_web_https_http_available',
            'internet_nl_web_https_http_redirect',
            'internet_nl_web_https_http_hsts',
            'internet_nl_web_https_http_compress',

            'internet_nl_web_https_tls_version',
            'internet_nl_web_https_tls_ciphers',
            'internet_nl_web_https_tls_secreneg',
            'internet_nl_web_https_tls_clientreneg',
            'internet_nl_web_https_tls_keyexchange',
            'internet_nl_web_https_tls_compress',

            'internet_nl_web_https_cert_domain',
            'internet_nl_web_https_cert_chain',
            'internet_nl_web_https_cert_sig',
            'internet_nl_web_https_cert_pubkey',

            'internet_nl_web_https_dane_exist',
            'internet_nl_web_https_dane_valid',
        ],

        'legacy': [
            'internet_nl_web_legacy_dane',
            'internet_nl_web_legacy_tls_ncsc_web',
            'internet_nl_web_legacy_hsts',
            'internet_nl_web_legacy_https_enforced',
            'internet_nl_web_legacy_tls_available',
            'internet_nl_web_legacy_ipv6_webserver',
            'internet_nl_web_legacy_ipv6_nameserver',
        ]
    }
}


# https://stackoverflow.com/questions/29351492/how-to-make-a-continuous-alphabetic-list-python-from-a-z-then-from-aa-ab

def iter_all_strings():
    for size in itertools.count(1):
        for s in itertools.product(ascii_uppercase, repeat=size):
            yield "".join(s)


def create_spreadsheet(account: Account, report_id: int):
    # Fails softly, without exceptions if there is nothing yet.
    report = UrlListReport.objects.all().filter(
        urllist__account=account,
        pk=report_id).select_related('urllist').first()

    if not report:
        return []

    calculation = report.calculation
    urls = calculation["urls"]

    protocol = 'dns_soa' if report.urllist.scan_type == 'mail' else 'dns_a_aaaa'

    # results is a matrix / 2-d array / array with arrays.
    data: List[List[Any]] = []
    # done: functions are not supported in ods, which makes the output look terrible... Should we omit this?
    # omitted, as it gives inconsistent results. Kept code to re-use it if there is a workaround for ods / or we
    # know this is an ods file.
    # data += [formula_row(protocol=protocol, function="=COUNTA(%(column_name)s8:%(column_name)s9999)")]
    # data += [formula_row(protocol=protocol, function="=COUNTIF(%(column_name)s8:%(column_name)s9999,1)")]
    # data += [formula_row(protocol=protocol, function="=COUNTIF(%(column_name)s8:%(column_name)s9999,0)")]
    # data += [formula_row(protocol=protocol, function="=COUNTIF(%(column_name)s8:%(column_name)s9999,\"?\")")]
    # add an empty row for clarity
    data += [[]]
    data += [category_headers('dns_soa')]
    data += [headers('dns_soa')]
    data += urllistreport_to_spreadsheet_data(category_name=report.urllist.name, urls=urls, protocol=protocol)

    filename = "internet nl dashboard report %s %s %s %s" % (
        report.pk, report.urllist.name, report.urllist.scan_type, report.at_when)

    # The sheet is created into memory and then passed to the caller. They may save it, or serve it, etc...
    # http://docs.pyexcel.org/en/latest/tutorial06.html?highlight=memory
    # An issue with Sheet prevents uneven row lengths to be added. But that works fine with bookdicts
    book = p.get_book(bookdict={slugify(filename): data})

    return filename, book


def category_headers(protocol: str = 'dns_soa'):
    headers: List[str] = ['', '', '', '', '']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += [group]

        for x in range(len(SANE_COLUMN_ORDER[protocol][group])-1):
            headers += ['']

        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    return headers


def headers(protocol: str = 'dns_soa'):
    headers = ['Category', 'Url', 'Port', 'Ip Version', '']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += SANE_COLUMN_ORDER[protocol][group]
        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    return headers


def formula_row(function: str, protocol: str = 'dns_soa'):
    data = []

    my_headers = headers(protocol)
    total = len(my_headers)

    empty_headers = []
    for i in range(total):
        if my_headers[i] == '':
            empty_headers.append(i)

    # log.debug(empty_headers)

    # there is probably a function that does both. I'm not very familiar with itertools.
    index = 0
    for column_name in itertools.islice(iter_all_strings(), total):
        if index in empty_headers:
            data.append('')
        else:
            data.append(function % {'column_name': column_name})

        index += 1

    return data


def urllistreport_to_spreadsheet_data(category_name: str, urls: List[Any], protocol: str = 'dns_soa'):
    data = []
    for url in urls:

        if len(url['endpoints']) == 1:
            # we can just put the whole result in one, which is nicer to look at.
            for endpoint in url['endpoints']:
                if endpoint['protocol'] != protocol:
                    continue
                keyed_ratings = keyed_list(endpoint['ratings'], key_column='type')
                data.append([category_name, url['url'], endpoint['port'], endpoint['ip_version'], ''] +
                            keyed_values_as_boolean(keyed_ratings, protocol))

        else:
            data.append([category_name, url['url']])

            for endpoint in url['endpoints']:
                if endpoint['protocol'] != protocol:
                    continue
                keyed_ratings = keyed_list(endpoint['ratings'], key_column='type')
                data.append(['', '', endpoint['port'], endpoint['ip_version'], ''] +
                            keyed_values_as_boolean(keyed_ratings, protocol))

    # log.debug(data)
    return data


def keyed_values_as_boolean(keyed_ratings: Dict[str, Any], protocol: str = 'dns_soa'):
    values = []

    for group in SANE_COLUMN_ORDER[protocol]:

        for issue_name in SANE_COLUMN_ORDER[protocol][group]:
            # the issue name might not exist, the 'ok' value might not exist. In those cases replace it with a ?
            values.append(keyed_ratings.get(issue_name, {'ok': '?'}).get('ok', '?'))

        # add empty thing after each group to make distinction per group clearer
        values += ['']

    return values


def keyed_list(any_list_with_dicts: List[Dict[Any, Any]], key_column='type'):
    """
    Ratings are a list, which can be in any order. To prevent tons of looping over this list for the correct element,
    just make a dict where the keys are the keys we need.

    :param any_list_with_dicts: as it says
    :param key_column: the column you wish to use as key for quick access.
    :return:
    """

    result: Dict[str, Dict[str, Any]] = {}

    for item in any_list_with_dicts:
        result[item[key_column]] = item

    return result
