# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-04 01:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20161222_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduler',
            name='last_alerted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scheduler',
            name='last_scheduled',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]