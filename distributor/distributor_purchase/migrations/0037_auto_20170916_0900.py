# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-16 03:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0036_auto_20170915_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_line_item',
            name='unit_id',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
