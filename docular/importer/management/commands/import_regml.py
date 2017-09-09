import argparse
import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from lxml import etree

from docular.layer.models import Layer, Span
from docular.structure.models import Expression, Work
from docular.structure.network import new_tree

logger = logging.getLogger(__name__)


class InlineProcessor:
    def __call__(self, root_xml):
        self.text = ''
        self.spans = []
        self.root_xml = root_xml

        self.recurse(root_xml)

        return self.text, self.spans

    def recurse(self, xml):
        start = len(self.text)
        self.text += xml.text or ''
        for child in xml:
            self.recurse(child)
            self.text += child.tail or ''
        end = len(self.text)

        if xml.tag == '{eregs}def':
            layer = Layer.objects.create(
                category='define', attributes={'term': self.text[start:end]})
            self.spans.append(Span(layer=layer, start=start, end=end))
        elif xml.tag == '{eregs}ref' and xml.attrib['reftype'] == 'term':
            layer = Layer.objects.create(
                category='term', attributes={'target': xml.attrib['target']})
            self.spans.append(Span(layer=layer, start=start, end=end))
        elif xml.tag == '{eregs}ref' and xml.attrib['reftype'] in (
                'internal', 'external'):
            layer = Layer.objects.create(
                category=xml.attrib['reftype'] + '-citation',
                attributes={'target': xml.attrib['target']}
            )
            self.spans.append(Span(layer=layer, start=start, end=end))


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
    def appendixSection(parent, xml):   # noqa
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
        title = xml.findtext('./{eregs}title') or ''
        text, spans = InlineProcessor()(xml.find('./{eregs}content'))
        if marker:
            category = 'lvl{0}'.format(len(label_parts) - 2)
            node = parent.add_child(category, label_parts[-1], marker=marker,
                                    text=text, title=title)
        else:
            node = parent.add_child('par', text=text, title=title)
        node.extra['spans'] = spans
        return node


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


def replace_or_create_expression(xml, work):
    expression_id = xml.findtext('.//{eregs}documentNumber')
    expression_date = datetime.strptime(
        xml.findtext('.//{eregs}effectiveDate'), '%Y-%m-%d').date()
    Expression.objects.filter(work=work, expression_id=expression_id).delete()
    return Expression.objects.create(
        work=work, expression_id=expression_id, date=expression_date,
        author='cfpb')


def parse_structure(part_xml, expression):
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
    root.extra['xml'] = part_xml
    for xml_child in part_xml:
        add_child(root, xml_child)
    root.renumber()
    for node in root.walk():
        node.struct.expression = expression
        node.struct.save()

        for span in node.extra.get('spans', []):
            span.doc_struct = node.struct
            span.save()

    return root


class Command(BaseCommand):
    help = ''   # noqa

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('rb'))

    def handle(self, *args, **options):
        xml = etree.parse(options['input_file'])

        work = get_or_create_work(xml)
        expression = replace_or_create_expression(xml, work)

        root = parse_structure(xml.find('.//{eregs}part'), expression)

        logger.info('Created %s DocStructs for %s/%s/%s/@%s',
                    root.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, expression.expression_id)
