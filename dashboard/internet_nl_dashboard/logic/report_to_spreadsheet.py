import itertools
import logging
from string import ascii_uppercase
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List

import pyexcel as p
from django.utils.text import slugify
from openpyxl import load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill

from dashboard.internet_nl_dashboard.logic.internet_nl_translations import (DJANGO_I18N_OUTPUT_PATH,
                                                                            get_po_as_dictionary)
from dashboard.internet_nl_dashboard.models import Account, UrlListReport

log = logging.getLogger(__package__)

# Hack to get internet.nl translations (which are inconsistent in naming) to a similar level as it's json counterpart.
# Todo: Perhaps we should just export the translations to JSON anyway...
po_file_location = f"{DJANGO_I18N_OUTPUT_PATH}en/LC_MESSAGES/django.po"
# log.debug(f"po_file_location: {po_file_location}")
try:
    po_file_as_dictionary = get_po_as_dictionary(po_file_location)
except OSError as e:
    raise SystemError(f"Missing PO file 'django.po' at {po_file_location}. Note that an exception about "
                      f"incorrect syntax may be misleading. This is also given when there is no file. "
                      f"The exception that is given: {e}")

"""
Creates spreadsheets containing report data.

Done: make sure the columns are in a custom order. Columns are defined in scanners. The order of the columns isn't.
Done: make sure you can download the spreadsheet in a single click
Done: add a sane logic to the spreadsheet content
Done: support ods and xlsx.
Done: can we support sum rows at the top for boolean values(?), only for excel. Not for ods, which is too bad.
Done: get column translations. From internet.nl PO files? How do they map to these variables?
Done: write some tests for these methods, once they are more table.
"""

