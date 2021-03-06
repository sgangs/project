# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 07:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase_receipt',
            name='vendor_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='vendor_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='vendor_pin',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='vendor_state',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='warehouse_city',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='warehouse_pin',
            field=models.CharField(default=1, max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase_receipt',
            name='warehouse_state',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
    ]
