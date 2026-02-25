# SPDX-License-Identifier: Apache-2.0
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from dashboard.internet_nl_dashboard.allauth_email import ensure_user_email_address_verified


@receiver(post_save, sender=get_user_model())
def ensure_allauth_email_verified(sender, instance, **kwargs):
    """
    Keep allauth EmailAddress in sync for users created/updated in Django admin.

    This deployment treats user emails as pre-verified; therefore each save
    ensures `EmailAddress(user, user.email)` exists and is marked verified.
    """
    ensure_user_email_address_verified(instance, commit=True)
