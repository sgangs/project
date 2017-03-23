# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 11:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_user', '0017_tenant_no_of_profile'),
        ('school_account', '0024_auto_20170313_0925'),
        ('school_salary', '0011_auto_20170310_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='monthly_deduction',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthlyDeduction_salary_user_tenant', to='school_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='monthly_deduction_list',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('display_payslip', models.BooleanField(db_index=True, default=True)),
                ('serial_no', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('deduction_type', models.PositiveSmallIntegerField(choices=[(1, 'Expense'), (2, 'Liability')], db_index=True)),
                ('affect_lop', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthlyDeductionList_salary_account_account', to='school_account.Account')),
                ('monthly_deduction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthlyDeductionList_monthlyDeduction', to='school_salary.monthly_salary')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthlyDeductionList_salary_user_tenant', to='school_user.Tenant')),
            ],
            options={
                'ordering': ('display_payslip', 'serial_no', 'id'),
            },
        ),
        migrations.AddField(
            model_name='yearly_salary_list',
            name='affect_esi',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='yearly_salary_list',
            name='affect_gratuity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='yearly_salary_list',
            name='affect_lop',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='yearly_salary_list',
            name='affect_pf',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='monthly_salary_list',
            name='display_payslip',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='yearly_salary_list',
            name='display_payslip',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
