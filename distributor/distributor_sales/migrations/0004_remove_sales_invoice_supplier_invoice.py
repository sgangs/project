# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-26 14:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_sales', '0003_invoice_line_item_unit_multi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sales_invoice',
            name='supplier_invoice',
        ),
    ]
