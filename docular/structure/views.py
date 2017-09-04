from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from docular.structure.models import DocStruct
from docular.structure.network import Cursor
from docular.structure.serializers import (FlatDocStructSerializer,
                                           RootSerializer)


class DocStructViewSet(viewsets.ModelViewSet):
    queryset = DocStruct.objects.select_related(
        'expression', 'expression__work')
    serializer_class = FlatDocStructSerializer
    ordering = ('expression_id', 'left')


@api_view(['GET'])
def nested_detail(request, doc_type, doc_subtype, work_id, expression_id,
                  author, label):
    root_struct = DocStruct.objects.get(
        expression__work__doc_type=doc_type,
        expression__work__doc_subtype=doc_subtype,
        expression__work__work_id=work_id,
        expression__expression_id=expression_id,
        expression__author=author,
        identifier=label
    )

    root = Cursor.load(
        root_struct,
        DocStruct.objects.select_related('expression', 'expression__work')
    )
    serializer = RootSerializer(root)
    return Response(serializer.data)
