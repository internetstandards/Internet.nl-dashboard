import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

log = logging.getLogger(__package__)


# We do not want to support the "signup" flow at all, this is a manual process.
# This requires some work with the adapter saying no to account signups, but we DO need to support account signups
# from openid. See this thread why we need this approach. https://codeberg.org/allauth/django-allauth/issues/345
class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        match = getattr(request, "resolver_match", None)
        if not match:
            return True

        # Close direct local signups, but allow social/OIDC signups.
        if match.url_name in {"account_signup", "account_signup_by_passkey"}:
            return False
        if (
            match.url_name == "signup"
            and "headless" in match.namespaces
            and "account" in match.namespaces
        ):
            return False
        return True


class OIDCGroupRestrictionAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):

        log.info("Checking authorized groups for OIDC login...")

        groups = sociallogin.account.extra_data.get("groups", [])
        for group in groups:
            log.info("Checking Group: %s...", group)
            if group == "/mygroup":
                log.info("YES ! User is in the required group.")
                return super().pre_social_login(request, sociallogin)

        log.debug("%s", sociallogin.serialize())

        raise PermissionDenied("You are not a member of the required group.")
