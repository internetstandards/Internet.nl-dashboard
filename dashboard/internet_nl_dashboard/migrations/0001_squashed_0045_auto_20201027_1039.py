# Generated by Django 3.1.6 on 2021-07-04 12:54

import datetime

import django.db.models.deletion
import django_countries.fields
import jsonfield.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("internet_nl_dashboard", "0001_initial"),
        ("internet_nl_dashboard", "0002_auto_20190318_1656"),
        ("internet_nl_dashboard", "0003_uploadlog"),
        ("internet_nl_dashboard", "0004_uploadlog_user"),
        ("internet_nl_dashboard", "0005_auto_20190320_1454"),
        ("internet_nl_dashboard", "0006_uploadlog_status"),
        ("internet_nl_dashboard", "0007_remove_account_enable_logins"),
        ("internet_nl_dashboard", "0008_auto_20190325_1721"),
        ("internet_nl_dashboard", "0009_accountinternetnlscan"),
        ("internet_nl_dashboard", "0010_auto_20190326_0957"),
        ("internet_nl_dashboard", "0011_auto_20190326_1013"),
        ("internet_nl_dashboard", "0012_account_can_connect_to_internet_nl_api"),
        ("internet_nl_dashboard", "0013_auto_20190326_1224"),
        ("internet_nl_dashboard", "0014_accountinternetnlscan_urllist"),
        ("internet_nl_dashboard", "0015_auto_20190329_1325"),
        ("internet_nl_dashboard", "0016_auto_20190401_1626"),
        ("internet_nl_dashboard", "0017_urllist_scan_type"),
        ("internet_nl_dashboard", "0018_auto_20190402_1554"),
        ("internet_nl_dashboard", "0019_urllistreport_created_on"),
        ("internet_nl_dashboard", "0020_auto_20190412_1157"),
        ("internet_nl_dashboard", "0021_auto_20190425_0910"),
        ("internet_nl_dashboard", "0022_auto_20190425_1438"),
        ("internet_nl_dashboard", "0023_auto_20190429_0910"),
        ("internet_nl_dashboard", "0024_auto_20190429_0923"),
        ("internet_nl_dashboard", "0025_auto_20190430_1021"),
        ("internet_nl_dashboard", "0026_auto_20190430_1452"),
        ("internet_nl_dashboard", "0027_auto_20190507_1233"),
        ("internet_nl_dashboard", "0028_auto_20190507_1509"),
        ("internet_nl_dashboard", "0029_auto_20190515_1206"),
        ("internet_nl_dashboard", "0030_auto_20190515_1209"),
        ("internet_nl_dashboard", "0031_account_report_settings"),
        ("internet_nl_dashboard", "0032_auto_20190528_1352"),
        ("internet_nl_dashboard", "0033_auto_20190604_1242"),
        ("internet_nl_dashboard", "0034_auto_20190613_0946"),
        ("internet_nl_dashboard", "0035_auto_20190624_0712"),
        ("internet_nl_dashboard", "0036_urllistreport_average_internet_nl_score"),
        ("internet_nl_dashboard", "0037_auto_20191121_1408"),
        ("internet_nl_dashboard", "0038_accountinternetnlscan_state_changed_on"),
        ("internet_nl_dashboard", "0039_accountinternetnlscan_report"),
        ("internet_nl_dashboard", "0040_auto_20200508_1013"),
        ("internet_nl_dashboard", "0041_auto_20200513_1351"),
        ("internet_nl_dashboard", "0042_auto_20200530_1735"),
        ("internet_nl_dashboard", "0043_auto_20201006_1309"),
        ("internet_nl_dashboard", "0044_dashboarduser_mail_after_mail_unsubscribe_code"),
        ("internet_nl_dashboard", "0045_auto_20201027_1039"),
    ]

    initial = True

    dependencies = [
        ("scanners", "0060_auto_20190116_0937"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("scanners", "0072_auto_20200506_1313"),
        ("organizations", "0053_url_do_not_find_subdomains"),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "internet_nl_api_username",
                    models.CharField(blank=True, help_text="Internet.nl API Username", max_length=255, null=True),
                ),
                (
                    "internet_nl_api_password",
                    models.TextField(blank=True, help_text="New values will automatically be encrypted.", null=True),
                ),
                ("enable_scans", models.BooleanField(default=True)),
                ("can_connect_to_internet_nl_api", models.BooleanField(default=False)),
                (
                    "report_settings",
                    jsonfield.fields.JSONField(
                        blank=True,
                        help_text="This stores reporting preferences: what fields are shown in the UI and so on (if any other).This field can be edited on the report page.",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DashboardUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notes", models.TextField(blank=True, max_length=800, null=True)),
                (
                    "account",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.account"),
                ),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                ("mail_preferred_language", django_countries.fields.CountryField(default="EN", max_length=2)),
                (
                    "mail_preferred_mail_address",
                    models.EmailField(
                        blank=True,
                        help_text="This address can deviate from the account mail address for password resets and other account features.",
                        max_length=254,
                        null=True,
                    ),
                ),
                (
                    "mail_send_mail_after_scan_finished",
                    models.BooleanField(
                        default=False,
                        help_text="After a scan is finished, an e-mail is sent informing the user that a report is ready.",
                    ),
                ),
                (
                    "mail_after_mail_unsubscribe_code",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="This is autofilled when sending an e-mail. The user can use this code to set mail_send_mail_after_scan_finished to false without logging in.",
                        max_length=255,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UploadLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "original_filename",
                    models.CharField(
                        blank=True,
                        help_text="The original filename of the file that has been uploaded. Django appends a random string if the file already exists. This is a reconstruction of the original filename and may not be 100% accurate.",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "internal_filename",
                    models.CharField(
                        blank=True,
                        help_text="Generated filename by Django. This can be used to find specific files for debugging purposes.",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "message",
                    models.CharField(
                        blank=True,
                        help_text="This message gives more specific information about what happened. For example, it might be the case that a file has been rejected because it had the wrong filetype etc.",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("upload_date", models.DateTimeField(blank=True, null=True)),
                (
                    "filesize",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Gives an indication if your local file has changed (different size). The size is in bytes.",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="What user performed this upload.",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="internet_nl_dashboard.dashboarduser",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        help_text="If the upload was successful or not. Might contain 'success' or 'error'.",
                        max_length=255,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UrlList",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the UrlList, for example name of the organization in it.", max_length=120
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        help_text="Who owns and manages this urllist.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="internet_nl_dashboard.account",
                    ),
                ),
                (
                    "urls",
                    models.ManyToManyField(blank=True, related_name="urls_in_dashboard_list", to="organizations.Url"),
                ),
                ("enable_scans", models.BooleanField(default=True)),
                (
                    "scan_type",
                    models.CharField(choices=[("web", "web"), ("mail", "mail")], default="web", max_length=4),
                ),
                (
                    "automated_scan_frequency",
                    models.CharField(
                        choices=[
                            ("disabled", "disabled"),
                            ("every half year", "every half year"),
                            ("at the start of every quarter", "at the start of every quarter"),
                            ("every 1st day of the month", "every 1st day of the month"),
                            ("twice per month", "twice per month"),
                        ],
                        default="disabled",
                        help_text="At what moment should the scan start?",
                        max_length=30,
                    ),
                ),
                (
                    "scheduled_next_scan",
                    models.DateTimeField(
                        default=datetime.datetime(2030, 1, 1, 1, 1, 1, 601526, tzinfo=datetime.timezone.utc),
                        help_text="An indication at what moment the scan will be started. The scan can take a while, thus this does not tell you when a scan will be finished. All dates in the past will be scanned and updated.",
                    ),
                ),
                ("deleted_on", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("last_manual_scan", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="UrlListReport",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_issues", models.IntegerField(default=0)),
                ("high", models.IntegerField(default=0)),
                ("medium", models.IntegerField(default=0)),
                ("low", models.IntegerField(default=0)),
                ("ok", models.IntegerField(default=0)),
                ("total_urls", models.IntegerField(default=0, help_text="Amount of urls for this organization.")),
                (
                    "high_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) high risk issues."),
                ),
                (
                    "medium_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) medium risk issues."),
                ),
                (
                    "low_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) low risk issues."),
                ),
                ("ok_urls", models.IntegerField(default=0, help_text="Amount of urls with zero issues.")),
                ("total_endpoints", models.IntegerField(default=0, help_text="Amount of endpoints for this url.")),
                (
                    "high_endpoints",
                    models.IntegerField(default=0, help_text="Amount of endpoints with (1 or more) high risk issues."),
                ),
                (
                    "medium_endpoints",
                    models.IntegerField(
                        default=0, help_text="Amount of endpoints with (1 or more) medium risk issues."
                    ),
                ),
                (
                    "low_endpoints",
                    models.IntegerField(default=0, help_text="Amount of endpoints with (1 or more) low risk issues."),
                ),
                ("ok_endpoints", models.IntegerField(default=0, help_text="Amount of endpoints with zero issues.")),
                ("total_url_issues", models.IntegerField(default=0, help_text="Total amount of issues on url level.")),
                ("url_issues_high", models.IntegerField(default=0, help_text="Number of high issues on url level.")),
                (
                    "url_issues_medium",
                    models.IntegerField(default=0, help_text="Number of medium issues on url level."),
                ),
                ("url_issues_low", models.IntegerField(default=0, help_text="Number of low issues on url level.")),
                ("url_ok", models.IntegerField(default=0, help_text="Zero issues on these urls.")),
                (
                    "total_endpoint_issues",
                    models.IntegerField(
                        default=0,
                        help_text="A sum of all endpoint issues for this endpoint, it includes all high, medium and lows.",
                    ),
                ),
                (
                    "endpoint_issues_high",
                    models.IntegerField(default=0, help_text="Total amount of high risk issues on this endpoint."),
                ),
                (
                    "endpoint_issues_medium",
                    models.IntegerField(default=0, help_text="Total amount of medium risk issues on this endpoint."),
                ),
                (
                    "endpoint_issues_low",
                    models.IntegerField(default=0, help_text="Total amount of low risk issues on this endpoint"),
                ),
                (
                    "endpoint_ok",
                    models.IntegerField(
                        default=0, help_text="Amount of measurements that resulted in an OK score on this endpoint."
                    ),
                ),
                (
                    "explained_total_issues",
                    models.IntegerField(default=0, help_text="The summed number of all vulnerabilities and failures."),
                ),
                (
                    "explained_high",
                    models.IntegerField(default=0, help_text="The number of high risk vulnerabilities and failures."),
                ),
                (
                    "explained_medium",
                    models.IntegerField(default=0, help_text="The number of medium risk vulnerabilities and failures."),
                ),
                (
                    "explained_low",
                    models.IntegerField(default=0, help_text="The number of low risk vulnerabilities and failures."),
                ),
                (
                    "explained_total_urls",
                    models.IntegerField(default=0, help_text="Amount of urls for this organization."),
                ),
                (
                    "explained_high_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) high risk issues."),
                ),
                (
                    "explained_medium_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) medium risk issues."),
                ),
                (
                    "explained_low_urls",
                    models.IntegerField(default=0, help_text="Amount of urls with (1 or more) low risk issues."),
                ),
                (
                    "explained_total_endpoints",
                    models.IntegerField(default=0, help_text="Amount of endpoints for this url."),
                ),
                (
                    "explained_high_endpoints",
                    models.IntegerField(default=0, help_text="Amount of endpoints with (1 or more) high risk issues."),
                ),
                (
                    "explained_medium_endpoints",
                    models.IntegerField(
                        default=0, help_text="Amount of endpoints with (1 or more) medium risk issues."
                    ),
                ),
                (
                    "explained_low_endpoints",
                    models.IntegerField(default=0, help_text="Amount of endpoints with (1 or more) low risk issues."),
                ),
                (
                    "explained_total_url_issues",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_url_issues_high",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_url_issues_medium",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_url_issues_low",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_total_endpoint_issues",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_endpoint_issues_high",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_endpoint_issues_medium",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                (
                    "explained_endpoint_issues_low",
                    models.IntegerField(default=0, help_text="Total amount of issues on endpoint level."),
                ),
                ("at_when", models.DateTimeField(db_index=True)),
                (
                    "calculation",
                    jsonfield.fields.JSONField(
                        help_text="Contains JSON with a calculation of all scanners at this moment, for all urls of this organization. This can be a lot."
                    ),
                ),
                (
                    "urllist",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.urllist"),
                ),
                (
                    "endpoint_not_applicable",
                    models.IntegerField(
                        default=0, help_text="Amount of things that are not applicable on this endpoint."
                    ),
                ),
                (
                    "endpoint_not_testable",
                    models.IntegerField(
                        default=0, help_text="Amount of things that could not be tested on this endpoint."
                    ),
                ),
                ("not_applicable", models.IntegerField(default=0)),
                ("not_testable", models.IntegerField(default=0)),
                (
                    "url_not_applicable",
                    models.IntegerField(default=0, help_text="Amount of things that are not applicable on this url."),
                ),
                (
                    "url_not_testable",
                    models.IntegerField(default=0, help_text="Amount of things that could not be tested on this url."),
                ),
                (
                    "average_internet_nl_score",
                    models.FloatField(
                        default=0,
                        help_text="Internet.nl scores are retrieved in point. The calculation done for that is complex and subject to change over time. Therefore it is impossible to re-calculate that score here.Instead the score is stored as a given.",
                    ),
                ),
                (
                    "endpoint_error_in_test",
                    models.IntegerField(default=0, help_text="Amount of errors in tests performed on this endpoint."),
                ),
                ("error_in_test", models.IntegerField(default=0)),
                (
                    "url_error_in_test",
                    models.IntegerField(default=0, help_text="Amount of errors in tests on this url."),
                ),
            ],
            options={
                "get_latest_by": "at_when",
                "index_together": {("at_when", "id")},
            },
        ),
        migrations.CreateModel(
            name="AccountInternetNLScan",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "account",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.account"),
                ),
                (
                    "scan",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to="scanners.internetnlv2scan"
                    ),
                ),
                (
                    "urllist",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.urllist"),
                ),
                ("state", models.CharField(blank=True, default="", help_text="The current state", max_length=255)),
                ("state_changed_on", models.DateTimeField(blank=True, null=True)),
                (
                    "report",
                    models.ForeignKey(
                        blank=True,
                        help_text="After a scan has finished, a report is created. This points to that report so no guessing is needed to figure out what report belongs to what scan.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="internet_nl_dashboard.urllistreport",
                    ),
                ),
                ("finished_on", models.DateTimeField(blank=True, null=True)),
                ("started_on", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="AccountInternetNLScanLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The state that was registered at a certain moment in time.",
                        max_length=255,
                    ),
                ),
                ("at_when", models.DateTimeField(blank=True, null=True)),
                (
                    "scan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.accountinternetnlscan"
                    ),
                ),
            ],
        ),
    ]
