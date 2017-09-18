from collections import defaultdict
from functools import lru_cache
from io import StringIO
from typing import Any, List, NamedTuple, Optional, Set

from rest_framework import serializers

from docular.layer.models import Span
from docular.structure.models import DocStruct
from docular.structure.serializers import RootSerializer


class Events(NamedTuple):
    starts: List[Span]
    ends: Set[Span]
    text_builder: StringIO

    @property
    def text(self):
        return self.text_builder.getvalue()

    @text.setter
    def text(self, value):
        self.text_builder.write(value)

    @classmethod
    def new(cls, starts=None, ends=None, text=''):
        if starts is None:
            starts = []
        if ends is None:
            ends = set()
        return cls(starts, ends, StringIO(text))

    def add_start(self, span: Span):
        """Maintain the list in descending order by length."""
        idx = 0
        for existing in self.starts:
            if existing.end < span.end:
                break
            idx += 1
        self.starts.insert(idx, span)


class InlineContent(NamedTuple):
    layer: Optional[Any]
    text: str
    children: List['NamedTuple']

    @classmethod
    def new(cls, layer=None, text='', children=None):
        if children is None:
            children = []
        return cls(layer, text, children)

    def serialize(self):
        return {'layer': self.layer and self.layer.serialize(),
                'text': self.text,
                'children': [c.serialize() for c in self.children]}


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
        for start, end in zip(breaks[:-1], breaks[1:]):
            self.events_by_idx[start].text = doc_struct.text[start:end]

        self.stack = [InlineContent.new()]
        self.span_stack = []
        self.reopened = False

    def close_inlines(self, ends, idx):
        ends = {e.layer.data for e in ends}
        while ends:
            span = self.stack.pop()
            span_s = self.span_stack.pop()
            if span.layer in ends:
                ends.remove(span.layer)
            else:
                self.events_by_idx[idx].add_start(span_s)

    def open_inlines(self, events):
        if events.starts:
            spans = [InlineContent.new(s.layer.data) for s in events.starts]
            spans[-1] = spans[-1]._replace(text=events.text)
            for span in spans:
                self.stack[-1].children.append(span)
                self.stack.append(span)
            self.span_stack.extend(events.starts)
        elif events.text:
            span = InlineContent.new(text=events.text)
            self.stack[-1].children.append(span)

    @lru_cache()
    def __call__(self):
        for _idx, events in sorted(self.events_by_idx.items()):
            self.close_inlines(events.ends, _idx)
            self.open_inlines(events)

        return [c.serialize() for c in self.stack[0].children]


class InlineSerializer(RootSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = DocStruct
        fields = ('identifier', 'tag', 'tag_number', 'marker', 'title',
                  'depth', 'children', 'content', 'meta')

    def get_content(self, instance):
        return ContentSplitter(instance)()
