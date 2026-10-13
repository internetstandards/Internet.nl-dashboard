# SPDX-License-Identifier: Apache-2.0
import errno
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import requests
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from kombu.exceptions import OperationalError
from websecmap.organizations.models import Url

from dashboard.internet_nl_dashboard.models import Account, AccountInternetNLScan, DashboardUser, UploadLog, UrlList
from dashboard.internet_nl_dashboard.problems import DocumentedApiError, ProblemType, problem_responses, raises


@pytest.fixture
def signed_in(db, client):
    account = Account.objects.create(name="HTTP contract account")
    user = User.objects.create_user(username="http-contract-user")
    DashboardUser.objects.create(user=user, account=account)
    client.force_login(user)
    return client, account, user


def assert_problem(response, status):
    assert response.status_code == status, "The HTTP status should describe the failure."
    assert response["Content-Type"] == "application/problem+json", "Failures must use the Problem Details media type."
    body = response.json()
    assert body["status"] == status, "The problem status should match the HTTP status."
    assert body["title"] and body["detail"], "Problems must include a readable title and detail."
    assert isinstance(body["detail"], str), "Problem detail must be text, including for validation errors."
    assert (
        not {"success", "error", "message", "timestamp", "state", "code"} & body.keys()
    ), "Errors must have no legacy envelope."
    assert "API-Version" in response, "Error responses must retain the API version header."
    return body


@pytest.mark.parametrize("state", ["new", "requested", "cancelled"])
def test_cancel_scan_and_repeat_are_no_content(signed_in, state):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    scan = AccountInternetNLScan.objects.create(account=account, urllist=urllist, state=state)
    for _ in range(2):
        response = client.delete(f"/api/v1/scans/{scan.id}")
        assert response.status_code == 204, "Cancelling an active or cancelled scan should succeed idempotently."
        assert response.content == b"", "A 204 response must have no body."
    scan.refresh_from_db()
    assert scan.state == "cancelled", "Cancellation must persist the scan state."


def test_cancel_finished_scan_is_conflict(signed_in):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    scan = AccountInternetNLScan.objects.create(account=account, urllist=urllist, state="finished")
    body = assert_problem(client.delete(f"/api/v1/scans/{scan.id}"), 409)
    assert body["type"] == ProblemType.SCAN_ALREADY_FINISHED, "The problem type should identify the state conflict."
    scan.refresh_from_db()
    assert scan.state == "finished", "A finished scan must not be changed by cancellation."


def test_cancel_scan_cannot_reach_another_account(signed_in):
    client, _, _ = signed_in
    other = Account.objects.create(name="Another account")
    urllist = UrlList.objects.create(account=other)
    scan = AccountInternetNLScan.objects.create(account=other, urllist=urllist, state="new")
    assert_problem(client.delete(f"/api/v1/scans/{scan.id}"), 404)
    assert_problem(client.delete("/api/v1/scans/999999"), 404)
    scan.refresh_from_db()
    assert scan.state == "new", "A foreign scan must remain unchanged."


@pytest.mark.parametrize("url", ["/api/v1/scans/not-an-integer", "/api/v1/urllists/not-an-integer"])
def test_invalid_path_parameters_are_bad_requests(signed_in, url):
    client, _, _ = signed_in
    body = assert_problem(client.delete(url), 400)
    assert body["errors"], "All schema validation errors should be available separately from the textual detail."


def test_authentication_and_method_errors_use_problem_details(client):
    assert_problem(client.delete("/api/v1/scans/1"), 401)
    response = client.put("/api/v1/scans/1", data={}, content_type="application/json")
    assert_problem(response, 405)
    assert "DELETE" in response["Allow"], "Method failures must retain the allowed methods."
    assert_problem(client.get("/api/v1/unknown-resource"), 404)


def test_csrf_failure_uses_problem_details(signed_in):
    _, _, user = signed_in
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    assert_problem(client.delete("/api/v1/scans/1"), 403)


def test_unexpected_failures_hide_internal_details(signed_in):
    client, _, _ = signed_in
    with patch("dashboard.internet_nl_dashboard.views.scans.get_scan_monitor_data", side_effect=RuntimeError("secret")):
        response = client.get("/api/v1/scans")
    body = assert_problem(response, 500)
    assert "secret" not in body["detail"], "Internal exceptions must not leak into the response."


