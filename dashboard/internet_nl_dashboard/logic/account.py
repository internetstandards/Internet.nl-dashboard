import logging

from dashboard.internet_nl_dashboard.logic import operation_response

log = logging.getLogger(__package__)


def save_report_settings(account, report_settings):
    account.report_settings = report_settings.get('filters', {})
    account.save()

    return operation_response(success=True, message="Settings updated")


def get_report_settings(account):
    return account.report_settings
