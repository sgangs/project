# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 03:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('distributor_account', '0001_initial'),
        ('distributor_user', '0001_initial'),
        ('distributor_master', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='purchase_receipt',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('receipt_id', models.PositiveIntegerField(db_index=True)),
                ('supplier_invoice', models.CharField(blank=True, max_length=200, null=True)),
                ('vendor_name', models.CharField(db_index=True, max_length=200)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('warehouse_address', models.TextField()),
                ('grand_discount_type', models.PositiveSmallIntegerField(default=0)),
                ('grand_discount', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('taxtotal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payable_by', models.DateField(blank=True, null=True)),
                ('final_payment_date', models.DateField(blank=True, null=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseReceipt_purchase_user_tenant', to='distributor_user.Tenant')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseReceipt_purchase_master_vendor', to='distributor_master.Vendor')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchaseReceipt_purchase_master_warehouse', to='distributor_master.Warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='purchasePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cheque_rtgs_number', models.CharField(blank=True, max_length=30, null=True)),
                ('paid_on', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('final_payment_delay', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('payment_mode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasePayment_purchase_accounts_paymentMode', to='distributor_account.payment_mode')),
                ('purchase_receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasePayment_purchaseReceipt', to='distributor_purchase.purchase_receipt')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchasePayment_purchase_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='receiptLineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('product_sku', models.CharField(max_length=50)),
                ('vat_type', models.CharField(max_length=15)),
                ('unit', models.CharField(max_length=20)),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('free_without_tax', models.PositiveSmallIntegerField(default=0)),
                ('free_with_tax', models.PositiveSmallIntegerField(default=0)),
                ('batch', models.CharField(blank=True, max_length=20, null=True)),
                ('serial_no', models.CharField(blank=True, max_length=100, null=True)),
                ('manufacturing_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tentative_sales_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('mrp', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='MRP')),
                ('discount_type', models.PositiveSmallIntegerField(default=0)),
                ('discount_value', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiptLineItem_purchase_master_product', to='distributor_master.Product')),
                ('purchase_receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiptLineItem_purchaseReceipt', to='distributor_purchase.purchase_receipt')),
                ('tax', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiptLineItem_purchase_master_taxStructure', to='distributor_master.tax_structure')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiptLineItem_purchase_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
    ]
