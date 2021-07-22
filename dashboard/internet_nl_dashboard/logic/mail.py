import logging
import string
import time
from random import choice

from constance import config
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from django_mail_admin import mail
from django_mail_admin.models import Outbox

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic.mail_admin_templates import xget_template
from dashboard.internet_nl_dashboard.logic.report import get_report_directly
from dashboard.internet_nl_dashboard.logic.report_comparison import (compare_report_in_detail,
                                                                     key_calculation,
                                                                     render_comparison_view)
from dashboard.internet_nl_dashboard.models import (AccountInternetNLScan, DashboardUser,
                                                    UrlListReport)

log = logging.getLogger(__package__)

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

    # remove calculation because textfields are slow while filtering. Have to retrieve the textfield later
    report = UrlListReport.objects.all().filter(id=scan.report.id).order_by("-id").defer('calculation').first()

    for user in users:

        # set unsubscribe code if it's not set yet. This allows the user to instantly unsubscribe from this feed.
        if user.dashboarduser.mail_after_mail_unsubscribe_code == "":
            user.dashboarduser.mail_after_mail_unsubscribe_code = generate_unsubscribe_code()
            user.dashboarduser.save()

        placeholders = {
            "unsubscribe_code": user.dashboarduser.mail_after_mail_unsubscribe_code,

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
            "scan_duration": (timezone.now() - scan.started_on).seconds,
            # Don't use 'mail_dashboard', only mail.
            "scan_type": scan.scan.type if scan.scan.type == "web" else "mail",

            "dashboard_address": config.EMAIL_DASHBOARD_ADDRESS,
        }

        previous = values_from_previous_report(
            report.id,
            report.get_previous_report_from_this_list(),
            user.dashboarduser.mail_preferred_language.code.lower()
        )
        placeholders = {**placeholders, **previous}

        mail.send(
            sender=config.EMAIL_NOTIFICATION_SENDER,
            recipients=user.dashboarduser.mail_preferred_mail_address,  # List of email addresses also accepted
            template=xget_template(
                template_name="scan_finished",
                preferred_language=user.dashboarduser.mail_preferred_language.code.lower()
            ),
            variable_dict=placeholders
        )

    # number of mails sent is equal to users configured their account to receive mails.
    return len(users)


def values_from_previous_report(report_id: int, previous_report: UrlListReport, mail_language: str):

    if not previous_report:
        return {
            "previous_report_available": str(False),
            "previous_report_average_internet_nl_score": 0,
            "compared_report_id": 0,
            "comparison_is_empty": str(True),
            "improvement": 0,
            "regression": 0,
            "neutral": 0,
            "comparison_report_available": str(False),
            "comparison_report_contains_improvement": str(False),
            "comparison_report_contains_regression": str(False),
            "days_between_current_and_previous_report": 0,
            "comparison_table_improvement": render_comparison_view({}, impact="improvement", language=mail_language),
            "comparison_table_regression": render_comparison_view({}, impact="regression", language=mail_language),
            "domains_exclusive_in_current_report": "",
            "domains_exclusive_in_other_report": "",
        }

    # Django retrieves fields that are deferred automatically when explicitly requested.
    # This is a direct select query, and thus faster than adding the textfield in the search query.
    comp = compare_report_in_detail(
        key_calculation(get_report_directly(report_id)),
        key_calculation(get_report_directly(previous_report.id))
    )

    difference = timezone.now() - previous_report.at_when
    days_between_current_and_previous_report = difference.days

    summary = comp['summary']
    comparison_is_empty = summary['neutral'] + summary['improvement'] + summary['regression'] < 1

    return {
        # comparison reports:
        # The template system only knows strings, so the boolean is coded as string here
        "previous_report_available": str(True),
        "previous_report_average_internet_nl_score": comp['old']['average_internet_nl_score'],
        "compared_report_id": previous_report.id,

        "comparison_is_empty": str(comparison_is_empty),
        "improvement": comp['summary']['improvement'],
        "regression": comp['summary']['regression'],
        "neutral": comp['summary']['neutral'],
        "comparison_report_available": str(True),
        "comparison_report_contains_improvement": str(comp['summary']['improvement'] > 0),
        "comparison_report_contains_regression": str(comp['summary']['regression'] > 0),

        "days_between_current_and_previous_report": days_between_current_and_previous_report,
        "comparison_table_improvement": render_comparison_view(comp, impact="improvement", language=mail_language),
        "comparison_table_regression": render_comparison_view(comp, impact="regression", language=mail_language),
        "domains_exclusive_in_current_report": ",".join(sorted(comp['urls_exclusive_in_new_report'])),
        "domains_exclusive_in_other_report": ",".join(sorted(comp['urls_exclusive_in_old_report'])),
    }


def generate_unsubscribe_code() -> str:
    # https://pynative.com/python-generate-random-string/
    # secure random is not needed, would be ridiculous. A sleep(1) is enough to deter any attack
    return ''.join(choice(string.ascii_letters + string.digits) for i in range(128))  # nosec


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
def send_queued_mail():
    """
    To use this, add a periodic task. The signature is:
    dashboard.internet_nl_dashboard.logic.mail.send_queued_mail

    Is added in the list of periodic tasks in the fixtures.
    :return:
    """
    call_command('send_queued_mail', processes=1, log_level=2)