SANE_COLUMN_ORDER = {
    # scanner
    'dns_a_aaaa': {
        'overall': [
            'internet_nl_score',
        ],

        'ipv6': [
            # Category
            'internet_nl_web_ipv6',

            'internet_nl_web_ipv6_ns_address',
            'internet_nl_web_ipv6_ns_reach',

            'internet_nl_web_ipv6_ws_address',
            'internet_nl_web_ipv6_ws_reach',
            'internet_nl_web_ipv6_ws_similar',
        ],

        'dnssec': [
            # Category
            'internet_nl_web_dnssec',

            'internet_nl_web_dnssec_exist',
            'internet_nl_web_dnssec_valid',
        ],

        'tls': [
            # Category
            'internet_nl_web_tls',

            # HTTP
            'internet_nl_web_https_http_available',
            'internet_nl_web_https_http_redirect',
            'internet_nl_web_https_http_compress',
            'internet_nl_web_https_http_hsts',

            # TLS
            'internet_nl_web_https_tls_version',
            'internet_nl_web_https_tls_ciphers',
            'internet_nl_web_https_tls_cipherorder',
            'internet_nl_web_https_tls_keyexchange',
            'internet_nl_web_https_tls_keyexchangehash',
            'internet_nl_web_https_tls_compress',
            'internet_nl_web_https_tls_secreneg',
            'internet_nl_web_https_tls_clientreneg',
            'internet_nl_web_https_tls_0rtt',
            'internet_nl_web_https_tls_ocsp',

            # Certificate
            'internet_nl_web_https_cert_chain',
            'internet_nl_web_https_cert_pubkey',
            'internet_nl_web_https_cert_sig',
            'internet_nl_web_https_cert_domain',

            # DANE
            'internet_nl_web_https_dane_exist',
            'internet_nl_web_https_dane_valid',
        ],

        # Added 24th of May 2019
        'appsecpriv': [
            # Category
            'internet_nl_web_appsecpriv',

            'internet_nl_web_appsecpriv_x_frame_options',
            'internet_nl_web_appsecpriv_x_content_type_options',
            'internet_nl_web_appsecpriv_x_xss_protection',
            'internet_nl_web_appsecpriv_csp',
            'internet_nl_web_appsecpriv_referrer_policy',
        ],

        'legacy': [
            'internet_nl_web_legacy_dnssec',
            'internet_nl_web_legacy_tls_available',
            'internet_nl_web_legacy_tls_ncsc_web',
            'internet_nl_web_legacy_https_enforced',
            'internet_nl_web_legacy_hsts',
            'internet_nl_web_legacy_ipv6_nameserver',
            'internet_nl_web_legacy_ipv6_webserver',
            'internet_nl_web_legacy_dane',
        ]
    },
    'dns_soa': {
        # any grouping, every group has a empty column between them. The label is not used.
        'overall': [
            'internet_nl_score'
        ],
        'ipv6': [
            # Category
            'internet_nl_mail_dashboard_ipv6',

            # name servers
            'internet_nl_mail_ipv6_ns_address',
            'internet_nl_mail_ipv6_ns_reach',

            # mail server(s)
            'internet_nl_mail_ipv6_mx_address',
            'internet_nl_mail_ipv6_mx_reach',
        ],

        'dnssec': [
            # Category
            'internet_nl_mail_dashboard_dnssec',

            # email address domain
            'internet_nl_mail_dnssec_mailto_exist',
            'internet_nl_mail_dnssec_mailto_valid',

            # mail server domain(s)
            'internet_nl_mail_dnssec_mx_exist',
            'internet_nl_mail_dnssec_mx_valid',
        ],

        'auth': [
            # Category
            'internet_nl_mail_dashboard_auth',

            # DMARC
            'internet_nl_mail_auth_dmarc_exist',
            'internet_nl_mail_auth_dmarc_policy',
            'internet_nl_mail_auth_dmarc_policy_only',  # Added 24th of May 2019
            'internet_nl_mail_auth_dmarc_ext_destination',  # Added 24th of May 2019

            # DKIM
            'internet_nl_mail_auth_dkim_exist',

            # SPF
            'internet_nl_mail_auth_spf_exist',
            'internet_nl_mail_auth_spf_policy',
        ],

        # perhaps split these into multiple groups.
        'tls': [
            'internet_nl_mail_dashboard_tls',

            # TLS
            'internet_nl_mail_starttls_tls_available',
            'internet_nl_mail_starttls_tls_version',
            'internet_nl_mail_starttls_tls_ciphers',
            'internet_nl_mail_starttls_tls_cipherorder',
            'internet_nl_mail_starttls_tls_keyexchange',
            'internet_nl_mail_starttls_tls_keyexchangehash',
            'internet_nl_mail_starttls_tls_compress',
            'internet_nl_mail_starttls_tls_secreneg',
            'internet_nl_mail_starttls_tls_clientreneg',
            'internet_nl_mail_starttls_tls_0rtt',

            # Certificate
            'internet_nl_mail_starttls_cert_chain',
            'internet_nl_mail_starttls_cert_pubkey',
            'internet_nl_mail_starttls_cert_sig',
            'internet_nl_mail_starttls_cert_domain',

            # DANE
            'internet_nl_mail_starttls_dane_exist',
            'internet_nl_mail_starttls_dane_valid',
            'internet_nl_mail_starttls_dane_rollover',
        ],

        'legacy': [
            'internet_nl_mail_legacy_dmarc',
            'internet_nl_mail_legacy_dkim',
            'internet_nl_mail_legacy_spf',
            'internet_nl_mail_legacy_dmarc_policy',
            'internet_nl_mail_legacy_spf_policy',
            'internet_nl_mail_legacy_start_tls',
            'internet_nl_mail_legacy_start_tls_ncsc',
            'internet_nl_mail_legacy_dnssec_email_domain',
            'internet_nl_mail_legacy_dnssec_mx',
            'internet_nl_mail_legacy_dane',
            'internet_nl_mail_legacy_ipv6_nameserver',
            'internet_nl_mail_legacy_ipv6_mailserver',
        ]
    },
}


