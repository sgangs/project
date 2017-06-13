# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-08 05:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_user', '0004_user_permission'),
        ('distributor_master', '0006_auto_20170607_0926'),
    ]

    operations = [
        migrations.CreateModel(
            name='retail_customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('phone_no', phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128)),
                ('address', models.CharField(blank=True, max_length=400, null=True, verbose_name='Address Line 2')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('gender', models.CharField(max_length=1)),
                ('age', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retailCustomer_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.RenameField(
            model_name='warehouse',
            old_name='is_sales_channel',
            new_name='is_retail_channel',
        ),
        migrations.AlterUniqueTogether(
            name='retail_customer',
            unique_together=set([('phone_no', 'tenant')]),
        ),
    ]
