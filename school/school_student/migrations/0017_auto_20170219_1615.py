# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_student', '0016_auto_20170209_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='student_education',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='student_guardian',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
