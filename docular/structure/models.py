from django.db import models


class Work(models.Model):
    doc_type = models.CharField(max_length=32, db_index=True)
    doc_subtype = models.CharField(max_length=32, blank=True)
    work_id = models.CharField(max_length=32)

    class Meta:
        unique_together = ('doc_type', 'doc_subtype', 'work_id')
        index_together = (
            unique_together,
            ('doc_type', 'doc_subtype'),
        )


class Entity(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    entity_id = models.CharField(max_length=32)
    date = models.DateField()

    class Meta:
        unique_together = ('work', 'entity_id')
        index_together = (
            unique_together,
            ('work', 'date'),
        )


class DocStruct(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=1024)
    tag = models.CharField(max_length=64)
    tag_number = models.CharField(max_length=16)
    marker = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=128, blank=True)
    text = models.TextField(blank=True)

    left = models.PositiveIntegerField()
    right = models.PositiveIntegerField()

    class Meta:
        unique_together = ('entity', 'identifier')
        index_together = (
            unique_together,
            ('entity', 'left'),
            ('entity', 'tag'),
        )
