# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-06 07:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_sales', '0020_auto_20170706_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice_line_item',
            name='quantity_returned',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
