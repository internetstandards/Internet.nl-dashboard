# SPDX-License-Identifier: Apache-2.0
from types import SimpleNamespace

import pytest
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from dashboard.allauth.oidcadapter import OIDCGroupRestrictionAdapter
from dashboard.internet_nl_dashboard.models import Account, DashboardUser


def _build_sociallogin(user, home_organisation, provider_id="openid_connect"):
    extra_data = {"userinfo": {"schac_home_organization": home_organisation}}
    return SimpleNamespace(
        provider=SimpleNamespace(id=provider_id),
        account=SimpleNamespace(extra_data=extra_data),
        user=user,
        serialize=lambda: {"extra_data": extra_data},
    )


def test_pre_social_login_creates_account_and_assigns_existing_user(db):
    user = get_user_model().objects.create_user(username="oidc-existing-1")
    sociallogin = _build_sociallogin(user=user, home_organisation="Team A")
    adapter = OIDCGroupRestrictionAdapter()

    adapter.pre_social_login(None, sociallogin)

    account = Account.objects.get(name="Team A")
    dashboard_user = DashboardUser.objects.get(user=user)
    assert dashboard_user.account_id == account.id


def test_pre_social_login_updates_existing_dashboarduser_account(db):
    user = get_user_model().objects.create_user(username="oidc-existing-2")
    old_account = Account.objects.create(name="Old Team")
    new_account = Account.objects.create(name="New Team")
    DashboardUser.objects.create(user=user, account=old_account)
    sociallogin = _build_sociallogin(user=user, home_organisation="New Team")
    adapter = OIDCGroupRestrictionAdapter()

    adapter.pre_social_login(None, sociallogin)

    dashboard_user = DashboardUser.objects.get(user=user)
    assert dashboard_user.account_id == new_account.id


def test_pre_social_login_denies_missing_home_organisation_claim(db):
    user = get_user_model().objects.create_user(username="oidc-existing-3")
    sociallogin = _build_sociallogin(user=user, home_organisation="")
    adapter = OIDCGroupRestrictionAdapter()

    with pytest.raises(PermissionDenied):
        adapter.pre_social_login(None, sociallogin)

    assert DashboardUser.objects.filter(user=user).count() == 0


def test_pre_social_login_denies_non_oidc_provider(db):
    user = get_user_model().objects.create_user(username="non-oidc-user")
    sociallogin = _build_sociallogin(user=user, home_organisation="Team A", provider_id="google")
    adapter = OIDCGroupRestrictionAdapter()

    with pytest.raises(PermissionDenied):
        adapter.pre_social_login(None, sociallogin)


def test_populate_user_sets_oidc_username_to_home_organisation(db, monkeypatch):
    new_user = get_user_model()()
    sociallogin = _build_sociallogin(user=new_user, home_organisation="team-b.example")
    adapter = OIDCGroupRestrictionAdapter()

    def fake_super_populate_user(self, request, sociallogin, data):
        return sociallogin.user

    monkeypatch.setattr(DefaultSocialAccountAdapter, "populate_user", fake_super_populate_user)

    user = adapter.populate_user(None, sociallogin, {})

    assert user.username == "team-b.example", "OIDC username should be populated from schac_home_organization."


def test_populate_user_keeps_oidc_preferred_username_when_available(db, monkeypatch):
    new_user = get_user_model()()
    sociallogin = _build_sociallogin(user=new_user, home_organisation="team-c.example")
    adapter = OIDCGroupRestrictionAdapter()

    def fake_super_populate_user(self, request, sociallogin, data):
        sociallogin.user.username = "preferred-user"
        return sociallogin.user

    monkeypatch.setattr(DefaultSocialAccountAdapter, "populate_user", fake_super_populate_user)

    user = adapter.populate_user(None, sociallogin, {})

    assert user.username == "preferred-user", "OIDC preferred_username should not be overwritten."


def test_save_user_assigns_new_user_to_home_organisation(db, monkeypatch):
    new_user = get_user_model()(username="oidc-new-user")
    sociallogin = _build_sociallogin(user=new_user, home_organisation="Team B")
    adapter = OIDCGroupRestrictionAdapter()

    def fake_super_save_user(self, request, sociallogin, form=None):
        sociallogin.user.save()
        return sociallogin.user

    monkeypatch.setattr(DefaultSocialAccountAdapter, "save_user", fake_super_save_user)

    saved_user = adapter.save_user(None, sociallogin)

    account = Account.objects.get(name="Team B")
    dashboard_user = DashboardUser.objects.get(user=saved_user)
    assert dashboard_user.account_id == account.id
