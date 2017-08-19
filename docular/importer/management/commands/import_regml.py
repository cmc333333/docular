import argparse
import logging
from datetime import datetime
from lxml import etree

from django.core.management.base import BaseCommand

from docular.structure.models import DocStruct, Entity, Work
from docular.structure.network import new_tree

logger = logging.getLogger(__name__)


class RegMLParser:
    @staticmethod
    def subpart(parent, xml):
        letter = xml.attrib['subpartLetter']
        return parent.add_child(
            'subpart', letter,
            marker='Subpart ' + letter,
            title=xml.findtext('./{eregs}title')
        )

    @staticmethod
    def section(parent, xml):
        parts = xml.findtext('./{eregs}subject').split(' ')
        return parent.add_child(
            'sec', xml.attrib['sectionNum'],
            marker=' '.join(parts[:2]),
            title=' '.join(parts[2:])
        )

    @staticmethod
    def appendix(parent, xml):
        marker, title = xml.findtext('./{eregs}appendixTitle').split('—', 1)
        return parent.add_child(
            'app', xml.attrib['appendixLetter'], marker=marker, title=title
        )

    @staticmethod
    def appendixSection(parent, xml):
        parts = xml.findtext('./{eregs}subject').split('—', 1)
        if len(parts) == 1:
            marker, title = parts[0].split(' ', 1)
        else:
            marker, title = parts
        return parent.add_child(
            'appsec', xml.attrib['appendixSecNum'], marker=marker, title=title
        )

    @staticmethod
    def paragraph(parent, xml):
        label_parts = xml.attrib['label'].split('-')
        marker = xml.attrib.get('marker')
        text = ''.join(xml.find('./{eregs}content').itertext()).strip()
        if marker:
            category = 'lvl{0}'.format(len(label_parts) - 2)
            return parent.add_child(category, label_parts[-1], marker=marker,
                                    text=text)
        else:
            return parent.add_child('par', text=text,
                                    title=xml.findtext('./title') or '')


def add_child(parent, xml):
    tag = xml.tag.replace('{eregs}', '')
    if hasattr(RegMLParser, tag):
        parent = getattr(RegMLParser, tag)(parent, xml)
        parent.extra['xml'] = xml
    for xml_child in xml:
        add_child(parent, xml_child)


def get_or_create_work(xml):
    cfr_title = xml.findtext('.//{eregs}cfr/{eregs}title')
    cfr_part = xml.findtext('.//{eregs}cfr/{eregs}section')

    work, _ = Work.objects.get_or_create(
        doc_type='cfr',
        doc_subtype='title_{0}'.format(cfr_title),
        work_id='part_{0}'.format(cfr_part),
    )
    return work


def replace_or_create_entity(xml, work):
    entity_id = xml.findtext('.//{eregs}documentNumber')
    entity_date = datetime.strptime(
        xml.findtext('.//{eregs}effectiveDate'), '%Y-%m-%d').date()
    Entity.objects.filter(work=work, entity_id=entity_id).delete()
    return Entity.objects.create(
        work=work, entity_id=entity_id, date=entity_date)


def parse_structure(part_xml, entity):
    cfr_part = part_xml.attrib['label']
    letter = part_xml.findtext('..//{eregs}regLetter')
    if letter:
        marker = 'Regulation {0} ({1})'.format(letter, cfr_part)
    else:
        marker = 'Regulation {0}'.format(cfr_part)
    root = new_tree(
        tag='part', tag_number=part_xml.attrib['label'], marker=marker,
        title=part_xml.findtext('..//{eregs}fdsys/{eregs}title')
    )
    for xml_child in part_xml:
        add_child(root, xml_child)
    root.renumber()
    for node in root.walk():
        node.struct.entity = entity
    DocStruct.objects.bulk_create(node.struct for node in root.walk())

    return root


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('rb'))

    def handle(self, *args, **options):
        xml = etree.parse(options['input_file'])

        work = get_or_create_work(xml)
        entity = replace_or_create_entity(xml, work)

        root = parse_structure(xml.find('.//{eregs}part'), entity)

        logger.info('Created %s DocStructs for %s/%s/%s/@%s',
                    root.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, entity.entity_id)
