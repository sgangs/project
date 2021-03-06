# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-02 06:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_issued',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='book_issue',
            name='is_late',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='book_return',
            name='is_late',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(blank=True, db_index=True, max_length=18, null=True, verbose_name='ISBN'),
        ),
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='publisher',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='purchased_on',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='school_book_code',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='School Book Code/Key'),
        ),
    ]
