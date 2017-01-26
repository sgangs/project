# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-23 13:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_genadmin', '0010_annual_calender_event_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='academic_year',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(blank=True, max_length=4, verbose_name='Academic Year: If year is 2016-17, enter 2016')),
                ('slug', models.SlugField()),
                ('current_academic_year', models.BooleanField()),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academicYear_genadmin_user_tenant', to='school_user.Tenant')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='academic_year',
            unique_together=set([('year', 'tenant')]),
        ),
    ]
