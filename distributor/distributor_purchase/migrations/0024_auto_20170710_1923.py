# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-10 13:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0023_auto_20170710_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debit_note_line_item',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='receipt_line_item',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
    ]
