# Generated by Django 2.0.3 on 2018-03-21 12:01
from pathlib import PurePath

from django.core.management import call_command
from django.db import migrations, models
import django.db.models.deletion
import uuid


def load_initial_metadata(yaml_file_name):
    def inner(apps, schema_editor):
        call_command(
            'loaddata',
            PurePath(__file__).parent / yaml_file_name
        )
    return inner

load_initial_policy_area = load_initial_metadata('0024_policy_area.yaml')
load_initial_policy_issue_type = load_initial_metadata('0024_issue_type.yaml')


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0023_add_net_company_receipt'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyArea',
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
        migrations.CreateModel(
            name='PolicyIssueType',
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
            name='policy_area',
            field=models.ForeignKey(blank=True, help_text='For policy feedback only.', null=True, on_delete=django.db.models.deletion.PROTECT, to='interaction.PolicyArea'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='policy_issue_type',
            field=models.ForeignKey(blank=True, help_text='For policy feedback only.', null=True, on_delete=django.db.models.deletion.PROTECT, to='interaction.PolicyIssueType'),
        ),
        migrations.RunPython(load_initial_policy_area, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(load_initial_policy_issue_type, reverse_code=migrations.RunPython.noop)
    ]