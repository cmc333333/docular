import re

from docular.layer.models import Layer, Span
from docular.structure.network import new_tree


def _parent(cursor, node):
    return cursor.parent


def enter_block_quote(cursor, ast_node):
    return cursor.add_child("blockquote")


def enter_code_block(cursor, ast_node):
    language = ast_node.info.lower()
    language = re.sub('[^a-z0-9]', '', language)
    if language:
        cursor.add_child(f"{language}-codeblock", text=ast_node.literal)
    else:
        cursor.add_child('codeblock', text=ast_node.literal)
    return cursor


def enter_document(cursor, ast_node):
    return new_tree('document')


def enter_emph(cursor, ast_node):
    cursor.extra['span_stack'] = cursor.extra.get('span_stack', [])
    layer, _ = Layer.objects.get_or_create(category='emphasis')
    cursor.extra['span_stack'].append(
        Span(layer=layer, start=len(cursor.struct.text)))
    return cursor


def enter_item(cursor, ast_node):
    return cursor.add_child('item')


def enter_heading(cursor, ast_node):
    return cursor.add_child(f"h{ast_node.level}")


def enter_list(cursor, ast_node):
    return cursor.add_child(ast_node.list_data['type'])


def enter_paragraph(cursor, ast_node):
    return cursor.add_child('par')


def enter_strong(cursor, ast_node):
    cursor.extra['span_stack'] = cursor.extra.get('span_stack', [])
    layer, _ = Layer.objects.get_or_create(category='strong')
    cursor.extra['span_stack'].append(
        Span(layer=layer, start=len(cursor.struct.text)))
    return cursor


def enter_text(cursor, ast_node):
    cursor.struct.text += ast_node.literal
    return cursor


def enter_thematic_break(cursor, ast_node):
    cursor.add_child('thematic-break')
    return cursor


def exit_emph(cursor, ast_node):
    cursor.extra['spans'] = cursor.extra.get('spans', [])

    to_rewind = []
    span = cursor.extra['span_stack'].pop()
    while span.layer.category != 'emphasis':
        to_rewind.append(span)
        span = cursor.extra['span_stack'].pop()

    span.end = len(cursor.struct.text)
    cursor.extra['spans'].append(span)

    cursor.extra['span_stack'].extend(reversed(to_rewind))
    return cursor


def exit_heading(cursor, ast_node):
    cursor.struct.title = cursor.struct.text
    return cursor.parent


def exit_strong(cursor, ast_node):
    cursor.extra['spans'] = cursor.extra.get('spans', [])

    to_rewind = []
    span = cursor.extra['span_stack'].pop()
    while span.layer.category != 'strong':
        to_rewind.append(span)
        span = cursor.extra['span_stack'].pop()

    span.end = len(cursor.struct.text)
    cursor.extra['spans'].append(span)

    cursor.extra['span_stack'].extend(reversed(to_rewind))
    return cursor


exit_block_quote = _parent
exit_item = _parent
exit_list = _parent
exit_paragraph = _parent


skips = (
    'exit_document',
)
