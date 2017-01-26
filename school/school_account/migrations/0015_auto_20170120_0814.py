# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-20 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_account', '0014_accounting_period_finalized'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(choices=[('Current Assets', 'Current Assets'), ('Long Term Assets', 'Long Term Assets'), ('Depreciation', 'Depreciation'), ('Current Liabilities', 'Current Liabilities'), ('Long Term Liabilities', 'Long Term Liabilities'), ('Revenue', 'Revenue'), ('Fees', 'Fees'), ('Indirect Revenue', 'Indirect Revenue'), ('Direct Expense', 'Direct Expense'), ('Salary', 'Salary'), ('Indirect Expense', 'Indirect Expense'), ('Equity', 'Equity')], max_length=30, verbose_name='Account type'),
        ),
    ]
