import logging
from datetime import datetime, timedelta

import pytz
from constance.admin import Config, ConstanceAdmin, ConstanceForm
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from jet.admin import CompactInline

from dashboard.internet_nl_dashboard import models
from dashboard.internet_nl_dashboard.forms import CustomAccountModelForm
from dashboard.internet_nl_dashboard.models import (Account, AccountInternetNLScan, DashboardUser,
                                                    UploadLog, UrlList)
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint

log = logging.getLogger(__package__)


class MyPeriodicTaskForm(PeriodicTaskForm):

    fieldsets = PeriodicTaskAdmin.fieldsets

    """
    Interval schedule does not support due_ or something. Which is absolutely terrible and vague.
    I can't understand why there is not an is_due() for each type of schedule. This makes it very hazy
    when something will run.

    Because of this, we'll move to the horrifically designed absolute nightmare format Crontab.
    Crontab would be half-great if the parameters where named.

    Get your crontab guru going, this is the only way you'll understand what you're doing.
    https://crontab.guru/#0_21_*_*_*
    """

    def clean(self):
        print('cleaning')

        cleaned_data = super(PeriodicTaskForm, self).clean()

        # if not self.cleaned_data['last_run_at']:
        #     self.cleaned_data['last_run_at'] = datetime.now(pytz.utc)

        return cleaned_data


class IEPeriodicTaskAdmin(PeriodicTaskAdmin, ImportExportModelAdmin):
    # most / all time schedule functions in celery beat are moot. So the code below likely makes no sense.

    list_display = ('name_safe', 'enabled', 'interval', 'crontab', 'next',  'due',
                    'precise', 'last_run_at', 'queue', 'task', 'args', 'last_run', 'runs')

    list_filter = ('enabled', 'queue', 'crontab')

    search_fields = ('name', 'queue', 'args')

    form = MyPeriodicTaskForm

    save_as = True

    @staticmethod
    def name_safe(obj):
        return mark_safe(obj.name)

    @staticmethod
    def last_run(obj):
        return obj.last_run_at

    @staticmethod
    def runs(obj):
        # print(dir(obj))
        return obj.total_run_count

    @staticmethod
    def due(obj):
        if obj.last_run_at:
            return obj.schedule.remaining_estimate(last_run_at=obj.last_run_at)
        else:
            # y in seconds
            z, y = obj.schedule.is_due(last_run_at=datetime.now(pytz.utc))
            date = datetime.now(pytz.utc) + timedelta(seconds=y)

            return naturaltime(date)

    @staticmethod
    def precise(obj):
        if obj.last_run_at:
            return obj.schedule.remaining_estimate(last_run_at=obj.last_run_at)
        else:
            return obj.schedule.remaining_estimate(last_run_at=datetime.now(pytz.utc))

    @staticmethod
    def next(obj):
        if obj.last_run_at:
            return obj.schedule.remaining_estimate(last_run_at=obj.last_run_at)
        else:
            # y in seconds
            z, y = obj.schedule.is_due(last_run_at=datetime.now(pytz.utc))
            # somehow the cron jobs still give the correct countdown even last_run_at is not set.

            date = datetime.now(pytz.utc) + timedelta(seconds=y)

            return date

    class Meta:
        ordering = ["-name"]


class IECrontabSchedule(ImportExportModelAdmin):
    pass


admin.site.unregister(PeriodicTask)
admin.site.unregister(CrontabSchedule)
admin.site.register(PeriodicTask, IEPeriodicTaskAdmin)
admin.site.register(CrontabSchedule, IECrontabSchedule)


class DashboardUserInline(CompactInline):
    model = DashboardUser
    can_delete = False
    verbose_name_plural = 'Dashboard Users'


# Thank you:
# https://stackoverflow.com/questions/47941038/how-should-i-add-django-import-export-on-the-user-model?rq=1
class UserResource(resources.ModelResource):
    class Meta:
        model = User
        # fields = ('first_name', 'last_name', 'email')


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group


class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    inlines = (DashboardUserInline, )

    list_display = ('username', 'in_account', 'first_name', 'last_name',
                    'email', 'is_active', 'is_staff', 'is_superuser', 'last_login')

    list_filter = ['is_active', 'is_staff', 'is_superuser'][::-1]

    search_fields = ['username', 'dashboarduser__account__name', 'dashboarduser__account__internet_nl_api_username']

    @staticmethod
    def in_account(obj):
        user = DashboardUser.objects.all().filter(user=obj).first()

        if not user:
            return '-'

        return user.account


# I don't know if the permissions between two systems have the same numbers... Only one way to find out :)
class GroupAdmin(BaseGroupAdmin, ImportExportModelAdmin):
    resource_class = GroupResource


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Overwrite the ugly Constance forms with something nicer
class CustomConfigForm(ConstanceForm):
    def __init__(self, *args, **kwargs):
        super(CustomConfigForm, self).__init__(*args, **kwargs)
        # ... do stuff to make your settings form nice ...


class ConfigAdmin(ConstanceAdmin):
    change_list_form = CustomConfigForm
    change_list_template = 'admin/config/settings.html'


