# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-23 14:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distribution_accounts', '0017_auto_20161023_1005'),
        ('distribution_purchase', '0005_debitnote_debitnotelinedetails_debitnotelineitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasepayment',
            name='cheque_rtgs_number',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='purchasepayment',
            name='payment_mode',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='purchasePayment_purchaseInvoice', to='distribution_accounts.paymentMode'),
            preserve_default=False,
        ),
    ]
