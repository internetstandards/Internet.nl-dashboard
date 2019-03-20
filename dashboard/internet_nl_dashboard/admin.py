from datetime import datetime, timedelta

import pytz
from constance.admin import Config, ConstanceAdmin, ConstanceForm
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from dashboard.internet_nl_dashboard.models import Account, DashboardUser, UploadLog, UrlList


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


class DashboardUserInline(admin.StackedInline):
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

    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'in_groups')

    actions = []

    @staticmethod
    def in_groups(obj):
        value = ""
        for group in obj.groups.all():
            value += group.name
        return value


# I don't know if the permissions between two systems have the same numbers... Only one way to find out :)
class GroupAdmin(BaseGroupAdmin, ImportExportModelAdmin):
    resource_class = GroupResource


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# todo: make sure this is implemented.
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

    list_display = ('name', 'enable_logins', 'internet_nl_api_username')
    search_fields = ('name', )
    list_filter = ['enable_logins'][::-1]
    fields = ('name', 'enable_logins', 'internet_nl_api_username', 'internet_nl_api_password')

    def save_model(self, request, obj, form, change):

        # If the internet_nl_api_password changed, encrypt the new value.
        # Example usage and docs: https://github.com/pyca/cryptography
        if 'internet_nl_api_password' in form.changed_data:
            f = Fernet(settings.FIELD_ENCRYPTION_KEY)
            encrypted = f.encrypt(obj.internet_nl_api_password.encode())
            obj.internet_nl_api_password = encrypted

            # You can decrypt using f.decrypt(token)

        super().save_model(request, obj, form, change)

    actions = []


@admin.register(UrlList)
class UrlListAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ('name', 'account', )
    search_fields = ('name', 'account__name')
    list_filter = ['account'][::-1]
    fields = ('name', 'account', 'urls')


@admin.register(UploadLog)
class UploadLogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('original_filename', 'internal_filename', 'message', 'user', 'upload_date', 'filesize')
    search_fields = ('internal_filename', 'orginal_filename', 'message')
    list_filter = ['message', 'upload_date', 'user'][::-1]

    fields = ('original_filename', 'internal_filename', 'message', 'user', 'upload_date', 'filesize')
