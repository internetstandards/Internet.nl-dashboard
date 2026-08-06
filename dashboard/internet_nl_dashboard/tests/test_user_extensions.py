# SPDX-License-Identifier: Apache-2.0
from allauth.mfa.models import Authenticator
from django.contrib.auth import get_user_model


def test_reset_2fa_removes_all_authenticators_for_user(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="reset-2fa-user")
    other_user = user_model.objects.create_user(username="other-user")

    for authenticator_type in Authenticator.Type.values:
        Authenticator.objects.create(user=user, type=authenticator_type, data={})
    Authenticator.objects.create(user=other_user, type=Authenticator.Type.TOTP, data={})

    deleted_count = user.reset_2fa()

    assert deleted_count == len(
        Authenticator.Type.values
    ), "reset_2fa() should report the number of removed authenticators"
    assert not Authenticator.objects.filter(user=user).exists(), "reset_2fa() should remove every authenticator type"
    assert Authenticator.objects.filter(user=other_user).count() == 1, "reset_2fa() should not affect other users"


def test_reset_2fa_is_safe_when_user_has_no_authenticators(db):
    user = get_user_model().objects.create_user(username="reset-2fa-without-authenticators")

    assert user.reset_2fa() == 0, "reset_2fa() should be idempotent"
