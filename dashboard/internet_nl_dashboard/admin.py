# SPDX-License-Identifier: Apache-2.0
import logging
import re
from datetime import datetime, timedelta, timezone

import nested_admin
from celery import group
from constance.admin import Config, ConstanceAdmin, ConstanceForm
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.paginator import Paginator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from jet.admin import CompactInline
from websecmap.organizations.models import Url
from websecmap.scanners.models import Endpoint
from websecmap.scanners_internetnl_web.admin import InternetNLV2ScanAdmin
from websecmap.scanners_internetnl_web.models import InternetNLV2Scan, InternetNLV2StateLog

from dashboard.internet_nl_dashboard import models
from dashboard.internet_nl_dashboard.forms import CustomAccountModelForm
from dashboard.internet_nl_dashboard.logic.domains import scan_urllist_now_ignoring_business_rules
from dashboard.internet_nl_dashboard.logic.mail import send_scan_finished_mails
from dashboard.internet_nl_dashboard.models import (
    Account,
    AccountInternetNLScan,
    AccountInternetNLScanLog,
    DashboardUser,
    TaggedUrlInUrllist,
    UploadLog,
    UrlList,
)
from dashboard.internet_nl_dashboard.scanners.scan_internet_nl_per_account import (
    creating_report,
    progress_running_scan,
    recover_and_retry,
)

log = logging.getLogger(__package__)


class TooManyRecordsPaginator(Paginator):
    def __init__(self, object_list, per_page, something, darkside):
        super().__init__(object_list, per_page, something, darkside)

    @property
    def count(self):  # pylint: disable=invalid-overridden-method
        return 13374223


def only_alphanumeric(data: str) -> str:
    return re.sub(r"[^A-Za-z0-9 ]+", "", data)


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
        print("cleaning")
        cleaned_data = super().clean()

        # if not self.cleaned_data['last_run_at']:
        #     self.cleaned_data['last_run_at'] = datetime.now(timezone.utc)

        return cleaned_data


class IEPeriodicTaskAdmin(PeriodicTaskAdmin, ImportExportModelAdmin):
    # most / all time schedule functions in celery beat are moot. So the code below likely makes no sense.

    list_display = (
        "name_safe",
        "enabled",
        "interval",
        "crontab",
        "next",
        "due",
        "precise",
        "last_run_at",
        "queue",
        "task",
        "args",
        "last_run",
        "runs",
    )

    list_filter = ("enabled", "queue", "crontab")

    search_fields = ("name", "queue", "args")

    form = MyPeriodicTaskForm

    save_as = True

    @staticmethod
    def name_safe(obj):
        return mark_safe(only_alphanumeric(obj.name))  # nosec

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

        # y in seconds
        _, y_in_seconds = obj.schedule.is_due(last_run_at=datetime.now(timezone.utc))
        date = datetime.now(timezone.utc) + timedelta(seconds=y_in_seconds)

        return naturaltime(date)

    @staticmethod
    def precise(obj):
        if obj.last_run_at:
            return obj.schedule.remaining_estimate(last_run_at=obj.last_run_at)

        return obj.schedule.remaining_estimate(last_run_at=datetime.now(timezone.utc))

    @staticmethod
    def next(obj):
        if obj.last_run_at:
            return obj.schedule.remaining_estimate(last_run_at=obj.last_run_at)

        # y in seconds
        _, y_in_seconds = obj.schedule.is_due(last_run_at=datetime.now(timezone.utc))
        # somehow the cron jobs still give the correct countdown even last_run_at is not set.

        date = datetime.now(timezone.utc) + timedelta(seconds=y_in_seconds)

        return date

    class Meta:  # pylint: disable=too-few-public-methods
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
    verbose_name_plural = "Dashboard Users"


# Thank you:
# https://stackoverflow.com/questions/47941038/how-should-i-add-django-import-export-on-the-user-model?rq=1
class UserResource(resources.ModelResource):
    class Meta:  # pylint: disable=too-few-public-methods
        model = User
        # fields = ('first_name', 'last_name', 'email')


class GroupResource(resources.ModelResource):
    class Meta:  # pylint: disable=too-few-public-methods
        model = Group


