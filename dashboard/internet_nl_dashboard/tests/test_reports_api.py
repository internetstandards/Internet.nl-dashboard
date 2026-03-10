# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime, timezone

from django.contrib.auth.models import User
from websecmap.organizations.models import Url
from websecmap.reporting.severity import get_severity
from websecmap.scanners.impact import get_impact
from websecmap.scanners.models import Endpoint, EndpointGenericScan

from dashboard.internet_nl_dashboard.models import Account, DashboardUser


def create_authenticated_client(client, *, is_staff: bool = False):
    user = User.objects.create(username=f"report-api-user-{'staff' if is_staff else 'regular'}", is_staff=is_staff)
    account = Account.objects.create(name="report-api-account")
    DashboardUser.objects.create(user=user, account=account)
    client.force_login(user)
    return client


def create_endpoint_scan(
    url_string: str,
    scan_type: str,
    rating: str,
    *,
    explanation: str,
    rating_determined_on: datetime,
    is_the_latest_scan: bool = True,
) -> EndpointGenericScan:
    url = Url.objects.filter(url=url_string).first()
    if not url:
        url = Url(
            url=url_string,
            created_on=datetime(2020, 1, 1, tzinfo=timezone.utc),
            not_resolvable=False,
            computed_subdomain="",
            computed_domain="",
            computed_suffix="",
        )
        Url.objects.bulk_create([url])
        url.refresh_from_db()

    endpoint, _ = Endpoint.objects.get_or_create(
        url=url,
        protocol="https",
        port=443,
        ip_version=4,
        defaults={
            "discovered_on": datetime(2020, 1, 1, tzinfo=timezone.utc),
            "is_dead": False,
        },
    )
    return EndpointGenericScan.objects.create(
        endpoint=endpoint,
        type=scan_type,
        rating=rating,
        explanation=explanation,
        evidence="https://batch.internet.nl/site/example/123/",
        rating_determined_on=rating_determined_on,
        is_the_latest_scan=is_the_latest_scan,
        comply_or_explain_is_explained=False,
    )


def expected_live_metric(scan: EndpointGenericScan) -> dict:
    severity = get_severity(scan)
    severity["impact"] = get_impact(severity)

    del severity["comply_or_explain_explained_by"]
    del severity["comply_or_explain_explanation"]
    del severity["comply_or_explain_explanation_valid_until"]
    del severity["comply_or_explain_valid_at_time_of_report"]
    del severity["comply_or_explain_explained_on"]

    severity.setdefault("translation", "")
    severity.setdefault("technical_details", "")
    severity.setdefault("test_result", "")

    return severity


def test_get_ad_hoc_live_latest_metrics_requires_auth(db, client):
    response = client.post(
        "/api/v1/reports/metrics/now/",
        data=json.dumps({"urls": ["example.nl"]}),
        content_type="application/json",
    )

    assert response.status_code == 401, "Unauthenticated access should be rejected."


def test_get_ad_hoc_live_latest_metrics_requires_staff_account(db, client):
    client = create_authenticated_client(client, is_staff=False)

    response = client.post(
        "/api/v1/reports/metrics/now/",
        data=json.dumps({"urls": ["internet.nl"]}),
        content_type="application/json",
    )

    assert response.status_code == 403, "Non-staff users should receive a forbidden response."
    assert (
        response.json()["message"] == "staff_account_required"
    ), "Forbidden response should explain the staff requirement."
    assert response.json()["error"] is True, "Forbidden response should be marked as an error."


def test_get_ad_hoc_live_latest_metrics_uses_default_urls_and_metrics(db, client):
    client = create_authenticated_client(client, is_staff=True)

    matching_scan = create_endpoint_scan(
        "internet.nl",
        "internet_nl_web_overall_score",
        "80",
        explanation="80 https://batch.internet.nl/site/internet.nl/123/",
        rating_determined_on=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    create_endpoint_scan(
        "internet.nl",
        "web_https_tls_version",
        "failed",
        explanation="TLS version issue",
        rating_determined_on=datetime(2024, 1, 3, tzinfo=timezone.utc),
    )
    create_endpoint_scan(
        "old-example.nl",
        "internet_nl_mail_overall_score",
        "100",
        explanation="100 https://batch.internet.nl/site/old-example.nl/123/",
        rating_determined_on=datetime(2024, 1, 4, tzinfo=timezone.utc),
        is_the_latest_scan=False,
    )

    response = client.post(
        "/api/v1/reports/metrics/now/",
        data=json.dumps({}),
        content_type="application/json",
    )

    assert response.status_code == 200, "Staff users should be allowed to fetch live latest metrics."
    assert response.json() == {
        "internet.nl": {
            "internet_nl_web_overall_score": expected_live_metric(matching_scan),
        }
    }, "Default request should return keyed metrics for the default url and default metric set only."


def test_get_ad_hoc_live_latest_metrics_filters_requested_metrics(db, client):
    client = create_authenticated_client(client, is_staff=True)

    create_endpoint_scan(
        "custom.example.nl",
        "internet_nl_web_overall_score",
        "90",
        explanation="90 https://batch.internet.nl/site/custom.example.nl/123/",
        rating_determined_on=datetime(2024, 2, 1, tzinfo=timezone.utc),
    )
    matching_scan = create_endpoint_scan(
        "custom.example.nl",
        "web_https_tls_version",
        "failed",
        explanation="TLS version issue",
        rating_determined_on=datetime(2024, 2, 2, tzinfo=timezone.utc),
    )

    response = client.post(
        "/api/v1/reports/metrics/now/",
        data=json.dumps({"urls": ["custom.example.nl"], "metrics": ["web_https_tls_version"]}),
        content_type="application/json",
    )

    assert response.status_code == 200, "Staff users should be allowed to fetch a requested metric subset."
    assert response.json() == {
        "custom.example.nl": {
            "web_https_tls_version": expected_live_metric(matching_scan),
        }
    }, "Explicit metric filtering should return only the requested metric keyed by url and type."


def test_get_ad_hoc_live_latest_metrics_openapi_example_and_defaults(db, client):
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200, "OpenAPI schema should be available."

    openapi = response.json()
    schema = openapi["components"]["schemas"]["LiveLatestMetricsInputSchema"]

    assert schema["example"] == {
        "urls": ["internet.nl"],
        "metrics": ["internet_nl_mail_overall_score", "internet_nl_web_overall_score"],
    }, "OpenAPI example should document the default request body."
    assert schema["properties"]["urls"]["default"] == ["internet.nl"], "OpenAPI should expose the default url list."
    assert schema["properties"]["metrics"]["default"] == [
        "internet_nl_mail_overall_score",
        "internet_nl_web_overall_score",
    ], "OpenAPI should expose the default metric list."
    assert (
        "First log in in the same browser via `/api/v1/allauth/openapi.html` or `/accounts/login/`"
        in openapi["info"]["description"]
    ), "OpenAPI description should explain how Swagger authenticated calls work."


def test_api_swagger_docs_include_csrf_support(db, client):
    response = client.get("/api/v1/docs")

    assert response.status_code == 200, "Swagger docs page should load."
    assert b'data-api-csrf="true"' in response.content, "Swagger docs should advertise CSRF support."
    assert b'data-csrf-token="' in response.content, "Swagger docs should embed a CSRF token for Try it out requests."
