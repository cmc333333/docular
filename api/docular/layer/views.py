from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

from docular.layer.serializers import InlineSerializer
from docular.structure.models import DocStruct
from docular.structure.network import Cursor


class NestedDetail(RetrieveAPIView):
    serializer_class = InlineSerializer

    def get_object(self):
        root_struct = get_object_or_404(
            DocStruct,
            expression__work__doc_type=self.kwargs['doc_type'],
            expression__work__doc_subtype=self.kwargs['doc_subtype'] or '',
            expression__work__work_id=self.kwargs['work_id'],
            expression__expression_id=self.kwargs['expression_id'],
            expression__author=self.kwargs['author'] or '',
            identifier=self.kwargs['label']
        )
        query = DocStruct.objects.\
            select_related('expression', 'expression__work').\
            prefetch_related('spans')

        return Cursor.load(root_struct, query)
