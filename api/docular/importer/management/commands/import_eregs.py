from django.core.management.base import BaseCommand

from docular.importer.api import Api
from docular.importer.eregs import fetch_and_save_all


class Command(BaseCommand):
    help = 'Import document data from an eRegs instance'    # noqa

    def add_arguments(self, parser):
        parser.add_argument('EREGS_API')

    def handle(self, *args, **options):
        fetch_and_save_all(Api.new(options['EREGS_API']))
