# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 03:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('distributor_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('key', models.CharField(max_length=20)),
                ('address_1', models.CharField(blank=True, max_length=200, null=True, verbose_name='Address Line 1')),
                ('address_2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Address Line 2')),
                ('state', models.CharField(blank=True, choices=[('ANI', 'Andaman & Nicobar Island'), ('AP', 'Andhra Pradesh'), ('AN', 'Andaman & Nicobar Island'), ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BI', 'Bihar'), ('CHN', 'Chandigarh'), ('CHT', 'Chattisgarh'), ('DNH', 'Dadra & Nagar Haveli'), ('DD', 'Daman & Diu'), ('DEL', 'National Capital Territory of Delhi'), ('GOA', 'Goa'), ('GUJ', 'Gujrat'), ('HAR', 'Haryana'), ('HP', 'Himachal Pradesh'), ('JK', 'Jammu & Kashmir'), ('JHA', 'Jharkhand'), ('KAR', 'Karnataka'), ('KER', 'Kerala'), ('LAK', 'Lakshadweep'), ('MP', 'Madhya Pradesh'), ('MAH', 'Maharashtra'), ('MAN', 'Manipur'), ('MEG', 'Meghalaya'), ('MIZ', 'Mizoram'), ('NAG', 'Nagaland'), ('OD', 'Odisha'), ('PUD', 'Puducherry'), ('PUN', 'Punjab'), ('RAJ', 'Rajashtan'), ('SIK', 'Sikkim'), ('TN', 'Tamil Nadu'), ('TEL', 'Telengana'), ('TRI', 'Tripura'), ('UP', 'Uttar Pradesh'), ('UTT', 'Uttarkhand'), ('WB', 'West Bengal')], max_length=4, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='City')),
                ('pin', models.CharField(blank=True, max_length=8, null=True, verbose_name='Pincode')),
                ('phone_no', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('cst', models.CharField(blank=True, max_length=20, null=True)),
                ('tin', models.CharField(blank=True, max_length=20, null=True)),
                ('gst', models.CharField(blank=True, max_length=20, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=10)),
                ('details', models.TextField(blank=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dimension_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manufacturer_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('sku', models.CharField(db_index=True, max_length=50)),
                ('vat_type', models.PositiveSmallIntegerField(choices=[(1, 'No VAT'), (2, 'On MRP'), (3, 'On Cost Price')], default=3, verbose_name='VAT type')),
                ('reorder_point', models.PositiveSmallIntegerField(default=0)),
                ('has_batch', models.BooleanField(default=False)),
                ('has_instance', models.BooleanField(default=False)),
                ('has_attribute', models.BooleanField(default=False)),
                ('remarks', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_brand', to='distributor_master.Brand')),
            ],
        ),
        migrations.CreateModel(
            name='product_attribute',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(db_index=True, max_length=50)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productAttribute_attribute', to='distributor_master.Attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productAttribute_product', to='distributor_master.Product')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productAttribute_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='product_price',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('tentative_purchase', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tentative_sales', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tentative_mrp', models.DecimalField(decimal_places=2, max_digits=12)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productPrice_product', to='distributor_master.Product')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productPrice_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='tax_structure',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('percentage', models.PositiveSmallIntegerField()),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taxStructure_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=30)),
                ('symbol', models.CharField(db_index=True, max_length=10)),
                ('multiplier', models.DecimalField(decimal_places=2, max_digits=6)),
                ('dimension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_dimension', to='distributor_master.Dimension')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('key', models.CharField(max_length=20)),
                ('address_1', models.CharField(blank=True, max_length=200, null=True, verbose_name='Address Line 1')),
                ('address_2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Address Line 2')),
                ('state', models.CharField(blank=True, choices=[('ANI', 'Andaman & Nicobar Island'), ('AP', 'Andhra Pradesh'), ('AN', 'Andaman & Nicobar Island'), ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BI', 'Bihar'), ('CHN', 'Chandigarh'), ('CHT', 'Chattisgarh'), ('DNH', 'Dadra & Nagar Haveli'), ('DD', 'Daman & Diu'), ('DEL', 'National Capital Territory of Delhi'), ('GOA', 'Goa'), ('GUJ', 'Gujrat'), ('HAR', 'Haryana'), ('HP', 'Himachal Pradesh'), ('JK', 'Jammu & Kashmir'), ('JHA', 'Jharkhand'), ('KAR', 'Karnataka'), ('KER', 'Kerala'), ('LAK', 'Lakshadweep'), ('MP', 'Madhya Pradesh'), ('MAH', 'Maharashtra'), ('MAN', 'Manipur'), ('MEG', 'Meghalaya'), ('MIZ', 'Mizoram'), ('NAG', 'Nagaland'), ('OD', 'Odisha'), ('PUD', 'Puducherry'), ('PUN', 'Punjab'), ('RAJ', 'Rajashtan'), ('SIK', 'Sikkim'), ('TN', 'Tamil Nadu'), ('TEL', 'Telengana'), ('TRI', 'Tripura'), ('UP', 'Uttar Pradesh'), ('UTT', 'Uttarkhand'), ('WB', 'West Bengal')], max_length=4, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='City')),
                ('pin', models.CharField(blank=True, max_length=8, null=True, verbose_name='Pincode')),
                ('phone_no', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('cst', models.CharField(blank=True, max_length=20, null=True)),
                ('tin', models.CharField(blank=True, max_length=20, null=True)),
                ('gst', models.CharField(blank=True, max_length=20, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address_1', models.CharField(max_length=200, verbose_name='Address Line 1')),
                ('address_2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Address Line 2')),
                ('state', models.CharField(choices=[('ANI', 'Andaman & Nicobar Island'), ('AP', 'Andhra Pradesh'), ('AN', 'Andaman & Nicobar Island'), ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BI', 'Bihar'), ('CHN', 'Chandigarh'), ('CHT', 'Chattisgarh'), ('DNH', 'Dadra & Nagar Haveli'), ('DD', 'Daman & Diu'), ('DEL', 'National Capital Territory of Delhi'), ('GOA', 'Goa'), ('GUJ', 'Gujrat'), ('HAR', 'Haryana'), ('HP', 'Himachal Pradesh'), ('JK', 'Jammu & Kashmir'), ('JHA', 'Jharkhand'), ('KAR', 'Karnataka'), ('KER', 'Kerala'), ('LAK', 'Lakshadweep'), ('MP', 'Madhya Pradesh'), ('MAH', 'Maharashtra'), ('MAN', 'Manipur'), ('MEG', 'Meghalaya'), ('MIZ', 'Mizoram'), ('NAG', 'Nagaland'), ('OD', 'Odisha'), ('PUD', 'Puducherry'), ('PUN', 'Punjab'), ('RAJ', 'Rajashtan'), ('SIK', 'Sikkim'), ('TN', 'Tamil Nadu'), ('TEL', 'Telengana'), ('TRI', 'Tripura'), ('UP', 'Uttar Pradesh'), ('UTT', 'Uttarkhand'), ('WB', 'West Bengal')], max_length=4)),
                ('city', models.CharField(max_length=50, verbose_name='City')),
                ('pin', models.CharField(max_length=8, verbose_name='Pincode')),
                ('remarks', models.TextField(blank=True, null=True)),
                ('default', models.BooleanField(default=False, verbose_name='Defaul Warehouse?')),
                ('is_active', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('key', models.CharField(db_index=True, max_length=20)),
                ('details', models.TextField(blank=True, null=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_master_user_tenant', to='distributor_user.Tenant')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='default_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_unit', to='distributor_master.Unit'),
        ),
        migrations.AddField(
            model_name='product',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_group', to='distributor_master.Group'),
        ),
        migrations.AddField(
            model_name='product',
            name='tax',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='distributor_master.tax_structure'),
        ),
        migrations.AddField(
            model_name='product',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_master_user_tenant', to='distributor_user.Tenant'),
        ),
        migrations.AddField(
            model_name='customer',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_zone', to='distributor_master.Zone'),
        ),
        migrations.AddField(
            model_name='brand',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_manufacturer', to='distributor_master.Manufacturer'),
        ),
        migrations.AddField(
            model_name='brand',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_master_user_tenant', to='distributor_user.Tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='warehouse',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='vendor',
            unique_together=set([('key', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='unit',
            unique_together=set([('name', 'tenant'), ('symbol', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='tax_structure',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='product_price',
            unique_together=set([('product', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='product_attribute',
            unique_together=set([('product', 'attribute', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('sku', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='manufacturer',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='dimension',
            unique_together=set([('name', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together=set([('key', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='brand',
            unique_together=set([('name', 'manufacturer', 'tenant')]),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set([('name', 'tenant')]),
        ),
    ]
