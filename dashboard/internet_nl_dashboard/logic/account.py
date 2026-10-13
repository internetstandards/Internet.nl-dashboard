# SPDX-License-Identifier: Apache-2.0


def save_report_settings(account, report_settings):
    account.report_settings = report_settings.get("filters", {})
    account.save()

    return None


def get_report_settings(account):
    return account.report_settings or {}