def test_settings_save_and_read_resource_data(signed_in):
    client, account, user = signed_in
    response = client.post(
        "/api/v1/settings/account/report", {"filters": {"web": {"visible": True}}}, content_type="application/json"
    )
    assert response.status_code == 204 and response.content == b"", "Saving report settings should return no content."
    response = client.get("/api/v1/settings/account/report")
    assert response.json() == {"web": {"visible": True}}, "Settings should be returned directly."
    response = client.post(
        "/api/v1/settings/user",
        {
            "first_name": "Updated",
            "last_name": "User",
            "mail_preferred_language": "en",
            "mail_preferred_mail_address": "updated@example.com",
            "mail_send_mail_after_scan_finished": True,
        },
        content_type="application/json",
    )
    assert response.status_code == 204 and response.content == b"", "Saving user settings should return no content."
    user.refresh_from_db()
    assert user.first_name == "Updated", "A successful response must correspond to a persisted update."


def test_validation_and_malformed_json_are_bad_requests(signed_in):
    client, _, _ = signed_in
    body = assert_problem(client.post("/api/v1/settings/user", {}, content_type="application/json"), 400)
    assert len(body["errors"]) >= 4, "Missing required fields should be reported together."
    assert body["type"] == ProblemType.INVALID_INPUT, "Schema failures must have a stable validation problem type."
    assert_problem(client.post("/api/v1/settings/user", "{invalid", content_type="application/json"), 400)
    assert_problem(client.post("/api/v1/settings/account/report", "{invalid", content_type="application/json"), 400)


@pytest.mark.parametrize(
    "field,value,problem_type",
    [
        ("mail_preferred_language", "unsupported", ProblemType.UNSUPPORTED_LANGUAGE),
        ("mail_preferred_mail_address", "invalid-email", ProblemType.INVALID_EMAIL_ADDRESS),
    ],
)
def test_user_setting_validation_identifies_the_problem_and_field(signed_in, field, value, problem_type):
    client, _, _ = signed_in
    data = {
        "first_name": "Example",
        "last_name": "User",
        "mail_preferred_language": "en",
        "mail_preferred_mail_address": "example@example.com",
        "mail_send_mail_after_scan_finished": True,
        field: value,
    }
    body = assert_problem(client.post("/api/v1/settings/user", data, content_type="application/json"), 400)
    assert body["type"] == problem_type, "The URI must distinguish the validation reason without a translation code."
    assert body["errors"] == [
        {"loc": ["body", field], "msg": body["detail"]}
    ], "Domain validation must identify the invalid field using the same structure as schema validation."


def test_list_creation_update_and_deletion_return_resources_or_no_content(signed_in):
    client, account, _ = signed_in
    data = {
        "id": -1,
        "name": "Created list",
        "enable_scans": False,
        "scan_type": "web",
        "automated_scan_frequency": "disabled",
        "automatically_share_new_reports": False,
        "enable_report_sharing_page": False,
    }
    response = client.post("/api/v1/urllists", data, content_type="application/json")
    assert response.status_code == 201, "Creating a list should return Created."
    body = response.json()
    assert body["name"] == data["name"] and "data" not in body, "The response should be the created list itself."
    data["name"] = "Updated list"
    response = client.put(f"/api/v1/urllists/{body['id']}", data, content_type="application/json")
    assert response.status_code == 200, "Updating a list should return the updated resource."
    assert response.json()["name"] == "Updated list", "The updated list should be returned directly."
    response = client.delete(f"/api/v1/urllists/{body['id']}")
    assert response.status_code == 204 and response.content == b"", "Deleting a list should return no content."
    assert_problem(client.delete(f"/api/v1/urllists/{body['id']}"), 404)


def test_list_failures_and_unchanged_foreign_url_cannot_succeed(signed_in):
    client, _, _ = signed_in
    other = Account.objects.create(name="Foreign URL account")
    urllist = UrlList.objects.create(account=other)
    url = Url.objects.create(url="example.com")
    urllist.urls.add(url)
    assert_problem(client.delete(f"/api/v1/urllists/{urllist.id}"), 404)
    assert_problem(
        client.put(
            f"/api/v1/urllists/{urllist.id}/urls/{url.id}",
            {"new_url_string": "example.com"},
            content_type="application/json",
        ),
        404,
    )
    assert_problem(
        client.post(f"/api/v1/urllists/{urllist.id}/urls", {"raw_urls": ""}, content_type="application/json"), 404
    )


