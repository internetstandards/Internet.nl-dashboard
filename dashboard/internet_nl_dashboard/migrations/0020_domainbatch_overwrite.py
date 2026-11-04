from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("internet_nl_dashboard", "0019_domainbatch_domainbatchitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="domainbatch",
            name="overwrite",
            field=models.BooleanField(default=False),
        ),
    ]
