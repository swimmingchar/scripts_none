# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 03:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0005_auto_20180516_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='hostname',
            field=models.CharField(max_length=50, unique=True, verbose_name='主机名'),
        ),
    ]
