# SPDX-License-Identifier: Apache-2.0
from allauth.mfa.models import Authenticator
from django.contrib.auth.base_user import AbstractBaseUser


def reset_2fa(user: AbstractBaseUser) -> int:
    """Remove all django-allauth MFA authenticators belonging to the user."""
    deleted_count, _ = Authenticator.objects.filter(user_id=user.pk).delete()
    return deleted_count
