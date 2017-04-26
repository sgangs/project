# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-25 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_genadmin', '0033_auto_20170407_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academic_year',
            name='year',
            field=models.PositiveSmallIntegerField(verbose_name='Academic Year: If year is 2017-18, enter 2017'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(blank=True, db_index=True, max_length=40, verbose_name='Subject Name'),
        ),
    ]
