# SPDX-License-Identifier: Apache-2.0
import orjson
from constance import config
from django.conf import settings as django_settings
from django.shortcuts import redirect
from django.urls import path, register_converter
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer
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


# Orjson means increased speed, why doesn't django-ninja use this as the default?
# https://django-ninja.dev/guides/response/response-renderers/
class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):  # noqa (unused variable response_status), matches api
        return orjson.dumps(data)


api = NinjaAPI(
    title=django_settings.OPEN_API_TITLE,
    openapi_extra={
        "info": {
            "contact": {
                "name": django_settings.OPEN_API_CONTACT_ORGANIZATION,
                "email": django_settings.OPEN_API_CONTACT_EMAIL,
                "url": django_settings.OPEN_API_CONTACT_URL,
            },
        },
    },
    version=django_settings.OPEN_API_VERSION,
    renderer=ORJSONRenderer(),
)

# Inject API-Version header into the generated OpenAPI schema for all responses.
# This workaround is generated code.
_orig_get_openapi_schema = api.get_openapi_schema


def _get_openapi_schema_with_version_header(**kwargs):
    schema = _orig_get_openapi_schema()
    components = schema.setdefault("components", {})
    headers = components.setdefault("headers", {})
    headers["API-Version"] = {
        "description": f"Semantic version of the {django_settings.OPEN_API_TITLE}",
        "schema": {"type": "string", "example": django_settings.OPEN_API_VERSION},
    }
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            responses = operation.get("responses", {})
            for response in responses.values():
                response_headers = response.setdefault("headers", {})
                response_headers["API-Version"] = {"$ref": "#/components/headers/API-Version"}
    return schema


api.get_openapi_schema = _get_openapi_schema_with_version_header


# ADR wants the version to be returned in every response. This cannot be described in django ninja.
# the X-prefix has not been recommended since 2012
# https://developer.overheid.nl/kennisbank/apis/api-design-rules/hoe-te-voldoen/version-header
def version_header(func):
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        response["API-Version"] = django_settings.OPEN_API_VERSION
        return response

    return wrapper


api.add_decorator(version_header, mode="view")

api.add_router("/config", app.router)
api.add_router("/signup", signup.router)
api.add_router("/session", session.router)
api.add_router("/settings", settings.router)
api.add_router("/urllists", urllists.router)
api.add_router("/scans", scans.router)
api.add_router("/reports", reports.router)
api.add_router("/public-reports", public_reports.router)
api.add_router("/mail", mail.router)
api.add_router("/admin", admin.router)


# todo: where was this used, is it still relevant?
register_converter(SpreadsheetFileTypeConverter, "spreadsheet_filetype")

urlpatterns = [
    path("", lambda request: redirect(config.DASHBOARD_FRONTEND_URL)),
    path("logout/", logout_view),
    path("api/v1/", api.urls),
    # dedicated upload-success that is used to handle uploads, this is not really integrated in the API.
    # This is used when the separate upload-button is used that selects one file, instead of drag and drop uploading
    path("upload/", spreadsheet.upload),
    # excluding this to have a nicer unsub path in mails. This needs to be a direct path. This old path is used
    # for legacy reasons: sent mails in older inboxes that trigger an unsub.
    path("mail/unsubscribe/<str:feed>/<str:unsubscribe_code>/", mail.unsubscribe_),
    path(".well-known/security.txt", security_txt, name="well_known_security_txt"),
    # Enabling the below path will bypass all second factor authentication, do not enable this path:
    # url(r'^/$', auth_views.LoginView.as_view(template_name='internet_nl_dashboard/registration/login.html')),
]
