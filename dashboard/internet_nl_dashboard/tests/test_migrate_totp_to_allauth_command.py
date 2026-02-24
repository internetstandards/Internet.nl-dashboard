# SPDX-License-Identifier: Apache-2.0
from base64 import b32encode
from binascii import unhexlify
from io import StringIO

from allauth.mfa import app_settings as mfa_app_settings
from allauth.mfa.models import Authenticator
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django_otp.plugins.otp_totp.models import TOTPDevice


def _create_user(username: str):
    user_model = get_user_model()
    return user_model.objects.create_user(username=username)


def _create_totp_device(user, **kwargs):
    defaults = {
        "user": user,
        "name": "default",
        "confirmed": True,
    }
    defaults.update(kwargs)
    return TOTPDevice.objects.create(**defaults)


def test_migrate_totp_to_allauth_dry_run_does_not_write(db):
    user = _create_user("dryrun-user")
    _create_totp_device(user=user)

    out = StringIO()
    call_command("migrate_totp_to_allauth", stdout=out)

    assert Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).count() == 0
    output = out.getvalue()
    assert "Running in DRY-RUN mode." in output
    assert "- migrated: 1" in output
    assert "Dry run complete. Re-run with --commit to apply." in output


def test_migrate_totp_to_allauth_commit_creates_authenticator_with_converted_secret(db):
    user = _create_user("commit-user")
    key_hex = "3132333435363738393031323334353637383930"
    _create_totp_device(user=user, key=key_hex)

    call_command("migrate_totp_to_allauth", "--commit")

    authenticator = Authenticator.objects.get(user=user, type=Authenticator.Type.TOTP)
    expected_secret = b32encode(unhexlify(key_hex.encode("ascii"))).decode("ascii")
    assert authenticator.data["secret"] == expected_secret


def test_migrate_totp_to_allauth_skips_existing_allauth_totp(db):
    user = _create_user("existing-user")
    _create_totp_device(user=user)
    Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.TOTP,
        data={"secret": "EXISTINGSECRET"},
    )

    out = StringIO()
    call_command("migrate_totp_to_allauth", "--commit", stdout=out)

    assert Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).count() == 1
    assert "- skipped_existing_allauth_totp: 1" in out.getvalue()


def test_migrate_totp_to_allauth_skips_incompatible_totpdevice(db):
    user = _create_user("incompatible-user")
    _create_totp_device(user=user, step=60)

    out = StringIO()
    call_command("migrate_totp_to_allauth", "--commit", stdout=out)

    assert Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).count() == 0
    output = out.getvalue()
    assert "- skipped_invalid_or_incompatible: 1" in output
    assert f"device.step=60 != MFA_TOTP_PERIOD={mfa_app_settings.TOTP_PERIOD}" in output


def test_migrate_totp_to_allauth_skips_users_with_multiple_devices(db):
    user = _create_user("duplicate-device-user")
    _create_totp_device(user=user, name="default")
    _create_totp_device(user=user, name="backup")

    out = StringIO()
    call_command("migrate_totp_to_allauth", "--commit", stdout=out)

    assert Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).count() == 0
    output = out.getvalue()
    assert "Skipping users with more than one confirmed TOTPDevice:" in output
    assert "- skipped_multiple_confirmed_devices: 2" in output


def test_migrate_totp_to_allauth_skips_invalid_hex_key(db):
    user = _create_user("invalid-key-user")
    device = _create_totp_device(user=user)
    device.key = "this-is-not-hex"
    device.save(update_fields=["key"])

    out = StringIO()
    call_command("migrate_totp_to_allauth", "--commit", stdout=out)

    assert Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).count() == 0
    output = out.getvalue()
    assert "- skipped_invalid_or_incompatible: 1" in output
    assert f"invalid hex key on TOTPDevice id={device.id}" in output


def test_migrate_totp_to_allauth_can_limit_to_user_id(db):
    included_user = _create_user("filter-included-user")
    excluded_user = _create_user("filter-excluded-user")
    _create_totp_device(user=included_user)
    _create_totp_device(user=excluded_user)

    call_command(
        "migrate_totp_to_allauth",
        "--commit",
        "--user-id",
        str(included_user.id),
    )

    assert Authenticator.objects.filter(user=included_user, type=Authenticator.Type.TOTP).count() == 1
    assert Authenticator.objects.filter(user=excluded_user, type=Authenticator.Type.TOTP).count() == 0
