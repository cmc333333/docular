# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-09 02:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('structure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=64)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('meta_for', models.ManyToManyField(blank=True, to='structure.DocStruct')),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField()),
                ('doc_struct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='structure.DocStruct')),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='layer.Layer')),
            ],
        ),
        migrations.CreateModel(
            name='Span',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.PositiveIntegerField()),
                ('end', models.PositiveIntegerField()),
                ('doc_struct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spans', to='structure.DocStruct')),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='layer.Layer')),
            ],
        ),
    ]
