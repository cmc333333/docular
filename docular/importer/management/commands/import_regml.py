import argparse
from datetime import datetime
from lxml import etree

from django.core.management.base import BaseCommand

from docular.structure.models import DocStruct, Entity, Work
from docular.structure.network import new_tree


class RegMLParser:
    @staticmethod
    def subpart(parent, xml):
        letter = xml.attrib['subpartLetter']
        return parent.add_child(
            'subpart', letter, number='Subpart ' + letter,
            title=xml.findtext('./{eregs}title')
        )

    @staticmethod
    def section(parent, xml):
        parts = xml.findtext('./{eregs}subject').split(' ')
        return parent.add_child(
            'sec', xml.attrib['sectionNum'], number=' '.join(parts[:2]),
            title=' '.join(parts[2:])
        )

    @staticmethod
    def appendix(parent, xml):
        number, title = xml.findtext('./{eregs}appendixTitle').split('—', 1)
        return parent.add_child(
            'app', xml.attrib['appendixLetter'], number=number, title=title
        )

    @staticmethod
    def appendixSection(parent, xml):
        parts = xml.findtext('./{eregs}subject').split('—', 1)
        if len(parts) == 1:
            number, title = parts[0].split(' ', 1)
        else:
            number, title = parts
        return parent.add_child(
            'appsec', xml.attrib['appendixSecNum'], number=number, title=title
        )

    @staticmethod
    def paragraph(parent, xml):
        label_parts = xml.attrib['label'].split('-')
        marker = xml.attrib.get('marker')
        text = ''.join(xml.find('./{eregs}content').itertext()).strip()
        if marker:
            category = 'lvl{0}'.format(len(label_parts) - 2)
            return parent.add_child(category, label_parts[-1], number=marker,
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
        root = new_tree(
            'part_{0}'.format(cfr_part), entity=entity, category='part',
            number='Regulation ' + xml.findtext('.//{eregs}regLetter'),
            title=xml.findtext('.//{eregs}fdsys/{eregs}title')
        )
        for xml_child in part_xml:
            add_child(root, xml_child)
        root.renumber()
        for node in root.walk():
            node.struct.entity = entity
        DocStruct.objects.bulk_create(node.struct for node in root.walk())

        for struct in DocStruct.objects.order_by('left'):
            print(struct.identifier)