def translate_field(field_label):
    """
    Try to solve the very inconsistent naming from the internet.nl translations (random dashes, case mixes etc)

    :param field_label:
    :return:
    """
    field_mapping = {
        # mail fields, see dashboard.js
        'internet_nl_mail_starttls_cert_domain': 'detail_mail_tls_cert_hostmatch_label',
        'internet_nl_mail_starttls_tls_version': 'detail_mail_tls_version_label',
        'internet_nl_mail_starttls_cert_chain': 'detail_mail_tls_cert_trust_label',
        'internet_nl_mail_starttls_tls_available': 'detail_mail_tls_starttls_exists_label',
        'internet_nl_mail_starttls_tls_clientreneg': 'detail_mail_tls_renegotiation_client_label',
        'internet_nl_mail_starttls_tls_ciphers': 'detail_mail_tls_ciphers_label',
        'internet_nl_mail_starttls_dane_valid': 'detail_mail_tls_dane_valid_label',
        'internet_nl_mail_starttls_dane_exist': 'detail_mail_tls_dane_exists_label',
        'internet_nl_mail_starttls_tls_secreneg': 'detail_mail_tls_renegotiation_secure_label',
        'internet_nl_mail_starttls_dane_rollover': 'detail_mail_tls_dane_rollover_label',
        'internet_nl_mail_starttls_cert_pubkey': 'detail_mail_tls_cert_pubkey_label',
        'internet_nl_mail_starttls_cert_sig': 'detail_mail_tls_cert_signature_label',
        'internet_nl_mail_starttls_tls_compress': 'detail_mail_tls_compression_label',
        'internet_nl_mail_starttls_tls_keyexchange': 'detail_mail_tls_fs_params_label',
        'internet_nl_mail_auth_dmarc_policy': 'detail_mail_auth_dmarc_policy_label',
        'internet_nl_mail_auth_dmarc_exist': 'detail_mail_auth_dmarc_label',
        'internet_nl_mail_auth_spf_policy': 'detail_mail_auth_spf_policy_label',
        'internet_nl_mail_auth_dkim_exist': 'detail_mail_auth_dkim_label',
        'internet_nl_mail_auth_spf_exist': 'detail_mail_auth_spf_label',
        'internet_nl_mail_dnssec_mailto_exist': 'detail_mail_dnssec_exists_label',
        'internet_nl_mail_dnssec_mailto_valid': 'detail_mail_dnssec_valid_label',
        'internet_nl_mail_dnssec_mx_valid': 'detail_mail_dnssec_mx_valid_label',
        'internet_nl_mail_dnssec_mx_exist': 'detail_mail_dnssec_mx_exists_label',
        'internet_nl_mail_ipv6_mx_address': 'detail_mail_ipv6_mx_aaaa_label',
        'internet_nl_mail_ipv6_mx_reach': 'detail_mail_ipv6_mx_reach_label',
        'internet_nl_mail_ipv6_ns_reach': 'detail_web_mail_ipv6_ns_reach_label',
        'internet_nl_mail_ipv6_ns_address': 'detail_web_mail_ipv6_ns_aaaa_label',
        'internet_nl_mail_starttls_tls_cipherorder': 'detail_mail_tls_cipher_order_label',
        'internet_nl_mail_starttls_tls_keyexchangehash': 'detail_mail_tls_kex_hash_func_label',
        'internet_nl_mail_starttls_tls_0rtt': 'detail_mail_tls_zero_rtt_label',


        # web fields, see dashboard.js
        'internet_nl_web_appsecpriv': 'results_domain_appsecpriv_http_headers_label',
        'internet_nl_web_appsecpriv_csp': 'detail_web_appsecpriv_http_csp_label',
        'internet_nl_web_appsecpriv_referrer_policy': 'detail_web_appsecpriv_http_referrer_policy_label',
        'internet_nl_web_appsecpriv_x_content_type_options': 'detail_web_appsecpriv_http_x_content_type_label',
        'internet_nl_web_appsecpriv_x_frame_options': 'detail_web_appsecpriv_http_x_frame_label',
        'internet_nl_web_appsecpriv_x_xss_protection': 'detail_web_appsecpriv_http_x_xss_label',
        'internet_nl_web_https_cert_domain': 'detail_web_tls_cert_hostmatch_label',
        'internet_nl_web_https_http_redirect': 'detail_web_tls_https_forced_label',
        'internet_nl_web_https_cert_chain': 'detail_web_tls_cert_trust_label',
        'internet_nl_web_https_tls_version': 'detail_web_tls_version_label',
        'internet_nl_web_https_tls_clientreneg': 'detail_web_tls_renegotiation_client_label',
        'internet_nl_web_https_tls_ciphers': 'detail_web_tls_ciphers_label',
        'internet_nl_web_https_http_available': 'detail_web_tls_https_exists_label',
        'internet_nl_web_https_dane_exist': 'detail_web_tls_dane_exists_label',
        'internet_nl_web_https_http_compress': 'detail_web_tls_http_compression_label',
        'internet_nl_web_https_http_hsts': 'detail_web_tls_https_hsts_label',
        'internet_nl_web_https_tls_secreneg': 'detail_web_tls_renegotiation_secure_label',
        'internet_nl_web_https_dane_valid': 'detail_web_tls_dane_valid_label',
        'internet_nl_web_https_cert_pubkey': 'detail_web_tls_cert_pubkey_label',
        'internet_nl_web_https_cert_sig': 'detail_web_tls_cert_signature_label',
        'internet_nl_web_https_tls_compress': 'detail_web_tls_compression_label',
        'internet_nl_web_https_tls_keyexchange': 'detail_web_tls_fs_params_label',
        'internet_nl_web_dnssec_valid': 'detail_web_dnssec_valid_label',
        'internet_nl_web_dnssec_exist': 'detail_web_dnssec_exists_label',
        'internet_nl_web_ipv6_ws_similar': 'detail_web_ipv6_web_ipv46_label',
        'internet_nl_web_ipv6_ws_address': 'detail_web_ipv6_web_aaaa_label',
        'internet_nl_web_ipv6_ns_reach': 'detail_web_mail_ipv6_ns_reach_label',
        'internet_nl_web_ipv6_ws_reach': 'detail_web_ipv6_web_reach_label',
        'internet_nl_web_ipv6_ns_address': 'detail_web_mail_ipv6_ns_aaaa_label',
        'internet_nl_web_https_tls_cipherorder': 'detail_web_tls_cipher_order_label',
        'internet_nl_web_https_tls_0rtt': 'detail_web_tls_zero_rtt_label',
        'internet_nl_web_https_tls_ocsp': 'detail_web_tls_ocsp_stapling_label',
        'internet_nl_web_https_tls_keyexchangehash': 'detail_web_tls_kex_hash_func_label',

        'internet_nl_web_tls': 'test_sitetls_label',
        'internet_nl_web_dnssec': 'test_sitednssec_label',
        'internet_nl_web_ipv6': 'test_siteipv6_label',
        'internet_nl_mail_dashboard_tls': 'test_mailtls_label',
        'internet_nl_mail_dashboard_auth': 'test_mailauth_label',
        'internet_nl_mail_dashboard_dnssec': 'test_maildnssec_label',
        'internet_nl_mail_dashboard_ipv6': 'test_mailipv6_label',
        'internet_nl_score': '% Score',

        # directly translated fields.
        'internet_nl_mail_legacy_dmarc': 'DMARC',
        'internet_nl_mail_legacy_dkim': 'DKIM',
        'internet_nl_mail_legacy_spf': 'SPF',
        'internet_nl_mail_legacy_dmarc_policy': 'DMARC policy',
        'internet_nl_mail_legacy_spf_policy': 'SPF policy',
        'internet_nl_mail_legacy_start_tls': 'STARTTLS',
        'internet_nl_mail_legacy_start_tls_ncsc': 'STARTTLS NCSC',
        'internet_nl_mail_legacy_dnssec_email_domain': 'DNSSEC e-mail domain',
        'internet_nl_mail_legacy_dnssec_mx': 'DNSSEC MX',
        'internet_nl_mail_legacy_dane': 'DANE',
        'internet_nl_mail_legacy_ipv6_nameserver': 'IPv6 nameserver',
        'internet_nl_mail_legacy_ipv6_mailserver': 'IPv6 mailserver',

        'internet_nl_web_legacy_dnssec': 'DNSSEC',
        'internet_nl_web_legacy_tls_available': 'TLS available',
        'internet_nl_web_legacy_tls_ncsc_web': 'TLS NCSC web',
        'internet_nl_web_legacy_https_enforced': 'HTTPS enforced',
        'internet_nl_web_legacy_hsts': 'HSTS',
        'internet_nl_web_legacy_ipv6_nameserver': 'IPv6 nameserver',
        'internet_nl_web_legacy_ipv6_webserver': 'IPv6 webserver',
        'internet_nl_web_legacy_dane': 'DANE',

        'legacy': 'nlgovernment_complyorexplain',
        'internet_nl_mail_dashboard_overall_score': 'Score',
        'internet_nl_web_overall_score': 'Score',
    }

    # handle inconsistent naming and (why cannot i load something else than django.po?)
    try:
        return po_file_as_dictionary.get(field_mapping[field_label], field_mapping[field_label])
    except KeyError:
        return field_label


