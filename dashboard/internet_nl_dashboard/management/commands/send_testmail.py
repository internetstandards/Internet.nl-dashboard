# SPDX-License-Identifier: Apache-2.0
from constance import config
from django.core.management.base import BaseCommand
from django_mail_admin import mail, models


class Command(BaseCommand):
    def handle(self, *args, **options):
        mail.send(
            sender=config.EMAIL_NOTIFICATION_SENDER,
            recipients=config.EMAIL_TEST_RECIPIENT,
            subject='Dashboard test e-mail',
            message='This is a test email from the dashboard.',
            priority=models.PRIORITY.now,
            html_message='This is a test email from the dashboard <strong>hi</strong>!',
        )
    print("Mail sent!")
