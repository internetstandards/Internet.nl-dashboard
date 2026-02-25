import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

from dashboard.internet_nl_dashboard.models import Account, DashboardUser

log = logging.getLogger(__package__)


# We do not want to support the "signup" flow at all, this is a manual process.
# This requires some work with the adapter saying no to account signups, but we DO need to support account signups
# from openid. See this thread why we need this approach. https://codeberg.org/allauth/django-allauth/issues/345
class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Local signup is fully disabled for this deployment.

        Returning False here blocks all account signup entrypoints (headed,
        headless and passkey variants). The OIDC-only exception is handled in
        `OIDCGroupRestrictionAdapter.is_open_for_signup()`, where provider
        context is available.
        """
        return False


class OIDCGroupRestrictionAdapter(DefaultSocialAccountAdapter):
    @staticmethod
    def _is_oidc_sociallogin(sociallogin) -> bool:
        provider = getattr(sociallogin, "provider", None)
        provider_id = getattr(provider, "id", None)
        return provider_id == "openid_connect"

    @staticmethod
    def _get_home_organisation_name(sociallogin) -> str:
        account = getattr(sociallogin, "account", None)
        extra_data = getattr(account, "extra_data", {}) or {}
        organisation = extra_data.get("shac_home_organisation", "")
        if not isinstance(organisation, str):
            return ""
        return organisation.strip()

    def _require_home_organisation_name(self, sociallogin) -> str:
        organisation = self._get_home_organisation_name(sociallogin)
        if not organisation:
            raise PermissionDenied(
                "OIDC claim 'shac_home_organisation' is required to determine the dashboard account."
            )
        return organisation

    @staticmethod
    def _get_or_create_account_by_name(account_name: str) -> Account:
        accounts = Account.objects.filter(name=account_name).order_by("id")
        account = accounts.first()
        if account:
            if accounts.count() > 1:
                log.warning(
                    "Multiple Account rows found for '%s'. Using oldest account id=%s.",
                    account_name,
                    account.id,
                )
            return account

        account = Account.objects.create(name=account_name)
        log.info("Created Account '%s' (id=%s) from OIDC claim.", account_name, account.id)
        return account

    def _sync_dashboard_account_from_oidc_claim(self, sociallogin, user=None, account_name=None) -> None:
        """
        Map an OIDC-authenticated user to a dashboard `Account` using:
        `sociallogin.account.extra_data['shac_home_organisation']`.

        Behavior:
        - If the claim points to an existing account name, use that account.
        - If it does not exist, create the account.
        - Ensure the user has a `DashboardUser` row mapped to that account.
        - If the user already has `DashboardUser`, update account when different.
        """
        if not self._is_oidc_sociallogin(sociallogin):
            return

        target_user = user or getattr(sociallogin, "user", None)
        if not target_user or not target_user.pk:
            # New social users are unsaved during pre_social_login; save_user handles those.
            return

        if not account_name:
            account_name = self._require_home_organisation_name(sociallogin)

        account = self._get_or_create_account_by_name(account_name)
        dashboard_user, created = DashboardUser.objects.get_or_create(
            user=target_user,
            defaults={"account": account},
        )

        if created:
            log.info("Created DashboardUser for user_id=%s in account_id=%s.", target_user.pk, account.id)
            return

        if dashboard_user.account_id != account.id:
            old_account_id = dashboard_user.account_id
            dashboard_user.account = account
            dashboard_user.save(update_fields=["account"])
            log.info(
                "Updated DashboardUser for user_id=%s: account_id %s -> %s.",
                target_user.pk,
                old_account_id,
                account.id,
            )

    def is_open_for_signup(self, request, sociallogin):
        """
        Allow signup only when the social provider is OpenID Connect.

        True case:
        - `sociallogin.provider.id == "openid_connect"`: user is in the OIDC
          social login/signup pipeline, which is the only allowed signup source.

        False case:
        - Any non-OIDC social provider is blocked from creating new users.
        - Local account signup is already blocked by `AccountAdapter`.
        """
        is_oidc_signup = self._is_oidc_sociallogin(sociallogin)
        if is_oidc_signup:
            log.info("Allowing signup because provider is OpenID Connect.")
        return is_oidc_signup

    def pre_social_login(self, request, sociallogin):
        """
        Allow only OpenID Connect logins that include `shac_home_organisation`.

        The claim is required because it determines which dashboard account the
        user belongs to.
        """
        log.info("Checking OIDC login claims...")

        if not self._is_oidc_sociallogin(sociallogin):
            raise PermissionDenied("Only OpenID Connect logins are supported.")

        account_name = self._require_home_organisation_name(sociallogin)

        # Existing users can be synchronized immediately. New users are synchronized in save_user().
        self._sync_dashboard_account_from_oidc_claim(sociallogin, account_name=account_name)
        return super().pre_social_login(request, sociallogin)

    def save_user(self, request, sociallogin, form=None):
        """
        Persist social user and then map the user to the dashboard account
        indicated by OIDC claim `shac_home_organisation`.
        """
        account_name = self._require_home_organisation_name(sociallogin)
        user = super().save_user(request, sociallogin, form=form)
        self._sync_dashboard_account_from_oidc_claim(sociallogin, user=user, account_name=account_name)
        return user