def test_domain_limit_is_a_typed_field_error_through_the_http_api(signed_in):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    with patch("dashboard.internet_nl_dashboard.logic.domains.constance_cached_value", return_value=0):
        response = client.post(
            f"/api/v1/urllists/{urllist.id}/urls", {"raw_urls": "example.com"}, content_type="application/json"
        )
    body = assert_problem(response, 400)
    assert (
        body["type"] == ProblemType.DOMAIN_LIMIT_EXCEEDED
    ), "The real import logic must identify a domain-limit error."
    assert body["errors"][0]["loc"] == ["body", "raw_urls"], "The field error must identify the submitted domains."
    assert urllist.urls.count() == 0, "A rejected import must leave the list unchanged."


def test_start_scan_accepts_work_and_reports_state_conflicts(signed_in):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    with patch.object(UrlList, "is_scan_now_available", return_value=True), patch.object(
        Account, "connect_to_internet_nl_api", return_value=True
    ), patch.object(Account, "decrypt_password", return_value=""), patch(
        "dashboard.internet_nl_dashboard.logic.domains.initialize_scan"
    ) as start:
        response = client.post(f"/api/v1/urllists/{urllist.id}/scans")
    assert response.status_code == 202, "Starting asynchronous work should return Accepted."
    assert start.call_count == 1, "Accepted work must actually be scheduled."
    with patch.object(UrlList, "is_scan_now_available", return_value=False):
        assert_problem(client.post(f"/api/v1/urllists/{urllist.id}/scans"), 409)
    assert_problem(client.post("/api/v1/urllists/999999/scans"), 404)


def test_discovery_retains_resource_state(signed_in):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    url = f"/api/v1/urllists/{urllist.id}/www-subdomain-discovery"
    body = assert_problem(client.get(url), 404)
    assert (
        body["type"] == ProblemType.DISCOVERY_NOT_STARTED
    ), "An unstarted discovery should identify the initial state."
    missing = assert_problem(client.get("/api/v1/urllists/999999/www-subdomain-discovery"), 404)
    assert (
        missing["type"] == ProblemType.LIST_NOT_FOUND
    ), "A missing list must be distinguishable from an unstarted scan."
    response = client.post(url)
    assert response.status_code == 202, "Discovery requests should be accepted."
    assert response.json()["state"] == "requested", "Scan state is useful resource data and must be retained."
    assert "success" not in response.json(), "Discovery data should have no operation envelope."
    response = client.get(url)
    assert response.status_code == 200 and response.json()["state"] == "requested", "Polling should return scan state."


def test_upload_acceptance_returns_the_upload_identifier(signed_in):
    client, _, _ = signed_in
    upload = SimpleUploadedFile("domains.csv", b"example.com\n")
    with patch("dashboard.internet_nl_dashboard.logic.spreadsheets.save_file", return_value="domains.csv"), patch(
        "dashboard.internet_nl_dashboard.logic.spreadsheets.log_spreadsheet_upload", return_value={"id": 42}
    ), patch("dashboard.internet_nl_dashboard.logic.spreadsheets.group"):
        response = client.post("/api/v1/urllists/import-spreadsheets", {"file": upload})
    assert response.status_code == 202, "Queued imports should return Accepted."
    assert response.json() == {"uploadlog_id": 42}, "The import identifier should be returned without an envelope."


@pytest.mark.parametrize("path", ["/api/v1/urllists/import-spreadsheets", "/api/v1/urllists/1/spreadsheets"])
@pytest.mark.parametrize("storage_errno", [errno.ENOSPC, errno.EDQUOT, errno.EBUSY])
def test_known_spreadsheet_storage_failures_are_service_unavailable(signed_in, path, storage_errno):
    client, _, _ = signed_in
    upload = SimpleUploadedFile("domains.csv", b"example.com\n")
    with patch(
        "dashboard.internet_nl_dashboard.logic.spreadsheet.FileSystemStorage.save",
        side_effect=OSError(storage_errno, "private storage path"),
    ), patch("dashboard.internet_nl_dashboard.logic.spreadsheets.group") as schedule:
        response = client.post(path, {"file": upload})
    body = assert_problem(response, 503)
    assert (
        body["type"] == ProblemType.SPREADSHEET_STORAGE_UNAVAILABLE
    ), "Known storage outages should have a specific problem type."
    assert "private storage path" not in body["detail"], "Storage internals must not be exposed in the response."
    assert schedule.call_count == 0, "An upload must not be scheduled when its file could not be saved."


