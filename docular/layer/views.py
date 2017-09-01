from django.http.response import HttpResponse, JsonResponse
from lxml import etree

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
        'depth': cursor.struct.depth,
        'children': [json_serialize(child) for child in cursor.children()],
    }
    if root:
        as_dict['frbr'] = {
            'work': {
                'doc_type': cursor.struct.expression.work.doc_type,
                'doc_subtype': cursor.struct.expression.work.doc_subtype,
                'work_id': cursor.struct.expression.work.work_id,
            },
            'expression': {
                'expression_id': cursor.struct.expression.expression_id,
                'date': cursor.struct.expression.date,
                'author': cursor.struct.expression.author,
            },
        }
        prev = DocStruct.objects.filter(
            expression=cursor.struct.expression, right=cursor.struct.left - 1
        ).first()
        following = DocStruct.objects.filter(
            expression=cursor.struct.expression, left=cursor.struct.right + 1
        ).first()
        up = DocStruct.objects.filter(
            expression=cursor.struct.expression, depth=cursor.struct.depth - 1,
            left__lt=cursor.struct.left, right__gt=cursor.struct.right
        ).first()
        as_dict['nav'] = {}
        if prev:
            as_dict['nav']['prev'] = {
                'identifier': prev.identifier,
                'marker': prev.marker,
                'title': prev.title,
            }
        if following:
            as_dict['nav']['next'] = {
                'identifier': following.identifier,
                'marker': following.marker,
                'title': following.title,
            }
        if up:
            as_dict['nav']['up'] = {
                'identifier': up.identifier,
                'marker': up.marker,
                'title': up.title,
            }
    return as_dict


def xml_serialize(cursor, root=False):
    elt = etree.Element(cursor.struct.tag, id=cursor.struct.identifier)
    if root:
        frbr = etree.SubElement(elt, 'frbr')
        etree.SubElement(frbr, 'FRBRWork',
                         doc_type=cursor.struct.expression.work.doc_type,
                         doc_subtype=cursor.struct.expression.work.doc_subtype,
                         work_id=cursor.struct.expression.work.work_id)
        etree.SubElement(frbr, 'FRBRExpression',
                         expression_id=cursor.struct.expression.expression_id,
                         date=cursor.struct.expression.date.isoformat())
    if cursor.struct.marker:
        etree.SubElement(elt, 'num').text = cursor.struct.marker
    if cursor.struct.title:
        etree.SubElement(elt, 'heading').text = cursor.struct.marker
    if cursor.struct.text:
        etree.SubElement(elt, 'content').text = cursor.struct.text

    elt.extend(xml_serialize(child) for child in cursor.children())
    return elt


def get(request, doc_type, doc_subtype, work_id, expression_id, author, label,
        fmt):
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
    if fmt == 'xml':
        elt = xml_serialize(root, True)
        return HttpResponse(etree.tostring(elt), content_type='text/xml')
    else:
        return JsonResponse(json_serialize(root, True))
