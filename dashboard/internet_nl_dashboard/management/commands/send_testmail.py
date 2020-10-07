from django.core.management.base import BaseCommand
from django_mail_admin import mail, models


class Command(BaseCommand):
    def handle(self, *args, **options):
        mail.send(
            'noreply@internet.nl',
            'elger@internetcleanup.foundation',
            subject='Dashboard test e-mail',
            message='This is a test email from the dashboard.',
            priority=models.PRIORITY.now,
            html_message='This is a test email from the dashboard <strong>hi</strong>!',
        )
    print("Mail sent!")
