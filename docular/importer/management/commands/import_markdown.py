import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

import CommonMark
from dateutil.parser import parse as parse_datetime
from django.core.management.base import BaseCommand

from docular.structure.models import DocStruct, Expression, Work
from docular.structure.network import new_tree

logger = logging.getLogger(__name__)


def valid_file(filename):
    path = Path(filename)
    if not path.is_file():
        raise argparse.ArgumentTypeError('Not a file: ' + filename)
    elif not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError('Not readable: ' + filename)
    return path


class Command(BaseCommand):
    help = ''   # noqa

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=valid_file)
        parser.add_argument('-d', '--doc_type', default='markdown')
        parser.add_argument('-s', '--doc_subtype', default='')
        parser.add_argument('-w', '--work_id', default=argparse.SUPPRESS)
        parser.add_argument('-e', '--expression_id', default=argparse.SUPPRESS)
        parser.add_argument('-t', '--expression_date', type=parse_datetime,
                            default=datetime.now())
        parser.add_argument('-a', '--author', default='')

    def handle(self, *args, **options):
        markdown_txt = options['input_file'].read_text(encoding='utf-8')
        parser = CommonMark.Parser()
        ast = parser.parse(markdown_txt)

        expression_date = options['expression_date'].date()
        work_id = options.get('work_id', options['input_file'].stem)
        expression_id = options.get('expression_id',
                                    expression_date.isoformat())

        work, _ = Work.objects.get_or_create(
            doc_type=options['doc_type'],
            doc_subtype=options['doc_subtype'],
            work_id=work_id,
        )
        Expression.objects.filter(
            work=work, expression_id=expression_id).delete()
        expression = Expression.objects.create(
            work=work, expression_id=expression_id, date=expression_date,
            author=options['author']
        )

        root = new_tree('root', '0', expression=expression)
        cursor = root

        for node, entering in ast.walker():
            if entering:
                if node.literal:
                    cursor = cursor.add_child(
                        node.t, expression=expression, text=node.literal)
                else:
                    cursor = cursor.add_child(node.t, expression=expression)
            if (node.literal is not None or not entering
                    or node.t in ('softbreak', 'thematic_break')):
                cursor = cursor.parent

        root.renumber()
        DocStruct.objects.bulk_create(n.struct for n in root.walk())

        logger.info('Created %s DocStructs for %s/%s/%s/@%s',
                    root.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, expression.expression_id)
