# SPDX-License-Identifier: Apache-2.0
from contextlib import nullcontext

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.internet_nl_dashboard.allauth_email import ensure_user_email_address_verified


class Command(BaseCommand):
    help = (
        "Ensure all users have an allauth EmailAddress for user.email and mark "
        "it verified. Defaults to dry-run mode."
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
            help="Limit to one or more user IDs. Can be provided multiple times.",
        )

    def handle(self, *args, **options):
        commit = options["commit"]
        user_ids = options.get("user_ids") or []

        self.stdout.write("Running in COMMIT mode." if commit else "Running in DRY-RUN mode.")

        user_model = get_user_model()
        queryset = user_model.objects.all().order_by("id")
        if user_ids:
            queryset = queryset.filter(id__in=set(user_ids))

        scanned = 0
        verified = 0
        already_verified = 0
        skipped_no_email = 0
        conflicts = 0

        context = transaction.atomic() if commit else nullcontext()
        with context:
            for user in queryset:
                scanned += 1
                result = ensure_user_email_address_verified(user, commit=commit)
                if result == "verified":
                    verified += 1
                elif result == "already_verified":
                    already_verified += 1
                elif result == "skipped_no_email":
                    skipped_no_email += 1
                elif result == "conflict":
                    conflicts += 1

        self.stdout.write("")
        self.stdout.write("Summary:")
        self.stdout.write(f"- scanned_users: {scanned}")
        self.stdout.write(f"- verified_now: {verified}")
        self.stdout.write(f"- already_verified: {already_verified}")
        self.stdout.write(f"- skipped_no_email: {skipped_no_email}")
        self.stdout.write(f"- verification_conflicts: {conflicts}")

        if not commit:
            self.stdout.write(self.style.WARNING("Dry run complete. Re-run with --commit to apply."))
