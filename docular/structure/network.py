import networkx as nx
from networkx.algorithms.dag import descendants, topological_sort


class Cursor:
    def __init__(self, graph: nx.DiGraph, key: str):
        self._g = graph
        self._key = key

        key_tail = key.split('__')[-1]
        self.category, self.idx = key_tail.split('_')

    @property
    def obj(self):
        return self._g.node[self._key]['obj']

    @property
    def left(self):
        return self._g.node[self._key]['left']

    @property
    def right(self):
        return self._g.node[self._key]['right']

    def __getitem__(self, child_key):
        full_key = '{0}__{1}'.format(self._key, child_key)
        if full_key not in self._g:
            raise KeyError('No {0} element'.format(full_key))
        return self.__class__(self._g, full_key)

    def add_child(self, obj, category, idx=None, left=None, right=None):
        order = self._g.out_degree(self._key)
        if idx is None:
            idx = str(order + 1)
        full_key = '{0}__{1}_{2}'.format(self._key, category, idx)
        self._g.add_node(full_key, obj=obj, left=left, right=right)
        self._g.add_edge(self._key, full_key, order=order)
        return self.__class__(self._g, full_key)

    def ancestor(self, distance):
        parts = self._key.split('__')
        parts = parts[:-distance]
        return self.__class__(self._g, '__'.join(parts))

    @property
    def parent(self):
        return self.ancestor(1)

    def children(self):
        edges = [(order, idx) for _, idx, order
                 in self._g.out_edges(self._key, data='order')]
        for _, key in sorted(edges):
            yield self.__class__(self._g, key)

    def walk(self):
        for key in topological_sort(self._g, {self._key}):
            yield self.__class__(self._g, key)

    def subtree_size(self):
        return len(descendants(self._g, self._key)) + 1

    def dump(self, dict_fn):
        root = dict_fn(self.obj)
        root['children'] = [child.dump(dict_fn) for child in self.children()]
        return root

    def renumber(self, left=1):
        self._g.node[self._key]['left'] = left
        self._g.node[self._key]['right'] = left + 2*self.subtree_size() - 1

        for child in self.children():
            child.renumber(left + 1)
            left = child.right

    @classmethod
    def new_tree(cls, obj, key, left=None, right=None):
        graph = nx.DiGraph()
        graph.add_node(key, obj=obj, left=left, right=right)
        return cls(graph, key)

    @classmethod
    def from_nested_set(cls, objs):
        root_obj, objs = objs[0], objs[1:]
        root = cls.new_tree(root_obj, root_obj.identifier, root_obj.left,
                            root_obj.right)
        cursor = root

        for obj in objs:
            while obj.left > cursor.right:
                cursor = cursor.parent
            cursor = cursor.add_child(obj, obj.category,
                                      obj.identifier.split('_')[-1],
                                      obj.left, obj.right)
        return root
