import json
import logging
from datetime import datetime, timedelta, timezone
from time import sleep

from constance import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_mail_admin import mail, models
from django_mail_admin.models import Log

from dashboard.celery import app
from dashboard.internet_nl_dashboard.logic import operation_response
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
    send_mail_async.s(form_data).apply_async()

    return JsonResponse(operation_response(success=True, message="access_requested"))


@app.task(queue="storage")
def send_mail_async(form_data):
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
