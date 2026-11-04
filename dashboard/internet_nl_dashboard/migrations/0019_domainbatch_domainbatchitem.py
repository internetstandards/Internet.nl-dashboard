import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("internet_nl_dashboard", "0018_alter_accountinternetnlscan_scan_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DomainBatch",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target_list", models.BooleanField(default=False)),
                ("source", models.CharField(default="text", max_length=20)),
                ("filename", models.CharField(blank=True, max_length=255)),
                ("file_path", models.TextField(blank=True)),
                ("raw_text", models.TextField(blank=True)),
                ("stage", models.CharField(default="validation", max_length=20)),
                ("status", models.CharField(db_index=True, default="queued", max_length=20)),
                ("message", models.TextField(blank=True)),
                ("total", models.PositiveIntegerField(default=0)),
                ("processed", models.PositiveIntegerField(default=0)),
                ("worker_token", models.CharField(blank=True, max_length=36)),
                ("created_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_on", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "account",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.account"),
                ),
                (
                    "urllist",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="internet_nl_dashboard.urllist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="internet_nl_dashboard.dashboarduser"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DomainBatchItem",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveIntegerField()),
                ("row", models.PositiveIntegerField()),
                ("list_name", models.TextField()),
                ("raw_domain", models.TextField()),
                ("domain", models.CharField(blank=True, max_length=255)),
                ("tags", models.JSONField(default=list)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("reason", models.CharField(blank=True, max_length=255)),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="internet_nl_dashboard.domainbatch",
                    ),
                ),
            ],
            options={
                "indexes": [models.Index(fields=["batch", "status", "position"], name="domain_batch_work")],
                "constraints": [models.UniqueConstraint(fields=("batch", "position"), name="domain_batch_position")],
            },
        ),
    ]
