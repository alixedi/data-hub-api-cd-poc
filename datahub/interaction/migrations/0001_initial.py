# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-01 15:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('metadata', '0004_servicedeliverystatus'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0012_auto_20170201_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('archived', models.BooleanField(default=False)),
                ('archived_on', models.DateTimeField(null=True)),
                ('archived_reason', models.TextField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('subject', models.TextField()),
                ('notes', models.TextField(max_length=4000)),
                ('archived_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='company.Company')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='company.Contact')),
                ('dit_advisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL)),
                ('dit_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Team')),
                ('interaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.InteractionType')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Service')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, ),
        ),
        migrations.CreateModel(
            name='ServiceDelivery',
            fields=[
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('archived', models.BooleanField(default=False)),
                ('archived_on', models.DateTimeField(null=True)),
                ('archived_reason', models.TextField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('subject', models.TextField()),
                ('notes', models.TextField(max_length=4000)),
                ('archived_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicedeliverys', to='company.Company')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicedeliverys', to='company.Contact')),
                ('country_of_interest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.Country')),
                ('dit_advisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicedeliverys', to=settings.AUTH_USER_MODEL)),
                ('dit_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Team')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.Sector')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Service')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, ),
        ),
        migrations.CreateModel(
            name='ServiceOffer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('dit_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Team')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.Service')),
            ],
        ),
        migrations.AddField(
            model_name='servicedelivery',
            name='service_offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='interaction.ServiceOffer'),
        ),
        migrations.AddField(
            model_name='servicedelivery',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.ServiceDeliveryStatus'),
        ),
        migrations.AddField(
            model_name='servicedelivery',
            name='uk_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.UKRegion'),
        ),
    ]
