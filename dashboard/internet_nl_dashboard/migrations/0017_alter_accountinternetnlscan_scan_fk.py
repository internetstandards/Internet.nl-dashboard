import django.db.models.deletion
from django.db import migrations, models


def clean_invalid_scan_references(apps, schema_editor):
    """Drop scan references that cannot point to an existing Internet.nl scan."""
    table = "internet_nl_dashboard_accountinternetnlscan"
    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name for column in schema_editor.connection.introspection.get_table_description(cursor, table)
        }
    if "scan_id" in columns:
        column_name = "scan_id"
    elif "scan" in columns:
        column_name = "scan"
    else:
        return

    quoted_table = schema_editor.quote_name(table)
    quoted_column = schema_editor.quote_name(column_name)
    scans_table = schema_editor.quote_name("scanners_internetnlv2scan")

    sql = f"""
        UPDATE {quoted_table}
        SET {quoted_column} = NULL
        WHERE {quoted_column} IS NOT NULL
          AND {quoted_column} NOT IN (SELECT id FROM {scans_table})
    """
    schema_editor.execute(sql)


class Migration(migrations.Migration):
    """Ensure AccountInternetNLScan.scan links to the external Internet.nl scan model."""

    dependencies = [
        ("internet_nl_dashboard", "0016_alter_accountinternetnlscan_scan"),
        ("scanners_internet_nl_web", "0001_initial"),
    ]

    operations = [
        # migrations.RunPython(clean_invalid_scan_references, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="accountinternetnlscan",
            name="scan",
            field=models.ForeignKey(
                db_column="scan_id",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="scanners_internet_nl_web.internetnlv2scan",
            ),
        ),
    ]
