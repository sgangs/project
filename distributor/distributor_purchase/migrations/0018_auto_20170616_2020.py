# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-16 14:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0017_auto_20170616_1801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment_line_item',
            name='purchase_payment',
        ),
        migrations.RemoveField(
            model_name='payment_line_item',
            name='purchase_receipt',
        ),
        migrations.RemoveField(
            model_name='payment_line_item',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='payment_line_item',
        ),
    ]
