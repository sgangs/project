# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-23 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distribution_master', '0017_auto_20161023_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subproduct',
            name='discount1',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4, null=True, verbose_name='Percent sales discount'),
        ),
        migrations.AlterField(
            model_name='subproduct',
            name='discount2',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='Sales discount in value'),
        ),
    ]
