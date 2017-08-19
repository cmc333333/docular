from django.http.response import JsonResponse

from docular.structure.models import DocStruct
from docular.structure.network import Cursor


def serialize(cursor, root=False):
    as_dict = {
        'identifier': cursor.struct.identifier,
        'category': cursor.struct.category,
        'title': cursor.struct.title,
        'number': cursor.struct.number,
        'text': cursor.struct.text,
        'children': [serialize(child) for child in cursor.children()],
    }
    if root:
        as_dict['entity'] = {'work': cursor.struct.entity.work_id,
                             'entity': cursor.struct.entity.identifier}
    return as_dict


def get(request, work, version, identifier):
    root_struct = DocStruct.objects.get(identifier=identifier,
                                        entity__identifier=version,
                                        entity__work__identifier=work)

    root = Cursor.load(
        root_struct, DocStruct.objects.select_related('entity'))
    return JsonResponse(serialize(root, True))
