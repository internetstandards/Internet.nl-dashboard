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

from dashboard.internet_nl_dashboard.logic.internet_nl_translations import (get_po_as_dictionary_v2,
                                                                            translate_field)
from dashboard.internet_nl_dashboard.models import Account, UrlListReport

log = logging.getLogger(__package__)

# todo: read the preferred language of the user and use the translations matching this user...
po_file_as_dictionary = get_po_as_dictionary_v2('en')

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
            'internet_nl_score_report',
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
            'internet_nl_web_appsecpriv_csp',
            'internet_nl_web_appsecpriv_referrer_policy',
        ],

        'legacy': [
            'internet_nl_web_legacy_dnssec',
            'internet_nl_web_legacy_tls_available',
            'internet_nl_web_legacy_tls_ncsc_web',
            'internet_nl_web_legacy_https_enforced',
            'internet_nl_web_legacy_hsts',
            'internet_nl_web_legacy_category_ipv6',
            'internet_nl_web_legacy_ipv6_nameserver',
            'internet_nl_web_legacy_ipv6_webserver',
            # Deleted on request
            # 'internet_nl_web_legacy_dane',

            # added may 2020, api v2
            'internet_nl_web_legacy_tls_1_3',
        ]
    },
    'dns_soa': {
        # any grouping, every group has a empty column between them. The label is not used.
        'overall': [
            'internet_nl_score',
            'internet_nl_score_report',
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
            # 'internet_nl_mail_auth_dmarc_policy_only',  # Added 24th of May 2019
            # 'internet_nl_mail_auth_dmarc_ext_destination',  # Added 24th of May 2019

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
            'internet_nl_mail_legacy_category_ipv6',
            'internet_nl_mail_legacy_ipv6_nameserver',
            'internet_nl_mail_legacy_ipv6_mailserver',

            # Added may 2020 internet.nl api v2
            'internet_nl_mail_legacy_mail_non_sending_domain',
            'internet_nl_mail_legacy_mail_sending_domain',
            'internet_nl_mail_legacy_mail_server_testable',
            'internet_nl_mail_legacy_mail_server_reachable',
            'internet_nl_mail_legacy_domain_has_mx',
            'internet_nl_mail_legacy_tls_1_3',

        ]
    },
}


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
        ws.insert_rows(0, amount=9)

        ws[f'B1'] = "Total"
        ws[f'B2'] = "Passed"
        ws[f'B3'] = "Info"
        ws[f'B4'] = "Warning"
        ws[f'B5'] = "Failed"
        ws[f'B6'] = "Not tested"
        ws[f'B7'] = "Error"
        ws[f'B8'] = "Test not applicable (mail only)"
        ws[f'B9'] = "Percentage passed"

        # bold totals:
        for i in range(1, 10):
            ws[f'B{i}'].font = Font(bold=True)

        data_columns = [
            'F', 'G', 'H', 'I', 'J', 'K', 'L', "M", "N", 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO',
            'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD',
            'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK'
        ]

        # add some statistics
        for cell in data_columns:
            # if header, then aggregate
            if ws[f'{cell}12'].value:
                # There is a max of 5000 domains per scan. So we set this to something lower.
                # There is no good support of headers versus data, which makes working with excel a drama
                # If you ever read this code, and want a good spreadsheet editor: try Apple Numbers. It's fantastic.
                ws[f'{cell}1'] = f'=COUNTA({cell}13:{cell}5050)'
                # todo: also support other values
                ws[f'{cell}2'] = f'=COUNTIF({cell}13:{cell}5050, "passed")'
                ws[f'{cell}3'] = f'=COUNTIF({cell}13:{cell}5050, "info")'
                ws[f'{cell}4'] = f'=COUNTIF({cell}13:{cell}5050, "warning")'
                ws[f'{cell}5'] = f'=COUNTIF({cell}13:{cell}5050, "failed")'
                ws[f'{cell}6'] = f'=COUNTIF({cell}13:{cell}5050, "not_tested")'
                ws[f'{cell}7'] = f'=' \
                                 f'COUNTIF({cell}13:{cell}5050, "error")+' \
                                 f'COUNTIF({cell}13:{cell}5050, "unreachable")+' \
                                 f'COUNTIF({cell}13:{cell}5050, "untestable")+' \
                                 f'COUNTIF({cell}13:{cell}5050, "not_testable")'
                ws[f'{cell}8'] = f'=' \
                                 f'COUNTIF({cell}13:{cell}5050, "no_mx")+' \
                                 f'COUNTIF({cell}13:{cell}5050, "not_applicable")'
                # Not applicable and not testable are subtracted from the total.
                # See https://github.com/internetstandards/Internet.nl-dashboard/issues/68
                # Rounding's num digits is NOT the number of digits behind the comma, but the total number of digits.
                # todo: we should use the calculations in report.py. And there include the "missing" / empty stuff IF
                # that is missing.
                #                   IF(     H1=0,0,ROUND(     H2÷     H1, 4))
                ws[f'{cell}9'] = f'=IF({cell}1=0,0,ROUND({cell}2/{cell}1, 4))'
                ws[f'{cell}9'].number_format = '0.00%'

        # make headers bold
        ws[f'A12'].font = Font(bold=True)  # List
        ws[f'B12'].font = Font(bold=True)  # Url
        ws[f'C11'].font = Font(bold=True)  # overall
        ws[f'C12'].font = Font(bold=True)  # % Score
        ws[f'D12'].font = Font(bold=True)  # Report
        for cell in data_columns:
            ws[f'{cell}11'].font = Font(bold=True)
            ws[f'{cell}12'].font = Font(bold=True)

        # Freeze pane to make navigation easier.
        ws.freeze_panes = ws['E13']

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
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"passed"'], stopIfTrue=True, fill=greenFill)
        )

        ws.conditional_formatting.add(
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"failed"'], stopIfTrue=True, fill=redFill)
        )

        ws.conditional_formatting.add(
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"warning"'], stopIfTrue=True, fill=orangeFill)
        )

        ws.conditional_formatting.add(
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"info"'], stopIfTrue=True, fill=blueFill)
        )

        ws.conditional_formatting.add(
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"good_not_tested"'], stopIfTrue=True, fill=altgrayFill)
        )

        ws.conditional_formatting.add(
            'F13:CD5050',
            CellIsRule(operator='=', formula=['"not_tested"'], stopIfTrue=True, fill=grayFill)
        )

        log.debug(ws.title)
        wb.save(tmp.name)

        return tmp


