# SPDX-License-Identifier: Apache-2.0
from constance import config
from django.shortcuts import redirect
from django.urls import path, register_converter
from ninja import NinjaAPI
from websecmap.map.views import security_txt

# We have to import the signals somewhere?!
import dashboard.internet_nl_dashboard.signals  # noqa  # pylint: disable=unused-import
from dashboard.internet_nl_dashboard.views import (
    admin,
    app,
    logout_view,
    mail,
    public_reports,
    reports,
    scans,
    session,
    settings,
    signup,
    spreadsheet,
    urllists,
)

"""
Side effects:

If you call a method that does not exist, you will get a ninja.errors.ConfigError:
    Router@'/...' has already been attached to ...:1.0.0
"""


class SpreadsheetFileTypeConverter:
    # Supports {"key": "value", "key2": "value2"} syntax.
    regex = "(xlsx|ods|csv)"

    @staticmethod
    def to_python(value):
        return str(value)

    @staticmethod
    def to_url(value):
        return f"{value}"


api = NinjaAPI(title="Internet.nl Dashboard API", version="1.0.0")
api.add_router("/config", app.router)
api.add_router("/signup", signup.router)
api.add_router("/session", session.router)
api.add_router("/settings", settings.router)
api.add_router("/urllists", urllists.router)
api.add_router("/scans", scans.router)
api.add_router("/reports", reports.router)
api.add_router("/public-reports", public_reports.router)
api.add_router("/admin", admin.router)

# todo: where was this used, is it still relevant?
register_converter(SpreadsheetFileTypeConverter, "spreadsheet_filetype")

urlpatterns = [
    path("", lambda request: redirect(config.DASHBOARD_FRONTEND_URL)),
    path("logout/", logout_view),
    path("data/", api.urls),
    # dedicated upload-success that is used to handle uploads, this is not really integrated in the API.
    # This is used when the separate upload-button is used that selects one file, instead of drag and drop uploading
    path("upload/", spreadsheet.upload),
    # excluding this to have a nicer unsub path in mails
    path("mail/unsubscribe/<str:feed>/<str:unsubscribe_code>/", mail.unsubscribe_),
    path(".well-known/security.txt", security_txt, name="well_known_security_txt"),
    # Enabling the below path will bypass all second factor authentication, do not enable this path:
    # url(r'^/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html')),
]
