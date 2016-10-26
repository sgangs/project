# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-23 20:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution_purchase', '0006_auto_20161023_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasepayment',
            name='payment_mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasePayment_purchase_accounts_paymentMode', to='distribution_accounts.paymentMode'),
        ),
    ]
