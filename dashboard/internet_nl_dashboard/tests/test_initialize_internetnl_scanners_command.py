# SPDX-License-Identifier: Apache-2.0
from django.core.management import call_command
from websecmap.reporting.models import ScanPolicy
from websecmap.reporting.time_cache import CACHE
from websecmap.scanners.models import Scanner, ScanType


def test_initialize_internetnl_scanners_provisions_scan_types_and_policies(db):
    CACHE["backend_scanmetadata"] = {"stale": True}

    call_command("initialize_internetnl_scanners")

    web_scanner = Scanner.objects.get(python_name="internet_nl_web")
    mail_scanner = Scanner.objects.get(python_name="internet_nl_mail")
    web_scan_type = ScanType.objects.get(name="internet_nl_web_overall_score")
    mail_scan_type = ScanType.objects.get(name="internet_nl_mail_dashboard_overall_score")

    assert web_scanner.creates_scan_types.filter(
        pk=web_scan_type.pk
    ).exists(), "expected internet_nl_web scanner to create internet_nl_web_overall_score"
    assert mail_scanner.creates_scan_types.filter(
        pk=mail_scan_type.pk
    ).exists(), "expected internet_nl_mail scanner to create internet_nl_mail_dashboard_overall_score"
    assert ScanPolicy.objects.filter(
        scan_type="internet_nl_mail_starttls_tls_available", conclusion="not_testable"
    ).exists(), "expected mail scanner startup to provision not_testable policy"
    assert "backend_scanmetadata" not in CACHE, "expected command to clear stale backend scan metadata cache"
