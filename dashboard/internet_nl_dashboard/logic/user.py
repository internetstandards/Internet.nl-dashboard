# SPDX-License-Identifier: Apache-2.0
import logging

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from dashboard.internet_nl_dashboard.logic import operation_response
from dashboard.internet_nl_dashboard.logic.domains import keys_are_present_in_object
from dashboard.settings import LANGUAGES

log = logging.getLogger(__package__)


def get_user_settings(dashboarduser_id):

    # one to one relation, error-friendly query using first.
    user = User.objects.all().filter(dashboarduser=dashboarduser_id).first()

    if not user:
        return {}

    data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': None,
        'last_login': None,
        'account_id': user.dashboarduser.account.id,
        'account_name': user.dashboarduser.account.name,
        'mail_preferred_mail_address': user.dashboarduser.mail_preferred_mail_address,
        'mail_preferred_language': user.dashboarduser.mail_preferred_language.code.lower(),
        'mail_send_mail_after_scan_finished': user.dashboarduser.mail_send_mail_after_scan_finished
    }

    return data


def save_user_settings(dashboarduser_id, data):

    user = User.objects.all().filter(dashboarduser=dashboarduser_id).first()

    if not user:
        return operation_response(error=True, message="save_user_settings_error_could_not_retrieve_user")

    """
    The only fields that can be changed by the user are:
    - first_name
    - last_name
    - mail_preferred_mail_address
    - mail_preferred_language (en, nl)
    - mail_send_mail_after_scan_finished
    """

    expected_keys = ['first_name', 'last_name', 'mail_preferred_mail_address', 'mail_preferred_language',
                     'mail_send_mail_after_scan_finished']
    if not keys_are_present_in_object(expected_keys, data):
        return operation_response(error=True, message="save_user_settings_error_incomplete_data")

    # validate data. Even if it's correct for the model (like any language), that's not what we'd accept.
    # this breaks the 'form-style' logic. Perhaps we'd move to django rest framework to optimize this.
    # Otoh there's no time for that now. Assuming the form is entered well this is no direct issue now.
    # I'm currently slowly developing a framework. But as long as it's just a few forms and pages it's fine.
    if data['mail_preferred_language'] not in [language_code for language_code, name in LANGUAGES]:
        return operation_response(error=True, message="save_user_settings_error_form_unsupported_language")

    # email is allowed to be empty:
    if data['mail_preferred_mail_address']:
        email_field = forms.EmailField()
        try:
            email_field.clean(data['mail_preferred_mail_address'])
        except ValidationError:
            return operation_response(error=True, message="save_user_settings_error_form_incorrect_mail_address")

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.save()

    user.dashboarduser.mail_preferred_mail_address = data['mail_preferred_mail_address']
    user.dashboarduser.mail_preferred_language = data['mail_preferred_language']
    user.dashboarduser.mail_send_mail_after_scan_finished = data['mail_send_mail_after_scan_finished']
    user.dashboarduser.save()

    return operation_response(success=True, message="save_user_settings_success")
