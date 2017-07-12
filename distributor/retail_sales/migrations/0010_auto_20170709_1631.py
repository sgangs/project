# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-09 11:01
from __future__ import unicode_literals

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_master', '0018_auto_20170705_1443'),
        ('distributor_user', '0010_auto_20170701_1225'),
        ('retail_sales', '0009_invoice_line_item_is_tax_included'),
    ]

    operations = [
        migrations.CreateModel(
            name='return_line_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('product_name', models.CharField(max_length=200)),
                ('product_sku', models.CharField(max_length=50)),
                ('product_hsn', models.CharField(blank=True, max_length=20, null=True)),
                ('unit', models.CharField(max_length=20)),
                ('unit_multi', models.DecimalField(decimal_places=2, default=1, max_digits=5)),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('batch', models.CharField(blank=True, max_length=20, null=True)),
                ('serial_no', models.CharField(blank=True, max_length=100, null=True)),
                ('manufacturing_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('return_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('other_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('cgst_percent', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('sgst_percent', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('cgst_value', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('sgst_value', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('line_before_tax', models.DecimalField(decimal_places=2, max_digits=12)),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retailReturnLineItem_sales_master_product', to='distributor_master.Product')),
            ],
        ),
        migrations.CreateModel(
            name='sales_return',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('return_id', models.PositiveIntegerField(db_index=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('customer_name', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('customer_address', models.CharField(blank=True, max_length=200, null=True)),
                ('customer_phone_no', phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=128, null=True)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer_gender', models.CharField(blank=True, max_length=1, null=True)),
                ('customer_dob', models.DateField(blank=True, null=True)),
                ('warehouse_address', models.TextField()),
                ('warehouse_state', models.CharField(max_length=4)),
                ('warehouse_city', models.CharField(max_length=50)),
                ('warehouse_pin', models.CharField(max_length=8)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cgsttotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('sgsttotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('igsttotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retailSalesReturn_retailsales_master_retailCustomer', to='distributor_master.retail_customer')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retailSalesReturn_retailInvoice', to='retail_sales.retail_invoice')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailSalesReturn_sales_user_tenant', to='distributor_user.Tenant')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retailSalesReturn_sales_master_warehouse', to='distributor_master.Warehouse')),
            ],
        ),
        migrations.AddField(
            model_name='return_line_item',
            name='sales_return',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailReturnLineItem_salesReturn', to='retail_sales.sales_return'),
        ),
        migrations.AddField(
            model_name='return_line_item',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailReturnLineItem_sales_user_tenant', to='distributor_user.Tenant'),
        ),
    ]