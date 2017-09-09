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


class Expression(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    expression_id = models.CharField(max_length=32)
    date = models.DateField()
    author = models.CharField(max_length=32)

    class Meta:
        unique_together = ('work', 'expression_id', 'author')
        index_together = (
            unique_together,
            ('work', 'expression_id'),
            ('work', 'date', 'author'),
            ('work', 'date'),
        )


class DocStruct(models.Model):
    expression = models.ForeignKey(Expression, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=1024)
    tag = models.CharField(max_length=64)
    tag_number = models.CharField(max_length=16)
    marker = models.CharField(max_length=64, blank=True)
    title = models.TextField(blank=True)
    text = models.TextField(blank=True)

    left = models.PositiveIntegerField()
    right = models.PositiveIntegerField()
    depth = models.PositiveIntegerField()

    class Meta:
        unique_together = ('expression', 'identifier')
        index_together = (
            unique_together,
            ('expression', 'left'),
            ('expression', 'left', 'depth'),
            ('expression', 'right'),
            ('expression', 'right', 'depth'),
            ('expression', 'tag'),
        )

    def previous(self):
        return self.__class__.objects.filter(
            expression=self.expression, right=self.left - 1).first()

    def following(self):
        return self.__class__.objects.filter(
            expression=self.expression, left=self.right + 1).first()

    def parent(self):
        return self.__class__.objects.filter(
            expression=self.expression, depth=self.depth - 1,
            left__lt=self.left, right__gt=self.right
        ).first()
