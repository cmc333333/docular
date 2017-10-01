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

    @classmethod
    def or_none(cls, instance):
        return instance and cls(instance).data


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
        context = dict(self.context, child=True)
        return self.__class__(
            instance.cursor.children(), context=context, many=True
        ).data

    def get_meta(self, instance):
        return {}


class RootSerializer(CursorSerializer):
    def get_meta(self, instance):
        meta = super().get_meta(instance)
        if not self.context.get('child'):
            expression = ExpressionSerializer().to_representation(
                instance.expression)
            meta.update(
                prev_doc=NavSerializer.or_none(instance.previous()),
                prev_peer=NavSerializer.or_none(instance.prev_peer()),
                next_doc=NavSerializer.or_none(instance.following()),
                next_peer=NavSerializer.or_none(instance.next_peer()),
                parent_doc=NavSerializer.or_none(instance.parent()),
                frbr={'work': expression.pop('work'),
                      'expression': expression},
            )
        return meta
