# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_student', '0020_remove_student_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='key',
            field=models.CharField(db_index=True, max_length=32),
        ),
    ]
