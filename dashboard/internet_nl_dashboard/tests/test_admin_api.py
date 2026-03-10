# SPDX-License-Identifier: Apache-2.0
import json

from django.contrib.auth.models import User

from dashboard.internet_nl_dashboard.models import Account


def create_superuser_client(client):
    user = User.objects.create_superuser(
        username="admin-api-user",
        email="admin-api-user@example.com",
        password="very-secure-admin-password",
    )
    client.force_login(user)
    return client


def test_save_instant_account_and_user_requires_email_address(db, client):
    client = create_superuser_client(client)
    account = Account.objects.create(name="existing-admin-account")

    response = client.post(
        "/api/v1/admin/accounts",
        data=json.dumps(
            {
                "new_username": "new-admin-managed-user",
                "new_password": "very-secure-user-password",
                "use_existing_account_id": account.id,
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 422, "Missing required email should fail schema validation."
    assert (
        "new_email_address" in response.json()["detail"][0]["loc"]
    ), "Validation error should reference the email field."


def test_save_instant_account_and_user_saves_email_on_user(db, client):
    client = create_superuser_client(client)
    account = Account.objects.create(name="existing-admin-account")

    response = client.post(
        "/api/v1/admin/accounts",
        data=json.dumps(
            {
                "new_username": "new-admin-managed-user",
                "new_email_address": "new-admin-managed-user@example.com",
                "new_password": "very-secure-user-password",
                "use_existing_account_id": account.id,
            }
        ),
        content_type="application/json",
    )

    created_user = User.objects.get(username="new-admin-managed-user")

    assert response.status_code == 201, "Admin account creation should succeed with a valid email address."
    assert (
        created_user.email == "new-admin-managed-user@example.com"
    ), "Created user should persist the requested email."
