from rest_framework import viewsets

from docular.structure.models import DocStruct
from docular.structure.serializers import FlatDocStructSerializer


class DocStructViewSet(viewsets.ModelViewSet):
    queryset = DocStruct.objects.select_related(
        'expression', 'expression__work')
    serializer_class = FlatDocStructSerializer
    ordering = ('expression_id', 'left')
