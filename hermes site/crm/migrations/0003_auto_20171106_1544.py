# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_auto_20171106_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]