# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-29 14:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_sales', '0005_auto_20170528_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice_line_item',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoiceLineItem_sales_master_product', to='distributor_master.Product'),
        ),
        migrations.AlterField(
            model_name='sales_invoice',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salesInvoice_sales_master_customer', to='distributor_master.Customer'),
        ),
        migrations.AlterField(
            model_name='sales_invoice',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salesInvoice_sales_master_warehouse', to='distributor_master.Warehouse'),
        ),
        migrations.AlterField(
            model_name='sales_payment',
            name='payment_mode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salesPayment_sales_accounts_paymentMode', to='distributor_account.payment_mode'),
        ),
    ]
