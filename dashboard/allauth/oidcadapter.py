import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

log = logging.getLogger(__package__)


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
