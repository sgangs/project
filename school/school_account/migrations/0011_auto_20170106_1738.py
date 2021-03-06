# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-06 12:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_account', '0010_account_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='account_year',
            name='closing_credit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='account_year',
            name='closing_debit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