class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    inlines = (DashboardUserInline,)

    list_display = (
        "username",
        "in_account",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
    )

    list_filter = ["is_active", "is_staff", "is_superuser"][::-1]

    search_fields = ["username", "dashboarduser__account__name", "dashboarduser__account__internet_nl_api_username"]

    @staticmethod
    def in_account(obj):
        user = DashboardUser.objects.all().filter(user=obj).first()

        if not user:
            return "-"

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
        super().__init__(*args, **kwargs)
        # ... do stuff to make your settings form nice ...


class ConfigAdmin(ConstanceAdmin):
    change_list_form = CustomConfigForm
    change_list_template = "admin/config/settings.html"


admin.site.unregister([Config])
admin.site.register([Config], ConfigAdmin)


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = CustomAccountModelForm

    list_display = ("name", "internet_nl_api_username", "can_connect_to_internet_nl_api", "no_of_users")
    search_fields = ("name", "can_connect_to_internet_nl_api")
    # list_filter = [][::-1]
    fields = ("name", "report_settings", "internet_nl_api_username", "new_password")

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
        return mark_safe(
            f"<a href='/admin/auth/user/?q={only_alphanumeric(obj.name)}#/tab/inline_0/'>"  # nosec
            f"🔎 {DashboardUser.objects.all().filter(account=obj).count()}"
        )

    def save_model(self, request, obj, form, change):

        # If the internet_nl_api_password changed, encrypt the new value.
        # Example usage and docs: https://github.com/pyca/cryptography
        if "new_password" in form.changed_data:
            obj.internet_nl_api_password = Account.encrypt_password(form.cleaned_data.get("new_password"))

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
    check_api_connectivity.short_description = "Check API credentials"  # type: ignore
    actions.append("check_api_connectivity")


@admin.register(UrlList)
class UrlListAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = (
        "pk",
        "name",
        "account",
        "scan_type",
        "no_of_urls",
        "no_of_endpoints",
        "automated_scan_frequency",
        "last_manual_scan",
        "is_deleted",
        "is_scan_now_available",
    )
    search_fields = ("name", "account__name")
    list_filter = [
        "account",
        "is_deleted",
        "scan_type",
        "enable_scans",
        "automated_scan_frequency",
        "last_manual_scan",
    ][::-1]

    # we don't add the urls as that might cause a deletion by mistake
    fields = (
        "name",
        "account",
        "scan_type",
        "enable_scans",
        "automated_scan_frequency",
        "scheduled_next_scan",
        "last_manual_scan",
        "is_deleted",
        "deleted_on",
        "enable_report_sharing_page",
        "automatically_share_new_reports",
        "default_public_share_code_for_new_reports",
    )

    @staticmethod
    def no_of_urls(obj):
        return Url.objects.all().filter(urls_in_dashboard_list_2=obj, is_dead=False, not_resolvable=False).count()

    @staticmethod
    def no_of_endpoints(obj):
        return (
            Endpoint.objects.all()
            .filter(url__urls_in_dashboard_list_2=obj, is_dead=False, url__is_dead=False, url__not_resolvable=False)
            .count()
        )

    actions = []

    def scan_urllist_now(self, request, queryset):
        feedback = ""
        for urllist in queryset:
            feedback += repr(f"List #{urllist.pk}: {scan_urllist_now_ignoring_business_rules(urllist)} ")

        self.message_user(request, feedback)

    # suppressing error: "Callable[[Any, Any, Any], Any]" has no attribute "short_description"
    # This comes from the manual... so, well.
    scan_urllist_now.short_description = "Scan now (bypassing quota and business rules)"  # type: ignore
    actions.append("scan_urllist_now")


@admin.register(TaggedUrlInUrllist)
class TaggedUrlInUrllistAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ("url", "urllist")
    fields = ("url", "urllist", "tags")


class InternetNLV2StateLogInline(nested_admin.NestedTabularInline):  # pylint: disable=no-member too-few-public-methods
    model = InternetNLV2StateLog
    can_delete = False

    readonly_fields = ("state", "state_message", "last_state_check", "at_when")

    def has_add_permission(self, *args, **kwargs):
        return False


