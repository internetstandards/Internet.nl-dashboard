from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = 'dashboard.internet_nl_dashboard'

    # See: https://django-activity-stream.readthedocs.io/en/latest/configuration.html
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('UrlList'))
        registry.register(self.get_model('AccountInternetNLScan'))
        registry.register(self.get_model('UrlListReport'))
        registry.register(self.get_model('Account'))
        registry.register(self.get_model('DashboardUser'))
