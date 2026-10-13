# SPDX-License-Identifier: Apache-2.0
import re
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import Client

from dashboard.internet_nl_dashboard.models import Account, DashboardUser, UrlList, UrlListReport
from dashboard.internet_nl_dashboard.problems import ProblemType
from dashboard.internet_nl_dashboard.tests.test_http_responses import assert_problem


@pytest.fixture
def account_client(db, client):
    account = Account.objects.create(name="ADR account")
    user = User.objects.create_user(username="adr-user", is_staff=True, is_superuser=True)
    DashboardUser.objects.create(user=user, account=account)
    client.force_login(user)
    return client, account, user


def test_openapi_paths_queries_and_get_methods_follow_the_contract(client):
    schema = client.get("/api/v1/openapi.json").json()
    for path, methods in schema["paths"].items():
        assert not path.endswith("/"), "Resource paths must not end in a slash."
        for operation in methods.values():
            for parameter in operation.get("parameters", []):
                if parameter["in"] == "query":
                    assert re.fullmatch(
                        r"[a-z][a-z\d]*([A-Z][a-z\d]*)*", parameter["name"]
                    ), "Query keys must use camelCase."
        assert "requestBody" not in methods.get("get", {}), "GET requests must not depend on a request body."
    assert "delete" in schema["paths"]["/api/v1/session"], "Session deletion must use DELETE."
    assert "post" in schema["paths"]["/api/v1/mail/unsubscriptions"], "Unsubscription must use POST."
    assert "/api/v1/session/logout" not in schema["paths"], "The unsafe GET logout route must be removed."


@pytest.mark.parametrize(
    "schema_name,field,expected_format",
    [
        ("UserSettingsSchema", "date_joined", "date-time"),
        ("UserSettingsSchema", "last_login", "date-time"),
        ("UrlListSummarySchema", "last_scan", "date-time"),
        ("UrlListSummarySchema", "last_report_date", "date-time"),
        ("UploadHistoryItemSchema", "upload_date", "date-time"),
        ("RecentReportItemSchema", "at_when", "date-time"),
        ("PublicReportItemSchema", "at_when", "date-time"),
        ("PubliclySharedReportSchema", "at_when", "date-time"),
        ("SharedReportMetadataSchema", "at_when", "date-time"),
        ("UrlListTimelineDataPointSchema", "date", "date"),
        ("SaveAdHocTaggedReportInputSchema", "custom_date", "date"),
        ("SaveAdHocTaggedReportInputSchema", "custom_time", "time-local"),
        ("UserStatisticsSchema", "start_date", "date"),
        ("UserStatisticsSchema", "end_date", "date"),
    ],
)
def test_openapi_describes_temporal_fields(client, schema_name, field, expected_format):
    schema = client.get("/api/v1/openapi.json").json()["components"]["schemas"][schema_name]["properties"][field]
    variants = schema.get("anyOf", [schema])
    assert any(
        variant.get("type") == "string" and variant.get("format") == expected_format for variant in variants
    ), "Temporal fields must declare the appropriate string format, including when nullable."


def test_metrics_rejects_the_trailing_slash(account_client):
    client, _, _ = account_client
    assert_problem(client.post("/api/v1/reports/metrics/now/", {}, content_type="application/json"), 404)
    response = client.post("/api/v1/reports/metrics/now", {}, content_type="application/json")
    assert response.status_code == 200, "The canonical metric resource should remain available."


def test_user_statistics_accepts_camel_case_queries(account_client):
    client, _, _ = account_client
    response = client.get(
        "/api/v1/admin/user-statistics", {"startDate": "2026-01-02", "endDate": "2026-01-04", "maxRecords": 3}
    )
    assert response.status_code == 200, "CamelCase date filters should be accepted."
    assert response.json() == {
        "start_date": "2026-01-02",
        "end_date": "2026-01-04",
        "max_records": 3,
        "actors": [],
    }, "The supplied query parameters must control the actual statistics window."
    assert_problem(client.get("/api/v1/admin/user-statistics", {"startDate": "invalid", "maxRecords": 0}), 400)


def test_get_cannot_log_out_and_delete_ends_the_session(account_client):
    client, _, user = account_client
    assert_problem(client.get("/api/v1/session/logout"), 404)
    assert_problem(client.get("/api/v1/session"), 405)
    assert client.session.get("_auth_user_id") == str(user.id), "GET requests must preserve the session."
    response = client.delete("/api/v1/session")
    assert (
        response.status_code == 204 and response.content == b""
    ), "Deleting the current session should return no content."
    assert "_auth_user_id" not in client.session, "A successful DELETE must end the session."


def test_session_delete_requires_csrf(account_client):
    _, _, user = account_client
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    assert_problem(client.delete("/api/v1/session"), 403)
    assert client.session.get("_auth_user_id") == str(user.id), "A rejected logout must preserve the session."


def test_unsubscribe_requires_an_explicit_post_and_legacy_links_are_safe(account_client):
    client, _, user = account_client
    member = user.dashboarduser
    member.mail_send_mail_after_scan_finished = True
    member.mail_after_mail_unsubscribe_code = "x" * 128
    member.save()
    token = member.mail_after_mail_unsubscribe_code
    assert_problem(client.get("/api/v1/mail/unsubscriptions"), 405)
    response = client.get(f"/mail/unsubscribe/scan_finished/{token}/")
    assert (
        response.status_code == 302 and "/unsubscribe?" in response["Location"]
    ), "Old email links should open confirmation."
    member.refresh_from_db()
    assert member.mail_send_mail_after_scan_finished, "Opening an email link must not change the subscription."
    with patch("dashboard.internet_nl_dashboard.logic.mail.time.sleep"):
        response = client.post(
            "/api/v1/mail/unsubscriptions",
            {"feed": "scan_finished", "unsubscribe_code": token},
            content_type="application/json",
        )
    assert response.status_code == 204, "Confirmed unsubscription should return no content."
    member.refresh_from_db()
    assert not member.mail_send_mail_after_scan_finished, "POST must persist the unsubscribe request."


