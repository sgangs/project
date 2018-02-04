# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-22 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_sales', '0037_sales_return_return_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales_invoice',
            name='return_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
