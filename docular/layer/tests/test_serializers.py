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
    assert result == [serializers.InlineContent(None, 'Some text', [])]


@pytest.mark.django_db
def test_content_full_span():
    struct = mommy.make(DocStruct, text='Some text')
    layer = mommy.make(Layer)
    struct.spans.create(start=0, end=len(struct.text), layer=layer)
    result = serializers.ContentSplitter(struct)()
    assert result == [serializers.InlineContent(layer.pk, 'Some text', [])]


@pytest.mark.django_db
def test_content_middle_text():
    struct = mommy.make(DocStruct, text='Some middle text')
    layer = mommy.make(Layer)
    struct.spans.create(start=len('Some '), end=len('Some middle'),
                        layer=layer)
    result = serializers.ContentSplitter(struct)()
    assert result == [
        serializers.InlineContent(None, 'Some ', []),
        serializers.InlineContent(layer.pk, 'middle', []),
        serializers.InlineContent(None, ' text', []),
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
        serializers.InlineContent(first.pk, 'Some ', []),
        serializers.InlineContent(second.pk, 'middle ', []),
        serializers.InlineContent(third.pk, 'text', []),
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
        serializers.InlineContent(None, 'Some ', []),
        serializers.InlineContent(outer.pk, '', [
            serializers.InlineContent(first.pk, 'more', []),
            serializers.InlineContent(None, ' ', []),
            serializers.InlineContent(second.pk, 'text', []),
            serializers.InlineContent(None, ' here', []),
        ]),
    ]


@pytest.mark.django_db
def test_content_overlapping():
    struct = mommy.make(DocStruct, text='123456789')
    first, second, third = mommy.make(Layer, _quantity=3)
    struct.spans.create(start=0, end=5, layer=first)
    struct.spans.create(start=3, end=7, layer=second)
    struct.spans.create(start=4, end=9, layer=third)
    result = serializers.ContentSplitter(struct)()
    assert result == [
        serializers.InlineContent(first.pk, '123', [
            serializers.InlineContent(second.pk, '4', [
                serializers.InlineContent(third.pk, '5', []),
            ]),
        ]),
        serializers.InlineContent(third.pk, '', [
            serializers.InlineContent(second.pk, '67', []),
            serializers.InlineContent(None, '89', []),
        ]),
    ]
