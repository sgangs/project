# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-06 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_user', '0002_auto_20170517_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='maintain_inventory',
            field=models.BooleanField(default=True, verbose_name='Do you want to maintain inventory'),
        ),
    ]
