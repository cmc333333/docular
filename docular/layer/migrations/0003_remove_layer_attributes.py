# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 00:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layer', '0002_auto_20170904_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='layer',
            name='attributes',
        ),
    ]