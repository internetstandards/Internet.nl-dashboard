import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import PermissionDenied

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
        provider = getattr(sociallogin, "provider", None)
        provider_id = getattr(provider, "id", None)
        is_oidc_signup = provider_id == "openid_connect"
        if is_oidc_signup:
            log.info("Allowing signup because provider is OpenID Connect.")
        return is_oidc_signup

    def pre_social_login(self, request, sociallogin):
        """
        Enforce OIDC group-based access using `settings.OIDC_ALLOWED_GROUPS`.

        The identity provider is expected to send a `groups` claim in
        `sociallogin.account.extra_data`.
        Access is granted when at least one configured allowed group is present
        in that claim.
        """
        log.info("Checking authorized groups for OIDC login...")

        allowed_groups = {group for group in settings.OIDC_ALLOWED_GROUPS if group}
        groups = sociallogin.account.extra_data.get("groups", [])
        if isinstance(groups, str):
            groups = [groups]
        user_groups = {group for group in groups if isinstance(group, str) and group}

        if user_groups.intersection(allowed_groups):
            log.info("User is in at least one configured OIDC allowed group.")
            return super().pre_social_login(request, sociallogin)

        log.debug("%s", sociallogin.serialize())
        raise PermissionDenied("You are not a member of the required group.")
