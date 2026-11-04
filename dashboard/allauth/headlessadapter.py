# SPDX-License-Identifier: Apache-2.0
from dataclasses import field, make_dataclass

from allauth.headless.adapter import DefaultHeadlessAdapter

from dashboard.internet_nl_dashboard.models import Account, DashboardUser


class HeadlessAdapter(DefaultHeadlessAdapter):
    def get_user_dataclass(self):
        return make_dataclass(
            "User",
            [
                (
                    "account_id",
                    int | None,
                    field(
                        default=None,
                        metadata={"description": "The dashboard account ID, distinct from the user ID."},
                    ),
                ),
                (
                    "account_name",
                    str | None,
                    field(
                        default=None,
                        metadata={"description": "The dashboard account name, distinct from the username."},
                    ),
                ),
                (
                    "is_superuser",
                    bool | None,
                    field(default=None, metadata={"description": "Whether the authenticated user is a superuser."}),
                ),
            ],
            bases=(super().get_user_dataclass(),),
        )

    def user_as_dataclass(self, user):
        data = super().user_as_dataclass(user)
        # Allauth also serializes users during password reset and incomplete
        # authentication. Do not disclose dashboard membership in those flows.
        if not self.request or not self.request.user.is_authenticated or self.request.user.id != user.id:
            return data

        dashboarduser = DashboardUser.objects.select_related("account").filter(user=user).first()
        if dashboarduser is None:
            # Preserve the legacy session endpoint's recovery for users created
            # without a dashboard account (for example via createsuperuser).
            account, _ = Account.objects.get_or_create(name="Fallback account for incomplete new users")
            dashboarduser, _ = DashboardUser.objects.get_or_create(user=user, defaults={"account": account})

        data.account_id = dashboarduser.account.id
        data.account_name = dashboarduser.account.name
        data.is_superuser = user.is_superuser
        return data
