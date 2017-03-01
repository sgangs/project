# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 19:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_genadmin', '0023_auto_20170226_1724'),
        ('school_classadmin', '0017_auto_20170226_1724'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam_report',
            name='total',
        ),
        migrations.AddField(
            model_name='exam_report',
            name='year',
            field=models.PositiveSmallIntegerField(db_index=True, default=2016),
        ),
        migrations.AddField(
            model_name='exam_year_final',
            name='subject',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='examYearFinal_classadmin_genadmin_subject', to='school_genadmin.Subject'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exam_report',
            name='final_score',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterUniqueTogether(
            name='exam_year_final',
            unique_together=set([('final_report', 'subject', 'tenant')]),
        ),
        migrations.RemoveField(
            model_name='exam_year_final',
            name='topic',
        ),
    ]
