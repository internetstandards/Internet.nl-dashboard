# SPDX-License-Identifier: Apache-2.0
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = 'dashboard.internet_nl_dashboard'

    # See: https://django-activity-stream.readthedocs.io/en/latest/configuration.html
    def ready(self):
        # Loading actstream is not possible yet, as the apps aren't loaded. Django will crash.
        from actstream import registry  # pylint: disable=import-outside-toplevel

        registry.register(self.get_model('UrlList'))
        registry.register(self.get_model('AccountInternetNLScan'))
        registry.register(self.get_model('UrlListReport'))
        registry.register(self.get_model('Account'))
        registry.register(self.get_model('DashboardUser'))
        registry.register(self.get_model('UploadLog'))