admin.site.unregister([Config])
admin.site.register([Config], ConfigAdmin)


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = CustomAccountModelForm

    list_display = ('name', 'internet_nl_api_username', 'can_connect_to_internet_nl_api', 'no_of_users')
    search_fields = ('name', 'can_connect_to_internet_nl_api')
    # list_filter = [][::-1]
    fields = ('name', 'internet_nl_api_username', 'new_password')

    # cannot use the DashboardUserInline, it acts like there are three un-assigned users and it breaks the 1 to 1
    # relation with the DashboardUser to user. Perhaps because Jet doesn't understands that type of relationship
    # in an inline, or this inline is just not designed for it.
    # inlines = [DashboardUserInline]

    # It's also impossible to 'just show a list of scans' through the many to many relationship. While we can
    # show the relationship with no effort, the contents or a list view of these scans remains invisible.
    # Even with .though models and declaring an N-N relationship explicitly in the Account model, it remains impossible
    # to get a nice list view. We can achieve it by using nested_admin, but that increases complexity a lot.
    # inlines = [CurrentScanInline]

    @staticmethod
    def no_of_users(obj):
        return mark_safe("<a href='/admin/auth/user/?q=%s#/tab/inline_0/'>🔎 %s" %
                         (obj.name, DashboardUser.objects.all().filter(account=obj).count()))

    def save_model(self, request, obj, form, change):

        # If the internet_nl_api_password changed, encrypt the new value.
        # Example usage and docs: https://github.com/pyca/cryptography
        if 'new_password' in form.changed_data:
            obj.internet_nl_api_password = Account.encrypt_password(form.cleaned_data.get('new_password'))

        # check if the username / password combination is valid

        super().save_model(request, obj, form, change)

    actions = []

    def check_api_connectivity(self, request, queryset):
        for account in queryset:
            username = account.internet_nl_api_username
            password = account.decrypt_password()
            account.can_connect_to_internet_nl_api = account.connect_to_internet_nl_api(username, password)
            account.save()
        self.message_user(request, "Checked account API connectivity.")

    # suppressing error: "Callable[[Any, Any, Any], Any]" has no attribute "short_description"
    # This comes from the manual... so, well.
    check_api_connectivity.short_description = "Check API credentials"   # type: ignore
    actions.append('check_api_connectivity')


@admin.register(UrlList)
class UrlListAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ('name', 'account', 'no_of_urls', 'no_of_endpoints')
    search_fields = ('name', 'account__name')
    list_filter = ['account'][::-1]
    fields = ('name', 'account', 'urls')

    def no_of_urls(self, obj):
        return Url.objects.all().filter(urls_in_dashboard_list=obj, is_dead=False, not_resolvable=False).count()

    def no_of_endpoints(self, obj):
        return Endpoint.objects.all().filter(url__urls_in_dashboard_list=obj, is_dead=False,
                                             url__is_dead=False, url__not_resolvable=False).count()


@admin.register(AccountInternetNLScan)
class AccountInternetNLScanAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ('account', 'account__name', 'scan', 'scan__finished', 'urllist')

    fields = ('account', 'scan', 'urllist')

    @staticmethod
    def account__name(obj):
        return obj.account.internet_nl_api_username

    @staticmethod
    def scan__finished(obj):
        return obj.scan.finished


@admin.register(UploadLog)
class UploadLogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('original_filename', 'internal_filename', 'status', 'message', 'user', 'upload_date', 'filesize')
    search_fields = ('internal_filename', 'orginal_filename', 'status')
    list_filter = ['message', 'upload_date', 'user'][::-1]

    fields = ('original_filename', 'internal_filename', 'status', 'message', 'user', 'upload_date', 'filesize')


@admin.register(models.UrlListReport)
class UrlListReportAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    def inspect_list(self, obj):
        return format_html('<a href="../../internet_nl_dashboard/urllist/{id}/change">inspect</a>',
                           id=format(obj.id))

    list_display = ('urllist', 'high', 'medium', 'low', 'ok', 'total_endpoints', 'ok_endpoints', 'when', 'inspect_list')
    search_fields = (['when'])
    list_filter = ['urllist', 'when'][::-1]
    fields = ('total_endpoints',
              'total_issues',

              'high',
              'medium',
              'low',
              'ok',
              'high_endpoints',
              'medium_endpoints',
              'low_endpoints',
              'ok_endpoints',
              'total_url_issues',
              'url_issues_high',
              'url_issues_medium',
              'url_issues_low',
              'url_ok',
              'total_endpoint_issues',
              'endpoint_issues_high',
              'endpoint_issues_medium',
              'endpoint_issues_low',
              'endpoint_ok',
              'explained_high',
              'explained_medium',
              'explained_low',
              'explained_high_endpoints',
              'explained_medium_endpoints',
              'explained_low_endpoints',
              'explained_total_url_issues',
              'explained_url_issues_high',
              'explained_url_issues_medium',
              'explained_url_issues_low',
              'explained_total_endpoint_issues',
              'explained_endpoint_issues_high',
              'explained_endpoint_issues_medium',
              'explained_endpoint_issues_low',

              'when', 'calculation')

    ordering = ["-when"]

    save_as = True
