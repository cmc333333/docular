# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-09 04:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layer', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='layer',
            old_name='data',
            new_name='attributes',
        ),
    ]