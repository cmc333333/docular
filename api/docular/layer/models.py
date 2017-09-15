from django.contrib.postgres.fields import JSONField
from django.db import models

from docular.layer.registry import registry
from docular.structure.models import DocStruct


class Layer(models.Model):
    category = models.CharField(max_length=64)
    attributes = JSONField(blank=True, null=True)
    meta_for = models.ManyToManyField(DocStruct, blank=True)

    @property
    def data(self):
        if self.category:
            return registry[self.category].from_dict(self.attributes or {})
        else:
            return None

    @data.setter
    def data(self, value):
        self.attributes = value.serialize()


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
