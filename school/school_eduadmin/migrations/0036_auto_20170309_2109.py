# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 15:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_eduadmin', '0035_auto_20170304_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='period_from',
            field=models.DateField(blank=True, null=True, verbose_name='Exam Class Starts'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='period_to',
            field=models.DateField(blank=True, null=True, verbose_name='Exam Class Ends'),
        ),
    ]
