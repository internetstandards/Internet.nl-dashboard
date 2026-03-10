# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path

import orjson
from constance import config
from django.conf import settings as django_settings
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.urls import path, register_converter
from ninja import NinjaAPI
from ninja.openapi.docs import Swagger, render_template
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

ALLAUTH_OPENAPI_DIR = Path(__file__).resolve().parent / "templates" / "openapi" / "allauth"


def allauth_openapi_swagger_css(request):
    asset_path = ALLAUTH_OPENAPI_DIR / "swagger-ui.css"
    if not asset_path.is_file():
        raise Http404
    response = FileResponse(asset_path.open("rb"), content_type="text/css; charset=utf-8")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def allauth_openapi_swagger_bundle(request):
    asset_path = ALLAUTH_OPENAPI_DIR / "swagger-ui-bundle.js"
    if not asset_path.is_file():
        raise Http404
    response = FileResponse(asset_path.open("rb"), content_type="application/javascript; charset=utf-8")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def allauth_openapi_swagger_init(request):
    asset_path = ALLAUTH_OPENAPI_DIR / "swagger-ui-init.js"
    if not asset_path.is_file():
        raise Http404
    response = FileResponse(asset_path.open("rb"), content_type="application/javascript; charset=utf-8")
    response["Cache-Control"] = "public, max-age=86400"
    return response


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


class CSRFAwareSwagger(Swagger):
    """
    Force CSRF support in the docs UI.

    The API applies `django_auth` on routers instead of on the top-level `NinjaAPI`.
    Django Ninja only auto-enables the CSRF request interceptor when `api.auth`
    is configured globally, so without this override Swagger "Try it out" requests
    omit `X-CSRFToken` and fail for authenticated mutating endpoints.
    """

    # following standard signature
    def render_page(self, request, api, **kwargs):  # pylint: disable=redefined-outer-name
        self.settings["url"] = self.get_openapi_url(api, kwargs)
        context = {
            "swagger_settings": json.dumps(self.settings, indent=1),
            "api": api,
            "add_csrf": True,
        }
        return render_template(request, self.template, self.template_cdn, context)


# /api/v1/allauth/openapi.html
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
    docs=CSRFAwareSwagger(),
    description="## Introduction\n\nThis is the dashboard API specification.\n\n "
    "## Authentication\n\nFor authentication you can login via "
    "allauth. The allauth swagger file can be found here: `/api/v1/allauth/openapi.html` .\n\n"
    "The internet.nl API, which is used inside the dashboard, can be found here: "
    "`https://batch.internet.nl/api/batch/openapi.yaml` and can be live-rendered via the following:"
    "url `https://redocly.github.io/redoc/?url=https://batch.internet.nl/api/batch/openapi.yaml`.\n\n"
    "## Using Swagger\n\nAuthenticated `POST`, `PUT`, `PATCH` and `DELETE` calls in `/api/v1/docs` use the current "
    "browser session and CSRF token. First log in in the same browser via `/api/v1/allauth/openapi.html` or "
    "`/accounts/login/`, then return to `/api/v1/docs` and use `Try it out`.",
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
    path(
        "api/v1/allauth/openapi-assets/swagger-ui.css",
        allauth_openapi_swagger_css,
        name="allauth_openapi_swagger_css",
    ),
    path(
        "api/v1/allauth/openapi-assets/swagger-ui-bundle.js",
        allauth_openapi_swagger_bundle,
        name="allauth_openapi_swagger_bundle",
    ),
    path(
        "api/v1/allauth/openapi-assets/swagger-ui-init.js",
        allauth_openapi_swagger_init,
        name="allauth_openapi_swagger_init",
    ),
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
