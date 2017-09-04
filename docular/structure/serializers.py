from drf_tweaks.serializers import ModelSerializer
from rest_framework import serializers

from docular.structure.models import DocStruct, Expression, Work


class WorkSerializer(ModelSerializer):
    class Meta:
        model = Work
        fields = ('doc_type', 'doc_subtype', 'work_id')


class ExpressionSerializer(ModelSerializer):
    work = WorkSerializer(read_only=True)

    class Meta:
        model = Expression
        fields = ('work', 'expression_id', 'date', 'author')


class FlatDocStructSerializer(ModelSerializer):
    expression = ExpressionSerializer(read_only=True)

    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'text', 'depth', 'expression')


class NavSerializer(ModelSerializer):
    class Meta:
        model = DocStruct
        fields = ('identifier', 'marker', 'title')


class CursorSerializer(ModelSerializer):
    children = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()

    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'text', 'depth', 'children', 'meta')

    def to_representation(self, instance):
        struct = instance.struct
        struct.cursor = instance
        return super().to_representation(struct)

    def get_children(self, instance):
        return self.__class__(instance.cursor.children(), many=True).data

    def get_meta(self, instance):
        return {}


class RootSerializer(CursorSerializer):
    def prev_doc(self, instance):
        prev = DocStruct.objects.filter(
            expression=instance.expression, right=instance.left - 1
        ).first()
        if prev:
            return NavSerializer(prev).data

    def next_doc(self, instance):
        following = DocStruct.objects.filter(
            expression=instance.expression, left=instance.right + 1
        ).first()
        if following:
            return NavSerializer(following).data

    def parent_doc(self, instance):
        up = DocStruct.objects.filter(
            expression=instance.expression, depth=instance.depth - 1,
            left__lt=instance.left, right__gt=instance.right
        ).first()
        if up:
            return NavSerializer(up).data

    def get_meta(self, instance):
        meta = super().get_meta(instance)
        if self.context:    # Only the root gets context
            expression = ExpressionSerializer().to_representation(
                instance.expression)
            meta.update(
                prev_doc=self.prev_doc(instance),
                next_doc=self.next_doc(instance),
                parent_doc=self.parent_doc(instance),
                frbr={'work': expression.pop('work'),
                      'expression': expression},
            )
        return meta
