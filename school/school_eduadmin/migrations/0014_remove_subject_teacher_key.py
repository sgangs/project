# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-04 20:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school_eduadmin', '0013_auto_20170205_0148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject_teacher',
            name='key',
        ),
    ]
