# SPDX-License-Identifier: Apache-2.0
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from dashboard.internet_nl_dashboard.models import DashboardUser, Account

log = logging.getLogger(__package__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        superusers = User.objects.all().filter(is_superuser=True)

        for user in superusers:
            if not DashboardUser.objects.filter(user=user).first():
                DashboardUser.objects.create(
                    user=user,
                    account=Account.objects.all().first(),  # should always exist
                    mail_preferred_language='en',
                    mail_send_mail_after_scan_finished=False,
                    mail_after_mail_unsubscribe_code='',
                )
                print(f"Added DashboardUser for superuser {user}")
        print("Done")
