# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-30 10:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor_user', '0008_tenant_tenant_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('email',)]),
        ),
    ]
