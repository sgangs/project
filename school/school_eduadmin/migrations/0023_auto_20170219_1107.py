# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 05:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_eduadmin', '0022_auto_20170219_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
