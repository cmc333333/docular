import logging
from collections import OrderedDict
from datetime import date, datetime
from enum import Enum, unique
from typing import Any, Callable, Dict, NamedTuple, Tuple

from docular.importer.api import Api
from docular.importer.doc_types import CFR
from docular.layer.models import Layer, Span
from docular.structure.models import Expression, Work
from docular.structure.network import Cursor, new_tree


@unique
class EregsLayer(Enum):
    P_MARKER = 'paragraph-markers'
    TERMS = 'terms'


Layers = Dict[EregsLayer, Dict[str, Any]]
logger = logging.getLogger(__name__)


class VersionInfo(NamedTuple):
    version: str
    regulation: str
    by_date: date

    @classmethod
    def from_json(cls, json_dict):
        by_date = datetime.strptime(json_dict['by_date'], '%Y-%m-%d').date()
        return cls(json_dict['version'], json_dict['regulation'], by_date)

    def work_and_expression(self, api: Api):
        meta = (api / 'layer' / 'meta' / 'cfr' / self.version
                / self.regulation).json()
        cfr_title = meta[self.regulation][0]['cfr_title_number']
        work, _ = Work.objects.get_or_create(
            doc_type='cfr', doc_subtype=f'title_{cfr_title}',
            work_id=f'part_{self.regulation}'
        )
        Expression.objects.filter(
            work=work, expression_id=self.version).delete()
        expression = Expression.objects.create(
            work=work, expression_id=self.version, date=self.by_date,
            author='eregs')
        return work, expression


class EregsTree(NamedTuple):
    label: Tuple[str]
    text: str
    node_type: str
    children: Tuple['EregsTree']
    title: str

    _cases = OrderedDict()

    @property
    def label_str(self):
        return '-'.join(self.label)

    @classmethod
    def from_json(cls, json_dict):
        children = tuple(
            cls.from_json(child) for child in json_dict['children'])
        return cls(
            tuple(json_dict['label']), json_dict['text'],
            json_dict['node_type'], children, json_dict.get('title', '')
        )

    @classmethod
    def case(cls, filter_fn: Callable[['EregsTree', Layers], bool]):
        def inner(fn: Callable[['EregsTree', Cursor, Layers], Cursor]):
            cls._cases[filter_fn] = fn
            return fn
        return inner

    def process(self, parent: Cursor, layers: Layers):
        for filter_fn, fn in self._cases.items():
            if filter_fn(self, layers):
                parent = fn(self, parent, layers)
                break

        for child in self.children:
            child.process(parent, layers)


@EregsTree.case(lambda et, layers: et.node_type == 'subpart')
def subpart(et: EregsTree, parent: Cursor, layers: Layers):
    letter = et.label[-1]
    return parent.add_child(CFR.SUBPART, letter,
                            marker=f'Subpart {letter}', title=et.title)


@EregsTree.case(lambda et, layers: et.node_type == 'regtext'
                and len(et.label) == 2)
def section(et: EregsTree, parent: Cursor, layers: Layers):
    _, sect_num, sect_title = et.title.split(' ', 2)
    parent = parent.add_child(CFR.SEC, et.label[-1],
                              marker=f'§ {sect_num}', title=sect_title)
    if et.text:
        parent.add_child(CFR.PAR, text=et.text)
    return parent


@EregsTree.case(lambda et, layers: et.node_type == 'regtext'
                and et.label_str in layers[EregsLayer.P_MARKER])
def marker(et: EregsTree, parent: Cursor, layers: Layers):
    lvl = 1
    ancestors = [parent] + list(parent.ancestors())
    for ancestor in ancestors:
        if ancestor.struct.tag.startswith('lvl'):
            lvl = int(ancestor.struct.tag[len('lvl'):]) + 1
            break

    marker = layers[EregsLayer.P_MARKER][et.label_str][0]['text']
    text = et.text.replace(marker, '', 1).strip()
    return parent.add_child(f'lvl{lvl}', et.label[-1],
                            marker=marker, text=text)


def defines_term(et: EregsTree, layers: Layers):
    for ref in layers[EregsLayer.TERMS]['referenced'].values():
        if ref['reference'] == et.label_str:
            return ref


@EregsTree.case(lambda et, layers: et.node_type == 'regtext'
                and defines_term(et, layers))
def defining_paragraph(et: EregsTree, parent: Cursor, layers: Layers):
    ref = defines_term(et, layers)
    cursor = parent.add_child(CFR.DEFPAR, et.label[-1][1:], text=et.text)
    layer = Layer.objects.create(
        category='define', attributes={'term': ref['term']})
    cursor.extra['spans'] = [
        Span(layer=layer, start=ref['position'][0], end=ref['position'][1]),
    ]
    return cursor


@EregsTree.case(lambda et, layers: et.node_type == 'regtext')
def markerless(et: EregsTree, parent: Cursor, layers: Layers):
    return parent.add_child(CFR.PAR, text=et.text)


def build_tree(api: Api, cfr_part: str, expression_id: str):
    eregs_tree = EregsTree.from_json(
        (api / 'regulation' / cfr_part / expression_id).json())
    layers = {layer: (api / 'layer' / layer.value / 'cfr' / expression_id
                      / cfr_part).json()
              for layer in EregsLayer}
    marker, title = eregs_tree.title.split('—', 1)
    root = new_tree(
        tag='part', tag_number=cfr_part, marker=marker, title=title)
    for eregs_child in eregs_tree.children:
        eregs_child.process(root, layers)
    return root


def fetch_and_save_all(api: Api):
    version_data = (api / 'regulation').json()
    versions = [VersionInfo.from_json(v) for v in version_data['versions']
                if v.get('by_date')]
    for version_info in versions:
        work, expression = version_info.work_and_expression(api)
        root = build_tree(api, version_info.regulation, version_info.version)
        root.renumber()
        for node in root.walk():
            node.struct.expression = expression
            node.struct.save()
            for span in node.extra.get('spans', []):
                span.doc_struct = node.struct
                span.save()
        logger.info('Created %s DocStructs for %s/%s/%s/@%s/%s',
                    root.subtree_size(), work.doc_type, work.doc_subtype,
                    work.work_id, expression.expression_id, expression.author)
