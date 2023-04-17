# SPDX-License-Identifier: Apache-2.0
from dashboard.internet_nl_dashboard.logic.account import get_report_settings, save_report_settings
from dashboard.internet_nl_dashboard.models import Account


def test_urllists(db) -> None:
    account, created = Account.objects.all().get_or_create(name="test")

    settings = {"filters": {
        "web": {"visible": True},
        "web_legacy": {"visible": True},
        "mail": {"visible": True},
        "mail_legacy": {"visible": True},
    }
    }
    save_report_settings(account, settings)
    retrieved_settings = get_report_settings(account)

    assert retrieved_settings['data'] == settings['filters']
