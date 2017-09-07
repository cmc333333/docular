from django.db import models

from docular.structure.models import DocStruct


class Layer(models.Model):
    category = models.CharField(max_length=64)
    meta_for = models.ManyToManyField(DocStruct, blank=True)


class Span(models.Model):
    doc_struct = models.ForeignKey(DocStruct, on_delete=models.CASCADE,
                                   related_name='spans')
    layer = models.ForeignKey(Layer)
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()


class Milestone(models.Model):
    doc_struct = models.ForeignKey(DocStruct, on_delete=models.CASCADE,
                                   related_name='milestones')
    layer = models.ForeignKey(Layer)
    position = models.PositiveIntegerField()