@pytest.mark.parametrize(
    "failure", [RuntimeError("private bug"), PermissionError(errno.EACCES, "private configuration")]
)
def test_unexpected_spreadsheet_storage_failures_use_shared_internal_error(signed_in, failure):
    client, _, _ = signed_in
    upload = SimpleUploadedFile("domains.csv", b"example.com\n")
    with patch("dashboard.internet_nl_dashboard.logic.spreadsheet.FileSystemStorage.save", side_effect=failure):
        response = client.post("/api/v1/urllists/import-spreadsheets", {"file": upload})
    body = assert_problem(response, 500)
    assert body["type"] == "about:blank", "Unexpected failures must use the generic HTTP problem type."
    assert "private" not in body["detail"], "Unexpected failures must use the shared generic detail."


def test_spreadsheet_queue_outage_is_service_unavailable_and_marks_upload_failed(signed_in, settings, tmp_path):
    client, _, _ = signed_in
    settings.MEDIA_ROOT = tmp_path
    upload = SimpleUploadedFile("domains.csv", b"example.com\n")
    with patch("dashboard.internet_nl_dashboard.logic.spreadsheets.group") as schedule:
        schedule.return_value.apply_async.side_effect = OperationalError("private broker connection")
        response = client.post("/api/v1/urllists/import-spreadsheets", {"file": upload})
    body = assert_problem(response, 503)
    assert (
        body["type"] == ProblemType.SPREADSHEET_QUEUE_UNAVAILABLE
    ), "A broker outage should be reported as temporary unavailability."
    assert "private broker" not in body["detail"], "Broker connection details must remain on the server."
    log = UploadLog.objects.get()
    assert log.status == "error", "An unscheduled upload must not remain indefinitely in the initializing state."
    assert log.message == body["detail"], "Upload history should explain why the import did not start."


def test_missing_spreadsheet_is_invalid_input_not_a_service_failure(signed_in):
    client, _, _ = signed_in
    with patch("dashboard.internet_nl_dashboard.logic.spreadsheets.group") as schedule:
        response = client.post("/api/v1/urllists/import-spreadsheets", {})
    assert_problem(response, 400)
    assert schedule.call_count == 0, "Invalid requests must not schedule an import."


@pytest.mark.parametrize(
    "failure,status,problem_type",
    [
        (requests.ConnectionError("private upstream"), 503, ProblemType.SUBDOMAIN_SUGGESTIONS_UNAVAILABLE),
        (requests.Timeout("private upstream"), 504, ProblemType.SUBDOMAIN_SUGGESTIONS_TIMEOUT),
        (500, 502, ProblemType.SUBDOMAIN_SUGGESTIONS_FAILED),
        (503, 503, ProblemType.SUBDOMAIN_SUGGESTIONS_UNAVAILABLE),
        (
            requests.exceptions.JSONDecodeError("private response", "?", 0),
            502,
            ProblemType.SUBDOMAIN_SUGGESTIONS_FAILED,
        ),
    ],
)
def test_subdomain_suggestion_dependency_failures_are_explicit(signed_in, failure, status, problem_type):
    client, _, _ = signed_in
    with patch(
        "dashboard.internet_nl_dashboard.logic.domains.tldextract.extract",
        return_value=SimpleNamespace(domain="example", suffix="com"),
    ), patch("dashboard.internet_nl_dashboard.logic.domains.requests.get") as upstream:
        if isinstance(failure, int):
            upstream.return_value.status_code = failure
        elif isinstance(failure, requests.exceptions.JSONDecodeError):
            upstream.return_value.status_code = 200
            upstream.return_value.json.side_effect = failure
        else:
            upstream.side_effect = failure
        response = client.get("/api/v1/urllists/1/url-suggestions", {"domain": "example.com"})
    body = assert_problem(response, status)
    assert body["type"] == problem_type, "Known dependency failures should retain their specific problem type."
    assert "private" not in body["detail"], "Upstream internals must not be exposed to clients."


