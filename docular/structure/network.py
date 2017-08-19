from typing import Optional

import networkx as nx
from networkx.algorithms.dag import descendants, topological_sort

from docular.structure.models import DocStruct


class Cursor:
    def __init__(self, tree: nx.DiGraph, idx: str):
        self._tree = tree
        self._idx = idx

    @property
    def struct(self):
        return self._tree.node[self._idx]['struct']

    @property
    def extra(self):
        extra = self._tree.node[self._idx].get('extra', {})
        self._tree.node[self._idx]['extra'] = extra
        return extra

    def __getitem__(self, child_idx: str):
        identifier = '{0}__{1}'.format(self._idx, child_idx)
        if identifier not in self._tree:
            raise KeyError('No {0} element'.format(identifier))
        return self.__class__(self._tree, identifier)

    def add_child(self, tag: str, tag_number: Optional[str] = None, **attrs):
        order = self._tree.out_degree(self._idx)
        if tag_number is None:
            tag_number = str(order + 1)
        identifier = '{0}__{1}_{2}'.format(self._idx, tag, tag_number)
        self._tree.add_node(identifier, struct=DocStruct(
            identifier=identifier, tag=tag, tag_number=tag_number, **attrs))
        self._tree.add_edge(self._idx, identifier, order=order)
        return self.__class__(self._tree, identifier)

    def subtree_size(self):
        return len(descendants(self._tree, self._idx)) + 1

    def ancestors(self):
        parts = self._idx.split('__')
        for right in range(1, len(parts)):
            yield self.__class__(self._tree, '__'.join(parts[:-right]))

    @property
    def parent(self):
        return next(self.ancestors())

    def children(self):
        edges = [(order, idx) for _, idx, order
                 in self._tree.out_edges(self._idx, data='order')]
        for _, identifier in sorted(edges):
            yield self.__class__(self._tree, identifier)

    def walk(self):
        for identifier in topological_sort(self._tree, {self._idx}):
            yield self.__class__(self._tree, identifier)

    def renumber(self, left=1):
        self.struct.left = left
        self.struct.right = left + 2 * self.subtree_size() - 1

        for child in self.children():
            child.renumber(left + 1)
            left = child.struct.right

    @classmethod
    def load(cls, root_struct, queryset=None):
        if queryset is None:
            queryset = DocStruct.objects
        child_structs = queryset.filter(
            left__gt=root_struct.left, right__lt=root_struct.right,
            entity=root_struct.entity
        ).order_by('left')

        graph = nx.DiGraph()
        graph.add_node(root_struct.identifier, struct=root_struct)
        cursor = Cursor(graph, root_struct.identifier)
        for struct in child_structs:
            while struct.left > cursor.struct.right:
                cursor = cursor.parent
            parent_idx = cursor.struct.identifier
            graph.add_node(struct.identifier, struct=struct)
            graph.add_edge(parent_idx, struct.identifier,
                           order=graph.out_degree(parent_idx))
            cursor = Cursor(graph, struct.identifier)

        return Cursor(graph, root_struct.identifier)


def new_tree(tag, tag_number, **attrs):
    graph = nx.DiGraph()
    identifier = '{0}_{1}'.format(tag, tag_number)
    graph.add_node(identifier, struct=DocStruct(
        identifier=identifier, tag=tag, tag_number=tag_number, **attrs
    ))
    return Cursor(graph, identifier)
