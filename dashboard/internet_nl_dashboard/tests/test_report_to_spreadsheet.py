# SPDX-License-Identifier: Apache-2.0
from websecmap.reporting.report import create_url_reports

from dashboard.internet_nl_dashboard.logic.domains import _add_to_urls_to_urllist, get_or_create_list_by_name
from dashboard.internet_nl_dashboard.logic.report_to_spreadsheet import create_spreadsheet, upgrade_excel_spreadsheet
from dashboard.internet_nl_dashboard.models import UrlListReport
from dashboard.internet_nl_dashboard.tests import create_scan_report, make_url_with_endpoint_and_scan


def test_report_to_spreadsheet(db) -> None:
    account, url, endpoint, scan = make_url_with_endpoint_and_scan()

    urllist = get_or_create_list_by_name(account, "test list 1")
    _add_to_urls_to_urllist(account, urllist, [url.url])
    create_url_reports(url)
    create_scan_report(account, urllist)

    # make sure there is a urllistreport to get a spreadsheet from
    assert UrlListReport.objects.all().count() == 1

    filename, spreadsheet = create_spreadsheet(account=account, report_id=urllist.pk)

    # there should be a spreadsheet
    assert spreadsheet

    tmp_file_handle = upgrade_excel_spreadsheet(spreadsheet)

    # and there should be a file handle
    assert tmp_file_handle


# def test_keyed_values_as_boolean():
#    keyed_ratings = {'internet_nl_mail_auth_dkim_exist': {'comply_or_explain_explained_on': '',
#                                      'comply_or_explain_explanation': '',
#                                      'comply_or_explain_explanation_valid_until': '',
#                                      'comply_or_explain_valid_at_time_of_report': False,
#                                      'explanation': 'Test '
#                                                     'internet_nl_mail_auth_dkim_exist '
#                                                     'resulted in failed.',
#                                      'high': 1,
#                                      'is_explained': False,
#                                      'last_scan': '2019-07-09T11:07:43.510452+00:00',
#                                      'low': 0,
#                                      'medium': 0,
#                                      'not_applicable': False,
#                                      'not_testable': False,
#                                      'ok': 0,
#                                      'scan': 43945,
#                                      'scan_type': 'internet_nl_mail_auth_dkim_exist',
#                                      'since': '2019-07-09T11:07:43.510175+00:00',
#                                      'type': 'internet_nl_mail_auth_dkim_exist'}}
#    rows = keyed_values_as_boolean(keyed_ratings)
#    assert rows == {}
