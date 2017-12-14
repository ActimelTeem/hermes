# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 12:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='order_location',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.OrderStatus'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.PaymentStatus'),
        ),
    ]