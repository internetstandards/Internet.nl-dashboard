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
from allauth.account import views as allauth_views
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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


frontend_urls = [
    path("", include("dashboard.internet_nl_dashboard.urls")),
    # Enabling the default auth logins can bypass the two factor authentication. Don't enable it.
    # path('', include('django.contrib.auth.urls')),
    re_path(r"", include(tf_urls)),
    # allauth also uses 429.html template when the included rate limits are reached. You can try this
    # by submitting a bunch of password changes in a second or so.
    # this exposes a password reset and change form.
    # the login and logout forms have to be removed as they bypass the django 2nd factor auth.
    # allauth does include 2nd factor auth but it has to be enabled and it might not be compatible
    # with the accounts we currently have. So social login might be feasible, but the normal log
    # not yet. Also disable reauthenticate
    #  -> this view is mandatory to register, but directing it to the wrong page on purpose
    path(
        "accounts/password/",
        not_supported,
        name="account_login",
    ),
    path("accounts/password/reset/", not_supported, name="account_reset_password"),
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
    # These have not yet been requested and not tested how the work and if they are useful.
    # path(
    #     "accounts/password/reset/", password_reset, name="account_reset_password"
    # ),
    # path(
    #     "accounts/password/reset/done/",
    #     password_reset_done,
    #     name="account_reset_password_done",
    # ),
    # re_path(
    #     r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
    #     password_reset_from_key,
    #     name="account_reset_password_from_key",
    # ),
    # path(
    #     "accounts/password/reset/key/done/",
    #     password_reset_from_key_done,
    #     name="account_reset_password_from_key_done",
    # ),
    path("accounts/", include("allauth.urls")),
]

urlpatterns = frontend_urls.copy()
urlpatterns += admin_urls  # type: ignore