def test_subdomain_suggestions_reject_invalid_domains_as_bad_requests(signed_in):
    client, _, _ = signed_in
    with patch(
        "dashboard.internet_nl_dashboard.logic.domains.tldextract.extract",
        return_value=SimpleNamespace(domain="", suffix=""),
    ), patch("dashboard.internet_nl_dashboard.logic.domains.requests.get") as upstream:
        response = client.get("/api/v1/urllists/1/url-suggestions", {"domain": "invalid"})
    body = assert_problem(response, 400)
    assert (
        body["type"] == ProblemType.INVALID_SUGGESTION_DOMAIN
    ), "An invalid domain should be identified as a request error."
    assert upstream.call_count == 0, "Invalid domains must be rejected before contacting the suggestion service."


@pytest.mark.parametrize("method,suffix", [("POST", "ad-hoc/preview"), ("POST", "ad-hoc")])
def test_ad_hoc_report_missing_resource_is_not_an_internal_error(signed_in, method, suffix):
    client, _, _ = signed_in
    response = client.generic(method, f"/api/v1/reports/999999/{suffix}", data="{}", content_type="application/json")
    body = assert_problem(response, 404)
    assert body["type"] == "about:blank", "A missing source report needs only the generic HTTP problem type."


def test_signup_errors_and_acceptance_use_http_status(db, client):
    form = {
        "access": [],
        "name": "Applicant",
        "email": "applicant@example.com",
        "mobile_phone_number": "",
        "organization_name": "Example",
        "nature_of_organization": "",
        "chamber_of_commerce_number": "",
        "reason_for_application": "Testing",
        "intended_usage_frequency": "",
        "terms_of_use": ["accepted"],
        "captcha": 41,
    }
    body = assert_problem(client.post("/api/v1/signup", {"form_data": form}, content_type="application/json"), 400)
    assert body["type"] == ProblemType.INVALID_CAPTCHA, "Invalid captcha should retain its problem type."
    form["captcha"] = 42
    with patch("dashboard.internet_nl_dashboard.views.signup.sleep"), patch(
        "dashboard.internet_nl_dashboard.views.signup.send_backoffice_mail_async"
    ), patch("dashboard.internet_nl_dashboard.views.signup.send_signup_received_mail_to_requester"):
        response = client.post("/api/v1/signup", {"form_data": form}, content_type="application/json")
    assert response.status_code == 202, "Queued application notifications should return Accepted."


def test_admin_conflict_and_missing_public_report_use_problem_details(signed_in):
    client, _, user = signed_in
    user.is_superuser = True
    user.save()
    body = assert_problem(
        client.post(
            "/api/v1/admin/accounts",
            {
                "new_username": user.username,
                "new_password": "long-test-password",
                "new_email_address": "test@example.com",
            },
            content_type="application/json",
        ),
        409,
    )
    assert (
        body["type"] == ProblemType.USERNAME_ALREADY_EXISTS
    ), "A duplicate username should be a translatable conflict."
    with patch("dashboard.internet_nl_dashboard.logic.report.sleep"):
        assert_problem(client.get("/api/v1/public-reports/missing-report"), 404)


@pytest.mark.parametrize(
    "field,problem_type",
    [
        ("new_username", ProblemType.USERNAME_ALREADY_EXISTS),
        ("new_account_name", ProblemType.ACCOUNT_NAME_ALREADY_EXISTS),
    ],
)
def test_admin_conflicts_share_http_status_but_identify_the_conflicting_field(signed_in, field, problem_type):
    client, account, user = signed_in
    user.is_superuser = True
    user.save()
    data = {
        "new_username": "unused-username",
        "new_account_name": "Unused account",
        "new_password": "long-test-password",
        "new_email_address": "test@example.com",
    }
    data[field] = user.username if field == "new_username" else account.name
    body = assert_problem(client.post("/api/v1/admin/accounts", data, content_type="application/json"), 409)
    assert body["type"] == problem_type, "The problem type must distinguish the two kinds of conflict."
    assert body["errors"][0]["loc"] == [
        "body",
        field,
    ], "The frontend should be able to highlight the conflicting field."