@pytest.mark.parametrize("token", ["", "x" * 127, "!" * 128])
def test_invalid_unsubscribe_tokens_cannot_match_users_with_unset_tokens(account_client, token):
    client, _, user = account_client
    member = user.dashboarduser
    member.mail_send_mail_after_scan_finished = True
    member.mail_after_mail_unsubscribe_code = ""
    member.save()
    response = client.post(
        "/api/v1/mail/unsubscriptions",
        {"feed": "scan_finished", "unsubscribe_code": token},
        content_type="application/json",
    )
    assert_problem(response, 400)
    member.refresh_from_db()
    assert (
        member.mail_send_mail_after_scan_finished
    ), "Invalid tokens must never affect users whose unsubscribe token is unset."


@pytest.mark.parametrize("method,share_code", [("get", None), ("post", "incorrect")])
def test_protected_report_uses_a_problem_and_preserves_password_form_metadata(account_client, method, share_code):
    client, account, _ = account_client
    urllist = UrlList.objects.create(account=account, name='Example "quoted" list')
    report = UrlListReport.objects.create(
        urllist=urllist,
        public_report_code="protected-report",
        public_share_code="secret",
        is_publicly_shared=True,
        at_when=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    url = "/api/v1/public-reports/protected-report"
    response = (
        client.get(url)
        if method == "get"
        else client.post(url, {"share_code": share_code}, content_type="application/json")
    )
    body = assert_problem(response, 403)
    assert body["type"] == ProblemType.REPORT_ACCESS_DENIED, "The error must identify report access denial."
    assert (
        body["report"]["id"] == report.id and body["report"]["urllist_name"] == urllist.name
    ), "The existing password form must retain report metadata."
    assert "T" in body["report"]["at_when"], "Problem metadata must serialize timestamps in ISO format."
    assert (
        "secret" not in response.content.decode() and "calculation" not in body["report"]
    ), "Access failures must not expose protected data."
    documented = client.get("/api/v1/openapi.json").json()["paths"]["/api/v1/public-reports/{report_code}"][method][
        "responses"
    ]
    assert "201" not in documented, "Access denial must not be documented as resource creation."
    assert documented["403"]["content"]["application/problem+json"]["schema"] == {
        "$ref": "#/components/schemas/SharedReportAccessProblemSchema"
    }, "OpenAPI must preserve the report extension schema."


def test_valid_report_share_code_returns_the_report_with_iso_timestamp(account_client):
    client, account, _ = account_client
    urllist = UrlList.objects.create(account=account, name='Example "quoted" list')
    UrlListReport.objects.create(
        urllist=urllist,
        public_report_code="protected-report",
        public_share_code="secret",
        is_publicly_shared=True,
        at_when=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    with patch("dashboard.internet_nl_dashboard.logic.report.retrieve_report_raw", return_value='{"urls": []}'):
        response = client.post(
            "/api/v1/public-reports/protected-report", {"share_code": "secret"}, content_type="application/json"
        )
    assert response.status_code == 200, "A valid share code must return the report."
    assert (
        response.json()["at_when"] == "2026-01-02T00:00:00+00:00"
    ), "Raw report serialization must use an ISO timestamp."
    assert (
        response.json()["urllist_name"] == urllist.name
    ), "Report metadata must remain valid JSON when names contain quotes."


def test_private_report_matches_its_object_schema_and_missing_reports_are_not_successful(account_client):
    client, account, _ = account_client
    urllist = UrlList.objects.create(account=account)
    report = UrlListReport.objects.create(urllist=urllist, at_when=datetime(2026, 1, 2, tzinfo=timezone.utc))
    with patch("dashboard.internet_nl_dashboard.logic.report.retrieve_report_raw", return_value='{"urls": []}'), patch(
        "dashboard.internet_nl_dashboard.logic.report.log_report_access_async.apply_async"
    ):
        response = client.get(f"/api/v1/reports/{report.id}")
    assert (
        response.status_code == 200 and response.json()["id"] == report.id
    ), "An existing report should be returned as one object."
    schema = client.get("/api/v1/openapi.json").json()["paths"]["/api/v1/reports/{report_id}"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["schema"]
    assert schema == {
        "$ref": "#/components/schemas/ReportSchema"
    }, "The documented shape must match the returned object."
    assert_problem(client.get("/api/v1/reports/999999"), 404)
    other = Account.objects.create(name="Other report account")
    report.urllist.account = other
    report.urllist.save()
    assert_problem(client.get(f"/api/v1/reports/{report.id}"), 404)


@pytest.mark.parametrize("data", [{"custom_date": "invalid"}, {"custom_time": "25:00"}, {"custom_time": "12:00+01:00"}])
def test_invalid_ad_hoc_temporal_input_is_rejected(account_client, data):
    client, _, _ = account_client
    assert_problem(client.post("/api/v1/reports/1/ad-hoc/preview", data, content_type="application/json"), 400)
