# SPDX-License-Identifier: Apache-2.0
# example: dashboard dashboard_celery worker -Q storage -l debug
from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand

from dashboard.internet_nl_dashboard.management.commands.dashboard_celery import \
    reusable_run_from_argv


class Command(BaseCommand):  # pylint: disable=abstract-method
    """Celery command wrapper."""

    help = __doc__

    # disable (MySQL) check on startup
    requires_system_checks = []

    def run_from_argv(self, argv):
        reusable_run_from_argv(argv)