def iter_all_strings():
    # https://stackoverflow.com/questions/29351492/how-to-make-a-continuous-alphabetic-list-python-from-a-z-then-from-aa-ab
    for size in itertools.count(1):
        for s in itertools.product(ascii_uppercase, repeat=size):
            yield "".join(s)


def create_spreadsheet(account: Account, report_id: int):
    # Fails softly, without exceptions if there is nothing yet.
    report = UrlListReport.objects.all().filter(
        urllist__account=account,
        pk=report_id).select_related('urllist').first()

    if not report:
        return None, None

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
    data += [category_headers(protocol)]
    data += [headers(protocol)]
    data += urllistreport_to_spreadsheet_data(category_name=report.urllist.name, urls=urls, protocol=protocol)

    filename = "internet nl dashboard report %s %s %s %s" % (
        report.pk, report.urllist.name, report.urllist.scan_type, report.at_when.date())

    # The sheet is created into memory and then passed to the caller. They may save it, or serve it, etc...
    # http://docs.pyexcel.org/en/latest/tutorial06.html?highlight=memory
    # An issue with Sheet prevents uneven row lengths to be added. But that works fine with bookdicts
    # The name of a sheet can only be 32 characters, make sure the most significant info is in the title first.
    tabname = f"{report.pk} {report.urllist.scan_type} {report.at_when.date()} {report.urllist.name}"[0:31]
    book = p.get_book(bookdict={slugify(tabname): data})

    return filename, book


