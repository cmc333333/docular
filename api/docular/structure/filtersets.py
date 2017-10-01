import django_filters

from docular.structure.models import DocStruct, Expression, Work


class WorkFilters(django_filters.FilterSet):
    class Meta:
        model = Work
        fields = {
            'doc_type': ('exact', 'in'),
            'doc_subtype': ('exact', 'in', 'isnull'),
            'work_id': ('exact', 'in'),
        }


class ExpressionFilters(django_filters.FilterSet):
    class Meta:
        model = Expression
        fields = {
            'expression_id': ('exact', 'in'),
            'date': ('exact', 'gt', 'gte', 'in', 'lt', 'lte'),
            'author': ('exact',),
        }
        fields.update({
            'work__' + key: value
            for key, value in WorkFilters.Meta.fields.items()
        })


class DocStructFilters(django_filters.FilterSet):
    class Meta:
        model = DocStruct
        fields = {
            'identifier': ('exact', 'in', 'startswith'),
            'tag': ('exact', 'in'),
            'tag_number': ('exact', 'in', 'gt', 'gte', 'lt', 'lte'),
            'marker': ('exact', 'in', 'isnull'),
            'left': ('exact', 'in', 'gt', 'gte', 'lt', 'lte'),
            'right': ('exact', 'in', 'gt', 'gte', 'lt', 'lte'),
            'depth': ('exact', 'in', 'gt', 'gte', 'lt', 'lte'),
        }
        fields.update({
            'expression__' + key: value
            for key, value in ExpressionFilters.Meta.fields.items()
        })
