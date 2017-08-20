import argparse
import logging

from dateutil.parser import parse as parse_date
from django.core.management.base import BaseCommand
from lxml import etree

from docular.structure.models import DocStruct, Entity, Work
from docular.structure.network import new_tree

logger = logging.getLogger(__name__)


class ECFRParser:
    @classmethod
    def add_child(cls, parent, xml):
        if hasattr(cls, xml.tag):
            parent = getattr(cls, xml.tag)(parent, xml)
            parent.extra['xml'] = xml
        for xml_child in xml:
            cls.add_child(parent, xml_child)

    @staticmethod
    def DIV6(parent, xml):
        marker, title = xml.findtext('./HEAD').split(' - ', 1)
        return parent.add_child(
            'subpart', xml.attrib['N'], marker=marker, title=title
        )

    @staticmethod
    def DIV7(parent, xml):
        marker, title = xml.findtext('./HEAD').split(' - ', 1)
        return parent.add_child('subjgrp', marker=marker, title=title)

    @staticmethod
    def DIV8(parent, xml):
        marker = xml.attrib['N']
        sec_no = marker.split('.', 1)[1]
        title = xml.findtext('./HEAD').split('   ', 1)[1]
        return parent.add_child('sec', sec_no, marker=marker, title=title)

    @staticmethod
    def P(parent, xml):
        text = ''.join(xml.itertext()).strip()
        return parent.add_child('par', text=text)


def get_or_create_work(part_xml):
    cfr_title = part_xml.attrib['NODE'].split(':')[0]
    cfr_part = part_xml.attrib['N']

    work, _ = Work.objects.get_or_create(
        doc_type='ecfr',
        doc_subtype='title_{0}'.format(cfr_title),
        work_id='part_{0}'.format(cfr_part),
    )
    return work


def replace_or_create_entity(root_xml, work):
    entity_date = parse_date(root_xml.findtext('.//AMDDATE'))
    entity_id = entity_date.strftime('%Y-%m-%d')
    Entity.objects.filter(work=work, entity_id=entity_id).delete()
    return Entity.objects.create(
        work=work, entity_id=entity_id, date=entity_date)


def parse_structure(part_xml, entity):
    marker, title = part_xml.findtext('./HEAD').split(' - ', 1)
    root = new_tree(
        tag='part', tag_number=part_xml.attrib['N'], marker=marker,
        title=title
    )
    for xml_child in part_xml:
        ECFRParser.add_child(root, xml_child)
    root.renumber()
    for node in root.walk():
        node.struct.entity = entity
    DocStruct.objects.bulk_create(node.struct for node in root.walk())

    return root


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('rb'))
        parser.add_argument('cfr_part')

    def handle(self, *args, **options):
        xml = etree.parse(options['input_file'])
        part_xml = xml.find('.//DIV5[@N="{0}"]'.format(options['cfr_part']))

        work = get_or_create_work(part_xml)
        entity = replace_or_create_entity(xml, work)

        root = parse_structure(part_xml, entity)

        logger.info('Created %s DocStructs for %s/%s/%s/@%s',
                    root.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, entity.entity_id)
