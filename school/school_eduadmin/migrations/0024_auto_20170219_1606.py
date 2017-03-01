# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_eduadmin', '0023_auto_20170219_1107'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exam',
            options={'ordering': ('term',)},
        ),
        migrations.AlterModelOptions(
            name='term',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='term',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Term Number'),
        ),
        migrations.AlterField(
            model_name='term',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
