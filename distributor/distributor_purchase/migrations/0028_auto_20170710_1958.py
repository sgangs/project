# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-10 14:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0027_auto_20170710_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt_line_item',
            name='unit_multi',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8),
        ),
    ]
