# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from base64 import b32encode
from binascii import Error as BinasciiError
from binascii import unhexlify
from contextlib import nullcontext

from allauth.mfa import app_settings as mfa_app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import TOTP
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = (
        "Migrate confirmed django-otp TOTP devices to allauth MFA TOTP authenticators. "
        "By default, this command performs a dry run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Persist changes. Without this flag, the command runs in dry-run mode.",
        )
        parser.add_argument(
            "--user-id",
            action="append",
            dest="user_ids",
            type=int,
            help="Limit migration to one or more user IDs. Can be provided multiple times.",
        )

    def handle(self, *args, **options):
        commit = options["commit"]
        user_ids = options.get("user_ids") or []
        selected_user_ids = set(user_ids)

        self.stdout.write("Running in COMMIT mode." if commit else "Running in DRY-RUN mode.")

        queryset = TOTPDevice.objects.filter(confirmed=True).select_related("user")
        if selected_user_ids:
            queryset = queryset.filter(user_id__in=selected_user_ids)

        duplicate_user_ids = set(
            queryset.values("user_id")
            .annotate(device_count=Count("id"))
            .filter(device_count__gt=1)
            .values_list("user_id", flat=True)
        )
        if duplicate_user_ids:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping users with more than one confirmed TOTPDevice: "
                    + ", ".join(str(uid) for uid in sorted(duplicate_user_ids))
                )
            )

        existing_totp_user_ids = set(
            Authenticator.objects.filter(type=Authenticator.Type.TOTP).values_list("user_id", flat=True)
        )
        if selected_user_ids:
            existing_totp_user_ids &= selected_user_ids

        examined = 0
        migrated = 0
        skipped_existing = 0
        skipped_invalid = 0
        skipped_duplicates = 0

        context = transaction.atomic() if commit else nullcontext()
        with context:
            for device in queryset.order_by("user_id", "id"):
                examined += 1

                if device.user_id in duplicate_user_ids:
                    skipped_duplicates += 1
                    continue

                if device.user_id in existing_totp_user_ids:
                    skipped_existing += 1
                    continue

                # allauth TOTP verification supports a global period/digits and t0=0.
                if device.step != mfa_app_settings.TOTP_PERIOD:
                    skipped_invalid += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping user_id={device.user_id}: "
                            f"device.step={device.step} != MFA_TOTP_PERIOD={mfa_app_settings.TOTP_PERIOD}"
                        )
                    )
                    continue
                if device.digits != mfa_app_settings.TOTP_DIGITS:
                    skipped_invalid += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping user_id={device.user_id}: "
                            f"device.digits={device.digits} != MFA_TOTP_DIGITS={mfa_app_settings.TOTP_DIGITS}"
                        )
                    )
                    continue
                if device.t0 != 0:
                    skipped_invalid += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping user_id={device.user_id}: device.t0={device.t0} is unsupported by allauth."
                        )
                    )
                    continue

                secret = self._to_base32_secret(device.key)
                if not secret:
                    skipped_invalid += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping user_id={device.user_id}: invalid hex key on TOTPDevice id={device.id}."
                        )
                    )
                    continue

                migrated += 1
                if commit:
                    TOTP.activate(device.user, secret)
                    existing_totp_user_ids.add(device.user_id)

        self.stdout.write("")
        self.stdout.write("Summary:")
        self.stdout.write(f"- examined: {examined}")
        self.stdout.write(f"- migrated: {migrated}")
        self.stdout.write(f"- skipped_existing_allauth_totp: {skipped_existing}")
        self.stdout.write(f"- skipped_invalid_or_incompatible: {skipped_invalid}")
        self.stdout.write(f"- skipped_multiple_confirmed_devices: {skipped_duplicates}")

        if not commit:
            self.stdout.write(self.style.WARNING("Dry run complete. Re-run with --commit to apply."))

    @staticmethod
    def _to_base32_secret(hex_key: str) -> str | None:
        try:
            key_bytes = unhexlify(hex_key.encode("ascii"))
        except (BinasciiError, ValueError, UnicodeEncodeError):
            return None
        return b32encode(key_bytes).decode("ascii")
