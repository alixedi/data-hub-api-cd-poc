# Generated by Django 2.2.1 on 2019-06-05 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0062_auto_20190405_1338'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='investmentproject',
            index=models.Index(fields=['created_on', 'id'], name='investment__created_b91445_idx'),
        ),
    ]