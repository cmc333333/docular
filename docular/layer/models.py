from django.db import models
from jsonfield import JSONField

from docular.structure.models import DocStruct


class Layer(models.Model):
    category = models.CharField(max_length=64)
    attributes = JSONField()
    meta_for = models.ManyToManyField(DocStruct, blank=True)


class Span(models.Model):
    doc_struct = models.ForeignKey(DocStruct)
    layer = models.ForeignKey(Layer)
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()


class Milestone(models.Model):
    doc_struct = models.ForeignKey(DocStruct)
    layer = models.ForeignKey(Layer)
    position = models.PositiveIntegerField()
