# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-04 14:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distribution_accounts', '0012_auto_20161004_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalgroup',
            name='default',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=3, verbose_name='Current Accounting Period?'),
            preserve_default=False,
        ),
    ]
