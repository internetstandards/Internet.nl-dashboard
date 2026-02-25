# SPDX-License-Identifier: Apache-2.0
from io import StringIO

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management import call_command


def test_signal_verifies_email_for_new_user(db):
    user = get_user_model().objects.create_user(
        username="signal-new-user",
        email="signal-new@example.com",
    )

    email = EmailAddress.objects.get(user=user, email="signal-new@example.com")
    assert email.verified is True


def test_signal_verifies_email_when_user_email_is_later_set(db):
    user = get_user_model().objects.create_user(
        username="signal-updated-user",
        email="",
    )
    assert EmailAddress.objects.filter(user=user).count() == 0

    user.email = "signal-updated@example.com"
    user.save(update_fields=["email"])

    email = EmailAddress.objects.get(user=user, email="signal-updated@example.com")
    assert email.verified is True


def test_verify_allauth_emails_dry_run_is_non_mutating(db):
    user = get_user_model().objects.create_user(
        username="command-dry-user",
        email="",
    )
    get_user_model().objects.filter(pk=user.pk).update(email="command-dry@example.com")
    user.refresh_from_db()
    assert EmailAddress.objects.filter(user=user).count() == 0

    out = StringIO()
    call_command("verify_allauth_emails", stdout=out)

    assert EmailAddress.objects.filter(user=user).count() == 0
    assert "Running in DRY-RUN mode." in out.getvalue()
    assert "- verified_now: 1" in out.getvalue()


def test_verify_allauth_emails_commit_creates_verified_emailaddress(db):
    user = get_user_model().objects.create_user(
        username="command-commit-user",
        email="",
    )
    get_user_model().objects.filter(pk=user.pk).update(email="command-commit@example.com")
    user.refresh_from_db()
    assert EmailAddress.objects.filter(user=user).count() == 0

    out = StringIO()
    call_command("verify_allauth_emails", "--commit", stdout=out)

    email = EmailAddress.objects.get(user=user, email="command-commit@example.com")
    assert email.verified is True
    assert "Running in COMMIT mode." in out.getvalue()


def test_verify_allauth_emails_reports_conflicts_for_duplicate_verified_email(db):
    existing_user = get_user_model().objects.create_user(
        username="existing-verified-user",
        email="duplicate@example.com",
    )
    assert (
        EmailAddress.objects.filter(
            user=existing_user,
            email="duplicate@example.com",
            verified=True,
        ).count()
        == 1
    )

    conflict_user = get_user_model().objects.create_user(
        username="duplicate-conflict-user",
        email="",
    )
    get_user_model().objects.filter(pk=conflict_user.pk).update(email="duplicate@example.com")
    conflict_user.refresh_from_db()
    assert EmailAddress.objects.filter(user=conflict_user).count() == 0

    out = StringIO()
    call_command(
        "verify_allauth_emails",
        "--commit",
        "--user-id",
        str(conflict_user.pk),
        stdout=out,
    )

    conflict_email = EmailAddress.objects.get(user=conflict_user, email="duplicate@example.com")
    assert conflict_email.verified is False
    assert "- verification_conflicts: 1" in out.getvalue()
