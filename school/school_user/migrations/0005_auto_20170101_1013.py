# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-01 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_user', '0004_auto_20161217_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('Master', 'Master'), ('Master Account', 'Master Account'), ('Teacher', 'Teacher'), ('Student', 'Student')], default='Master', max_length=20),
        ),
    ]
