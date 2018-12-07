# Generated by Django 2.1.3 on 2018-12-04 13:31

import django.core.validators
from django.db import migrations, models
import re


def set_duns_number_to_null(apps, schema_editor):
    Company = apps.get_model('company', 'Company')
    Company.objects.filter(duns_number='').update(duns_number=None)


def set_duns_number_to_blank(apps, schema_editor):
    Company = apps.get_model('company', 'Company')
    Company.objects.filter(duns_number__isnull=True).update(duns_number='')


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0049_populate_one_list_tier_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='duns_number',
            field=models.CharField(blank=True, help_text='Dun & Bradstreet unique identifier. Nine-digit number with leading zeros.', max_length=9, null=True, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.MaxLengthValidator(9), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z'), code='invalid', message='Enter a valid integer.')]),
        ),
        migrations.RunPython(set_duns_number_to_null, set_duns_number_to_blank, elidable=True),
    ]