import logging

from dashboard.internet_nl_dashboard.logic import operation_response

log = logging.getLogger(__package__)


def save_report_settings(account, report_settings):
    account.report_settings = report_settings.get('filters', {})
    account.save()

    return operation_response(success=True, message="settings.updated")


def get_report_settings(account):
    return operation_response(
        success=True,
        message="report.settings.restored_from_database",
        data=account.report_settings if account.report_settings else {}
    )
