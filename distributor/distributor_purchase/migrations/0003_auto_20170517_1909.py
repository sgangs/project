# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 13:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0002_auto_20170517_1234'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='purchasePayment',
            new_name='purchase_payment',
        ),
        migrations.RenameModel(
            old_name='receiptLineItem',
            new_name='receipt_line_item',
        ),
    ]
