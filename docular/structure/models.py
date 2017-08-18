from django.db import models


class Work(models.Model):
    identifier = models.CharField(max_length=32, primary_key=True)


class Entity(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=32)
    date = models.DateField()

    class Meta:
        unique_together = (
            ('work', 'identifier'),
        )


class DocStruct(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    category = models.CharField(max_length=64)
    identifier = models.CharField(max_length=1024)
    text = models.TextField(blank=True)
    number = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=128, blank=True)

    left = models.PositiveIntegerField()
    right = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('entity', 'identifier'),
        )
