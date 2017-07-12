# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-10 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_inventory', '0010_auto_20170710_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initial_inventory',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='purchase_quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='quantity_available',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory_ledger',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory_reserve',
            name='quantity_reserve',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory_transfer_items',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='inventory_wastage',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
    ]