@pytest.mark.parametrize(
    "message,status,problem_type,detail",
    [
        ("list_does_not_exist", 404, ProblemType.LIST_NOT_FOUND, "List does not exist."),
        ("add_domains_list_does_not_exist", 404, ProblemType.LIST_NOT_FOUND, "List does not exist."),
        ("too_many_domains", 400, ProblemType.DOMAIN_LIMIT_EXCEEDED, "Too many domains."),
        (
            "The uploaded file contained no data.",
            400,
            ProblemType.INVALID_SPREADSHEET,
            "The uploaded file contained no data.",
        ),
        (None, 400, ProblemType.INVALID_SPREADSHEET, "Spreadsheet could not be imported."),
    ],
)
def test_synchronous_spreadsheet_errors_use_problem_details(signed_in, message, status, problem_type, detail):
    client, _, _ = signed_in
    upload = SimpleUploadedFile("domains.csv", b"example.com\n")
    with patch(
        "dashboard.internet_nl_dashboard.views.urllists.upload_domain_spreadsheet_to_list",
        return_value={"error": True, "message": message},
    ):
        response = client.post("/api/v1/urllists/999999/spreadsheets", {"file": upload})
    body = assert_problem(response, status)
    assert body["type"] == problem_type, "Import failures must have stable identifiers independent of their text."
    assert body["detail"] == detail, "Spreadsheet validation messages belong in the readable detail."
    if status == 400:
        assert body["errors"][0]["loc"] == ["body", "file"], "Invalid uploads must identify the file field."


def resolve_openapi_response(schema, response):
    if "$ref" in response:
        assert set(response) == {
            "$ref"
        }, "A response reference must not have ignored description/content/header siblings."
        prefix = "#/components/responses/"
        assert response["$ref"].startswith(prefix), "Shared responses should use local component references."
        return schema["components"]["responses"][response["$ref"][len(prefix) :]]
    return response


def test_openapi_documents_the_http_contract(client):
    schema = client.get("/api/v1/openapi.json").json()
    scan = schema["paths"]["/api/v1/scans/{scan_id}"]["delete"]["responses"]
    assert "204" in scan, "OpenAPI must document the bodyless cancellation response."
    assert "content" not in scan["204"], "A 204 response must not advertise JSON content."
    server_error = resolve_openapi_response(schema, scan["500"])
    assert "application/problem+json" in server_error["content"], "Errors must advertise the problem media type."
    assert "400" in scan, "Invalid path parameters must be documented as Bad Request."
    assert "422" not in scan, "The schema should not advertise Ninja's default validation status."
    assert {"status", "title", "detail"} <= set(
        schema["components"]["schemas"]["ProblemSchema"]["required"]
    ), "The Problem schema must require the ADR fields."
    problem_schema = schema["components"]["schemas"]["ProblemSchema"]
    assert "code" not in problem_schema["properties"], "OpenAPI must advertise the standard type without a custom code."
    assert {"$ref": "#/components/schemas/ProblemType"} in problem_schema["properties"]["type"][
        "anyOf"
    ], "The problem schema must reference the generated domain type inventory."
    assert set(schema["components"]["schemas"]["ProblemType"]["enum"]) == {
        str(problem_type) for problem_type in ProblemType
    }, "OpenAPI must expose every domain problem identifier directly from the code."
    field_errors = problem_schema["properties"]["errors"]["anyOf"][0]["items"]
    assert field_errors == {
        "$ref": "#/components/schemas/FieldErrorSchema"
    }, "Structured field errors must reference a resolvable OpenAPI component."
    assert "FieldErrorSchema" in schema["components"]["schemas"], "The referenced field error schema must exist."


def test_cancel_scan_openapi_matches_observed_failures(signed_in):
    client, account, _ = signed_in
    urllist = UrlList.objects.create(account=account)
    scan = AccountInternetNLScan.objects.create(account=account, urllist=urllist, state="finished")
    responses = client.get("/api/v1/openapi.json").json()["paths"]["/api/v1/scans/{scan_id}"]["delete"]["responses"]
    assert set(responses) == {
        "204",
        "400",
        "401",
        "403",
        "404",
        "409",
        "500",
    }, "Cancellation must explicitly document every expected success, domain and framework failure."
    assert "already cancelled" in responses["204"]["description"], "Cancellation retries should be documented."
    assert "integer" in responses["400"]["description"], "The 400 description must explain invalid scan IDs."
    assert "current account" in responses["404"]["description"], "The 404 description must explain account scoping."
    assert (
        "finished" in responses["409"]["description"]
    ), "The 409 description must explain the incompatible scan state."
    for scan_id in (999999, scan.id):
        response = client.delete(f"/api/v1/scans/{scan_id}")
        body = assert_problem(response, 404 if scan_id == 999999 else 409)
        documented = responses[str(response.status_code)]["content"]
        assert set(documented) == {"application/problem+json"}, "Only the actual error media type should be advertised."
        assert (
            documented["application/problem+json"]["example"] == body
        ), "Documented cancellation examples must match the actual client responses."


