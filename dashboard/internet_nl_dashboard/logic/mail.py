import string
import time
from random import choice
from typing import Any

from constance import config
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from django_mail_admin import mail
from django_mail_admin.models import EmailTemplate, Outbox

from dashboard.celery import app
from dashboard.internet_nl_dashboard.models import (AccountInternetNLScan, DashboardUser,
                                                    UrlListReport)


"""
Mail is sent when a scan is finished and a report is ready. It uses django_mail_admin, a straightforward library
that simplifies template management and sending. A sample template is below:

Name:           scan_finished_en
Description:    Used when a the scan on a list is finished and a report is being sent. You can translate this template
                to other languages by creating a new template with _nl or another language code instead of _en for
                english.
Subject:        Report ready for {{list_name}}, scoring {{report_average_internet_nl_score}}
Email text:     Hi {{recipient}}!<br>
                <br>
                Good news! The scan on {{list_name}} has finished. The average score of this report is
                {{report_average_internet_nl_score}}. <br>
                <br>
                View the report at this link: <br>
                <a href="https://dashboard.internet.nl/spa/#/report/{{report_id}}">
                        https://dashboard.internet.nl/spa/#/report/{{report_id}}</a>/<br>
                <br>
                Regards,<br>
                internet.nl<br>
                <br>
                <br>
                [
                <a href="http://localhost:8000/spa/#/unsubscribe?feed=scan_finished&unsubscribe_code=
                {{unsubscribe_code}}">unsubscribe</a>
                -
                <a href="http://localhost:8000/spa/#/preferences">preferences</a>
                 ]
"""


def email_configration_is_correct():
    # we use outboxes now
    outbox_exists = Outbox.objects.all().first()
    if outbox_exists:
        return True
    return False


def get_users_to_send_mail_to(scan: AccountInternetNLScan):

    # Only send mail to users that are active and of course have a mail address...
    return User.objects.all().filter(
        dashboarduser__account=scan.account,
        dashboarduser__mail_preferred_mail_address__isnull=False,
        dashboarduser__mail_send_mail_after_scan_finished=True,
        is_active=True
    ).exclude(
        dashboarduser__mail_preferred_mail_address=""
    )


def send_scan_finished_mails(scan: AccountInternetNLScan):
    """
    Sends mails, depending on user configuration, to all users associated with a scan.

    Will adhere user settings such as language and mail preferences.

    :param scan:
    :return:
    """

    users = get_users_to_send_mail_to(scan)

    # remove calculation because textfields are slow while filtering
    report = UrlListReport.objects.all().filter(urllist=scan.urllist).order_by("-id").defer('calculation').first()

    for user in users:

        # set unsubscribe code if it's not set yet. This allows the user to instantly unsubscribe from this feed.
        if user.dashboarduser.mail_after_mail_unsubscribe_code == "":
            user.dashboarduser.mail_after_mail_unsubscribe_code = generate_unsubscribe_code()
            user.dashboarduser.save()

        placeholders = {
            "recipient": user.first_name if user.first_name else user.last_name if user.last_name else user.username,
            "user_id": user.id,

            "list_name": scan.urllist.name,

            "report_id": report.id,
            "report_average_internet_nl_score": report.average_internet_nl_score,
            "report_number_of_urls": report.total_urls,

            "scan_id": scan.id,
            "scan_started_on": scan.started_on.isoformat(),
            # the scan is not yet completely finished, because this step (mailing) is still performed
            # so perform a guess, which might be a few minutes off...
            "scan_finished_on": timezone.now().isoformat(),
            "scan_duration": timezone.now() - scan.started_on,

            "scan_type": scan.scan.type,

            # todo: set unsubscribe code in database, to be something random when is empty and sending mail.
            "unsubscribe_code": "9023u01923091283093123",
        }

        mail.send(
            sender=config.EMAIL_NOTIFICATION_SENDER,
            recipients=user.dashboarduser.mail_preferred_mail_address,  # List of email addresses also accepted
            template=xget_template(
                template_name="scan_finished",
                preferred_language=user.dashboarduser.mail_preferred_language
            ),
            variable_dict=placeholders
        )

    # number of mails sent is equal to users configured their account to receive mails.
    return len(users)


def xget_template(template_name: str = "scan_finished", preferred_language: Any = None):
    """

    :param template_name:
    :param preferred_language: Countryfield value.
    :return:
    """

    # tries to retrieve the preferred language for emails. If that template is not available,
    # the fallback language (EN) is used.

    template = EmailTemplate.objects.filter(name=f'{template_name}_{preferred_language.code.lower()}').first()
    if template:
        return template

    template = EmailTemplate.objects.filter(name=f'{template_name}_{config.EMAIL_FALLBACK_LANGUAGE}').first()
    if template:
        return template

    raise LookupError(f"Could not find e-mail template {template_name}, neither for language {preferred_language} nor"
                      f"the fallback language {config.EMAIL_FALLBACK_LANGUAGE}.")


def generate_unsubscribe_code():
    # https://pynative.com/python-generate-random-string/
    # secure random is not needed, would be ridiculous. A sleep(1) is enough to deter any attack
    return ''.join(choice(string.ascii_letters + string.digits) for i in range(128))


def unsubscribe(feed: str = "scan_finished", unsubscribe_code: str = ""):
    # deter brute force attacks, no random sleep time is need, as there is no pii involved.
    # example: https://dashboard.internet.nl/mail/unsubscribe/scan_finished/{{unsubscribe_code}}/
    time.sleep(1)

    if feed == "scan_finished":
        users = DashboardUser.objects.all().filter(
            mail_after_mail_unsubscribe_code=unsubscribe_code,
            mail_send_mail_after_scan_finished=True
        )
        for user in users:
            user.mail_send_mail_after_scan_finished = False
            # reset the unsubscribe code, so it cannot be reused. A new code will be created when a mail is sent.
            user.mail_after_mail_unsubscribe_code = ""
            user.save()

    # always say that the user has been unsubscribed, even if there was no subscription
    return {'unsubscribed': True}


@app.task(queue='storage')
def send_mail():
    """
    To use this, add a periodic task. The signature is:
    dashboard.internet_nl_dashboard.logic.mail.send_mail

    Todo: loops, the message does not get sent but other messages are being added.

    :return:
    """
    call_command('send_queued_mail', processes=1, log_level=2)
