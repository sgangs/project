# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-12 04:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_user', '0009_auto_20170123_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
