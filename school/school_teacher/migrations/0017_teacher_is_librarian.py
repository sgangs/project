# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-22 17:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_teacher', '0016_auto_20170320_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_librarian',
            field=models.BooleanField(default=False),
        ),
    ]
