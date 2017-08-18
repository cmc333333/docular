from django.http.response import JsonResponse

from docular.structure.models import DocStruct
from docular.structure.network import Cursor


def serializer(doc):
    return {
        'entity': '{0}@{1}'.format(doc.entity.work_id, doc.entity.identifier),
        'category': doc.category,
        'identifier': doc.identifier,
        'text': doc.text,
        'number': doc.number,
        'title': doc.title,
    }


def get(request, work, version, identifier):
    root = DocStruct.objects.get(identifier=identifier,
                                 entity__identifier=version,
                                 entity__work__identifier=work)
    docs = DocStruct.objects.filter(
        left__gte=root.left, right__lte=root.right, entity=root.entity
    ).order_by('left')

    cursor = Cursor.from_nested_set(docs)
    return JsonResponse(cursor.dump(serializer))
