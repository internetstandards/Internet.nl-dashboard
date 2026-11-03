# SPDX-License-Identifier: Apache-2.0
from urllib.parse import parse_qs, urlsplit

import pytest
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint
from websecmap.scanners_internet_nl_web.models import InternetNLV2Scan

from dashboard.internet_nl_dashboard.admin import InputListFilter
from dashboard.internet_nl_dashboard.models import (
    Account,
    AccountInternetNLScan,
    AccountInternetNLScanLog,
    DashboardUser,
    SubdomainDiscoveryScan,
    TaggedUrlInUrllist,
    UploadLog,
    UrlList,
    UrlListReport,
)


@pytest.fixture
def admin_request(rf, admin_user):
    request = rf.get("/admin/internet_nl_dashboard/")
    request.user = admin_user
    request.session = {}
    return request


@pytest.fixture
def admin_records(db):
    scans = []
    for number in range(6):
        account = Account.objects.create(name=f"Account {number}")
        urllist = UrlList.objects.create(account=account, name=f"List {number}")
        user = DashboardUser.objects.create(account=account, user=User.objects.create(username=f"user-{number}"))
        url = Url.objects.create(url=f"example-{number}.nl")
        TaggedUrlInUrllist.objects.create(url=url, urllist=urllist)
        report = UrlListReport.objects.create(urllist=urllist, at_when=timezone.now(), calculation={"large": "report"})
        scan = AccountInternetNLScan.objects.create(
            account=account,
            urllist=urllist,
            scan=InternetNLV2Scan.objects.create(type="web", retrieved_scan_report={"large": "scan"}),
            report=report,
            state="finished",
        )
        scans.append(scan)
        AccountInternetNLScanLog.objects.create(scan=scan, state="finished", at_when=timezone.now())
        UploadLog.objects.create(user=user, message=f"Uploaded file {number}")
        SubdomainDiscoveryScan.objects.create(urllist=urllist, state="finished")
    return scans


@pytest.mark.parametrize(
    "model",
    (
        Account,
        UrlList,
        TaggedUrlInUrllist,
        AccountInternetNLScan,
        AccountInternetNLScanLog,
        UploadLog,
        SubdomainDiscoveryScan,
        UrlListReport,
    ),
)
def test_admin_pages_use_bounded_queries(
    model, admin_records, admin_request, django_assert_max_num_queries, monkeypatch
):
    def reject_report_payload(*args):
        pytest.fail("Admin list pages must not retrieve or decompress report payloads.")

    for field in (
        UrlListReport._meta.get_field("calculation"),
        InternetNLV2Scan._meta.get_field("retrieved_scan_report"),
        InternetNLV2Scan._meta.get_field("retrieved_scan_report_technical"),
    ):
        monkeypatch.setattr(field, "from_db_value", reject_report_payload)

    # Six rows already expose per-row relation/count queries; the budget includes Jet's menu queries.
    with django_assert_max_num_queries(12):
        response = admin.site._registry[model].changelist_view(admin_request)
        response.render()

    assert response.status_code == 200, "Every dashboard model's admin list should render successfully."
    assert len(response.context_data["cl"].result_list) == 6, "The optimized query should preserve all matching rows."


def test_scan_id_filter_does_not_load_choices(admin_records, admin_request, django_assert_num_queries):
    model_admin = admin.site._registry[AccountInternetNLScanLog]
    with django_assert_num_queries(0):
        spec = InputListFilter(
            AccountInternetNLScanLog._meta.get_field("scan"),
            admin_request,
            {},
            AccountInternetNLScanLog,
            model_admin,
            "scan",
        )
    assert spec.has_output(), "The scan ID input should remain available without enumerating scans."


@pytest.mark.parametrize("value", ("", " ", "invalid", "999999999999999999999999999999999"))
def test_scan_id_filter_handles_invalid_or_empty_input(value, admin_records, admin_request):
    model_admin = admin.site._registry[AccountInternetNLScanLog]
    spec = InputListFilter(
        AccountInternetNLScanLog._meta.get_field("scan"),
        admin_request,
        {"scan__id__exact": [value]},
        AccountInternetNLScanLog,
        model_admin,
        "scan",
    )
    if value == "invalid":
        with pytest.raises(IncorrectLookupParameters):
            spec.queryset(admin_request, AccountInternetNLScanLog.objects.all())
    else:
        expected_count = 6 if not value.strip() else 0
        assert (
            spec.queryset(admin_request, AccountInternetNLScanLog.objects.all()).count() == expected_count
        ), "Empty IDs should leave results unfiltered, and out-of-range IDs should match no rows."


