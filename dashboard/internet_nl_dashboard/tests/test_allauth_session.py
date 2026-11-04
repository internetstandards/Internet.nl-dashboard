# SPDX-License-Identifier: Apache-2.0
import pytest
from allauth.core import context
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory

from dashboard.allauth.headlessadapter import HeadlessAdapter
from dashboard.internet_nl_dashboard.models import Account, DashboardUser

SESSION = "/api/v1/allauth/browser/v1/auth/session"


@pytest.fixture
def account_user(db):
    account = Account.objects.create(id=42, name="Shared dashboard account")
    user = User.objects.create_user(
        id=7, username="individual-user", password="session-test-password", is_superuser=True
    )
    DashboardUser.objects.create(user=user, account=account)
    return account, user


@pytest.mark.parametrize("superuser", [False, True])
def test_allauth_session_contains_dashboard_account_and_privileges(client, account_user, superuser):
    account, user = account_user
    user.is_superuser = superuser
    user.save()
    client.force_login(user)
    response = client.get(SESSION)
    assert response.status_code == 200, "An authenticated session should be available through allauth."
    payload = response.json()
    assert payload["meta"]["is_authenticated"] is True, "Allauth supplies the authentication flag separately."
    data = payload["data"]["user"]
    assert data["id"] == user.id, "The standard allauth ID must remain the user ID."
    assert data["username"] == user.username, "The standard allauth username must be preserved."
    assert data["account_id"] == account.id, "Sharing and scan tracking require the dashboard account ID."
    assert data["account_name"] == account.name, "The menu needs the account name rather than a username."
    assert data["is_superuser"] is superuser, "Admin visibility must reflect the current user's privileges."


def test_allauth_login_returns_dashboard_data_without_another_request(client, account_user):
    account, _ = account_user
    response = client.post(
        "/api/v1/allauth/browser/v1/auth/login",
        {"username": "individual-user", "password": "session-test-password"},
        content_type="application/json",
    )
    assert response.status_code == 200, "The real login response should complete authentication."
    assert response.json()["data"]["user"]["account_id"] == account.id, "Login must include the dashboard account."


def test_allauth_session_reflects_account_switching(client, account_user):
    _, user = account_user
    other = Account.objects.create(name="Switched account")
    client.force_login(user)
    response = client.post(f"/api/v1/admin/accounts/{other.id}/impersonation")
    assert response.status_code == 200, "A superuser should be able to switch the dashboard account."
    data = client.get(SESSION).json()["data"]["user"]
    assert data["account_id"] == other.id, "Reloading must use the switched dashboard account."
    assert data["account_name"] == other.name, "The menu should show the switched account name."
    assert data["id"] == user.id, "Switching accounts must preserve the authenticated user identity."


def test_allauth_session_preserves_fallback_for_users_without_dashboard_membership(db, client):
    user = User.objects.create_user(username="incomplete-user")
    client.force_login(user)
    response = client.get(SESSION)
    assert response.status_code == 200, "Users created without a dashboard account must still be able to log in."
    data = response.json()["data"]["user"]
    member = DashboardUser.objects.get(user=user)
    assert data["account_id"] == member.account.id, "Recovery must create and expose a real dashboard membership."
    assert data["account_name"] == "Fallback account for incomplete new users", "The existing fallback must remain."


@pytest.mark.parametrize("request_user", ["anonymous", "other"])
def test_partial_user_serialization_does_not_expose_dashboard_membership(db, request_user):
    user = User.objects.create_user(username="reset-or-pending-user", is_superuser=True)
    request = RequestFactory().get(SESSION)
    request.user = AnonymousUser() if request_user == "anonymous" else User.objects.create_user(username="other-user")
    with context.request_context(request):
        data = HeadlessAdapter().serialize_user(user)
    assert "account_id" not in data, "Partial authentication must not disclose dashboard membership."
    assert "account_name" not in data, "Partial authentication must not disclose dashboard account names."
    assert "is_superuser" not in data, "Partial authentication must not disclose privilege information."
    assert not DashboardUser.objects.filter(user=user).exists(), "Partial flows must not create fallback memberships."


def test_anonymous_allauth_session_has_no_dashboard_data(db, client):
    response = client.get(SESSION)
    assert response.status_code == 401, "An anonymous allauth session uses the normal unauthenticated response."
    assert response.json()["meta"]["is_authenticated"] is False, "An anonymous session cannot authenticate the UI."
    assert "user" not in response.json()["data"], "An anonymous session must not contain dashboard user data."


def test_allauth_logout_accepts_csrf_and_clears_the_session(account_user):
    _, user = account_user
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    client.get("/api/v1/allauth/browser/v1/config")
    response = client.delete(SESSION, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
    assert response.status_code == 401, "Successful allauth logout returns the new unauthenticated state."
    assert response.json()["meta"]["is_authenticated"] is False, "Logout must clear authentication."
    assert "_auth_user_id" not in client.session, "Logout must remove the real Django session identity."
    assert "user" not in response.json()["data"], "Logout must not retain account or privilege data."


def test_allauth_openapi_documents_dashboard_fields(client):
    response = client.get("/api/v1/allauth/openapi.json")
    assert response.status_code == 200, "The customized headless schema must remain available."
    properties = response.json()["components"]["schemas"]["User"]["properties"]
    assert {"account_id", "account_name", "is_superuser"} <= properties.keys(), (
        "The schema must include dashboard fields."
    )
    assert "distinct from the user ID" in properties["account_id"]["description"], "Account IDs must be unambiguous."
