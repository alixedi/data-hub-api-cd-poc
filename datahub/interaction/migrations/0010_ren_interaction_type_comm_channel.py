# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-02 09:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0009_add_interaction_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interaction',
            old_name='interaction_type',
            new_name='communication_channel',
        ),
    ]