def upgrade_excel_spreadsheet(spreadsheet_data):

    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        log.debug(f"Saving temp outout to {tmp.name}")
        spreadsheet_data.save_as(array=spreadsheet_data, filename=tmp.name)

        wb = load_workbook(tmp.name)
        ws = wb.active

        # nicer columns
        ws.column_dimensions["A"].width = "30"
        ws.column_dimensions["B"].width = "30"

        # Add statistic rows:
        ws.insert_rows(0, amount=8)

        ws[f'B1'] = "Total"
        ws[f'B2'] = "Contains passed"
        ws[f'B3'] = "Contains info"
        ws[f'B4'] = "Contains warning"
        ws[f'B5'] = "Contains failed"
        ws[f'B6'] = "Contains good_not_tested"
        ws[f'B7'] = "Contains not_tested"
        ws[f'B8'] = "Percentage passed (ignoring not_tested)"

        # bold totals:
        for i in range(1, 9):
            ws[f'B{i}'].font = Font(bold=True)

        data_columns = [
            'H', 'I', 'J', 'K', 'L', "M", "N", 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO',
            'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD',
            'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS',
            'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ'
        ]

        for cell in data_columns:
            # if header, then aggregate
            if ws[f'{cell}11'].value:
                # There is a max of 5000 domains per scan. So we set this to something lower.
                # There is no good support of headers versus data, which makes working with excel a drama
                # If you ever read this code, and want a good spreadsheet editor: try Apple Numbers. It's fantastic.
                ws[f'{cell}1'] = f'=COUNTA({cell}11:{cell}5050)'
                # todo: also support other values
                ws[f'{cell}2'] = f'=COUNTIF({cell}11:{cell}5050, "passed")'
                ws[f'{cell}3'] = f'=COUNTIF({cell}11:{cell}5050, "info")'
                ws[f'{cell}4'] = f'=COUNTIF({cell}11:{cell}5050, "warning")'
                ws[f'{cell}5'] = f'=COUNTIF({cell}11:{cell}5050, "failed")'
                ws[f'{cell}6'] = f'=COUNTIF({cell}11:{cell}5050, "good_not_tested")'
                ws[f'{cell}7'] = f'=COUNTIF({cell}11:{cell}5050, "not_tested")'
                # Not applicable and not testable are subtracted from the total.
                # See https://github.com/internetstandards/Internet.nl-dashboard/issues/68
                # Rounding's num digits is NOT the number of digits behind the comma, but the total number of digits.
                # todo: we should use the calculations in report.py. And there include the "missing" / empty stuff IF
                # that is missing.
                ws[f'{cell}8'] = f'=ROUND({cell}2/({cell}1 - ({cell}6 + {cell}7)), 4)'
                ws[f'{cell}8'].number_format = '0.00%'

        # fold port and ip-version (and protocol?) from report as it's not useful in this case?
        ws.column_dimensions.group('C', 'E', hidden=True)

        # line 9 is an empty line

        # make headers bold
        ws[f'A11'].font = Font(bold=True)
        ws[f'B11'].font = Font(bold=True)
        ws[f'F10'].font = Font(bold=True)
        ws[f'F11'].font = Font(bold=True)
        for cell in data_columns:
            ws[f'{cell}10'].font = Font(bold=True)
            ws[f'{cell}11'].font = Font(bold=True)

        # Freeze pane to make navigation easier.
        ws.freeze_panes = ws['H11']

        # there is probably a feature that puts this in a single conditional value.
        greenFill = PatternFill(start_color='B7FFC8', end_color='B7FFC8', fill_type='solid')
        redFill = PatternFill(start_color='FFB7B7', end_color='FFB7B7', fill_type='solid')
        blueFill = PatternFill(start_color='B7E3FF', end_color='B7E3FF', fill_type='solid')
        orangeFill = PatternFill(start_color='FFD9B7', end_color='FFD9B7', fill_type='solid')
        grayFill = PatternFill(start_color='99FFFF', end_color='DBDBDB', fill_type='solid')
        altgrayFill = PatternFill(start_color='99FFFF', end_color='C0C0C0', fill_type='solid')
        # Set the measurements to green/red depending on value using conditional formatting.
        # There is no true/false, but we can color based on value.
        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"passed"'], stopIfTrue=True, fill=greenFill)
        )

        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"failed"'], stopIfTrue=True, fill=redFill)
        )

        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"warning"'], stopIfTrue=True, fill=orangeFill)
        )

        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"info"'], stopIfTrue=True, fill=blueFill)
        )

        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"good_not_tested"'], stopIfTrue=True, fill=altgrayFill)
        )

        ws.conditional_formatting.add(
            'H12:CD9999',
            CellIsRule(operator='=', formula=['"not_tested"'], stopIfTrue=True, fill=grayFill)
        )

        log.debug(ws.title)
        wb.save(tmp.name)

        return tmp


