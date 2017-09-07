import pytest
from model_mommy import mommy

from docular.layer import serializers
from docular.layer.models import Layer
from docular.structure.models import DocStruct


@pytest.mark.django_db
def test_content_no_spans():
    struct = mommy.make(DocStruct, text='')
    result = serializers.ContentSplitter(struct)()
    assert result == []


@pytest.mark.django_db
def test_content_only_text():
    struct = mommy.make(DocStruct, text='Some text')
    result = serializers.ContentSplitter(struct)()
    assert result == [serializers.ContentSpan(None, 'Some text', [])]


@pytest.mark.django_db
def test_content_full_span():
    struct = mommy.make(DocStruct, text='Some text')
    layer = mommy.make(Layer)
    struct.spans.create(start=0, end=len(struct.text), layer=layer)
    result = serializers.ContentSplitter(struct)()
    assert result == [serializers.ContentSpan(layer.pk, 'Some text', [])]


@pytest.mark.django_db
def test_content_middle_text():
    struct = mommy.make(DocStruct, text='Some middle text')
    layer = mommy.make(Layer)
    struct.spans.create(start=len('Some '), end=len('Some middle'),
                        layer=layer)
    result = serializers.ContentSplitter(struct)()
    assert result == [
        serializers.ContentSpan(None, 'Some ', []),
        serializers.ContentSpan(layer.pk, 'middle', []),
        serializers.ContentSpan(None, ' text', []),
    ]


@pytest.mark.django_db
def test_content_adjacent_spans():
    struct = mommy.make(DocStruct, text='Some middle text')
    first, second, third = mommy.make(Layer, _quantity=3)
    struct.spans.create(start=0, end=len('Some '), layer=first)
    struct.spans.create(start=len('Some '), end=len('Some middle '),
                        layer=second)
    struct.spans.create(start=len('Some middle '), end=len('Some middle text'),
                        layer=third)
    result = serializers.ContentSplitter(struct)()
    assert result == [
        serializers.ContentSpan(first.pk, 'Some ', []),
        serializers.ContentSpan(second.pk, 'middle ', []),
        serializers.ContentSpan(third.pk, 'text', []),
    ]


@pytest.mark.django_db
def test_content_nested():
    struct = mommy.make(DocStruct, text='Some more text here')
    outer, first, second = mommy.make(Layer, _quantity=3)
    struct.spans.create(start=len('Some '), end=len(struct.text), layer=outer)
    struct.spans.create(start=len('Some '), end=len('Some more'), layer=first)
    struct.spans.create(start=len('Some more '), end=len('Some more text'),
                        layer=second)
    result = serializers.ContentSplitter(struct)()
    assert result == [
        serializers.ContentSpan(None, 'Some ', []),
        serializers.ContentSpan(outer.pk, '', [
            serializers.ContentSpan(first.pk, 'more', []),
            serializers.ContentSpan(None, ' ', []),
            serializers.ContentSpan(second.pk, 'text', []),
            serializers.ContentSpan(None, ' here', []),
        ]),
    ]
