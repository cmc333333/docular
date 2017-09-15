import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

import CommonMark
from dateutil.parser import parse as parse_datetime
from django.core.management.base import BaseCommand

from docular.importer import markdown as markdown_transforms
from docular.structure.models import Expression, Work

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

        cursor = None
        for ast_node, entering in ast.walker():
            if entering:
                fn_name = f"enter_{ast_node.t}"
            else:
                fn_name = f"exit_{ast_node.t}"

            if hasattr(markdown_transforms, fn_name):
                cursor = getattr(markdown_transforms, fn_name)(
                    cursor, ast_node)
            elif fn_name not in markdown_transforms.skips:
                logger.warning("Don't know how to parse %s", fn_name)

        cursor.renumber()
        for node in cursor.walk():
            node.struct.expression = expression
            node.struct.save()

            for span in node.extra.get('spans', []):
                span.doc_struct = node.struct
                span.save()

        logger.info('Created %s DocStructs for %s/%s/%s/@%s',
                    cursor.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, expression.expression_id)
