# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-04 20:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('layer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='doc_struct',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='structure.DocStruct'),
        ),
        migrations.AlterField(
            model_name='span',
            name='doc_struct',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spans', to='structure.DocStruct'),
        ),
    ]