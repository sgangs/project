# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-24 04:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_teacher', '0007_teacher_class_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='local_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='School teacher ID'),
        ),
    ]
