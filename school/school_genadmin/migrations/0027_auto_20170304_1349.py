# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_genadmin', '0026_auto_20170301_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='end_year',
            field=models.PositiveSmallIntegerField(verbose_name='Batch Ending Year'),
        ),
        migrations.AlterField(
            model_name='batch',
            name='start_year',
            field=models.PositiveSmallIntegerField(verbose_name='Batch Starting Year'),
        ),
    ]
