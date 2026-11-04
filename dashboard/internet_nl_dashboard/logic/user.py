# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime
from typing import Optional

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ninja import Schema

from dashboard.internet_nl_dashboard.logic.domains import keys_are_present_in_object
from dashboard.internet_nl_dashboard.problems import ApiError, ProblemType
from dashboard.settings import LANGUAGES

log = logging.getLogger(__package__)


class UserSettingsSchema(Schema):
    first_name: str
    last_name: str
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None
    account_id: int
    account_name: str
    mail_preferred_mail_address: Optional[str] = None
    mail_preferred_language: str
    mail_send_mail_after_scan_finished: bool


class SaveUserSettingsInputSchema(Schema):
    first_name: str
    last_name: str
    mail_preferred_mail_address: Optional[str] = None
    mail_preferred_language: str
    mail_send_mail_after_scan_finished: bool


def get_user_settings(dashboarduser_id) -> UserSettingsSchema:

    # one to one relation, error-friendly query using first.
    user = User.objects.all().filter(dashboarduser=dashboarduser_id).first()

    if not user:
        # Return an empty schema to keep response type consistent
        return UserSettingsSchema(
            first_name="",
            last_name="",
            date_joined=None,
            last_login=None,
            account_id=-1,
            account_name="",
            mail_preferred_mail_address=None,
            mail_preferred_language="en",
            mail_send_mail_after_scan_finished=False,
        )

    data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        # Explicitly hide timestamps in API as per previous behavior
        "date_joined": None,
        "last_login": None,
        "account_id": user.dashboarduser.account.id,
        "account_name": user.dashboarduser.account.name,
        "mail_preferred_mail_address": user.dashboarduser.mail_preferred_mail_address,
        # Ensure language is a lowercased string code for API
        "mail_preferred_language": (
            user.dashboarduser.mail_preferred_language.code.lower()
            if hasattr(user.dashboarduser.mail_preferred_language, "code")
            else str(user.dashboarduser.mail_preferred_language).lower()
        ),
        "mail_send_mail_after_scan_finished": user.dashboarduser.mail_send_mail_after_scan_finished,
    }

    return UserSettingsSchema(**data)


def save_user_settings(dashboarduser_id, data: SaveUserSettingsInputSchema | dict) -> None:

    user = User.objects.all().filter(dashboarduser=dashboarduser_id).first()

    if not user:
        raise ApiError(404, "User settings could not be found.", ProblemType.USER_SETTINGS_NOT_FOUND)

    """
    The only fields that can be changed by the user are:
    - first_name
    - last_name
    - mail_preferred_mail_address
    - mail_preferred_language (en, nl)
    - mail_send_mail_after_scan_finished
    """

    # Convert schema to dict if needed
    if hasattr(data, "dict"):
        data = data.dict()

    expected_keys = [
        "first_name",
        "last_name",
        "mail_preferred_mail_address",
        "mail_preferred_language",
        "mail_send_mail_after_scan_finished",
    ]
    if not keys_are_present_in_object(expected_keys, data):
        raise ApiError(
            400,
            "Required settings are missing.",
            ProblemType.INVALID_INPUT,
            errors=[{"loc": ["body", key], "msg": "Field required"} for key in expected_keys if key not in data],
        )

    # validate data. Even if it's correct for the model (like any language), that's not what we'd accept.
    if data["mail_preferred_language"] not in [language_code for language_code, name in LANGUAGES]:
        raise ApiError(
            400,
            "The selected language is not supported.",
            ProblemType.UNSUPPORTED_LANGUAGE,
            field="mail_preferred_language",
        )

    # email is allowed to be empty:
    if data["mail_preferred_mail_address"]:
        email_field = forms.EmailField()
        try:
            email_field.clean(data["mail_preferred_mail_address"])
        except ValidationError:
            raise ApiError(
                400,
                "The email address is invalid.",
                ProblemType.INVALID_EMAIL_ADDRESS,
                field="mail_preferred_mail_address",
            )

    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.save()

    user.dashboarduser.mail_preferred_mail_address = data["mail_preferred_mail_address"]
    user.dashboarduser.mail_preferred_language = data["mail_preferred_language"]
    user.dashboarduser.mail_send_mail_after_scan_finished = data["mail_send_mail_after_scan_finished"]
    user.dashboarduser.save()

    return None
