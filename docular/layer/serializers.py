from collections import OrderedDict, defaultdict
from functools import lru_cache
from typing import List, NamedTuple, Optional, Set

from rest_framework import serializers

from docular.layer.models import Span
from docular.structure.models import DocStruct
from docular.structure.serializers import RootSerializer


class Events(NamedTuple):
    starts: List[Span]
    ends: Set[Span]

    @classmethod
    def new(cls, starts=None, ends=None):
        if starts is None:
            starts = []
        if ends is None:
            ends = set()
        return cls(starts, ends)

    def add_start(self, span: Span):
        """Maintain the list in descending order by length."""
        idx = 0
        for existing in self.starts:
            if existing.end < span.end:
                break
            idx += 1
        self.starts.insert(idx, span)


class ContentSpan(NamedTuple):
    layer_id: Optional[int]
    text: str
    children: List['NamedTuple']

    @classmethod
    def new(cls, layer_id=None, text='', children=None):
        if children is None:
            children = []
        return cls(layer_id, text, children)


class ContentSplitter:
    def __init__(self, doc_struct):
        self.events_by_idx = defaultdict(Events.new)
        for span in doc_struct.spans.all():
            self.events_by_idx[span.start].add_start(span)
            self.events_by_idx[span.end].ends.add(span)

        if doc_struct.text and 0 not in self.events_by_idx:
            self.events_by_idx[0] = Events.new()
        if doc_struct.text and len(doc_struct.text) not in self.events_by_idx:
            self.events_by_idx[len(doc_struct.text)] = Events.new()

        breaks = list(sorted(self.events_by_idx))
        self.text_by_idx = OrderedDict()
        for start, end in zip(breaks[:-1], breaks[1:]):
            self.text_by_idx[start] = doc_struct.text[start:end]

    @lru_cache()
    def __call__(self):
        stack = [ContentSpan.new()]
        for start, text in self.text_by_idx.items():
            print(repr(text))
            for _ in self.events_by_idx[start].ends:
                stack.pop()

            spans = [ContentSpan.new(started.layer_id)
                     for started in self.events_by_idx[start].starts]
            if spans:
                spans[-1] = spans[-1]._replace(text=text)
                for span in spans:
                    stack[-1].children.append(span)
                    stack.append(span)
            else:
                span = ContentSpan.new(text=text)
                stack[-1].children.append(span)

        return stack[0].children


class InlineSerializer(RootSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'depth', 'expression', 'children', 'content')

    def get_content(self, instance):
        return ContentSplitter(instance)()
