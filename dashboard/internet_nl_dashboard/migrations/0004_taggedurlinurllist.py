# Generated by Django 3.1.13 on 2021-09-08 12:29

import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('organizations', '0060_auto_20200908_1055'),
        ('internet_nl_dashboard', '0003_urllistreport_report_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaggedUrlInUrllist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.',
                                                         through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.url')),
                ('urllist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internet_nl_dashboard.urllist')),
            ],
            options={
                'db_table': 'internet_nl_dashboard_urllist_x_tagged_url',
                'unique_together': {('urllist', 'url')},
            },
        ),
    ]