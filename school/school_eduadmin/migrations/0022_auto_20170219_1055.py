# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 05:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_eduadmin', '0021_auto_20170219_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='name',
            field=models.CharField(db_index=True, max_length=40),
        ),
    ]
