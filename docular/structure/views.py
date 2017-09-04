from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView

from docular.structure.models import DocStruct
from docular.structure.network import Cursor
from docular.structure.serializers import (FlatDocStructSerializer,
                                           RootSerializer)


class DocStructViewSet(viewsets.ModelViewSet):
    queryset = DocStruct.objects.select_related(
        'expression', 'expression__work')
    serializer_class = FlatDocStructSerializer
    ordering = ('expression_id', 'left')


class NestedDetail(RetrieveAPIView):
    serializer_class = RootSerializer

    def get_object(self):
        root_struct = DocStruct.objects.get(
            expression__work__doc_type=self.kwargs['doc_type'],
            expression__work__doc_subtype=self.kwargs['doc_subtype'],
            expression__work__work_id=self.kwargs['work_id'],
            expression__expression_id=self.kwargs['expression_id'],
            expression__author=self.kwargs['author'],
            identifier=self.kwargs['label']
        )

        return Cursor.load(
            root_struct,
            DocStruct.objects.select_related('expression', 'expression__work')
        )
