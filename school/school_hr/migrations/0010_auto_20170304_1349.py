# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_hr', '0009_auto_20170224_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher_attendance',
            name='is_authorized',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='teacher_attendance',
            name='date',
            field=models.DateField(db_index=True),
        ),
    ]
