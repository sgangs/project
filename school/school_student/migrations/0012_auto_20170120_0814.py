# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-20 02:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_student', '0011_auto_20170106_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_student_genadmin_batch', to='school_genadmin.Batch'),
        ),
    ]