def test_id_filter_preserves_other_filters_and_resets_pagination(admin_records, admin_request):
    scan = admin_records[0]
    admin_request.GET = admin_request.GET.copy()
    admin_request.GET.update({"scan__id__exact": str(scan.id), "state": "finished", "q": "Account", "p": "0"})
    model_admin = admin.site._registry[AccountInternetNLScanLog]
    changelist = model_admin.get_changelist_instance(admin_request)
    spec = next(spec for spec in changelist.filter_specs if isinstance(spec, InputListFilter))
    choice = next(spec.choices(changelist))

    assert tuple(changelist.queryset.values_list("scan", flat=True)) == (
        scan.id,
    ), "The scan ID must combine with the selected state and account search."
    other_parameters = dict(choice["other_parameters"])
    assert other_parameters == {
        "state": "finished",
        "q": "Account",
    }, "Submitting an input filter should retain search/other filters and return to the first page."
    assert parse_qs(urlsplit(choice["clear_url"]).query) == {
        "state": ["finished"],
        "q": ["Account"],
    }, "Clearing an input filter should remove only that filter and pagination."

    html = render_to_string(
        "admin/input_filter.html", {"title": spec.title, "spec": spec, "choices": spec.choices(changelist)}
    )
    assert (
        'class="changelist-filter-popup"' in html
    ), "Jet must retain the input when it moves filters into the toolbar."
    assert 'type="number"' in html, "Related-object filters should accept IDs through a numeric input."
    assert 'name="scan__id__exact"' in html, "Existing scan-filter URLs must continue to use Django's exact-ID lookup."


def test_text_filter_matches_partial_message(admin_records, admin_request):
    model_admin = admin.site._registry[UploadLog]
    spec = InputListFilter(
        UploadLog._meta.get_field("message"),
        admin_request,
        {"message__icontains": ["FILE 2"]},
        UploadLog,
        model_admin,
        "message",
    )
    result = spec.queryset(admin_request, UploadLog.objects.all()).get()
    assert result.message == "Uploaded file 2", "Message filters should support case-insensitive partial text searches."


def test_urllist_counts_exclude_inactive_urls_and_endpoints(
    db, admin_request, django_assert_num_queries, django_assert_max_num_queries
):
    account = Account.objects.create(name="Counts")
    urllist = UrlList.objects.create(account=account, name="Populated")
    empty = UrlList.objects.create(account=account, name="Empty")
    shared = UrlList.objects.create(account=account, name="Shared domain")
    for number, flags in enumerate(({}, {}, {"is_dead": True}, {"not_resolvable": True})):
        url = Url.objects.create(url=f"counts-{number}.nl", **flags)
        TaggedUrlInUrllist.objects.create(url=url, urllist=urllist)
        if number == 0:
            TaggedUrlInUrllist.objects.create(url=url, urllist=shared)
        for port in (80, 443, 8443):
            Endpoint.objects.create(
                url=url, port=port, protocol="https", discovered_on=timezone.now(), is_dead=port == 8443
            )

    model_admin = admin.site._registry[UrlList]
    with django_assert_max_num_queries(6):
        results = {item.id: item for item in model_admin.get_changelist_instance(admin_request).result_list}
    with django_assert_num_queries(0):
        assert model_admin.no_of_urls(results[urllist.id]) == 2, "Multiple endpoints must not multiply the URL count."
        assert (
            model_admin.no_of_endpoints(results[urllist.id]) == 4
        ), "Only living endpoints belonging to living, resolvable URLs should be counted."
        assert model_admin.no_of_urls(results[empty.id]) == 0, "Empty lists must display zero URLs."
        assert model_admin.no_of_endpoints(results[empty.id]) == 0, "Empty lists must display zero endpoints."
        assert model_admin.no_of_urls(results[shared.id]) == 1, "Shared domains should be counted separately per list."
        assert model_admin.no_of_endpoints(results[shared.id]) == 2, "Endpoint totals should belong to their own list."


@pytest.mark.parametrize(
    "enabled,deleted,states,expected",
    (
        (True, False, (), True),
        (False, False, (), False),
        (True, False, ("finished",), True),
        (True, False, ("cancelled",), True),
        (True, False, ("finished", "running"), False),
        (True, False, ("running", "finished"), True),
        (True, False, ("",), False),
        (True, True, ("running",), True),
    ),
)
def test_scan_availability_matches_model(
    enabled, deleted, states, expected, db, admin_request, django_assert_num_queries
):
    account = Account.objects.create(name="Scan availability")
    urllist = UrlList.objects.create(account=account, name="Availability", enable_scans=enabled, is_deleted=deleted)
    for state in states:
        AccountInternetNLScan.objects.create(account=account, urllist=urllist, state=state)
    model_admin = admin.site._registry[UrlList]
    result = model_admin.get_changelist_instance(admin_request).result_list[0]

    assert urllist.is_scan_now_available() is expected, "Exercise the existing scan-availability rules."
    with django_assert_num_queries(0):
        assert (
            model_admin.is_scan_now_available(result) is expected
        ), "Admin availability must preserve latest-scan, enabled, and deleted-list behavior without queries."


def test_scan_admin_supports_pending_scans_without_internetnl_scan(db, admin_request):
    account = Account.objects.create(name="Pending")
    urllist = UrlList.objects.create(account=account, name="Pending")
    AccountInternetNLScan.objects.create(account=account, urllist=urllist, state="requested")
    response = admin.site._registry[AccountInternetNLScan].changelist_view(admin_request)
    response.render()
    assert response.status_code == 200, "Pending scans should display before an Internet.nl scan has been assigned."
