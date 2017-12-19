# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-26 08:05
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_user', '0018_user_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_permission',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='user_permission',
            name='user',
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, null=True, size=None),
        ),
        migrations.DeleteModel(
            name='user_permission',
        ),
    ]