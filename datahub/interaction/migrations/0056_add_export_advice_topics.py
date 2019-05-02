# Generated by Django 2.2 on 2019-05-02 10:27
import uuid
from pathlib import PurePath

import django.db.models.deletion
from django.db import migrations, models

from datahub.core.migration_utils import load_yaml_data_in_migration


def load_initial_export_advice_topics(apps, schema_editor):
    ExportAdviceTopic = apps.get_model('interaction', 'ExportAdviceTopic')

    # only load the fixtures if there aren't any already in the database
    # this is because we don't know if they have been changed via the django admin.
    if not ExportAdviceTopic.objects.exists():
        load_yaml_data_in_migration(
            apps,
            PurePath(__file__).parent / '0056_export_advice_topics.yaml'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0055_archived_not_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportAdviceTopic',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='interaction',
            name='export_advice_topic',
            field=models.ForeignKey(blank=True, help_text='For export advice and information service only.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='interaction.ExportAdviceTopic'),
        ),
        migrations.RunPython(load_initial_export_advice_topics, migrations.RunPython.noop),
    ]