def test_declared_errors_with_the_same_status_are_all_documented():
    class InvalidEmail(DocumentedApiError):
        status = 400
        detail = "The email address is invalid."
        problem_type = ProblemType.INVALID_EMAIL_ADDRESS

    class UnsupportedLanguage(DocumentedApiError):
        status = 400
        detail = "The selected language is unsupported."
        problem_type = ProblemType.UNSUPPORTED_LANGUAGE

    @raises(InvalidEmail, UnsupportedLanguage)
    def save_settings(error):
        raise error()

    response = problem_responses(save_settings)["responses"][400]
    examples = response["content"]["application/problem+json"]["examples"]
    assert len(examples) == 2, "Different errors sharing an HTTP status must not overwrite each other's documentation."
    for error in (InvalidEmail, UnsupportedLanguage):
        with pytest.raises(error) as raised:
            save_settings(error)
        example = examples[error.__name__]["value"]
        assert example["status"] == raised.value.status_code, "The documented status must come from the raised error."
        assert example["detail"] == str(raised.value), "The documented detail must come from the raised error."
        assert (
            example["type"] == raised.value.problem_type
        ), "The documented problem type must come from the raised error."
        assert str(raised.value) in response["description"], "Each documented error must contribute its explanation."


@pytest.mark.parametrize(
    "path,method,statuses,description_fragments",
    [
        ("/api/v1/urllists/{urllist_id}", "delete", {204, 404}, {404: "current account"}),
        ("/api/v1/urllists/{urllist_id}", "put", {200, 404}, {404: "current account"}),
        ("/api/v1/urllists/{urllist_id}/scans", "post", {202, 400, 404, 409}, {400: "credentials", 409: "conditions"}),
        ("/api/v1/urllists/{urllist_id}/urls", "post", {201, 400, 404}, {400: "list limit"}),
        ("/api/v1/urllists/{urllist_id}/urls/{url_id}", "put", {200, 400, 404}, {400: "format", 404: "URL"}),
        ("/api/v1/urllists/{urllist_id}/urls/{url_id}", "delete", {204, 404}, {404: "URL"}),
        (
            "/api/v1/urllists/{urllist_id}/spreadsheets",
            "post",
            {200, 400, 404, 503},
            {400: "spreadsheet", 503: "storage"},
        ),
        ("/api/v1/urllists/import-spreadsheets", "post", {202, 500, 503}, {503: "storage"}),
        (
            "/api/v1/urllists/{urllist_id}/url-suggestions",
            "get",
            {200, 400, 502, 503, 504},
            {400: "domain", 502: "response", 503: "unavailable", 504: "time"},
        ),
        ("/api/v1/urllists/{urllist_id}/www-subdomain-discovery", "post", {202, 404}, {404: "list"}),
        ("/api/v1/urllists/{urllist_id}/www-subdomain-discovery", "get", {200, 404}, {404: "no discovery scan"}),
        ("/api/v1/settings/user", "post", {204, 400, 404}, {400: "language", 404: "user"}),
        ("/api/v1/reports/{report_id}/share", "post", {200, 404}, {404: "already shared"}),
        ("/api/v1/reports/{report_id}/share", "delete", {200, 404}, {404: "not currently shared"}),
        ("/api/v1/reports/{report_id}/share/report-code", "put", {200, 404}, {404: "not currently shared"}),
        ("/api/v1/reports/{report_id}/share/share-code", "put", {200, 404}, {404: "not currently shared"}),
        ("/api/v1/reports/metrics/now", "post", {200, 403}, {403: "staff"}),
        ("/api/v1/reports/{report_id}/ad-hoc/preview", "post", {200, 404}, {404: "current account"}),
        ("/api/v1/reports/{report_id}/ad-hoc", "post", {204, 404}, {404: "current account"}),
        ("/api/v1/public-reports/{report_code}", "get", {200, 403, 404}, {404: "report code"}),
        ("/api/v1/public-reports/{report_code}", "post", {200, 403, 404}, {404: "report code"}),
        ("/api/v1/admin/accounts/{account_id}/impersonation", "post", {200, 404}, {404: "account"}),
        (
            "/api/v1/admin/accounts",
            "post",
            {201, 400, 404, 409},
            {400: "password", 404: "existing account", 409: "username"},
        ),
        ("/api/v1/signup", "post", {202, 400}, {400: "captcha"}),
    ],
)
def test_openapi_explains_expected_domain_failures(client, path, method, statuses, description_fragments):
    schema = client.get("/api/v1/openapi.json").json()
    responses = schema["paths"][path][method]["responses"]
    assert {str(status) for status in statuses} <= set(
        responses
    ), "Expected domain outcomes must be explicit in OpenAPI."
    for status, fragment in description_fragments.items():
        assert (
            fragment in responses[str(status)]["description"]
        ), "Each domain failure must explain its endpoint-specific cause."
    for status, response in responses.items():
        if int(status) >= 400:
            response = resolve_openapi_response(schema, response)
            assert set(response["content"]) == {
                "application/problem+json"
            }, "Every error should advertise its actual media type."


