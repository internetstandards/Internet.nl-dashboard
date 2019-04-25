# Generated by Django 2.2 on 2019-04-25 09:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internet_nl_dashboard', '0020_auto_20190412_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='urllist',
            name='automated_scan_frequency',
            field=models.CharField(choices=[('disabled', 'disabled'), ('every half year', 'every half year'), ('at the start of every quarter', 'at the start of every quarter'), (
                'every 1st day of the month', 'every 1st day of the month'), ('twice per month', 'twice per month')], default='disabled', help_text='At what moment should the scan start?', max_length=30),
        ),
        migrations.AddField(
            model_name='urllist',
            name='scheduled_next_scan',
            field=models.DateTimeField(default=django.utils.timezone.now,
                                       help_text='An indication at what moment the scan will be started. The scan can take a while, thus this does not tell you when a scan will be finished.'),
            preserve_default=False,
        ),
    ]