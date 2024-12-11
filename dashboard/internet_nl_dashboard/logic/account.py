# SPDX-License-Identifier: Apache-2.0
from dashboard.internet_nl_dashboard.logic import operation_response


def save_report_settings(account, report_settings):
    account.report_settings = report_settings.get("filters", {})
    account.save()

    return operation_response(success=True, message="settings.updated")


def get_report_settings(account):
    return operation_response(
        success=True,
        message="settings.restored_from_database",
        data=account.report_settings if account.report_settings else {},
    )