def test_openapi_reuses_shared_errors_and_retains_domain_overrides(client):
    schema = client.get("/api/v1/openapi.json").json()
    paths = schema["paths"]
    for path, method in [
        ("/api/v1/config", "get"),
        ("/api/v1/scans/{scan_id}", "delete"),
        ("/api/v1/settings/user", "post"),
        ("/api/v1/urllists/import-spreadsheets", "post"),
        ("/api/v1/public-reports/{report_code}", "get"),
        ("/api/v1/signup", "post"),
    ]:
        response = paths[path][method]["responses"]["500"]
        assert response == {
            "$ref": "#/components/responses/InternalServerError"
        }, "Generic server errors should reference one reusable response definition."
        resolved = resolve_openapi_response(schema, response)
        assert resolved["headers"]["API-Version"] == {
            "$ref": "#/components/headers/API-Version"
        }, "The shared response must include the API version header."

    cancellation = paths["/api/v1/scans/{scan_id}"]["delete"]["responses"]
    assert cancellation["401"] == {
        "$ref": "#/components/responses/AuthenticationRequired"
    }, "Authentication errors should use a shared response."
    assert cancellation["403"] == {
        "$ref": "#/components/responses/CsrfVerificationFailed"
    }, "Session mutation endpoints should reference the shared CSRF response."
    settings = paths["/api/v1/settings/user"]["post"]["responses"]
    assert settings["403"] == cancellation["403"], "CSRF documentation must be identical across session mutations."
    scan_monitor = paths["/api/v1/scans"]["get"]["responses"]
    assert "403" not in scan_monitor, "Safe reads must not advertise a CSRF check."
    signup = paths["/api/v1/signup"]["post"]["responses"]
    assert not {"401", "403"} & signup.keys(), "Public, CSRF-exempt signup must not advertise session failures."

    invalid_input = paths["/api/v1/scans/{scan_id}"]["delete"]["responses"]["400"]
    assert (
        "$ref" not in invalid_input and "integer" in invalid_input["description"]
    ), "An endpoint-specific validation explanation must remain intact."
    upload_error = paths["/api/v1/urllists/import-spreadsheets"]["post"]["responses"]["503"]
    assert (
        "$ref" not in upload_error and "temporarily unavailable" in upload_error["description"]
    ), "Expected service failures must retain their explanation under the appropriate status."
    staff_error = paths["/api/v1/reports/metrics/now"]["post"]["responses"]["403"]
    assert (
        "$ref" not in staff_error and "staff" in staff_error["description"]
    ), "Permission failures must not be replaced by the generic CSRF response."


def test_all_operations_reserve_500_for_shared_unexpected_server_failures(client):
    schema = client.get("/api/v1/openapi.json").json()
    for path in schema["paths"].values():
        for operation in path.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue
            assert operation["responses"]["500"] == {
                "$ref": "#/components/responses/InternalServerError"
            }, "Expected failures should have their own appropriate status rather than overriding the generic 500."
