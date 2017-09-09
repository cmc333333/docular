from typing import NamedTuple

from docular.layer.registry import registry


class Define(NamedTuple):
    term: str

    @classmethod
    def from_dict(cls, attrs):
        attrs = dict(attrs)
        if 'name' in attrs:
            del attrs['name']
        return cls(**attrs)

    def serialize(self):
        resp = self._asdict()
        resp['name'] = 'define'
        return resp


class Term(NamedTuple):
    target: str

    @classmethod
    def from_dict(cls, attrs):
        attrs = dict(attrs)
        if 'name' in attrs:
            del attrs['name']
        return cls(**attrs)

    def serialize(self):
        resp = self._asdict()
        resp['name'] = 'term'
        return resp


class InternalCitation(NamedTuple):
    target: str

    @classmethod
    def from_dict(cls, attrs):
        attrs = dict(attrs)
        if 'name' in attrs:
            del attrs['name']
        return cls(**attrs)

    def serialize(self):
        resp = self._asdict()
        resp['name'] = 'internal-citation'
        return resp


class ExternalCitation(NamedTuple):
    target: str

    @classmethod
    def from_dict(cls, attrs):
        attrs = dict(attrs)
        if 'name' in attrs:
            del attrs['name']
        return cls(**attrs)

    def serialize(self):
        resp = self._asdict()
        resp['name'] = 'external-citation'
        return resp


registry['define'] = Define
registry['term'] = Term
registry['internal-citation'] = InternalCitation
registry['external-citation'] = ExternalCitation
