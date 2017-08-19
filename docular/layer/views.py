from django.http.response import JsonResponse

from docular.structure.models import DocStruct
from docular.structure.network import Cursor


def json_serialize(cursor, root=False):
    as_dict = {
        'identifier': cursor.struct.identifier,
        'tag': cursor.struct.tag,
        'tag_number': cursor.struct.tag_number,
        'marker': cursor.struct.marker,
        'title': cursor.struct.title,
        'text': cursor.struct.text,
        'children': [json_serialize(child) for child in cursor.children()],
    }
    if root:
        as_dict['frbr'] = {
            'work': {
                'doc_type': cursor.struct.entity.work.doc_type,
                'doc_subtype': cursor.struct.entity.work.doc_subtype,
                'work_id': cursor.struct.entity.work.work_id,
            },
            'entity': {
                'entity_id': cursor.struct.entity.entity_id,
                'date': cursor.struct.entity.date,
            },
        }
    return as_dict


def get(request, doc_type, doc_subtype, work_id, entity_id, label, fmt):
    root_struct = DocStruct.objects.get(
        entity__work__doc_type=doc_type,
        entity__work__doc_subtype=doc_subtype,
        entity__work__work_id=work_id,
        entity__entity_id=entity_id,
        identifier=label
    )

    root = Cursor.load(
        root_struct,
        DocStruct.objects.select_related('entity', 'entity__work')
    )
    return JsonResponse(json_serialize(root, True))
