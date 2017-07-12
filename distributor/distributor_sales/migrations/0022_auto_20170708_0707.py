# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-08 01:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_sales', '0021_invoice_line_item_quantity_returned'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales_invoice',
            name='gst_type',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='sales_invoice',
            name='is_b2b_registered',
            field=models.BooleanField(default=True),
        ),
    ]