class AccountInternetNLScanLogInl(nested_admin.NestedTabularInline):  # pylint: disable=no-member too-few-public-methods
    model = AccountInternetNLScanLog
    can_delete = False
    # readonly_fields = ('scan', 'account', 'urllist', 'log')
    readonly_fields = ("state", "at_when")
    # todo: restrict any form of editing and creating things here.

    def has_add_permission(self, *args, **kwargs):
        return False


class AccountInternetNLScanInline(nested_admin.NestedTabularInline):  # pylint: disable=no-member too-few-public-methods
    model = AccountInternetNLScan
    can_delete = False
    inlines = [AccountInternetNLScanLogInl]

    readonly_fields = ("account", "urllist", "report", "state", "started_on", "finished_on", "state_changed_on")

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(AccountInternetNLScan)
class AccountInternetNLScanAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # prefetch account, scan and urllist, as loading this takes ages because of subqueries.
        qs = qs.select_related("account", "urllist", "scan")

        # this column prevents loading of long lists
        qs = qs.defer("scan__subject_urls", "scan__retrieved_scan_report", "scan__retrieved_scan_report_technical")

        return qs

    inlines = [AccountInternetNLScanLogInl]

    list_display = (
        "id",
        "account",
        "account__name",
        "state",
        "internetnl_scan",
        "internetnl_scan_type",
        "urllist",
        "started_on",
        "finished_on",
        "report",
    )

    list_filter = ["account", "urllist", "state", "started_on", "finished_on"][::-1]
    search_fields = ("urllist__name", "account__name")

    fields = ("state", "state_changed_on", "account", "scan", "urllist", "started_on", "finished_on")

    readonly_fields = ("account", "scan", "urllist")

    @staticmethod
    def account__name(obj):
        return obj.account.internet_nl_api_username

    @staticmethod
    def internetnl_scan(obj):
        return obj.scan.id

    @staticmethod
    def internetnl_scan_type(obj):
        return obj.scan.type

    actions = []

    def attempt_rollback(self, request, queryset):
        for scan in queryset:
            recover_and_retry.apply_async([scan.id])
        self.message_user(request, "Rolling back asynchronously. May take a while.")

    attempt_rollback.short_description = "Attempt rollback (async)"  # type: ignore
    actions.append("attempt_rollback")

    def progress_scan(self, request, queryset):
        log.debug("Attempting to progress scan.")
        for scan in queryset:
            log.debug("Progressing scan %s.", scan)
            tasks = progress_running_scan(scan.id)
            log.debug("Created task %s.", tasks)
            tasks.apply_async()
        self.message_user(request, "Attempting to progress scans (async).")

    progress_scan.short_description = "Progress scan (async)"  # type: ignore
    actions.append("progress_scan")

    def send_finish_mail(self, request, queryset):
        sent = 0
        for scan in queryset:
            if scan.finished:
                sent += 1
                send_scan_finished_mails(scan.id)
        self.message_user(request, "A total of %s mails have been sent.", sent)

    send_finish_mail.short_description = "Queue finished mail (finished only)"  # type: ignore
    actions.append("send_finish_mail")

    # This is used to create ad-hoc reports for testing the send_finish_mail function.
    def create_extra_report(self, request, queryset):
        tasks = []
        for scan in queryset:
            tasks.append(creating_report(scan.id))
        group(tasks).apply_async()
        self.message_user(request, "Creating additional reports (async).")

    create_extra_report.short_description = "Create additional report (async) (finished only)"  # type: ignore
    actions.append("create_extra_report")


class InternetNLV2ScanAdminNew(InternetNLV2ScanAdmin, nested_admin.NestedModelAdmin):  # pylint: disable=no-member
    # add some inlines to make debugging easier.

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # this column prevents loading of long lists
        qs = qs.defer("subject_urls", "retrieved_scan_report", "retrieved_scan_report_technical")

        return qs

    list_display = (
        "id",
        "type",
        "scan_id",
        "online",
        "state",
        "state_message",
        "last_state_check",
        "last_state_change",
        "account_scan",
    )

    list_filter = InternetNLV2ScanAdmin.list_filter + ()

    def account_scan(self, obj):
        account = (
            AccountInternetNLScan.objects.all()
            .filter(scan=obj)
            .only("id", "account__internet_nl_api_username", "urllist__name")
            .first()
        )
        return (
            f"{account.id} - {account.account.internet_nl_api_username} - " f"{account.urllist.name}"
            if account
            else None
        )

    inlines = [InternetNLV2StateLogInline, AccountInternetNLScanInline]


