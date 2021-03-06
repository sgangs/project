# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-15 12:53
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('retail_sales', '0013_auto_20170913_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice_line_item',
            name='product_hsn',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='retail_invoice',
            name='customer_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='retail_invoice',
            name='customer_phone_no',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='sales_return',
            name='customer_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='sales_return',
            name='customer_phone_no',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
    ]
