# SPDX-License-Identifier: Apache-2.0
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from websecmap.reporting.time_cache import CACHE


DEFAULT_APP_LABELS = ["scanners_internet_nl_web", "scanners_internet_nl_mail"]


class Command(BaseCommand):
    help = "Run the Internet.nl scanner app startup hooks to provision scanners, scan types, schedules and policies."

    def add_arguments(self, parser):
        parser.add_argument(
            "app_labels",
            nargs="*",
            default=DEFAULT_APP_LABELS,
            help=(
                "Django app labels to initialize. Defaults to: "
                f"{', '.join(DEFAULT_APP_LABELS)}."
            ),
        )

    def handle(self, *args, **options):
        initialized = []

        for app_label in options["app_labels"]:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError as exception:
                raise CommandError(f"Unknown Django app label: {app_label}") from exception

            startup = getattr(app_config, "startup", None)
            if not callable(startup):
                raise CommandError(f"Django app '{app_label}' has no callable startup() hook.")

            startup_result = startup()
            initialized.append((app_label, startup_result))

        CACHE.pop("backend_scanmetadata", None)

        for app_label, startup_result in initialized:
            scanner = startup_result.get("scanner") if isinstance(startup_result, dict) else None
            scan_types = startup_result.get("scan_types", []) if isinstance(startup_result, dict) else []
            scanner_name = getattr(scanner, "python_name", None) or "-"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Initialized {app_label}: scanner={scanner_name}, scan_types={len(scan_types)}",
                ),
            )

        self.stdout.write("Cleared backend_scanmetadata cache.")
