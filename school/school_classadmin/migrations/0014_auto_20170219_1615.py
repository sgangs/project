# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_classadmin', '0013_auto_20170219_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='exam_coscholastic_report',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='exam_report',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='homework',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
