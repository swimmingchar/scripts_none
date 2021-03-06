# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 02:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0004_auto_20180516_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='hostname',
            field=models.CharField(max_length=50, null=True, verbose_name='主机名'),
        ),
        migrations.AlterField(
            model_name='host',
            name='ip',
            field=models.GenericIPAddressField(verbose_name='IP地址'),
        ),
        migrations.AlterField(
            model_name='host',
            name='os',
            field=models.CharField(blank=True, max_length=30, verbose_name='系统版本'),
        ),
    ]
