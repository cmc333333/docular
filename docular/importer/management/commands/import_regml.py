import argparse
import logging
import re
from datetime import datetime
from lxml import etree

from django.core.management.base import BaseCommand

from docular.structure.models import DocStruct, Entity, Work
from docular.structure.network import Cursor

logger = logging.getLogger(__name__)


def add_children(xml, parent_cursor):
    for xml_child in xml:
        cursor = parent_cursor
        tag = xml_child.tag.replace('{eregs}', '')
        if tag == 'subpart':
            cursor = cursor.add_child(xml_child, 'subpart',
                                      xml_child.attrib['subpartLetter'])
        elif tag == 'section':
            cursor = cursor.add_child(xml_child, 'sec',
                                      xml_child.attrib['sectionNum'])
        elif tag == 'appendix':
            cursor = cursor.add_child(xml_child, 'app',
                                      xml_child.attrib['appendixLetter'])
        elif tag == 'appendixSection':
            cursor = cursor.add_child(xml_child, 'appsec',
                                      xml_child.attrib['appendixSecNum'])
        elif tag == 'paragraph':
            label_parts = xml_child.attrib['label'].split('-')
            last = label_parts[-1]
            if re.match('p\d+', last):
                cursor = cursor.add_child(xml_child, 'par')
            else:
                child_type = 'lvl{0}'.format(len(label_parts) - 2)
                cursor = cursor.add_child(xml_child, child_type, last)
        add_children(xml_child, cursor)


def generate_structs(entity: Entity, root: Cursor):
    for node in root.walk():
        text = ''
        if node.category == 'part':
            number = 'Regulation ' + node.obj.findtext('..//{eregs}regLetter')
            title = node.obj.findtext('..//{eregs}fdsys/{eregs}title')
        elif node.category == 'subpart':
            number = 'Subpart ' + node.obj.attrib['subpartLetter']
            title = node.obj.findtext('./{eregs}title')
        elif node.category == 'sect':
            parts = node.obj.findtext('./{eregs}subject').split(' ')
            number = ' '.join(parts[:2])
            title = ' '.join(parts[2:])
        elif node.category == 'app':
            number, title = node.obj.findtext('./{eregs}appendixTitle').split(
                '—', 1)
        elif node.category == 'appsec':
            parts = node.obj.findtext('./{eregs}subject').split('—', 1)
            if len(parts) == 1:
                number, title = parts[0].split(' ', 1)
            else:
                number, title = parts
        elif node.category == 'par':
            number = ''
            title = node.obj.findtext('./title') or ''
        elif node.category.startswith('lvl'):
            number = node.obj.attrib['marker']
            title = node.obj.findtext('./title') or ''

        yield DocStruct(
            entity=entity, category=node.category, identifier=node._key,
            left=node.left, right=node.right,
            number=number, title=title, text=text
        )


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('rb'))

    def handle(self, *args, **options):
        xml = etree.parse(options['input_file'])

        cfr_title = xml.findtext('.//{eregs}cfr/{eregs}title')
        cfr_part = xml.findtext('.//{eregs}cfr/{eregs}section')
        work_id = '{0} CFR {1}'.format(cfr_title, cfr_part)
        entity_id = xml.findtext('.//{eregs}documentNumber')
        entity_date = datetime.strptime(
            xml.findtext('.//{eregs}effectiveDate'), '%Y-%m-%d').date()

        work, _ = Work.objects.get_or_create(identifier=work_id)
        Entity.objects.filter(work=work, identifier=entity_id).delete()
        entity = Entity.objects.create(
            work=work, identifier=entity_id, date=entity_date)

        # first build a tree structure, keeping the original XML
        part_xml = xml.find('.//{eregs}part')
        cursor = Cursor.new_tree(part_xml, 'part_{0}'.format(cfr_part))
        add_children(part_xml, cursor)
        cursor.renumber(1)
        DocStruct.objects.bulk_create(generate_structs(entity, cursor))

        for struct in DocStruct.objects.order_by('left'):
            print(struct.identifier)
