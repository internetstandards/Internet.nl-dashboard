import json
import logging
from time import sleep

from constance import config
from django.http import JsonResponse
from django_mail_admin import mail, models

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.views import get_json_body

log = logging.getLogger(__package__)


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

    # prevent some abuse, don't go into logging mode just yet in this incarnation, perhaps this is more than
    # enough protection. You can work around a lot of stuff...
    sleep(3)

    email_subject = "Access to API / dashboard requested"
    email_content = json.dumps({"form_data": form_data}, indent=4)
    email_addresses = config.DASHBOARD_SIGNUP_NOTIFICATION_EMAIL_ADRESSES.split(",")

    mail.send(
        sender=config.EMAIL_NOTIFICATION_SENDER,
        recipients=email_addresses,
        subject=email_subject,
        message=email_content,
        priority=models.PRIORITY.now,
        html_message=email_content,
    )

    return JsonResponse(operation_response(success=True, message="access_requested"))
