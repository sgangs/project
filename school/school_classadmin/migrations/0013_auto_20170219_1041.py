# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 05:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_classadmin', '0012_auto_20170218_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam_coscholastic_report',
            name='topic',
            field=models.CharField(choices=[('Life', 'Life Skills'), ('Work', 'Work Education'), ('VPA', 'Visual & Performing Art'), ('AV', 'Attitude & Values'), ('CSA', 'Co-Scholastic Actitivies'), ('HPE', 'Health & Physical Education')], max_length=4),
        ),
    ]