def category_headers(protocol: str = 'dns_soa'):
    headers: List[str] = ['', '']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += [translate_field(group, translation_dictionary=po_file_as_dictionary)]

        for x in range(len(SANE_COLUMN_ORDER[protocol][group])-1):
            headers += ['']

        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    return headers


def headers(protocol: str = 'dns_soa'):
    headers = ['List', 'Url']
    for group in SANE_COLUMN_ORDER[protocol]:
        headers += SANE_COLUMN_ORDER[protocol][group]
        # add empty thing after each group to make distinction per group clearer
        headers += ['']

    # translate them:
    headers = [translate_field(header, translation_dictionary=po_file_as_dictionary) for header in headers]

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
                data.append([category_name, url['url']] + keyed_values_as_boolean(keyed_ratings, protocol))

        else:
            data.append([category_name, url['url']])

            for endpoint in url['endpoints']:
                if endpoint['protocol'] != protocol:
                    continue
                keyed_ratings = endpoint['ratings_by_type']
                data.append(['', ''] + keyed_values_as_boolean(keyed_ratings, protocol))

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
            elif issue_name == 'internet_nl_score_report':
                # fake column to give the column a title per #205, also makes the report more explicit.
                values.append(keyed_ratings['internet_nl_score']['internet_nl_url'])
                # add empty column
                values.append(" ")
            else:
                # the issue name might not exist, the 'ok' value might not exist. In those cases replace it with a ?
                value = keyed_ratings.get(issue_name, {'ok': '?',
                                                       'not_testable': False,
                                                       'not_applicable': False, 'error_in_test': False})

                # api v2, tls1.3 update
                if value.get('test_result', False):
                    test_value = value.get('test_result', '?')
                    # per 205, translate not_testable to untestable. This is cosmetic as the 'not_testable' is
                    # everywhere in the software and is just renamed, and will probably be renamed a few times
                    # more in the future.
                    if test_value == "not_testable":
                        test_value = "untestable"
                    values.append(test_value)

                else:
                    # unknown columns and data will be empty.
                    if "simple_verdict" not in value:
                        values.append('')
                    else:
                        # backward compatible with api v1 reportsunreachable
                        if value['simple_verdict'] == "not_testable":
                            values.append('untestable')
                        elif value['simple_verdict'] == "not_applicable":
                            values.append('not_applicable')
                        elif value['simple_verdict'] == "error_in_test":
                            values.append('error')
                        else:
                            # When the value doesn't exist at all, we'll get a questionmark.
                            values.append(value.get('ok', '?'))

        # add empty thing after each group to make distinction per group clearer
        # overall group already adds an extra value (url), so we don't need this.
        if group != "overall":
            values += ['']

    return values
