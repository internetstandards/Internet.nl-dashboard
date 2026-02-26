# SPDX-License-Identifier: Apache-2.0
"""dashboard2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path

from allauth.account import views as allauth_views
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.urls import include, path, re_path
from two_factor.urls import urlpatterns as tf_urls

from . import __version__

admin.site.site_header = f"Dashboard Admin {__version__}"
# Don't show version in title, as that might be shared without auth
admin.site.site_title = "Dashboard Admin"


def trigger_error(request):
    # See: https://docs.sentry.io/platforms/python/django/
    raise ZeroDivisionError("This is a test for celery.")


admin_urls = [
    path("sentry-debug/", trigger_error),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/jet/", include("jet.urls", "jet")),
    re_path(r"^admin/jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    re_path(r"^nested_admin/", include("nested_admin.urls")),
    re_path(r"^activity/", include("actstream.urls")),
]


def not_supported(**args):
    return HttpResponse("Feature not supported.")


ALLAUTH_OPENAPI_ASSETS = {
    "swagger-ui.css": "text/css; charset=utf-8",
    "swagger-ui-bundle.js": "application/javascript; charset=utf-8",
}


def allauth_openapi_asset(request, asset):
    if asset not in ALLAUTH_OPENAPI_ASSETS:
        raise Http404
    asset_path = Path(settings.BASE_DIR) / "internet_nl_dashboard" / "templates" / "openapi" / "allauth" / asset
    if not asset_path.is_file():
        raise Http404
    response = FileResponse(asset_path.open("rb"), content_type=ALLAUTH_OPENAPI_ASSETS[asset])
    response["Cache-Control"] = "public, max-age=86400"
    return response


frontend_urls = [
    path(
        "api/v1/allauth/openapi-assets/<str:asset>",
        allauth_openapi_asset,
        name="allauth_openapi_asset",
    ),
    path("api/v1/allauth/", include("allauth.headless.urls")),
    path("", include("dashboard.internet_nl_dashboard.urls")),
    # Enabling the default auth logins can bypass the two factor authentication. Don't enable it.
    # path('', include('django.contrib.auth.urls')),
    re_path(r"", include(tf_urls)),
    # https://github.com/pennersr/django-allauth/issues/468
    path(
        "accounts/password/change/",
        login_required(
            allauth_views.PasswordChangeView.as_view(
                success_url="/account/authentication/?password_change_success=true"
            )
        ),
        name="account_change_password",
    ),
    # Required for social provider callback URLs (e.g. `openid_connect_callback`)
    # that are still resolved server-side during headless redirect flows.
    # In `HEADLESS_ONLY=True`, this does not expose headed account pages.
    path("accounts/", include("allauth.urls")),
    # todo: how to get idp urls working. Does this just work inside the API?
    # path("", include("allauth.idp.urls")),
]

urlpatterns = frontend_urls.copy()
urlpatterns += admin_urls  # type: ignore