def create_modeladmin(modeladmin, model, name=None):
    # This creates a proxy model so there can be a different view on organization data.
    # In this case we can create WhoisOrganization which only allows easy overview and record editing
    # of registrar information.
    # https://stackoverflow.com/questions/2223375/multiple-modeladmins-views-for-same-model-in-django-admin
    class Meta:  # pylint: disable=too-few-public-methods
        proxy = True
        app_label = model._meta.app_label

    attrs = {"__module__": "", "Meta": Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


create_modeladmin(InternetNLV2ScanAdminNew, name="internetNlScanInspection", model=InternetNLV2Scan)


@admin.register(AccountInternetNLScanLog)
class AccountInternetNLScanLogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    paginator = TooManyRecordsPaginator

    list_display = ("id", "scan", "state", "at_when")
    list_filter = ["scan", "state", "at_when"][::-1]
    search_fields = ("scan__urllist__name", "scan__account__name")
    fields = list_display


@admin.register(UploadLog)
class UploadLogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("original_filename", "internal_filename", "status", "message", "user", "upload_date", "filesize")
    search_fields = ("internal_filename", "orginal_filename", "status")
    list_filter = ["message", "upload_date", "user"][::-1]

    fields = ("original_filename", "internal_filename", "status", "message", "user", "upload_date", "filesize")


@admin.register(models.SubdomainDiscoveryScan)
class SubdomainDiscoveryScanAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("urllist", "state", "state_changed_on", "state_message")
    fields = ("urllist", "state", "state_changed_on", "state_message", "domains_discovered")
    list_filter = ("state", "state_changed_on", "state_message")


@admin.register(models.UrlListReport)
class UrlListReportAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    @staticmethod
    def inspect_list(obj):
        return format_html('<a href="../../internet_nl_dashboard/urllist/{id}/change">inspect</a>', id=format(obj.id))

    # do NOT load the calculation field, as that will be slow.
    # https://stackoverflow.com/questions/34774028/how-to-ignore-loading-huge-fields-in-django-admin-list-display
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # tell Django to not retrieve mpoly field from DB
        qs = qs.defer("calculation")
        return qs

    list_display = (
        "urllist",
        "average_internet_nl_score",
        "high",
        "medium",
        "low",
        "ok",
        "total_endpoints",
        "ok_endpoints",
        "is_publicly_shared",
        "is_shared_on_homepage",
        "at_when",
        "inspect_list",
    )
    search_fields = ["at_when"]
    list_filter = ["urllist", "at_when", "is_publicly_shared"][::-1]
    fields = (
        "urllist",
        "report_type",
        "is_publicly_shared",
        "is_shared_on_homepage",
        "public_report_code",
        "public_share_code",
        "at_when",
        "calculation",
        "average_internet_nl_score",
        "total_endpoints",
        "total_issues",
        "high",
        "medium",
        "low",
        "ok",
        "high_endpoints",
        "medium_endpoints",
        "low_endpoints",
        "ok_endpoints",
        "total_url_issues",
        "url_issues_high",
        "url_issues_medium",
        "url_issues_low",
        "url_ok",
        "total_endpoint_issues",
        "endpoint_issues_high",
        "endpoint_issues_medium",
        "endpoint_issues_low",
        "endpoint_ok",
        "explained_high",
        "explained_medium",
        "explained_low",
        "explained_high_endpoints",
        "explained_medium_endpoints",
        "explained_low_endpoints",
        "explained_total_url_issues",
        "explained_url_issues_high",
        "explained_url_issues_medium",
        "explained_url_issues_low",
        "explained_total_endpoint_issues",
        "explained_endpoint_issues_high",
        "explained_endpoint_issues_medium",
        "explained_endpoint_issues_low",
    )

    ordering = ["-at_when"]
    readonly_fields = ["calculation"]

    save_as = True
