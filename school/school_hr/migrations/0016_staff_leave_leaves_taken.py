# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-25 11:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_hr', '0015_auto_20170325_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_leave',
            name='leaves_taken',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
