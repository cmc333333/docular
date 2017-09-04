from drf_tweaks import serializers

from docular.structure.models import DocStruct, Expression, Work


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ('doc_type', 'doc_subtype', 'work_id')


class ExpressionSerializer(serializers.ModelSerializer):
    work = WorkSerializer(read_only=True)

    class Meta:
        model = Expression
        fields = ('work', 'expression_id', 'date', 'author')


class FlatDocStructSerializer(serializers.ModelSerializer):
    expression = ExpressionSerializer(read_only=True)

    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'text', 'depth', 'expression')


class NavSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocStruct
        fields = ('identifier', 'marker', 'title')


class CursorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'text', 'depth')

    def to_representation(self, instance):
        rep = super().to_representation(instance.struct)
        rep['children'] = CursorSerializer(many=True).to_representation(
            instance.children())
        rep['meta'] = {}
        return rep


class RootSerializer(CursorSerializer):
    def prev_doc(self, instance):
        prev = DocStruct.objects.filter(
            expression=instance.struct.expression,
            right=instance.struct.left - 1
        ).first()
        if prev:
            return NavSerializer(prev).data

    def next_doc(self, instance):
        following = DocStruct.objects.filter(
            expression=instance.struct.expression,
            left=instance.struct.right + 1
        ).first()
        if following:
            return NavSerializer(following).data

    def parent_doc(self, instance):
        up = DocStruct.objects.filter(
            expression=instance.struct.expression,
            depth=instance.struct.depth - 1,
            left__lt=instance.struct.left, right__gt=instance.struct.right
        ).first()
        if up:
            return NavSerializer(up).data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        expression = ExpressionSerializer().to_representation(
            instance.struct.expression)
        rep['meta'].update(
            prev_doc=self.prev_doc(instance),
            next_doc=self.next_doc(instance),
            parent_doc=self.parent_doc(instance),
            frbr={'work': expression.pop('work'),
                  'expression': expression},
        )
        return rep
