# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-27 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_account', '0005_tax_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal_entry',
            name='activity_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Debit'), (2, 'Credit')], null=True, verbose_name='Activity Type'),
        ),
    ]
