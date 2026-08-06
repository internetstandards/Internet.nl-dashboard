# SPDX-License-Identifier: Apache-2.0
from django.apps import AppConfig
from django.contrib.auth import get_user_model


class DashboardConfig(AppConfig):
    name = "dashboard.internet_nl_dashboard"

    # See: https://django-activity-stream.readthedocs.io/en/latest/configuration.html
    def ready(self):
        # Loading actstream is not possible yet, as the apps aren't loaded. Django will crash.
        from actstream import registry  # pylint: disable=import-outside-toplevel

        import dashboard.internet_nl_dashboard.signals  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel
        from dashboard.internet_nl_dashboard.user_extensions import reset_2fa  # pylint: disable=import-outside-toplevel

        get_user_model().add_to_class("reset_2fa", reset_2fa)

        registry.register(self.get_model("UrlList"))
        registry.register(self.get_model("AccountInternetNLScan"))
        registry.register(self.get_model("UrlListReport"))
        registry.register(self.get_model("Account"))
        registry.register(self.get_model("DashboardUser"))
        registry.register(self.get_model("UploadLog"))
