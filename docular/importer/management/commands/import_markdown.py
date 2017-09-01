import argparse

import mistune
from django.core.management.base import BaseCommand

from docular.structure.network import new_tree


class NodeRenderer(mistune.Renderer):
    def __init__(self):
        super().__init__(use_xhtml=True)
        self.cursor = new_tree(tag='root', tag_number='0')

    def block_code(self, code, language=None):
        child = self.cursor.add_child('code', text=code)
        child.extra['language'] = language
        return ''

    def block_quote(self, text):
        print("bq_text", text)
        self.cursor.add_child('quote', text=text)
        return ''

    def block_html(self, html):
        return ''

    def header(self, text, level, raw=None):
        while level <= self.cursor.struct.depth:
            self.cursor = self.cursor.parent
        self.cursor = self.cursor.add_child('lvl{0}'.format(level),
                                            title=raw or '')
        return ''

    def hrule(self):
        return ''

    def list(self, body, ordered=True):
        return ''

    def list_item(self, text):
        return ''

    def paragraph(self, text):
        self.cursor.add_child('p', text=text)
        return ''

    def table(self, header, body):
        return ''

    def table_row(self, content):
        return ''

    def table_cell(self, content, **flags):
        return ''


class Command(BaseCommand):
    help = ''   # noqa

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('rb'))

    def handle(self, *args, **options):
        markdown_txt = options['input_file'].read().decode('utf-8')
        options['input_file'].close()
        renderer = NodeRenderer()
        print(mistune.Markdown(renderer=renderer)(markdown_txt))
        for node in renderer.cursor.root.walk():
            print('---', node.struct.identifier, node.struct.title)
            print(node.struct.text)
