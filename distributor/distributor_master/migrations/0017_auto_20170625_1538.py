# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-25 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_master', '0016_auto_20170622_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]