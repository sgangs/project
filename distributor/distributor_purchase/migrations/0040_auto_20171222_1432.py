# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-22 09:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_purchase', '0039_auto_20171011_1757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debit_note_line_item',
            name='tax_percent',
        ),
        migrations.RemoveField(
            model_name='debit_note_line_item',
            name='vat_type',
        ),
    ]
