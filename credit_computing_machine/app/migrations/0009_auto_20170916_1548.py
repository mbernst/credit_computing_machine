# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-16 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20170912_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditgroup',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
