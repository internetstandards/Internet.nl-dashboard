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
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from two_factor.urls import urlpatterns as tf_urls

admin.site.site_header = 'Dashboard Admin'
admin.site.site_title = 'Dashboard Admin'


def trigger_error(request):
    # See: https://docs.sentry.io/platforms/python/django/
    raise ZeroDivisionError("This is a test for celery.")


admin_urls = [
    path('sentry-debug/', trigger_error),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^activity/', include('actstream.urls')),
]

frontend_urls = [
    url('', include('dashboard.internet_nl_dashboard.urls')),
    # Enabling the default auth logins can bypass the two factor authentication. Don't enable it.
    # path('', include('django.contrib.auth.urls')),
    url(r'', include(tf_urls)),
]

urlpatterns = frontend_urls.copy()
urlpatterns += admin_urls  # type: ignore
