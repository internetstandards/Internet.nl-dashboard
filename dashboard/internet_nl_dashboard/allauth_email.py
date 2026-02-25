# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Literal

from allauth.account.models import EmailAddress

log = logging.getLogger(__package__)

EnsureResult = Literal[
    "skipped_no_email",
    "already_verified",
    "verified",
    "conflict",
]


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def ensure_user_email_address_verified(user, *, commit: bool = True) -> EnsureResult:
    """
    Ensure `allauth.account.EmailAddress` exists for `user.email` and is verified.

    Returns a status string:
    - skipped_no_email: user has no email value
    - already_verified: matching EmailAddress already verified
    - verified: verified now (new or existing EmailAddress)
    - conflict: verification blocked (e.g. unique verified email conflict)
    """
    email = normalize_email(getattr(user, "email", ""))
    if not email:
        return "skipped_no_email"

    email_address = EmailAddress.objects.filter(user=user, email=email).order_by("id").first()
    if not email_address:
        has_primary = EmailAddress.objects.filter(user=user, primary=True).exists()
        email_address = EmailAddress(
            user=user,
            email=email,
            verified=False,
            primary=not has_primary,
        )
        if commit:
            email_address.save()

    if email_address.verified:
        return "already_verified"

    can_verify = email_address.can_set_verified()
    if can_verify and commit:
        email_address.set_verified(commit=True)
    if can_verify:
        return "verified"

    log.warning(
        "Could not mark EmailAddress verified due to conflict. user_id=%s email=%s",
        user.pk,
        email,
    )
    return "conflict"