def category_headers(protocol: str = 'dns_soa'):
    headers: List[str] = ['', '', '', '', '']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += [translate_field(group)]

        for x in range(len(SANE_COLUMN_ORDER[protocol][group])-1):
            headers += ['']

        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    return headers


def headers(protocol: str = 'dns_soa'):
    headers = ['List', 'Url', 'Port', 'Ip Version', '']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += SANE_COLUMN_ORDER[protocol][group]
        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    # translate them:
    headers = [translate_field(header) for header in headers]

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
                keyed_ratings = endpoint['ratings_by_type']
                data.append([category_name, url['url'], endpoint['port'], endpoint['ip_version'], ''] +
                            keyed_values_as_boolean(keyed_ratings, protocol))

        else:
            data.append([category_name, url['url']])

            for endpoint in url['endpoints']:
                if endpoint['protocol'] != protocol:
                    continue
                keyed_ratings = endpoint['ratings_by_type']
                data.append(['', '', endpoint['port'], endpoint['ip_version'], ''] +
                            keyed_values_as_boolean(keyed_ratings, protocol))

    # log.debug(data)
    return data


def keyed_values_as_boolean(keyed_ratings: Dict[str, Any], protocol: str = 'dns_soa'):
    """
    Keyed rating:
    {'internet_nl_mail_auth_dkim_exist': {'comply_or_explain_explained_on': '',
                                      'comply_or_explain_explanation': '',
                                      'comply_or_explain_explanation_valid_until': '',
                                      'comply_or_explain_valid_at_time_of_report': False,
                                      'explanation': 'Test '
                                                     'internet_nl_mail_auth_dkim_exist '
                                                     'resulted in failed.',
                                      'high': 1,
                                      'is_explained': False,
                                      'last_scan': '2019-07-09T11:07:43.510452+00:00',
                                      'low': 0,
                                      'medium': 0,
                                      'not_applicable': False,
                                      'not_testable': False,
                                      'ok': 0,
                                      'scan': 43945,
                                      'scan_type': 'internet_nl_mail_auth_dkim_exist',
                                      'since': '2019-07-09T11:07:43.510175+00:00',
                                      'type': 'internet_nl_mail_auth_dkim_exist'},...

    :param keyed_ratings:
    :param protocol:
    :return:
    """

    values = []

    for group in SANE_COLUMN_ORDER[protocol]:

        for issue_name in SANE_COLUMN_ORDER[protocol][group]:

            if issue_name == 'internet_nl_score':
                # Handle the special case of the score column.
                # explanation":"75 https://batch.internet.nl/mail/portaal.digimelding.nl/289480/",
                # Not steadily convertable to a percentage, so printing it as an integer instead.
                values.append(int(keyed_ratings[issue_name]['internet_nl_score']))
                values.append(keyed_ratings[issue_name]['internet_nl_url'])
            else:
                # the issue name might not exist, the 'ok' value might not exist. In those cases replace it with a ?
                value = keyed_ratings.get(issue_name, {'ok': '?', 'not_testable': False, 'not_applicable': False})

                # api v2, tls1.3 update
                if value.get('test_result', False):
                    values.append(value.get('test_result', '?'))

                else:
                    # backward compatible with api v1 reports
                    if value['simple_verdict'] == "not_testable":
                        values.append('not_testable')
                    elif value['simple_verdict'] == "not_applicable":
                        values.append('not_applicable')
                    else:
                        # When the value doesn't exist at all, we'll get a questionmark.
                        values.append(value.get('ok', '?'))

        # add empty thing after each group to make distinction per group clearer
        # overall group already adds an extra value (url), so we don't need this.
        if group != "overall":
            values += ['']

    return values
