import json
import logging
import re
from datetime import datetime, timedelta, timezone
from time import sleep

from constance import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_mail_admin import mail, models
from django_mail_admin.models import Log

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.mail_admin_templates import xget_template
from dashboard.internet_nl_dashboard.views import get_json_body

log = logging.getLogger(__package__)


@csrf_exempt
def process_application(request):
    data = get_json_body(request)

    required_fields = ["access", "name", "email", "mobile_phone_number", "organization_name", "nature_of_organization",
                       "chamber_of_commerce_number", "reason_for_application", "intended_usage_frequency",
                       "terms_of_use", "captcha"]

    form_data = data.get("form_data", {})

    for field in required_fields:
        if field not in form_data:
            return JsonResponse(operation_response(error=True, message="incomplete_form_submitted"))

    if form_data.get("captcha") not in [42, "42"]:
        return JsonResponse(operation_response(error=True, message="incorrect_captcha"))

    sleep(1)

    # prevent abuse case where millions of requests are made, who would even bother.
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    if Log.objects.all().filter(date__gt=one_hour_ago).count() > 50:
        return JsonResponse(operation_response(success=True, message="access_requested"))

    # sending mail can take a while, so don't wait for it.
    send_backoffice_mail_async.s(form_data).apply_async()

    # also send a mail to the requester, this is a templated mail with some parameters
    # the mail is always in dutch, as we don't ask for a language
    send_signup_received_mail_to_requester.s(form_data).apply_async()

    return JsonResponse(operation_response(success=True, message="access_requested"))


@app.task(queue="storage", ignore_result=True)
def send_backoffice_mail_async(form_data):
    email_subject = "Access to API / dashboard requested"
    json_content = json.dumps({"form_data": form_data}, indent=4)
    email_addresses = config.DASHBOARD_SIGNUP_NOTIFICATION_EMAIL_ADRESSES.split(",")

    email_content = f"""Access to the API/dashboard requested by {form_data.get("name", "")} at {datetime.now()}<br>
<br>
Signup details:<br>
<pre>{json_content}</pre><br>
<br>
Kind regards,<br>
The Dashboard Team<br>
<br>
<br>
"""

    mail.send(
        sender=config.EMAIL_NOTIFICATION_SENDER,
        recipients=email_addresses,
        subject=email_subject,
        message=email_content.replace("<br>", ""),
        priority=models.PRIORITY.now,
        html_message=email_content,
    )


@app.task(queue="storage", ignore_result=True)
def send_signup_received_mail_to_requester(form_data):

    # perform some validation that this looks like a valid mail address
    # https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", form_data['email']):
        return

    # also set some sort of rate limit in case someone smart wants to send 1000's of mails quickly.

    # the backoffice team will see a mail coming in every request, so don't add those addresses here...
    mail.send(
        sender=config.EMAIL_NOTIFICATION_SENDER_FOR_SIGNUP,
        recipients=form_data['email'],  # List of email addresses also accepted
        template=xget_template(
            template_name="signup_thank_you",
            preferred_language="nl"
        ),
        variable_dict=form_data
    )
